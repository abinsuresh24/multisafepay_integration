# -*- coding: utf-8 -*-
{
    'name': "MultiSafePay",
    'version': '16.0.1.0.0',
    'author': "Cybrosys_Technologies",
    'category': 'Accounting',
    'summary': 'Multisafepay integration',
    'description': """
    payment provider multisafepay integration
    """,
    'depends': ['base', 'payment', 'website'],
    'data': [
        'views/multisafe_payment.xml',
        'views/payment_multisafepay_template.xml',
        'data/payment_provider_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'AGPL-3',
}
