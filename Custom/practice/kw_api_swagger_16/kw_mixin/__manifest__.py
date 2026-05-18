{
    'name': 'Mixins',
    'summary': '''
        Technical module that provides a set of reusable mixins
        for Odoo models.
        Includes functionality for:
        * Year-based operations and computations
        * Week number handling and week-based calculations
        * Month-based operations and validations
        * Quarter-based operations and validations
        * Day of week utilities and name conversions
    ''',

    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/addons',

    'category': 'Hidden/Tools',
    'license': 'LGPL-3',
    'version': '16.0.1.7.0',

    'depends': [
        'base',
    ],

    'external_dependencies': {'python': [], },

    'data': [
    ],
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

    'price': 0,
    'currency': 'EUR',

}
