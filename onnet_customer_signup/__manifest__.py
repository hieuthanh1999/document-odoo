# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Onnet Customer signup',
    'version': '1.1',
    'summary': 'Onnet Customer signup software',
    'sequence': 10,
    'description': """Onnet Customer signup software""",
    'category': 'Uncategorized',
    'website': 'https://www.odoo.com',
    'depends': [
        'sale_subscription',
        'product',
        'onnet_custom_subscription',
        'website_sale', 'crm'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/common.xml',
        'views/inherit_lead_views.xml',
        'views/email_active_sale.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            '/onnet_customer_signup/static/src/css/customer_style_sheet.css',
            '/onnet_customer_signup/static/src/js/user_custom_javascript.js',
        ]
    },
    'license': 'LGPL-3',
}
