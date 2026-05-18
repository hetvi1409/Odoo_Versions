# -*- coding: utf-8 -*-
{
    'name':'Real Estate.',
    'version':'19.0.1.0.0',
    'category':'Real Estate Conditional Assessment',
    'sequence':14,
    'summary':'',
    'description':""" Real Estate Management
      - Properties Hierarchy
      - Google Maps Integration
      - Units Reservation
      - Ownership Contracts Managament
      - Easy Tenant Management
      - Invoicing Management & Accounting Integration
      - Property Refund
      - Email Notifications
      - Integration with Odoo Website
      - Comprehensive Reporting
      """,
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends':['base','itsys_real_estate'],
    'data':[
        'security/ir.model.access.csv',
        'views/conditional_assessment_views.xml',
    ],
'assets': {
        'web.assets_backend': [
            'itsys_real_estate_conditional_assessment/static/src/css/table.css'
]
},
    'images': ['static/description/images/splash-screen.jpg'],
    'installable':True,
    'auto_install':False,
    'application':True,
    'license': "AGPL-3",
   }