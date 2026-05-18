# -*- coding: utf-8 -*-

{
    'name': 'Audit Request Form (Internal and External)',
    'version': '6.2.4',
    'category': 'Accounting/Accounting',
    'summary': """Internal and External Audit Request and Flow""",
    'description': """
Audit Request Form (Internal and External)
Internal and External Audit Request and Flow
internal audit
external audit
erp audit
account audit
accouting audit
journal entry audit
audit request
audit request form
odoo audit
audit odoo
employee audit
sales audit
report audit
audit report
    """,
    'license': 'Other proprietary',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'images': ['static/description/image.png'],
    'depends': ['mail', 'website', 'portal'],
    'data': [
        'security/audit_request_security.xml',
        'security/ir.model.access.csv',  
        'report/report_audit_request.xml',
        'report/report_audit_request_template.xml',        
        'data/audit_request_data.xml',
        'data/audit_sequence_data.xml',
        'data/audit_category_data.xml',
        'wizard/audit_refuse.xml',
        'views/audit_request.xml',
        'views/audit_category.xml',
        'views/audit_tag.xml',
        'views/audit_request_portal_template.xml',        
    ],
    'installable': True,
    'auto_install': False
}

