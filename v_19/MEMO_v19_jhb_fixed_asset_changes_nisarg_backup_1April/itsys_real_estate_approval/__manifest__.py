# -*- coding: utf-8 -*-
{
    'name':'Real Estate.',
    'version':'19.0.1.0.0',
    'category':'Real Estate Approval',
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
    'depends':['base','itsys_real_estate','mail'],
    'data':[
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/mail_template_data.xml',
        'views/building_approval_views.xml',
        'views/menu_items.xml',
    ],
    'images': ['static/description/images/splash-screen.jpg'],
    'installable':True,
    'auto_install':False,
    'application':True,
    'license': "AGPL-3",
   }