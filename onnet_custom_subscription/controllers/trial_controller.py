# -*- coding: utf-8 -*-
from requests import get

from odoo import http, fields
from odoo.http import request
from odoo.addons.sale_subscription.controllers.portal import PaymentPortal
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.payment import utils as payment_utils
from odoo.exceptions import ValidationError

class TrialController(http.Controller):

    @http.route('/plans', type='http', auth='public', website=True, sitemap=True)
    def index(self, **kw):
        subscription = request.env['product.template'].sudo().search([])
        industry_management = request.env['industry.management'].search([])

        return request.render('onnet_custom_subscription.website_index_plans', {
            'subscription_plans': subscription,
            'industry_management': industry_management
    })

    @http.route('/active-instance/<int:subscription_id>/<int:partner_id>', type='http', auth='public', website=True, sitemap=True)
    def index_active(self, subscription_id, partner_id):
        if subscription_id and partner_id:
            subscription_record = request.env['sale.subscription'].sudo().search([('id', '=', int(subscription_id))])
            partner = request.env['res.partner'].sudo().search([('id', '=', int(partner_id))])
            subscription_record.create_vive_software()
            request.session['invite_partner'] = partner_id
            request.session['subscription_domain'] = subscription_record.id
            check_pass = request.env['res.users'].sudo().search([('partner_id', '=', partner_id)])
            if not check_pass.password:
                return request.redirect(str(partner.signup_url + '&redirect=invite-screen') or "")
            else:
                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                return request.redirect(str(base_url + '/web/login?redirect=invite-screen') or "")

    @http.route('/firework',  type='http', auth='public', website=True, sitemap=False)
    def firework(self, **kw):
        if kw.get('product_id') and kw.get('industry_id'):
            plans_id = int(kw.get('product_id'))
            industry_id = int(kw.get('industry_id'))
            if not plans_id:
                return request.redirect('/plans/')
            name_plans = request.env['product.template'].sudo().search([('id', '=',  plans_id)]).name
            name_industry = request.env['industry.management'].sudo().search([('id', '=',  industry_id)]).industry_name
            return request.render('onnet_custom_subscription.website_index_firework', {
                'name_plans': name_plans,
                'name_industry': name_industry
            })
        else:
            return request.render('onnet_custom_subscription.website_index_firework')

    @http.route('/create-instance', type='http', auth='public', website=True, sitemap=False)
    def fireworksend(self, **kw):
        id_partner = request.session.get('partner_id_session')

        partner = request.env['res.partner'].sudo().search([('id', '=', id_partner)])
        partner_check = request.env['res.users'].sudo().search([('partner_id', '=', id_partner)])
        subscription_order_id = request.session.get('subscription_order')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # Create user
        if not partner_check:
            request.env['res.users'].sudo().create({
                'active': True,
                'login': partner.email,
                'partner_id': partner.id,
                'instance_url': str(base_url + '/active-instance/' + str(subscription_order_id) + '/' + str(partner.id))
            })
        else:
            partner_check.browse(partner_check.id).sudo().write({
                'instance_url': str(base_url + '/' + str(subscription_order_id) + '/' + str(partner.id))
            })
            self._send_email(id_partner, subscription_order_id)

        return request.redirect('/welcome')

    def _send_email(self, partner_id, subscription_order_id):
        template_id = request.env.ref('onnet_custom_subscription.patient_card_email_active_template').id
        template = request.env['mail.template'].sudo().browse(template_id)

        partner = request.env['res.partner'].sudo().search([('id', '=', partner_id)])
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        sale_sub_id = str(subscription_order_id)
        partner_id = str(partner.id)
        if template:
            receipt_list = partner.email
            email_subject = "Welcome onboard!"
            body = template.body_html
            body = body.replace("--name--", str(partner.name) or "")
            body = body.replace("--email--", str(partner.email) or "")
            body = body.replace("--url_object--",  str(base_url + '/active-instance/' + sale_sub_id + '/' + partner_id) or "")
            mail_values = {
                'subject': email_subject,
                'body_html': body,
                'email_to': receipt_list
            }

            request.env['mail.mail'].sudo().create(mail_values).send()

class InheritSaleSubscription(PaymentPortal):

    @http.route('/my/subscription/transaction/<int:subscription_id>', type='json', auth='public')
    def subscription_transaction(
            self, subscription_id, access_token, is_validation=False, **kwargs
    ):
        """ Create a draft transaction and return its processing values.
        :param int subscription_id: The subscription for which a transaction is made, as a
                                    `sale.subscription` id
        :param str access_token: The UUID of the subscription used to authenticate the partner
        :param bool is_validation: Whether the operation is a validation
        :param dict kwargs: Locally unused data passed to `_create_transaction`
        :return: The mandatory values for the processing of the transaction
        :rtype: dict
        :raise: ValidationError if the subscription id or the access token is invalid
        """
        Subscription = request.env['sale.subscription']
        user = request.env.user
        if user._is_public():  # The user is not logged in
            Subscription = Subscription.sudo()
        subscription_record = Subscription.sudo().search([('id', '=', subscription_id)])
        sub_line = subscription_record.recurring_invoice_line_ids[0]
        Subscription.browse(subscription_id).sudo().write({
            'recurring_invoice_line_ids': sub_line
        })
        request.session['active_invoice'] = 1
        subscription = Subscription.browse(subscription_id).exists()
        # Check the access token against the subscription uuid
        # The fields of the subscription are accessed in sudo mode in case the user is logged but
        # has no read access on the record.
        if not subscription or access_token != subscription.sudo().uuid:
            raise ValidationError("The subscription id or the access token is invalid.")

        kwargs.update(partner_id=subscription.partner_id.id)
        kwargs.pop('custom_create_values', None)  # Don't allow passing arbitrary create values
        common_callback_values = {
            'callback_model_id': request.env['ir.model']._get_id(subscription._name),
            'callback_res_id': subscription.id,
        }
        if not is_validation:  # Renewal transaction
            # Create an invoice to compute the total amount with tax, and the currency
            invoice_values = subscription.sudo().with_context(lang=subscription.partner_id.lang) \
                ._prepare_invoice()  # In sudo mode to read on account.fiscal.position fields
            invoice_sudo = request.env['account.move'].sudo().create(invoice_values)
            kwargs.update({
                'reference_prefix': subscription.code,  # There is no sub_id field to rely on
                'amount': invoice_sudo.amount_total,
                'currency_id': invoice_sudo.currency_id.id,
                'tokenization_requested': True,  # Renewal transactions are always tokenized
            })

            # Delete the invoice to avoid bloating the DB with draft invoices. It is re-created on
            # the fly in the callback when the payment is confirmed.
            invoice_sudo.unlink()

            # Create the transaction. The `invoice_ids` field is populated later with the final inv.
            tx_sudo = self._create_transaction(
                custom_create_values={
                    **common_callback_values,
                    'callback_method': '_reconcile_and_assign_token',
                },
                is_validation=is_validation,
                **kwargs
            )
        else:  # Validation transaction
            kwargs['reference_prefix'] = payment_utils.singularize_reference_prefix(
                prefix='validation'  # Validation transactions use their own reference prefix
            )
            tx_sudo = self._create_transaction(
                custom_create_values={
                    **common_callback_values,
                    'callback_method': '_assign_token',
                },
                is_validation=is_validation,
                **kwargs
            )

        return tx_sudo._get_processing_values()