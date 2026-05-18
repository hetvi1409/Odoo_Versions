{
    'name': 'Valuation Roll Import',
    'version': '2.0',
    'category': 'Tools',
    'summary': 'Module for importing XML files via a wizard',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends': ['itsys_real_estate'],
    'data': [
        'security/ir.model.access.csv',
        'views/building_type_views.xml',
        'wizard/valuation_roll_import_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}