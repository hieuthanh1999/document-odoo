import json
import logging
import os
import uuid

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from ..helpers import get_bin, execute_sys_command

_logger = logging.getLogger(__name__)

current_path = os.path.join(os.path.dirname(os.path.abspath(__file__))) + "/.."


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    domain = fields.Char(string=_("Domain"))
    kubectl = fields.Char(string=_("Kubectl Path"), compute='_get_bin_path')
    awscli = fields.Char(string=_("Kubectl Path"), compute='_get_bin_path')
    database_password = fields.Char(string=_("Database password"))
    code_lower = fields.Char(string=_("Code Losercase"), compute='_get_code_lower_case')
    
    def _get_code_lower_case(self):
        for subscription in self:
            subscription.code_lower = subscription.code.lower()
    
    @api.model
    def _get_bin_path(self):
        for subscription in self:
            subscription.kubectl, subscription.awscli = get_bin(subscription)

    def create_vive_software(self):
        self.create_database()
        self.create_route_53_record()
        self.create_k8s_pod()

    def create_k8s_pod(self):
        database_endpoint = self.env['ir.config_parameter'].sudo().get_param(
            'vsaas_subscription_aws_k8s.database_endpoint')
        access_key_id = self.env['ir.config_parameter'].sudo().get_param(
            'vsaas_subscription_aws_k8s.access_key_id')
        secret_key = self.env['ir.config_parameter'].sudo().get_param(
            'vsaas_subscription_aws_k8s.secret_key')
        aws_region = self.env['ir.config_parameter'].sudo().get_param(
            'vsaas_subscription_aws_k8s.aws_region')
        aws_s3_bucket_name = self.env['ir.config_parameter'].sudo().get_param(
            'vsaas_subscription_aws_k8s.aws_s3_bucket_name')

        manifests = [
            "default-networkpolicy.yaml",
            "web-namespace.yaml",
            "web-secret.yaml",
            "web-deployment.yaml",
            "web-ingress.yaml",
            "web-service.yaml",
        ]
        env = os.environ.copy()
        aws_bin = self.awscli.strip("/aws")
        env['PATH'] = env["PATH"] + ":/%s" % aws_bin
        user_email = self.partner_id.email
        mail_server = self.env['ir.mail_server'].search([('active', '=', True)], limit=1)
        mail_server_str = '|-|'.join(str(x) for x in [
            mail_server.smtp_host,
            mail_server.smtp_port,
            mail_server.smtp_encryption,
            mail_server.smtp_user,
            mail_server.smtp_pass,
        ])
        for m in manifests:
            manifest_file_path = current_path + "/k8s/%s" % m
            execute_sys_command(' '.join([
                'sed',
                '-e',
                r"'s/${CUSTOMER_NAME}/%s/g'" % self.code_lower,
                '-e',
                r"'s/${DB_HOST}/%s/g'" % database_endpoint,
                '-e',
                r"'s/${DB_PASSWORD}/%s/g'" % self.database_password,
                '-e',
                r"'s/${DB_USER}/%s/g'" % self.code_lower,
                '-e',
                r"'s/${DOMAIN_NAME}/%s/g'" % self.website,
                '-e',
                r"'s/${USER_EMAIL}/%s/g'" % user_email,
                '-e',
                r"'s/${SMTP_SERVER}/%s/g'" % mail_server_str,
                '-e',
                r"'s/${ACCESS_ID}/%s/g'" % access_key_id,
                '-e',
                r"'s/${SECRET_KEY}/%s/g'" % secret_key,
                '-e',
                r"'s/${BUCKET_NAME}/%s/g'" % aws_s3_bucket_name,
                '-e',
                r"'s/${REGION}/%s/g'" % aws_region,
                manifest_file_path,
                " | ",
                self.kubectl,
                "apply",
                "-f",
                "-"
            ]), shell=True, env=env)

    def create_route_53_record(self):
        zone_id = self.env['ir.config_parameter'].sudo().get_param('vsaas_subscription_aws_k8s.route53_hosted_zone_id')
        elb_endpoint = self.env['ir.config_parameter'].sudo().get_param('vsaas_subscription_aws_k8s.elb_endpoint')
        config = {
            "Comment": "Create new record",
            "Changes": [
                {"Action": "CREATE",
                 "ResourceRecordSet":
                     {"Name": self.website,
                      "Type": "CNAME",
                      "TTL": 1200,
                      "ResourceRecords": [
                          {"Value": elb_endpoint}
                      ]
                      }
                 }
            ]
        }
        execute_sys_command([
            self.awscli,
            "route53",
            "change-resource-record-sets",
            "--hosted-zone-id",
            zone_id,
            "--change-batch",
            json.dumps(config)
        ])

    def create_alb(self):
        pass

    def get_database_credentials(self):
        master_db_user = self.env['ir.config_parameter'].sudo().get_param('vsaas_subscription_aws_k8s.database_user')
        master_db_password = self.env['ir.config_parameter'].sudo().get_param('vsaas_subscription_aws_k8s.database_password')
        database_endpoint = self.env['ir.config_parameter'].sudo().get_param('vsaas_subscription_aws_k8s.database_endpoint')
        database_fwd_port = self.env['ir.config_parameter'].sudo().get_param('vsaas_subscription_aws_k8s.database_fwd_port')
        master_database = self.env['ir.config_parameter'].sudo().get_param('vsaas_subscription_aws_k8s.master_database')
        return master_db_user, master_db_password, database_endpoint, database_fwd_port, master_database
        
    def create_database(self):
        db_password = self.generate_random_password()
        master_db_user, master_db_password, database_endpoint, database_fwd_port, master_database = self.get_database_credentials()
        env = os.environ.copy()
        env['PGPASSWORD'] = master_db_password
        try:
            execute_sys_command([
                "psql",
                "-U",
                master_db_user,
                "-d",
                master_database,
                "-p",
                database_fwd_port,
                "-h",
                "localhost",
                "-c",
                "CREATE USER {username} WITH PASSWORD '{password}' CREATEDB LOGIN;".format(username=self.code_lower, password=db_password)
            ], env=env)
            self.write({'database_password': db_password})
        except Exception as e:
            raise ValidationError(_("Failed to connect to the database, please check the configuration to AWS RDS"))
        env['PGPASSWORD'] = db_password
        execute_sys_command([
            "psql",
            "-U",
            self.code_lower,
            "-d",
            master_database,
            "-p",
            database_fwd_port,
            "-h",
            "localhost",
            "-c",
            "CREATE DATABASE {username} WITH OWNER '{username}'".format(username=self.code_lower)
        ], env=env)

    def generate_random_password(self):
        return str(uuid.uuid4())

    def cleanup_vive_software(self):
        self.cleanup_k8s()
        self.cleanup_database()
        self.cleanup_route_53_record()

    def cleanup_database(self):
        master_db_user, master_db_password, database_endpoint, database_fwd_port, master_database = self.get_database_credentials()
        env = os.environ.copy()
        env['PGPASSWORD'] = self.database_password
        try:
            execute_sys_command([
                "psql",
                "-U",
                self.code_lower,
                "-d",
                master_database,
                "-p",
                database_fwd_port,
                "-h",
                "localhost",
                "-c",
                "DROP DATABASE {username} WITH (FORCE)".format(username=self.code_lower)
            ], env=env)
        except Exception as e:
            raise ValidationError(_("Failed to connect to the database, please check the configuration to AWS RDS"))

        env['PGPASSWORD'] = master_db_password
        execute_sys_command([
            "psql",
            "-U",
            master_db_user,
            "-p",
            database_fwd_port,
            "-d",
            master_database,
            "-h",
            "localhost",
            "-c",
            "DROP USER {username};".format(username=self.code_lower)
        ], env=env)

    def cleanup_k8s(self):
        env = os.environ.copy()
        aws_bin = self.awscli.strip("/aws")
        env['PATH'] = env["PATH"] + ":/%s" % aws_bin
        # Remove deployment, ingress, secret, service, ... within subscription's namespace
        execute_sys_command([
            self.kubectl,
            "delete",
            "all",
            "--all",
            "-n",
            self.code_lower
        ], env=env)

        # Remove deployment, ingress, secret, service, ... within subscription's namespace
        execute_sys_command([
            self.kubectl,
            "delete",
            "namespaces",
            self.code_lower
        ], env=env)

    def cleanup_route_53_record(self):
        zone_id = self.env['ir.config_parameter'].sudo().get_param('vsaas_subscription_aws_k8s.route53_hosted_zone_id')
        elb_endpoint = self.env['ir.config_parameter'].sudo().get_param('vsaas_subscription_aws_k8s.elb_endpoint')
        config = {
            "Comment": "Delete record for subscription: %s" % self.code_lower,
            "Changes": [
                {"Action": "DELETE",
                 "ResourceRecordSet":
                     {"Name": self.website,
                      "Type": "CNAME",
                      "TTL": 120,
                      "ResourceRecords": [
                          {"Value": elb_endpoint}
                      ]
                      }
                 }
            ]
        }
        execute_sys_command([
            self.awscli,
            "route53",
            "change-resource-record-sets",
            "--hosted-zone-id",
            zone_id,
            "--change-batch",
            json.dumps(config)
        ])