# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    trial_period = fields.Integer(string='Trial period (days)')
    db_expiration_time = fields.Integer(string='Database expiration time (days)')
    instance_removal_period_trial = fields.Integer(string='Instance removal period for Trial description plans (days)')
    instance_removal_period_active = fields.Integer(string='Instance removal period for Active description plans (days)')
    user_product_subscription_id = fields.Many2one('product.template',
                                      string='User Product',
                                      domain="[('detailed_type', '=', 'service')]",
                                      config_parameter='onnet_custom_subscription.user_product_subscription',
                                      help="A product that represents the number of user for a subscription",
                                      default=lambda self: self.env.ref('onnet_custom_subscription.default_user_product_subscription', False))
    annually_product_pricelist_id = fields.Many2one('product.pricelist',
                                                   string='Annually pricelist',
                                                   config_parameter='onnet_custom_subscription.annually_product_pricelist',
                                                   default=lambda self: self.env.ref(
                                                       'onnet_custom_subscription.default_annually_product_pricelist',
                                                       False))
    month_product_pricelist_id = fields.Many2one('product.pricelist',
                                                    string='Month pricelist',
                                                    config_parameter='onnet_custom_subscription.month_product_pricelist',
                                                    default=lambda self: self.env.ref(
                                                        'onnet_custom_subscription.default_month_product_pricelist',
                                                        False))
    trial_field = fields.Many2one('sale.subscription.stage',
                                    string='Trial Order',
                                    config_parameter='onnet_custom_subscription.sale_subscription_trial',
                                    default=lambda self: self.env.ref(
                                    'onnet_custom_subscription.default_sale_subscription_trial',
                                    False))
    draft_field = fields.Many2one('sale.subscription.stage',
                                    string='Draft Order',
                                    config_parameter='onnet_custom_subscription.sale_subscription_draft',
                                    default=lambda self: self.env.ref(
                                    'onnet_custom_subscription.default_sale_subscription_draft',
                                    False))
    progress_field = fields.Many2one('sale.subscription.stage',
                                    string='Progress Order',
                                    config_parameter='onnet_custom_subscription.sale_subscription_progress',
                                    default=lambda self: self.env.ref(
                                    'onnet_custom_subscription.default_sale_subscription_progress',
                                    False))
    closed_field = fields.Many2one('sale.subscription.stage',
                                     string='Closed Subscription',
                                     config_parameter='onnet_custom_subscription.sale_subscription_closed',
                                     default=lambda self: self.env.ref(
                                         'onnet_custom_subscription.default_sale_subscription_closed',
                                         False))
    maintain_field = fields.Many2one('sale.subscription.stage',
                                   string='Maintain Subscription',
                                   config_parameter='onnet_custom_subscription.sale_subscription_maintain',
                                   default=lambda self: self.env.ref(
                                       'onnet_custom_subscription.default_sale_subscription_maintain',
                                       False))
    annually_template = fields.Many2one('sale.subscription.template',
                                                 string='Annually Template',
                                                 config_parameter='onnet_custom_subscription.annually_template',
                                                 default=lambda self: self.env.ref(
                                                     'onnet_custom_subscription.default_annually_template',
                                                     False))
    monthly_template = fields.Many2one('sale.subscription.template',
                                                string='Monthly Template',
                                                config_parameter='onnet_custom_subscription.monthly_template',
                                                default=lambda self: self.env.ref(
                                                    'onnet_custom_subscription.default_monthly_template',
                                                    False))
    trial_template = fields.Many2one('sale.subscription.template',
                                     string='Trial Template',
                                     config_parameter='onnet_custom_subscription.trial_template',
                                     default=lambda self: self.env.ref(
                                         'onnet_custom_subscription.default_trial_template',
                                         False))
    config_domain = fields.Char(string='Default domain', config_parameter='onnet_custom_subscription.config_domain',default='hiiboss.com')
    user_product_extend_id = fields.Many2one('product.template',
                                                   string='Product Extend',
                                                   domain="[('detailed_type', '=', 'service')]",
                                                   config_parameter='onnet_custom_subscription.user_product_extend',
                                                   help="A product extend of order subscription",
                                                   default=lambda self: self.env.ref(
                                                       'onnet_custom_subscription.default_user_product_extend',
                                                       False))
    monthly_billing_period = fields.Integer(string='Default monthly', config_parameter='onnet_custom_subscription.monthly_billing_period', default=30)
    yearly_billing_period = fields.Integer(string='Default yearly',
                                            config_parameter='onnet_custom_subscription.yearly_billing_period', default=360)
    text_popular = fields.Char(string='Default popular',
                                           config_parameter='onnet_custom_subscription.text_popular',
                                           default='Most Popular')
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['trial_period'] = \
            self.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.trial_period', default=15)
        res['db_expiration_time'] = \
            self.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.db_expiration_time', default=3)
        res['instance_removal_period_trial'] = \
            self.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.period_trial', default=90)
        res['instance_removal_period_active'] = \
            self.env['ir.config_parameter'].sudo().get_param('onnet_custom_subscription.period_active', default=180)
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('onnet_custom_subscription.trial_period',
                                                         self.trial_period)
        self.env['ir.config_parameter'].sudo().set_param('onnet_custom_subscription.db_expiration_time',
                                                         self.db_expiration_time)
        self.env['ir.config_parameter'].sudo().set_param('onnet_custom_subscription.period_trial',
                                                         self.instance_removal_period_trial)
        self.env['ir.config_parameter'].sudo().set_param('onnet_custom_subscription.period_active',
                                                         self.instance_removal_period_active)
        super(ResConfigSettings, self).set_values()

