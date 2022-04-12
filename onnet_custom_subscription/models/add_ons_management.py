# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AddOnsManagement(models.Model):
    _inherit = 'product.template'
    _description = "Add-ons Management"
    _order = "sequence asc, id desc"

    is_add_ons = fields.Boolean(string='Add-ons', default=False)
    sequence = fields.Integer("Sequence")