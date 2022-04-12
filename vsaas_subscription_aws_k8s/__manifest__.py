{
    'name': 'V-SAAS Subscription AWS K8s',
    'category': 'subscription',
    'author': 'LongDT',
    'summary': 'This module integrate Odoo subscription with AWS K8s.',
    'depends': ['sale_subscription'],
    'images': [],
    'data': [
        "wizards/aws_configuration.xml",
        "views/res_config_settings_view.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
