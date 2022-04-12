# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound

class SigninController(http.Controller):

    @http.route('/sign-in', type='http', auth='public', website=True, sitemap=True)
    def sigin_index(self, **kw):
        return request.render('onnet_trial_custom.onnent_signin_views', {
        })

    @http.route('/comfirm-password', type='http', auth='public', website=True, sitemap=True)
    def comfirm_index(self, **kw):
        return request.render('onnet_trial_custom.comfirm_password', {
        })

    @http.route('/web/invite-screen', type='http', auth='public', website=True, sitemap=True)
    def invite_index(self, **kw):
        return request.render('onnet_trial_custom.invite_views', {
        })

    @http.route('/done-screen', type='http', auth='public', website=True, sitemap=True, csrf=False, cors='*')
    def done_index(self, **kw):
        redirect_domain_id = request.session.get('subscription_domain')
        if redirect_domain_id:
            subscription_record = request.env['sale.subscription'].sudo().search([('id', '=', int(redirect_domain_id))])
            return request.render('onnet_trial_custom.done_screen_views', {
                'redirect_domain': subscription_record
            })

    @http.route('/send_email', csrf=False, type='json', auth='public', website=True)
    def send_email(self, arr_key, arr_value):
        template_id = request.env.ref('onnet_trial_custom.patient_card_email_template').id

        template = request.env['mail.template'].sudo().browse(template_id)
        partner_invite = request.session.get('invite_partner')
        domain_invite = request.session.get('subscription_domain')
        partner_name = request.env['res.partner'].sudo().search([('id', '=', int(partner_invite))])
        list_data = dict(zip(arr_key, arr_value))
        subscription_record = request.env['sale.subscription'].sudo().search([('id', '=', int(domain_invite))])
        for key in list_data:
            if template:
                receipt_list = list_data[key]
                email_subject = str(partner_name.name) + " " + "from" + " " + str(partner_name.company_name) + " invites you to connect to HiiBoss"
                body = template.body_html
                body = body.replace('--name--', key)
                body = body.replace('--email--',  list_data[key])
                body = body.replace('--domain--', str(subscription_record.website))
                body = body.replace('--user--', str(partner_name.name))
                body = body.replace('--company--', str(partner_name.company_name))
                mail_values = {
                    'subject': email_subject,
                    'body_html': body,
                    'email_to': receipt_list
                }
                request.env['mail.mail'].sudo().create(mail_values).send()