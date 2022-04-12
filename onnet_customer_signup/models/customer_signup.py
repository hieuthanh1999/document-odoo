# -*- coding: utf-8 -*-

from odoo import api, fields, models, api

class CustomerSignup(models.Model):
    _name = "customer.signup"
    _description = "Customer signup"

    name = fields.Char()
