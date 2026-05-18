# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Physical Record Management',
    'version': '16.0.1.0.0',
    'price': 19.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'depends': [
        'contacts',
        'mail',
        'hr',
    ],
    'category': 'Human Resources/Employees',
    'summary':  """This app allows you to manage physical records management.""",
    'description': """
This app allows you to manage physical document records management. 
physical record management
record management
physical records
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'images': ['static/description/111pdr.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/physical_document_records_manage/1057',#'https://youtu.be/V9xouHuG3tE',
    'data': [
        'security/physical_record_security.xml',
        'security/ir.model.access.csv',
        'views/physical_record_keeper_view.xml',
        'views/physical_record_stage_view.xml',
        'views/physical_record_report_view.xml',
        'views/physical_record_view.xml',
        'views/physical_location_view.xml',
        'views/physical_destruction_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
