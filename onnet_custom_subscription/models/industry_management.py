# -*- coding: utf-8 -*-
from odoo import api, fields, models

class IndustryManagement(models.Model):
    _name = "industry.management"
    _description = "Industry Management"
    _rec_name = 'industry_name'
    _order = "sequence asc, id desc"

    industry_name = fields.Char('Industry Name')
    subscription_plan = fields.Many2many(comodel_name='product.template',
                                string="Subscription Plans",
                                relation='product_template_industry',
                                column1='industry_id',
                                column2='product_template_id', domain="[('is_subscription_plans','=',True)]")
    sequence = fields.Integer("Sequence")