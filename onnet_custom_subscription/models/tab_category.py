# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions


class TabCategory(models.Model):
    _name = "tab.category"
    _description = "Tab Category"

    category_id = fields.Many2one(
        'category.management', string='Category Name',
        change_default=True, ondelete='restrict', copy=False)

    plans = fields.Many2one('product.template', string='Subscription Plans', required=True, ondelete='cascade',
                            index=True, copy=False)

    modules = fields.Many2many('modules.management', string='Modules Management',
                               domain="[('category_segment', 'in', category_id)]", copy=False)

    @api.onchange('category_id')
    def update_category(self):
        for tab in self:
            if tab.category_id.modules:
                tab.modules = tab.category_id.modules

    @api.onchange('modules')
    def update_modules(self):
        for tab in self:
            if tab.modules:
                for module in tab.modules:
                    self.env['modules.management'].search([('id', '=', module.ids[0])]).write({'category_segment': tab.category_id})

    @api.model
    def create(self, vals):
        if self.env['tab.category'].search([('category_id', '=', vals['category_id']), ('plans', '=', vals['plans'])]):
            category_name = self.env['category.management'].browse(vals['category_id']).name
            raise exceptions.ValidationError(_('Category {category} already exists on plan').format(category=category_name))
        res = super(TabCategory, self).create(vals)
        return res



