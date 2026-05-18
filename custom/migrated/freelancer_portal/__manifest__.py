# -*- coding: utf-8 -*-
{
    'name': 'Freelancer Portal',
    'version': '1.0.0',
    'category': 'Website',
    'summary': 'Portal for freelancers to manage projects and tasks',
    'description': """
        Freelancer Portal
        =================
        This module provides a dedicated portal for freelancers to:
        * View and manage assigned projects
        * Track tasks and milestones
        * Submit timesheets
        * Communicate with clients
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'portal',
        'project',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/freelancer_portal_views.xml',
        # 'views/freelancer_portal_templates.xml',
    ],
    'assets': {
        # 'web.assets_frontend': [
        #     'freelancer_portal/static/src/css/freelancer_portal.css',
        #     'freelancer_portal/static/src/js/freelancer_portal.js',
        # ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}