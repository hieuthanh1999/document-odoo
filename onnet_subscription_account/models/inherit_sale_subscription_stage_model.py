# -*- coding: utf-8 -*-
from odoo import api, fields, models

class InheritSaleSubscriptionStage(models.Model):
    _inherit = 'sale.subscription.stage'

    category = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('cancel', 'Cancel'),
        ('maintenance', 'Maintenance'),
        ('closed', 'Closed')], required=True, default='draft', help="Category of the stage")
    is_check_show = fields.Boolean(string='Show on portal', default=False)