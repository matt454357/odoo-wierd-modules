# -*- coding: utf-8 -*-

{
    'name': 'Paypal Simple IPN',
    'category': 'Technical Settings',
    'summary': 'Payment Acquirer: Paypal Simple IPN Improvement',
    'version': '1.0',
    'description': """
Improve the Paypal Payment Acquirer module to work without a complete e-commerce configuration.
When a customer pays an invoice through PayPal, an IPN is generated.  But, the IPN can't be processed because the transaction was not initiated through the Odoo web module.
This module creates the transaction, if it doesn't exist.  It also adds a column to the invoice tree view, indicating that an IPN transaction has been received from PayPal.
    """,
    'author': 'matt454357',
    'depends': ['payment','payment_paypal'],
    'data': [
        'invoice.xml',
    ],
    'installable': True,
}
