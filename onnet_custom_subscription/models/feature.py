# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions


class TabFeature(models.Model):
    _name = "tab.feature"
    _description = "Tab Feature"

    name = fields.Html('Feature Name', translate=True)
    note = fields.Html(string='Description', translate=True)
    planss = fields.Many2one('product.template', string='Subscription Plans', required=True, ondelete='cascade',
                            index=True, copy=False)

