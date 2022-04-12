# -*- coding: utf-8 -*-

from odoo import api, fields, models, api

class OrderSubcription(models.Model):
    _inherit = 'sale.subscription'

    access_token = fields.Text('Access Token')
    order_id = fields.Many2one('sale.order', string='Order id', required=False, index=True, copy=False)
    website = fields.Char('Website')
    is_extra_maintenance = fields.Boolean(string='Extra Maintenance', default=False)
    is_check_trial = fields.Boolean(string='Is Check', default=False)