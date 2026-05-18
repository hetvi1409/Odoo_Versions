
# -*- coding: utf-8 -*-
{
    'name': 'Remove Powered by Odoo',
    'version': '1.0.0',
    'summary': """Remove Powered by Odoo from Login, Portal and Brand Promotion from website footer.
    Remove Odoo branding from the footer of portal pages. Connect with your software
    Removing the 'Powered by' block entirely
        Remove from the portal sidebar.
        Remove from the login page.
        Remove from the brand promotion.
        Remove Odoo branding from the footer of portal pages.
        Remove branding
        De branding Odoo
        Hide Powered by odoo
        login page
        connect with your software
        odoo signin page
        odoo signup page
        odoo sign screen
        hide connect with your software
    """,
    'description': """ Remove Powered by Odoo from Portal
        Removing the 'Powered by' block entirely
        Remove from the portal sidebar.
        Remove from the login page.
        Remove from the brand promotion.
        Remove Odoo branding from the footer of portal pages.
        Remove branding
        Hide Powered by odoo
        login page
    """,
    'license': 'LGPL-3',
    'sequence': 10,
    'category': 'Tools',
    'depends': ['portal', 'base_setup', 'mail', 'website'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/background_images.xml',
        'views/footer_copyright.xml',
        'views/mail_notification_layout.xml',
        'views/login_layout.xml',
        'views/portal_record_sidebar.xml',
        'views/brand_promotion.xml',
    ],
    'application': True,
    'external_dependencies': {
        'python': [],
    },
    'assets': {
        'web.assets_backend': [
            'powered_by_odoo_remove/static/src/js/res_config_edition_patch.js',
            'powered_by_odoo_remove/static/src/xml/res_config_edition_patch.xml',
            'powered_by_odoo_remove/static/src/scss/font_family.scss',
        ],
        'web.assets_frontend': [
            'powered_by_odoo_remove/static/src/scss/font_family.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
