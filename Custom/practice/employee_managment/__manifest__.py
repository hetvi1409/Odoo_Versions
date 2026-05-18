# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Employee Managment',
    'version': '1.1',
    'summary': 'Employee Managment',
    'sequence': 10,
    'description': """
        Employee Managment
    """,
    'category': 'Human Resources/Employees',
    'website': 'www.website.com',
    'depends': ['base'],
    'data': [

        # 'views/ir.actions.client.xml'
        
    ],
    "assets": {
        "web.assets_backend": [
            # 'employee_managment/static/src/js/client_action/employee_dashboard.js',
            # 'employee_managment/static/src/js/client_action/employee_dashboard_template.xml',
        ]
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
