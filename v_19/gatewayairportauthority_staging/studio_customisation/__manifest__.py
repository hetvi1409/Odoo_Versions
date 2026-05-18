# -*- coding: utf-8 -*-
{
    'name': 'Studio Customisation',
    'version': '1.0',
    'category': 'Uncategorized',
    'summary': 'Studio Customisation',
    'description': '''Studio Customisation''',
    'depends': ['base', 'contacts' ,'audit_meter_report'],
    'data': [
        'security/ir.model.access.csv',
		'views/dwelling_types_views.xml',
		'views/property_category_views.xml',
		'views/meter_manufacturer_views.xml',
		'views/meter_condition_views.xml',
        'views/action_menus.xml',
		# 'views/res_partner_views.xml',
],
    'installable': True,
    'application': False,
    'auto_install': False,
}