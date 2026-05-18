# -*- coding: utf-8 -*-
# Powered by Mindphin.
# © 2024 Mindphin. (<https://www.mindphin.com>).

{
    'name': 'Portal Customer Statement',
    'version': '18.0.1.0',
    'category': 'Accounting/Accounting',
    'summary': """This module enables portal users to view or download customer statements for a specified date range. | Portal | Customer Statement | Account Statement | Date Range Filter | Overdue Payments | Portal Accounting | Website Reports | B2B Portal | Financial Reports | Customer Ledger | Outstanding Balance | Invoice History""",
    'description': """Portal Customer Statement | Customer Statement |
                    Date-wise statement reports | Custom date filters | Website Customer Statement | Customer Overdue Payments Reports | Customer Statement
    """,
    'author': 'Mindphin',
    'website': 'https://www.mindphin.com',
    'license': 'OPL-1',
    'depends': ['account', 'portal'],
    'data': [
        'views/portal_template_views.xml',
        # 'views/res_partner_form_view.xml',
        'reports/report_customer_statement.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'assets': {
        'web.assets_frontend': [
            'md_portal_customer_statement/static/src/js/portal_datepicker.js',
            'md_portal_customer_statement/static/src/js/custom.js'],
    },
    'sequence': 1,
    'installable': True,
    'price': 80,
    'currency': 'USD',
}

