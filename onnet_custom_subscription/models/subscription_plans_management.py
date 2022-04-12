# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SubscriptionPlansManagement(models.Model):
    _inherit = 'product.template'
    _description = "Subscription Plans Management"
    _order = "sequence asc, id desc"

    quantity_user = fields.Integer(string='User quantity')
    detailed_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type', default='service', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    is_subscription_plans = fields.Boolean(string='Subscription Plans', default=False)
    industry = fields.Many2many(comodel_name='industry.management',
                                string="Industry Name",
                                relation='product_template_industry',
                                column1='product_template_id',
                                column2='industry_id')
    tab_module = fields.One2many('tab.category', 'plans', string='Category Management', copy=True, auto_join=True)
    tab_feature = fields.One2many('tab.feature', 'planss', string='Feature Tab', copy=True, auto_join=True)
    sequence = fields.Integer("Sequence")
