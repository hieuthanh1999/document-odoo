# -*- coding: utf-8 -*-
from werkzeug.exceptions import Forbidden

import odoo
import werkzeug
from odoo import http, fields, _
from dateutil.relativedelta import relativedelta
from odoo.http import request
from datetime import datetime, timedelta
# from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager
import uuid

class ModalAccountInherit(odoo.addons.sale_subscription.controllers.portal.SaleSubscription):

    @http.route(
        ['/my/subscription/<int:subscription_id>',
         '/my/subscription/<int:subscription_id>/<string:access_token>'],
        type='http', methods=['GET'], auth='public', website=True
    )
    def subscription(self, subscription_id, access_token='', message='', message_class='', **kw):
        res = super(ModalAccountInherit, self).subscription(subscription_id, access_token, message, message_class, **kw)
        values = res.qcontext
        countries = request.env['res.country'].sudo().search([])
        langs = request.env['res.lang'].sudo().search([])
        exp_date = values['account'].recurring_next_date.strftime('%b %d,%Y')
        order_line_grade = request.env['sale.order'].sudo().search(
            [('state', '=', 'sale'),('origin', '=', values['account'].code)], limit =1)
        data = {
            'countries': countries,
            'langs': langs,
            'exp_date': exp_date,
        }
        if order_line_grade:
            data.update({
                'display_edit': False
            })
        else:
            data.update({
                'display_edit': True
            })
        if values['account'].stage_category == 'maintenance' or values['account'].stage_category == 'cancel':
            values['display_close'] = False
        else:
            values['display_close'] = True
        values.update(data)
        return http.request.render('sale_subscription.subscription', values)

    @http.route('/data', csrf=False, type='json', auth='public', website=True)
    def get_ajax_order(self, id_sub, stage, id_order):
        if int(id_sub):
            sale_sub = request.env['sale.subscription'].sudo().search(
                [('id', '=', int(id_sub))]).recurring_invoice_line_ids.product_id
        else:
            sale_sub = []

        product_list = request.env['product.product'].sudo().search([('id', 'in', sale_sub.mapped('id'))])
        if int(id_sub) and stage and int(id_order):
            if stage == 'trial':
                values = {
                    'html': request.env.ref('onnet_subscription_account.order_view_plans')._render({
                        'list_product': product_list,
                    }),
                    'check_active': 1
                }
            else:
                values = {
                    'check_active': 2
                }
        return values

    @http.route('/data/5', csrf=False, type='json', auth='public', website=True)
    def get_ajax_andress(self, id_sub, total=None, product_id=None, type=None, quantity=None, credit=None, price_new_one_user=None):
        if int(id_sub):
            account = request.env['sale.subscription'].sudo().search([('id', '=', int(id_sub))])

        countries = request.env['res.country'].sudo().search([])
        langs = request.env['res.lang'].sudo().search([])

        values = {
            'html': request.env.ref('onnet_subscription_account.andress_order_sub')._render({
                'account': account,
                'countries': countries,
                'langs': langs,
                'product_id': product_id,
                'quantity': quantity,
                'type': type,
                'credit': credit,
                'price_new_one_user': price_new_one_user,
                'total': total,
                'partner_id': account.partner_id.id,
            })
        }

        return values

    @http.route('/data/6', csrf=False, type='json', auth='public', website=True)
    def get_ajax_order_view(self, id_sub, data_info):

        if int(id_sub):
            account = request.env['sale.subscription'].sudo().search([('id', '=', int(id_sub))])
            id_partner_sub = int(account.partner_id.id)
            order_id = request.env['sale.subscription'].sudo().search([('id', '=', int(id_sub))]).order_id.id
            # Set Stage
            draft_id = request.env['ir.config_parameter'].sudo().get_param(
                'onnet_custom_subscription.sale_subscription_draft')
            draft_order = request.env['sale.subscription.stage'].sudo().search([('id', '=', int(draft_id))])
        if data_info:
            data_partner = {
                'name': data_info.get('name'),
                'email': data_info.get('email'),
                'phone': data_info.get('phone'),
                'company_name': data_info.get('company'),
                'country_id': int(data_info.get('country')),
                'lang': data_info.get('lang'),
            }

        # partner id
        partner_id = self._save_edit_partner(data_partner, id_partner_sub)
        if int(id_sub):
            request.session['total_price'] = data_info.get('total_price')

        request.session['id_order'] = int(order_id)

    @http.route('/plans/payment', csrf=False, type='http', auth='public', website=True)
    def customer_payment_order(self, **kw):
        if request.session.get('id_order'):
            order_id = request.session.get('id_order')
        else:
            return request.redirect('/my/home/')
        if order_id:
            order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
        if request.session.get('total_price'):
            total_price = request.session.get('total_price')
        else:
            total_price = order.amount_total

        render_values = {
            'partner_id': order.partner_id.id,
            'website_sale_order': order,
            'order': order,
            'currency': order.currency_id,
            'amount': total_price,
            'total_price': total_price,
            'access_token': order.access_token,
            'transaction_route': f'/shop/payment/transaction/{order.id}',
            'landing_route': '/shop/payment/validate',
        }
        acquirers_sudo = request.env['payment.acquirer'].sudo().search([('state', 'in', ['enabled', 'test'])])
        render_values.update({
            'acquirers': acquirers_sudo,
            'tokens': request.env['payment.token'].search(
                [('acquirer_id', 'in', acquirers_sudo.ids)])
        })

        return http.request.render('onnet_subscription_account.payment', render_values)

    # function save change partner
    def _save_edit_partner(self, data_chage, partner_id):
        partner_model = request.env['res.partner']
        if partner_id:
            partner_model.browse(partner_id).sudo().write(data_chage)
        return partner_id

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

    # modal order subscription
    @http.route('/showproduct', csrf=False, type='json', auth='public', website=True)
    def modal_upsell_order(self, data):
        values = {
            'order_id': data['id_order']
        }
        if int(data['id_order']):
            sale_sub = request.env['sale.subscription'].sudo().search(
                [('id', '=', int(data['id_order']))]).recurring_invoice_line_ids.product_id
            product_id = sale_sub[0]
            if data['type'] == 'upgrade':
                product_list = request.env['product.template'].sudo().search([('list_price', '>=', sale_sub[0].list_price), ('id', '!=', product_id.id), ('is_subscription_plans', '=', True)])
            else:
                product_list = request.env['product.template'].sudo().search(
                    [('list_price', '<', sale_sub[0].list_price), ('id', '!=', product_id.id), ('is_subscription_plans', '=', True)])

            order_subscription = request.env['sale.subscription'].sudo().search([('id', '=', int(data['id_order']))])
            quanty = (order_subscription.recurring_invoice_line_ids)[0].quantity

            values.update({
                'html': request.env.ref('onnet_subscription_account.get_list_product')._render({
                    'list_product': product_list,
                    'product_id': product_id,
                    'order_id': data['id_order'],
                    'type': data['type'],
                    'quanty_order': int(quanty)
                })
            })
        return values

    # detail sale order
    @http.route('/detail_sale_order', csrf=False, type='json', auth='public', website=True)
    def detail_sale_order(self, data):
        product_id = data['product_id']
        order_id = data['order_id']
        numUser = data['numUser']
        products_plan = request.env['product.template'].sudo().search([('id', '=', product_id)], limit=1)
        if products_plan:
            product_pro = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', int(products_plan.id))], limit=1)
        # pricelist annually month
        order_subscription = request.env['sale.subscription'].sudo().search([('id', '=', order_id)])
        if order_subscription.order_id:
            order = request.env['sale.order'].sudo().search([('id', '=', order_subscription.order_id.id)])
        # price of product in new order
        products_plan = request.env['product.template'].sudo().search([('id', '=', product_id)], limit=1)
        # number of plan in order subscription
        quanty = (order_subscription.recurring_invoice_line_ids)[0].quantity
        if quanty > int(numUser):
            quantity = quanty
        else:
            quantity = int(numUser)

        annually_template = int(
            request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.annually_template'))
        monthly_billing_period = int(
            request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.monthly_billing_period'))
        yearly_billing_period = int(
            request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.yearly_billing_period'))
        if products_plan:
            product_pro = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', int(products_plan.id))], limit=1)
            product_pro_price = product_pro.list_price
            if order_subscription.pricelist_id:
                pro_info = products_plan._get_combination_info(False, int(product_pro.id or 0), 1,
                                                               request.env['product.pricelist'].browse(
                                                                   int(order_subscription.pricelist_id)))
                product_pro_price = pro_info['list_price']
            # number of days in one invoice period
            if order_subscription.template_id.id == annually_template:
                billing_total_days = yearly_billing_period
            else:
                billing_total_days = monthly_billing_period
        today = fields.Date.from_string(datetime.today())
        next_billing_date = fields.Date.from_string(order_subscription.recurring_next_date)
        if data['type'] == 'upgrade':
            # total price of old plan in order
            total_price_old = (order_subscription.recurring_invoice_line_ids)[0].price_subtotal
            # price in 1 day of order
            single_price = total_price_old / billing_total_days
            single_price_new = product_pro_price*quantity / billing_total_days
            # price total not use yet
            not_use_yet_price = single_price * (next_billing_date - today).days
            # price total new order
            price_new = single_price_new * (next_billing_date - today).days
            price_new_one_user = (product_pro_price/billing_total_days)*(next_billing_date - today).days
            # price new order - price use
            total_price = round(price_new - not_use_yet_price , 2)
            msg = _("Upgrade - Invoicing period from") + ": %s - %s" % (today.strftime('%b %d,%Y'), next_billing_date.strftime('%b %d,%Y'))
            values = {
                'html': request.env.ref('onnet_subscription_account.order_view_plans')._render({
                    'list_product': product_pro,
                    'quantity': int(quantity),
                    'product_id': int(product_id),
                    'price_new_one_user': price_new_one_user,
                    'product_pro_price': product_pro_price,
                    'not_use_yet_price': not_use_yet_price,
                    'price_new': price_new,
                    'total_price': total_price,
                    'type': data['type'],
                    'next_billing_date': next_billing_date.strftime('%b %d,%Y'),
                    'msg': msg
                })
            }
        else:
            msg = _("Downgrade - Invoicing for next billing period from") + ": %s " % (next_billing_date.strftime('%b %d,%Y'))
            values = {
                'html': request.env.ref('onnet_subscription_account.order_view_plans')._render({
                    'list_product': product_pro,
                    'quantity': int(quantity),
                    'product_pro_price': product_pro_price,
                    'price_new': product_pro_price,
                    'total_price': product_pro_price*quantity,
                    'product_id': int(product_id),
                    'type': data['type'],
                    'next_billing_date': next_billing_date.strftime('%b %d,%Y'),
                    'msg': msg
                })
            }

        return values

    # create sale order
    @http.route('/create_sale_order', csrf=False, type='json', auth='public', website=True)
    def create_sale_order(self, order_id, data):
        if data:
            data_partner = {
                'name': data.get('name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'company_name': data.get('company'),
                'country_id': int(data.get('country')),
                'lang': data.get('lang'),
            }
        product_id = int(data.get('product_id'))
        id_partner_sub = int(data.get('partner_id'))
        quantity = int(data.get('quantity'))
        price_new_one_user = data.get('price_new_one_user')
        if data.get('credit'):
            credit = data.get('credit')
        else:
            credit = 0
        # edit user
        self._save_edit_partner(data_partner, id_partner_sub)
        # pricelist annually month
        order_subscription = request.env['sale.subscription'].sudo().search([('id', '=', order_id)])
        if order_id:
            order = request.env['sale.order'].sudo().search([('id', '=', order_id)])

        # price of product in old order
        name_old = (order_subscription.recurring_invoice_line_ids)[0].name
        # price of product in new order
        products_plan = request.env['product.template'].sudo().search([('id', '=', product_id)], limit=1)

        name_new = products_plan.name
        if products_plan:
            product_pro = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', int(products_plan.id))], limit=1)
            product_pro_price = product_pro.list_price
            if order_subscription.pricelist_id:
                pro_info = products_plan._get_combination_info(False, int(product_pro.id or 0), 1,
                                                               request.env['product.pricelist'].browse(
                                                                   int(order_subscription.pricelist_id)))
                product_pro_price = pro_info['list_price']

        today = fields.Date.from_string(datetime.today())
        next_billing_date = fields.Date.from_string(order_subscription.recurring_next_date)
        # fomrmat name
        lang = request.env['res.lang'].sudo().search([('code', '=', order.partner_invoice_id.lang)])
        format_date = request.env['ir.qweb.field.date'].with_context(lang=lang).value_to_html
        period_msg = products_plan.name + _(" Invoicing period") + ": %s - %s" % (
            format_date(today, {}), format_date(next_billing_date, {}))
        name = products_plan.name + '\n' + period_msg
        if data['type'] == 'upgrade':
            credit_name = _("Credit Invoicing period") + ": %s - %s" % (format_date(today, {}), format_date(next_billing_date, {}))
            note_order = 'upsell'
            msg = ''
            # get id product credit of order
            credit_id = int(request.env['ir.config_parameter'].sudo().get_param(
                'onnet_custom_subscription.user_product_subscription'))
            product_credit = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', int(credit_id))], limit=1)
            order_lines = [(0, 0, {
                'product_id': product_pro.id,
                'name': name,
                'product_uom_qty': quantity,
                'price_unit': price_new_one_user,
                'subscription_id': int(order_id),
            }), (0, 0, {
                'product_id': product_credit.id,
                'name': credit_name,
                'product_uom_qty': 1,
                'price_unit': float(credit) * -1,
                'subscription_id': int(order_id),
            })]
        else:
            note_order = 'renew'
            msg = "You have successfully changed your subscription from %s to %s. The change will become effective on %s" % (
                name_old, name_new, next_billing_date.strftime('%b %d,%Y'))
            order_lines = [(0, 0, {
                'product_id': product_pro.id,
                'name': name,
                'product_uom_qty': quantity,
                'price_unit': product_pro_price,
                'subscription_id': int(order_id),
            })]

        sale_orders = {
            'origin': order_subscription.code,
            'partner_id': order_subscription.partner_id.id,
            'pricelist_id': order_subscription.pricelist_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_lines,
            'invoice_status': 'no',
            'subscription_management': note_order,
            'access_token': str(uuid.uuid4())
        }

        #  created sale order
        order_new = request.env['sale.order'].sudo().create(sale_orders)
        request.session['total_price'] = data.get('total')
        request.session['session_subscription_redirect'] = order_subscription.id
        request.session['sale_order_id'] = order_new.id
        request.session['active_firework'] = 1
        if order_new:
            request.session['id_order'] = order_new.id
            values = {
                'check': True,
                'order_id': order_new.id,
                'type': data['type'],
                'messeger': msg
            }
        else:
            values = {
                'check': False
            }
            
        return values

    @http.route(['/my/subscription/<int:account_id>/cancel'], type='http', methods=["POST"], auth="public", website=True)
    def cancel_account(self, account_id, token=None, **kw):
        # res = super(ModalAccountInherit, self).close_account(account_id, uuid=None, **kw)
        account = request.env['sale.subscription'].sudo().browse(account_id)
        cancel_reason = request.env['sale.subscription.close.reason'].browse(int(kw.get('close_reason_id')))
        account.close_reason_id = cancel_reason
        if kw.get('closing_text'):
            account.message_post(body=_('Cancel text: %s', kw.get('closing_text')))
        if kw.get('is_extra_maintenance') == 'extend':
            extend_id = int(request.env['ir.config_parameter'].sudo().get_param(
                'onnet_custom_subscription.user_product_extend'))

            product_pro = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', int(extend_id))], limit=1)
            product_pro_price = product_pro.list_price
            exp_date = fields.Date.from_string(account.recurring_next_date)
            exp_date_cancel = fields.Date.from_string(account.recurring_next_date + relativedelta(months=1))
            # fomrmat name
            # if account.order_id:
            #     order = request.env['sale.order'].sudo().search([('id', '=', account.order_id.id)])
            # lang = request.env['res.lang'].sudo().search([('code', '=', order.partner_invoice_id.lang)])
            format_date = request.env['ir.qweb.field.date'].with_context().value_to_html
            period_msg = product_pro.name + _(" Invoicing period") + ": %s - %s" % (
                format_date(exp_date, {}), format_date(exp_date_cancel, {}))

            name = product_pro.name + '\n' + period_msg
            order_lines = [(0, 0, {
                'product_id': product_pro.id,
                'name': name,
                'product_uom_qty': 1,
                'price_unit': product_pro_price,
                'subscription_id': int(account_id),
            })]
            sale_orders = {
                'origin': account.code,
                'partner_id': account.partner_id.id,
                'pricelist_id': account.pricelist_id.id,
                'date_order': fields.Datetime.now(),
                'validity_date': exp_date_cancel,
                'order_line': order_lines,
                'amount_total': product_pro_price,
                'subscription_management': 'upsell',
                'access_token': str(uuid.uuid4())
            }
            # created sale order
            order_new = request.env['sale.order'].sudo().create(sale_orders)
            # update Expiration day in subscription order
            request.session['session_subscription_redirect'] = account.id
            request.session['id_order'] = order_new.id
            request.session['active_firework'] = 1
            url = '/plans/payment'
        else:
            self.set_cancel(account)
            url = '/my/subscription/%s/%s ' % (account_id, token)
        return request.redirect(url)

    def set_cancel(self, account):
        today = fields.Date.from_string(datetime.today())
        search = request.env['sale.subscription.stage'].search
        stage = search([('category', '=', 'cancel'), ('sequence', '>=', account.stage_id.sequence)], limit=1)
        if not stage:
            stage = search([('category', '=', 'cancel')], limit=1)
        values = {'stage_id': stage.id, 'to_renew': False}
        if account.recurring_rule_boundary == 'unlimited' or not account.date or today < account.date:
            values['date'] = account.recurring_next_date
        account.write(values)
        return True

    def create_order(self, account):
        today = fields.Date.from_string(datetime.today())
        search = request.env['sale.subscription.stage'].search
        stage = search([('category', '=', 'cancel'), ('sequence', '>=', account.stage_id.sequence)], limit=1)
        if not stage:
            stage = search([('category', '=', 'cancel')], limit=1)
        values = {'stage_id': stage.id, 'to_renew': False}
        if account.recurring_rule_boundary == 'unlimited' or not account.date or today < account.date:
            values['date'] = datetime.date.today().strftime('%Y-%m-%d')
        account.write(values)
        return True

    # get plan subscription
    @http.route('/get-plan', csrf=False, type='json', auth='public', website=True)
    def ajax_get_plan(self, data):
        numuser = 0
        if int(data['order_id']):
            sale_sub = request.env['sale.subscription'].sudo().search(
                [('id', '=', int(data['order_id']))]).recurring_invoice_line_ids.product_id
            if data['type'] == 'upgrade':
                product_list = request.env['product.template'].sudo().search(
                    [('list_price', '>=', sale_sub[0].list_price), ('is_subscription_plans', '=', True)])
            else:
                product_list = request.env['product.template'].sudo().search(
                    [('list_price', '<', sale_sub[0].list_price), ('is_subscription_plans', '=', True)])
            quanty = (request.env['sale.subscription'].sudo().search(
                [('id', '=', int(data['order_id']))]).recurring_invoice_line_ids)[0].quantity

        if  product_list:
            for item in product_list:
                numuser = item[0].quantity_user

        if quanty > numuser:
            numuser = int(quanty)
            
        values = {
            'html': request.env.ref('onnet_subscription_account.get_list_plan')._render({
                'list_plan': product_list
            }),
            'numuser': numuser
        }
        return values

    # get user number plan subscription
    @http.route('/get-user-number', csrf=False, type='json', auth='public', website=True)
    def ajax_get_user_number(self, data):
        numuser = 0
        if int(data['product_id']):
            product_list = request.env['product.template'].sudo().search(
                [('id', '=', data['product_id']), ('is_subscription_plans', '=', True)])
            numuser = product_list.quantity_user

        if int(data['order_id']):
            order_subscription = request.env['sale.subscription'].sudo().search([('id', '=', int(data['order_id']))])
            quanty = (order_subscription.recurring_invoice_line_ids)[0].quantity
            if quanty > numuser:
                numuser = int(quanty)
        values = {
            'numuser': numuser
        }
        return values