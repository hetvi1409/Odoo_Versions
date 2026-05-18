{
    'name': 'Home Screen Icon Layout',
    'version': '19.0.1.0.0',
    'summary': 'Allows you to customize the layout of icons on the Odoo home screen',
    'description': """
        Allows you to customize the layout of icons on the Odoo home screen.
        Features:
        - Customize icon column count
        - Customize icon size
        - Customize icon text size
        - Customize icon inner spacing
        - Customize icon margin
        - Customize icon corner radius
        - Customize icon top margin
        - You can fit the icons to the screen width.
    """,
    'author': 'Burak Şipşak',
    'category': 'Extra Tools',
    'depends': ['base', 'web'],
    'images': ['images/main_screenshot.png'],
    'assets': {
        'web.assets_backend': [
            'home_customizer/static/src/xml/*.xml',
            'home_customizer/static/src/js/*.js',
            'home_customizer/static/src/scss/settings_modal.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
