# -*- coding: utf-8 -*-

{
    'name': 'Adyen Recurring Payment Acquirer',
    'category': 'Payment',
    'summary': 'Payment Acquirer: Adyen Recurring Implementation',
    'version': '1.0',
    'description': """Adyen Recurring Payment Acquirer""",
    'author': 'OpenERP SA',
    'depends': ['payment_adyen', 'ip_web_addons'],
    'data': [
        'data/ir.sequence.csv',
        'data/ir.sequence.type.csv',
        'views/adyen_recurrent.xml',
        'views/autoship.xml',
        'views/payment_acquirer.xml',
        'wizard/recurringDetailsWizard.xml',
    ],
    'installable': True,
}
