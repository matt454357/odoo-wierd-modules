# -*- coding: utf-8 -*-

{
    'name': 'Check Layout US',
    'category': 'Generic Modules/Accounting',
    'summary': 'Check Layout Report for US Top',
    'version': '1.0',
    'description': """
Check Layout US - Top
================================================
Create a new check layout for the standard QuickBooks style pre-printed format.
Adds item "Check-US" to the Print menu on the Check Writing list and form views.
 - 3-part checks
 - Top check style
    """,
    'author': 'matt454357',
    'depends': ['account_check_writing'],
    'data': [
        'paperformat_check_layout_us.xml',
        'check_layout_report_us.xml',
        'report_check_us.xml',
    ],
    #'css': [
    #    'static/src/css/report_check_us.css',
    #],
    'installable': True,
}
