# -*- coding: utf-8 -*-

{
    'name': 'Check Layout OpenSupplies',
    'category': 'Generic Modules/Accounting',
    'summary': 'Check Layout Report for OpenSupplies Format',
    'version': '1.0',
    'description': """
Check Layout OpenSupplies
================================================
Create a new check layout for the OpenSupplies pre-printed format.
    """,
    'author': 'matt454357',
    'depends': ['account_check_writing'],
    'data': [
        'check_layout_paperformat.xml',
        'check_layout_report_os.xml',
        'report_check_os.xml',
    ],
    'css': [
        'static/src/css/report_check_os.css',
    ],
    'installable': True,
}
