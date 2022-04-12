# -*- coding: utf-8 -*-
import datetime
from odoo import http, fields, _
from odoo.http import request
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.addons.website_sale.controllers.main import WebsiteSale
from dateutil.relativedelta import relativedelta
import logging
from markupsafe import Markup
from bs4 import BeautifulSoup
from datetime import timedelta
from datetime import datetime

_logger = logging.getLogger(__name__)

import psycopg2
import json
import uuid
from werkzeug.exceptions import Forbidden, NotFound

class Signup(http.Controller):

    @http.route('/pricing-plans', auth='public', website=True)
    def customer_pricing_plans(self, **kw):
        if not (kw.get('industry') and kw.get('plan')):
            return request.redirect('/plans/')
        countries = request.env['res.country'].sudo().search([])
        langs = request.env['res.lang'].sudo().search([])
        partner_id = int(request.env.user.partner_id.id)
        partner_info = request.env.user.partner_id
        # default trial = 1 user trial, trial = 2 user book now
        trial = 2
        industry = request.env['industry.management'].search([('id', '=', kw.get('industry'))])
        subscription = request.env['product.template'].sudo().search([('industry', '=', industry.id)])
        pricelist = request.website.get_current_pricelist()
        plan_id = kw.get('plan')
        plan_active = request.env['product.template'].sudo().search([('id', '=', kw.get('plan'))])
        text_popular = request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.text_popular')
        annually_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.annually_product_pricelist'))
        month_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.month_product_pricelist'))
        annually = request.env['product.pricelist'].search([('id', '=', annually_id)])
        month = request.env['product.pricelist'].search([('id', '=', month_id)])
        if request and request.session.get('website_sale_current_pl'):
            pricelist_id = request.session['website_sale_current_pl']
        else:
            request.session['website_sale_current_pl'] = annually_id
            pricelist_id = annually_id
        if kw.get('trial'):
            trial = kw.get('trial')
        most_popular = False
        for sub in subscription:
            if sub.priority == '1':
                most_popular = True

        values = {
            'users_num': 1,
            'subscription_plans': subscription,
            'industry': industry,
            'pricelist_id': pricelist_id,
            'product': plan_active,
            'product_id': int(plan_id),
            'trial': int(trial),
            'checkout': partner_info,
            'countries': countries,
            'langs': langs,
            'annually_id': annually_id,
            'month_id': month_id,
            'annually': annually,
            'month': month,
            'text_popular': text_popular,
            'most_popular': most_popular,
        }
        return http.request.render('onnet_customer_signup.pricing_plan', values)

    def _checkout_form_save(self, mode, checkout, all_values):
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            partner_id = Partner.sudo().with_context(tracking_disable=True).create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    @http.route('/plans/step1', csrf=False, type='json', auth='public', website=True)
    def get_addon_ajax(self, trial, product_order):
        addons = request.env['product.template']
        line_ids = []
        if product_order:
            line_ids = product_order.split(',')
            line_ids = [int(numeric_string) for numeric_string in line_ids]
        values = {
            'html': request.env.ref('onnet_customer_signup.view_addons')._render({
                'add_ons': addons.sudo().search([]),
                'trial': int(trial),
                'product_order': line_ids,
            })
        }
        return values

    @http.route('/plans/step2', csrf=False, type='json', auth='public', website=True)
    def get_addon_ajax_step2(self, trial):
        countries = request.env['res.country'].sudo().search([])
        langs = request.env['res.lang'].sudo().search([])
        if request.env.user.partner_id.id:
            partner_id = int(request.env.user.partner_id.id)
            partner_info = request.env.user.partner_id
        else:
            partner_id = int(-1)
            partner_info =[]
        seting_domain = request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.config_domain')
        values = {
            'html': request.env.ref('onnet_customer_signup.review_order_ajax')._render({
                'trial': int(trial),
                'countries': countries,
                'langs': langs,
                'checkout': partner_info,
                'partner_id': partner_id,
                'seting_domain': seting_domain,
            })
        }
        return values

    @http.route('/plans/step3', csrf=False, type='json', auth='public', website=True)
    def get_addon_ajax_step3(self, trial, reg_name, reg_email, reg_phone, reg_company_name, reg_country, reg_language_id, reg_domain, product_order, product_id, number_user, reg_industry):
        pricelist_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.annually_product_pricelist'))
        if request and request.session.get('website_sale_current_pl'):
            pricelist_id = request.session['website_sale_current_pl']
        if int(trial) == 1:
            pricelist_id = int(request.env['ir.config_parameter'].sudo().get_param(
                'onnet_custom_subscription.month_product_pricelist'))
        if request.env.user.partner_id.id:
            partner_id = int(request.env.user.partner_id.id)
            mode = ('edit', 'billing')
        if partner_id ==4:
            mode = ('new', 'billing')
        post = {
            'name': reg_name,
            'email': reg_email,
            'phone': reg_phone,
            'company_name': reg_company_name,
            'country_id': int(reg_country),
            'lang': reg_language_id,
        }
        all_values = {
            'name': reg_name,
            'email': reg_email,
            'phone': reg_phone,
            'company_name': reg_phone,
            'country_id': int(reg_country),
            'lang': reg_language_id,
            'website': reg_domain,
            'submitted': '1',
            'partner_id': partner_id,
            'callback': '',
            'field_required': 'phone,name'
        }
        line_ids = []
        if product_order:
            line_ids = product_order.split(',')
            line_ids = [int(numeric_string) for numeric_string in line_ids]
        # create sale order
        order_lines = []
        invoice_lines = []
        # Stage
        trial_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.sale_subscription_trial'))
        draft_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.sale_subscription_draft'))
        if int(trial) == 1:
            id_stage = trial_id
        else:
            id_stage = draft_id
        products_plan = request.env['product.template'].sudo().search([('id', '=', product_id)])
        request.session['buy_subscription_id'] = product_id
        request.session['buy_industry_id'] = reg_industry
        if products_plan:
            product_pro = request.env['product.product'].sudo().search([('product_tmpl_id', '=', products_plan.id)], limit=1)
            price_plan = product_pro.list_price
            pricelist_plan = products_plan._get_combination_info(False, int(product_pro.id or 0), int(number_user), request.env['product.pricelist'].browse(int(pricelist_id)))
            if int(trial) == 1:
                price_plan = 0
            else:
                if pricelist_plan['list_price']:
                    price_plan = pricelist_plan['list_price']
            if product_pro:
                order_lines.append((0, 0, {
                    'product_id': product_pro.id,
                    'name': product_pro.name,
                    'product_uom_qty': int(number_user),
                    'price_unit': price_plan,
                }))
                invoice_lines.append((0, 0, {
                    'name': product_pro.name,
                    'product_id': product_pro.id,
                    'quantity': int(number_user),
                    'price_unit': price_plan,
                    'uom_id': product_pro.uom_id.id,
                }))
        list_products = request.env['product.template'].sudo().search([('id', 'in', line_ids)])
        for line in list_products:
            product_addon = request.env['product.product'].sudo().search([('product_tmpl_id', '=', line.id)], limit=1)
            price_pro = product_addon.list_price
            if int(trial) == 1:
                price_pro = 0
            if product_addon:
                order_lines.append((0, 0, {
                    'product_id': product_addon.id,
                    'name': product_addon.name,
                    'product_uom_qty': 1,
                    'price_unit': price_pro,
                }))
                invoice_lines.append((0, 0, {
                    'name': product_addon.name,
                    'product_id': product_addon.id,
                    'quantity': 1,
                    'price_unit': price_pro,
                    'uom_id': product_pro.uom_id.id,
                }))

        partner_id = self._checkout_form_save(mode, post, all_values)
        request.session['partner_id_session'] = partner_id
        sale_orders = {
            'partner_id': partner_id,
            'date_order': fields.Datetime.now(),
            'order_line': order_lines,
            'pricelist_id': pricelist_id,
        }
        #  id template
        annually_template = int(
            request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.annually_template'))
        month_template = int(
            request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.month_template'))
        trial_template = int(
            request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.trial_template'))
        annually_id = int(
            request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.annually_product_pricelist'))
        seting_domain = request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.config_domain')
        #  created sale order
        order = request.env['sale.order'].sudo().create(sale_orders)
        date_start = fields.Datetime.now()
        if pricelist_id == annually_id:
            recurring_next_date = fields.Datetime.now() + relativedelta(years=1)
            template_id = annually_template
        else:
            recurring_next_date = fields.Datetime.now() + relativedelta(months=1)
            template_id = month_template
        is_check = True
        if int(trial) == 1:
            template_id = trial_template
            days = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.trial_period'))
            recurring_next_date = fields.Datetime.now() + relativedelta(days=days)
            is_check = False

        domain = reg_domain + '.' + seting_domain
        subscription_order = request.env['sale.subscription'].sudo().create({
            'name': 'Subscription book',
            'partner_id': partner_id,
            'pricelist_id': pricelist_id,
            'template_id': template_id,
            'date_start': date_start,
            'recurring_next_date': recurring_next_date,
            'stage_id': id_stage,
            'order_id': order.id,
            'website': domain,
            'is_check_trial': is_check
        })
        # create product subcription
        subscription_order.write({'recurring_invoice_line_ids': invoice_lines})
        request.session['subscription_order'] = subscription_order.id
        render_values = {
            'trial': int(trial),
            'checkout': post,
            'partner_id': partner_id,
        }
        if order:
            request.session['my_orders_plans'] = order.id
            request.session['sale_order_id'] = order.id
            render_values.update({
                'website_sale_order': order,
                'order': order,
                'currency': order.currency_id,
                'amount': order.amount_total,
                'partner_id': order.partner_id.id,
                'total_price': order.amount_total,
                'access_token': order._portal_ensure_token(),
                'transaction_route': f'/shop/payment/transaction/{order.id}',
                'landing_route': '/shop/payment/validate',
            })
        acquirers_sudo = request.env['payment.acquirer'].sudo().search([('state', 'in', ['enabled', 'test'])])
        logged_in = not request.env.user._is_public()
        tokens = request.env['payment.token'].sudo().search(
            [('acquirer_id', 'in', acquirers_sudo.ids), ('partner_id', '=', order.partner_id.id)]
        ) if logged_in else request.env['payment.token']
        render_values.update({
            'acquirers': acquirers_sudo,
            'tokens': tokens
        })
        if int(trial) == 1:
            id_language = request.env['res.lang'].sudo().search([('code', '=', reg_language_id)])
            lead_line = self.save_lead_line(int(reg_industry), line_ids, int(product_id))
            request.env['crm.lead'].sudo().create({
                'name': reg_name,
                'contact_name': reg_name,
                'partner_name': reg_company_name,
                'email_from': reg_email,
                'phone': reg_phone,
                'lang_id': int(id_language),
                'country_id': int(reg_country),
                'lead_line': lead_line
            })
            values = {
                'trial': int(trial),
                'id_plans': product_id
            }
        else:
            values = {
                'trial': int(trial),
                'order_id': order.id
             }
        return values

    def save_lead_line(self, id_industry, list_addons_id, subscription_id):
        lead_line = []
        industry = request.env['industry.management'].search([('id', '=', id_industry)])
        lead_line.append((0, 0, {
            'name': 'Industry:' + ' ' + industry.industry_name
        }))
        subscription = request.env['product.template'].sudo().search([('id', '=', subscription_id)])
        lead_line.append((0, 0, {
            'name': 'Subscription Plans:' + ' ' + subscription.name
        }))
        for product_line in list_addons_id:
            item = request.env['product.template'].sudo().search([('id', '=', int(product_line))])
            lead_line.append((0, 0, {
                'name': 'Add-on:' + ' ' + item.name
            }))
        return lead_line

    @http.route('/pricing-payment', csrf=False, type='http', auth='public', website=True)
    def customer_payment_order(self, **kw):
        if request.session.get('my_orders_plans'):
            order_id = request.session['my_orders_plans']
        else:
            return request.redirect('/plans/')
        if order_id:
            order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
        annually_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.annually_product_pricelist'))
        month_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.month_product_pricelist'))
        annually = request.env['product.pricelist'].sudo().search([('id', '=', annually_id)])
        month = request.env['product.pricelist'].sudo().search([('id', '=', month_id)])
        render_values = {
            'website_sale_order': order,
            'order': order,
            'currency': order.currency_id,
            'amount': order.amount_total,
            'partner_id': order.partner_id.id,
            'total_price': order.amount_total,
            'access_token': order.access_token,
            'transaction_route': f'/shop/payment/transaction/{order.id}',
            'landing_route': '/shop/payment/validate',
            'annually': annually,
            'month': month,
        }
        acquirers_sudo = request.env['payment.acquirer'].sudo().search([('state', 'in', ['enabled', 'test'])])
        render_values.update({
            'acquirers': acquirers_sudo,
            'tokens': request.env['payment.token'].search(
                [('acquirer_id', 'in', acquirers_sudo.ids)])
        })
        return http.request.render('onnet_customer_signup.payment', render_values)

    # check user
    @http.route('/check-user', csrf=False, type='json', auth='public', website=True)
    def ajax_check_user(self, email=None, partner_id = None):
        check = False
        if email:
            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            user_curent = request.env['res.partner'].sudo().search(
                [('email', '=', email)], limit=1)
            if user or user_curent:
                check = True
                user_curent = request.env['res.partner'].sudo().search(
                [('email', '=', email), ('id', '=', partner_id)], limit=1)
                if user_curent:
                    check = False
        return check

    # check domain
    @http.route('/check-domain', csrf=False, type='json', auth='public', website=True)
    def ajax_check_domain(self, domain):
        check = 2
        seting_domain = request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.config_domain')
        if domain:
            domain = domain + '.' + seting_domain
            domain_exist = request.env['sale.subscription'].sudo().search([('website','=', domain)])
            if domain_exist:
                check = 1
        values = {
            'check': check
        }

        return values

class OrderSubcriptionData(PaymentPostProcessing):

    @http.route('/payment/status/poll', type='json', auth='public')
    def poll_status(self):
        """ Fetch the transactions to display on the status page and finalize their post-processing.

              :return: The post-processing values of the transactions
              :rtype: dict
              """
        # Retrieve recent user's transactions from the session
        limit_date = fields.Datetime.now() - timedelta(days=1)
        monitored_txs = request.env['payment.transaction'].sudo().search([
            ('id', 'in', self.get_monitored_transaction_ids()),
            ('last_state_change', '>=', limit_date)
        ])
        if not monitored_txs:  # The transaction was not correctly created
            return {
                'success': False,
                'error': 'no_tx_found',
            }

        # Build the list of display values with the display message and post-processing values
        display_values_list = []
        for tx in monitored_txs:
            display_message = None
            # get stage config
            progress_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.sale_subscription_progress'))
            maitenance_id = int(request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.sale_subscription_maintain'))
            progress_order = request.env['sale.subscription.stage'].sudo().search([('id', '=', progress_id)])
            maitenance_order = request.env['sale.subscription.stage'].sudo().search([('id', '=', maitenance_id)])
            subscription_order = request.env['sale.subscription'].sudo().search([('order_id', '=', tx.sale_order_ids.id)])
            subscription_order_active = request.env['sale.subscription'].sudo().search([('code', '=', tx.sale_order_ids.origin)])
            if tx.state == 'pending':
                display_message = tx.acquirer_id.pending_msg
            elif tx.state == 'done':
                active_invoice = request.session.get('active_invoice')
                # active_buy = request.session.get('check_buy')
                if subscription_order:
                    if not active_invoice and not active_invoice == 1:
                        if not subscription_order.is_check_trial == True:
                                # order line
                                sale_orders = {
                                    'date_order': fields.Datetime.now()
                                }
                                month_template_id = int(
                                    request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.month_template'))
                                sale_subs = {
                                    'name': 'Subscription book',
                                    'partner_id': subscription_order.partner_id.id,
                                    'pricelist_id': subscription_order.pricelist_id.id,
                                    'template_id': month_template_id,
                                    'date_start': fields.Datetime.now(),
                                    'recurring_next_date': fields.Datetime.now() + relativedelta(months=1),
                                    'stage_id': int(progress_order),
                                    'order_id': int(subscription_order.order_id.id)
                                }
                                sale_id_product = request.env['sale.subscription'].sudo().search(
                                    [('id', '=', int(subscription_order.id))]).recurring_invoice_line_ids.product_id
                                sale_id_line = request.env['sale.subscription'].sudo().search(
                                    [('id', '=', int(subscription_order.id))]).recurring_invoice_line_ids
                                product_list = request.env['product.product'].sudo().search(
                                    [('id', 'in', sale_id_product.mapped('id'))])

                                order_line_id = request.env['sale.order'].sudo().search(
                                    [('id', '=', int(subscription_order.id))]).order_line.product_id
                                order_line = request.env['sale.order'].sudo().search([('id', '=', int(subscription_order.order_id.id))]).order_line
                                product_list_order = request.env['product.product'].sudo().search(
                                    [('id', 'in', order_line_id.mapped('id'))])

                                if int(subscription_order.id):
                                #Change order
                                    self._save_change_sale_line(sale_id_line, product_list)
                                    self._save_change_sale_order(sale_orders, int(subscription_order.order_id.id))
                                    self._save_change_sale_subscription(sale_subs, int(subscription_order.id))
                                    self._handling_order_line(order_line, product_list_order)
                                    subscription_order.browse(int(subscription_order.id)).sudo().write({
                                        'is_check_trial': True
                                    })
                                    self._send_active(subscription_order)
                                    request.session['active_firework'] = 1
                                    request.session['session_subscription_redirect'] = subscription_order.id
                                    request.session['sale_order_id'] = subscription_order.id
                                request.session['total_price'] = 0
                                display_message = tx.acquirer_id.done_msg
                        if subscription_order_active.stage_id.id == progress_order.id:
                            subscription_order_active.write(
                                {'stage_id': int(maitenance_order.id), 'to_renew': False, 'is_extra_maintenance': True})
                        else:
                            subscription_order.write({'stage_id': int(progress_order)})
                request.session['active_invoice'] = 0
            elif tx.state == 'cancel':
                display_message = tx.acquirer_id.cancel_msg
            display_values_list.append({
                'display_message': display_message,
                **tx._get_post_processing_values(),
            })

        # Stop monitoring already post-processed transactions
        post_processed_txs = monitored_txs.filtered('is_post_processed')
        self.remove_transactions(post_processed_txs)

        # Finalize post-processing of transactions before displaying them to the user
        txs_to_post_process = (monitored_txs - post_processed_txs).filtered(
            lambda t: t.state == 'done'
        )
        success, error = True, None
        try:
            txs_to_post_process._finalize_post_processing()
        except psycopg2.OperationalError:  # A collision of accounting sequences occurred
            request.env.cr.rollback()  # Rollback and try later
            success = False
            error = 'tx_process_retry'
        except Exception as e:
            request.env.cr.rollback()
            success = False
            error = str(e)
            _logger.exception(
                "encountered an error while post-processing transactions with ids %s:\n%s",
                ', '.join([str(tx_id) for tx_id in txs_to_post_process.ids]), e
            )

        return {
            'success': success,
            'error': error,
            'display_values_list': display_values_list,
        }

    # function save change product template
    def _save_change_sale_subscription(self, data_change, id_sale):
        subscriptions_model = request.env['sale.subscription']
        if id_sale:
            subscriptions_model.browse(id_sale).sudo().write(data_change)

    # function save change product template
    def _save_change_sale_order(self, data_chage, id_order):
        subscriptions_model = request.env['sale.order']
        if id_order:
            subscriptions_model.browse(id_order).sudo().write(data_chage)

    # Change Sale Subscription Line
    def _save_change_sale_line(self, sale_id_line, product_list):
        line_model = request.env['sale.subscription.line']
        for id_line in sale_id_line:
            for id_product in product_list:
                if int(id_line.product_id) == int(id_product.id):
                    if id_product.quantity_user:
                        line_model.browse(int(id_line)).sudo().write({
                            'name': id_product.name,
                            'product_id': id_product.id,
                            'quantity': id_product.quantity_user,
                            'price_unit': id_product.list_price,
                            'uom_id': 1
                        })
                    else:
                        line_model.browse(int(id_line)).sudo().write({
                            'name': id_product.name,
                            'product_id': id_product.id,
                            'quantity': 1,
                            'price_unit': id_product.list_price,
                            'uom_id': 1
                        })
                    break

    def _handling_order_line(self, order_line_id, product_list_order):
        #  created sale order
        model_order_line = request.env['sale.order.line']
        for id_line in order_line_id:
            for id_product in product_list_order:
                if int(id_line.product_id) == int(id_product.id):
                    if id_product.quantity_user:
                        model_order_line.browse(int(id_line)).sudo().write({
                            'product_id': id_product.id,
                            'name': id_product.name,
                            'product_uom_qty': id_product.quantity_user,
                            'price_unit': id_product.list_price,
                        })
                    else:
                        model_order_line.browse(int(id_line)).sudo().write({
                            'product_id': id_product.id,
                            'name': id_product.name,
                            'product_uom_qty': 1,
                            'price_unit': id_product.list_price,
                        })
                    break

    def _send_active(self, subsctiption):
        template_id = request.env.ref('onnet_customer_signup.active_sale_subscription_to_trial').id
        template = request.env['mail.template'].sudo().browse(template_id)
        if template:
            receipt_list = subsctiption.partner_id.email
            email_subject = "Upgrade Trial!"
            body = template.body_html
            i = 1
            texts = ''
            for index in subsctiption.recurring_invoice_line_ids:
                texts += Markup('<tr style="text-align:center;">') + Markup('<td style="padding:10px;">') \
                         + str(i) + Markup('</td>') + Markup('<td style="padding:10px;">') \
                         + str(index.name) + Markup('</td>') + Markup('<td style="padding:10px;">') \
                         + str(index.quantity) + Markup('</td>') + Markup('<td style="padding:10px;">') \
                         + str("{:,.2f}".format(index.price_unit)) + ' ' + str(index.currency_id.name) + Markup('</td>') + Markup('<td style="padding:10px;">') \
                         + str("{:,.2f}".format(index.price_subtotal)) + ' ' + str(index.currency_id.name) + Markup('</td></tr>')
                i += 1

            body = body.replace("--code--", str(subsctiption.code) or "")
            body = body.replace("--name--", str(subsctiption.partner_id.name) or "")
            body = body.replace("--row--", texts or "")
            body = body.replace("--date--", str(datetime.today().strftime('%Y-%m-%d')) or "")
            body = body.replace("--subtotal--", str("{:,.2f}".format(subsctiption.recurring_total)) or "")
            body = body.replace("--taxes--", str("{:,.2f}".format(subsctiption.recurring_tax)) or "")
            body = body.replace("--amount--", str("{:,.2f}".format(subsctiption.recurring_total_incl)) or "")
            body = body.replace("--currency--", str(index.currency_id.name) or "")

            mail_values = {
                'subject': email_subject,
                'body_html': body,
                'email_to': receipt_list
            }

            request.env['mail.mail'].sudo().create(mail_values).send()




class WebsiteSaleInherit(WebsiteSale):
    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        active_fire = request.session.get('active_firework')
        sale_sub_trial = request.session.get('session_subscription_redirect')
        if not order or (order.amount_total and not tx):
            if active_fire == 1 and sale_sub_trial:
                uuid_token = request.env['sale.subscription'].sudo().search([('id', '=', int(sale_sub_trial))])
                request.session['active_firework'] = 0
                return request.redirect('/my/subscription/' + str(sale_sub_trial) + '/' + str(uuid_token.uuid))

        if order and not order.amount_total and not tx:
            order.with_context(send_email=True).action_confirm()
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        PaymentPostProcessing.remove_transactions(tx)
        
        if active_fire == 1 and sale_sub_trial:
            uuid_token = request.env['sale.subscription'].sudo().search([('id', '=', int(sale_sub_trial))])
            request.session['active_firework'] = 0
            return request.redirect('/my/subscription/' + str(sale_sub_trial) + '/' + str(uuid_token.uuid))

        subscription_buy = request.session.get('buy_subscription_id')
        industry_buy = request.session.get('buy_industry_id')
        return request.redirect('/firework?product_id=' + str(subscription_buy) + '&industry_id=' + str(industry_buy))


