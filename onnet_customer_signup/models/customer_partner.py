# -*- coding: utf-8 -*-

from odoo import api, fields, models, api

class CustomerPartner(models.Model):
    _inherit = 'res.partner'

#     is_trial = fields.Integer(default=1)
