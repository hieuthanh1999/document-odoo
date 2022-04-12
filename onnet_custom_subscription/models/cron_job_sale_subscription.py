# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.http import request
import os
from dateutil.relativedelta import relativedelta

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    def _cron_send_email(self):
        today = fields.Date.from_string(datetime.today())
        list_sub = self.env['sale.subscription'].sudo().search([('stage_category','=','progress')])
        for item in list_sub:
            date_one = fields.Date.from_string(item.recurring_next_date)
            days = (date_one - today).days
            if days > 0 and days == 1:
                self._cron_send(item.partner_id.email, item.partner_id.name, item)
            elif days == 3:
                self._cron_send(item.partner_id.email, item.partner_id.name, item)
            elif days == 5:
                self._cron_send(item.partner_id.email, item.partner_id.name, item)
            elif days == 7:
                self._cron_send(item.partner_id.email, item.partner_id.name, item)


    def _cron_send(self, email_tos, name, item):
        template_id = self.env.ref('onnet_custom_subscription.email_dunning_payment_views_template').id

        template = self.env['mail.template'].sudo().browse(template_id)
        email_tox = email_tos
        email_subject = "Your Subscription Billing Date Reminder"
        body = template.body_html
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        body = body.replace("--name--", str(name) or "")
        body = body.replace("--email--", str(email_tox) or "")
        body = body.replace("--link--", str(base_url + '/my/subscription/' + str(item.id) + '/' + str(item.uuid)) or "")
        body = body.replace("--code--", str(item.code) or "")
        mail_values = {
            'subject': email_subject,
            'body_html': body,
            'email_to': email_tox
        }
        self.env['mail.mail'].sudo().create(mail_values).send()

    def _cron_auto_create_invoice(self):
        today = fields.Date.from_string(datetime.today())
        # today = '2022-04-28'
        # update order subscription Next Invoice 'upsell'
        list_sub = self.env['sale.subscription'].sudo().search([('stage_category', '=', 'progress'), ('recurring_next_date', '=', today)])
        for item in list_sub:
            order_sales = self.env['sale.order'].sudo().search([('origin', '=', item.code)], limit =1)
            # upsell order
            if order_sales.state == 'sale' and order_sales.subscription_management == 'upsell':
                self.change_item(item, order_sales)
            # renew order
            if order_sales and order_sales.subscription_management == 'renew':
                self.change_item(item, order_sales)
            # cancel order

            if order_sales.state == 'cancel':
                self.change_item(item, order_sales)
                item.browse(item.id).sudo().write({
                                    'stage_category': 'cancel',
                                    'recurring_next_date': fields.Date.from_string(datetime.today() + relativedelta(months=1))
                                })
        stage_closed = int(
            request.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.sale_subscription_closed'))
        list_sub_cancel = self.env['sale.subscription'].sudo().search([('stage_category', '=', 'cancel'), ('recurring_next_date', '=', today)])
        for item in list_sub_cancel:
            item.browse(item.id).sudo().write({
                'stage_category': 'closed',
                'stage_id': stage_closed
            })
        # update order subscription trial next close
        list_sub_trial = self.env['sale.subscription'].sudo().search(
            [('stage_category', '=', 'trial'), ('recurring_next_date', '=', today)])
        for item2 in list_sub_trial:
            # trial order
            order_trials = self.env['sale.order'].sudo().search([('id', '=', item2.order_id.id)], limit=1)
            if order_trials.state == 'draft':
                item2.order_id.browse(item2.order_id.id).sudo().write({
                    'state': 'cancel'
                })
                item2.browse(item2.id).sudo().write({
                    'stage_category': 'closed',
                    'stage_id': stage_closed
                })
    def change_item(self, item, sale_order):
            # update order subscription Next Invoice 'upsell'
            list_order_line_new = self.get_list_order_new(sale_order, item.id)
            list_order_line_old = self.get_list_order_new(item.order_id,  item.id)

            # Change item first list
            list_order_line_old[0] = list_order_line_new[0]
            # Delete sale subscription line item
            self.delete_sale_line(item)
            # update sale subscription line item
            item.browse(item.id).sudo().write({
                'recurring_invoice_line_ids':list_order_line_old
            })

    def get_list_order_new(self, new_order, id_sale):
        sale_line_item_new = []
        for line in new_order.order_line:
            sale_line_item_new.append((0, 0,{
                'name': line.name,
                'product_id': line.product_id.id,
                'analytic_account_id': int(id_sale),
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'uom_id': 1
            }))
        return sale_line_item_new

    def delete_sale_line(self, sale_sub):
        if sale_sub:
           for link in sale_sub.recurring_invoice_line_ids:
                link.unlink()
