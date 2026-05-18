# -*- coding: utf-8 -*-
{
    'name': "Sale-Invoice Email Notification Restriction",

    'summary': "Prevent automatic email notifications to Salesperson on assignment",

    'description': """
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Sales',
    'version': '18.0.1.0.0',


 'depends': ['base', 'mail', 'account','accountant' ,'sale', 'stock'],

    'data': [
        'views/menus.xml',
        ]


}
