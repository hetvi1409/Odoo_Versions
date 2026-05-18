# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Frontdesk',
    'category': 'Human Resources/Frontdesk',
    'description': 'A comprehensive front desk management system that enables guests to effortlessly check in and out while ensuring seamless notifications for hosts.',
    'summary': 'Visitor management system',
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
    'version': '1.0',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends': [
        'hr',
        'sms',
        'website',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/frontdesk_report_views.xml',
        'views/frontdesk_drink_views.xml',
        'views/frontdesk_visitor_views.xml',
        'views/frontdesk_frontdesk_views.xml',
        'views/frontdesk_menus.xml',
        'views/frontdesk_templates.xml',
        'views/frontdesk_qr_expiration.xml',
        'data/mail_template_data.xml',
        'data/sms_template_data.xml',
        'data/frontdesk_data.xml',
    ],
    'demo': [
        'demo/frontdesk_demo.xml',
    ],
    'assets': {
        # 'web.assets_frontend': [
        #     # Load Bootstrap functions & variables first
        #     "web/static/lib/bootstrap/scss/_functions.scss",
        #     "web/static/lib/bootstrap/scss/_variables.scss",
        #     "web/static/lib/bootstrap/scss/_mixins.scss",
        #
        #     # Load frontdesk variables & overrides
        #     "frontdesk/static/src/primary_variables.scss",
        #     "frontdesk/static/src/bootstrap_overridden.scss",
        #
        #     # Load web helpers and pre_variables
        #     ("include", "web._assets_helpers"),
        #     ("include", "web._assets_frontend_helpers"),
        #     ("include", "web._assets_primary_variables"),
        #     "web/static/src/scss/pre_variables.scss",
        #
        #     # Load frontend Bootstrap (must be after variables)
        #     ("include", "web._assets_bootstrap_frontend"),
        #
        #     # Load Frontdesk SCSS files (after Bootstrap is ready)
        #     "frontdesk/static/src/frontdesk.scss",
        #     "frontdesk/static/src/host_page/many2one/many2one.scss",
        #
        #     # Load all Frontdesk JS and XML
        #     "frontdesk/static/src/frontdesk.js",
        #     "frontdesk/static/src/frontdesk.xml",
        #     "frontdesk/static/src/use_inactivity.js",
        #     "frontdesk/static/src/**/*.js",
        #     "frontdesk/static/src/**/*.xml",
        # ],
        'web.assets_frontend': [
            # Load Bootstrap functions & variables first
            "web/static/lib/bootstrap/scss/_functions.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            "web/static/lib/bootstrap/scss/_mixins.scss",
            # 1 Define frontdesk variables (takes priority over frontend ones)
            "frontdesk/static/src/primary_variables.scss",
            "frontdesk/static/src/frontdesk.scss",
            "frontdesk/static/src/bootstrap_overridden.scss",

            # 2 Load frontend variables
            ("include", "web._assets_helpers"),
            ("include", "web._assets_frontend_helpers"),
            ("include", "web._assets_primary_variables"),
            "web/static/src/scss/pre_variables.scss",

            # 3 Load Bootstrap and frontend bundles
            "web/static/lib/bootstrap/scss/_functions.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            ("include", "web._assets_bootstrap_frontend"),

            # 4 Frontdesk's specific assets
            'web/static/lib/zxing-library/zxing-library.js',
            "frontdesk/static/src/use_inactivity.js",
            "frontdesk/static/src/welcome_page/welcome_page.js",
            "frontdesk/static/src/js/frontdesk.js",

            "frontdesk/static/src/welcome_page/welcome_page.xml",
            "frontdesk/static/src/navbar/navbar.js",
            "frontdesk/static/src/navbar/navbar.xml",
            "frontdesk/static/src/visitor_form/visitor_form.js",
            "frontdesk/static/src/visitor_form/visitor_form.xml",
            "frontdesk/static/src/quick_check_in/quick_check_in.js",
            "frontdesk/static/src/quick_check_in/quick_check_in.xml",
            "frontdesk/static/src/host_page/many2one/many2one.js",
            "frontdesk/static/src/host_page/many2one/many2one.xml",
            "frontdesk/static/src/host_page/many2one/many2one.scss",
            "frontdesk/static/src/host_page/host_page.js",
            "frontdesk/static/src/host_page/host_page.xml",
            "frontdesk/static/src/register_page/register_page.js",
            "frontdesk/static/src/register_page/register_page.xml",
            "frontdesk/static/src/drink_page/drink_page.js",
            "frontdesk/static/src/drink_page/drink_page.xml",
            "frontdesk/static/src/end_page/end_page.js",
            "frontdesk/static/src/end_page/end_page.xml",
            'frontdesk/static/src/js/frontdesk.xml',
        ],

        'web.assets_common': [
            '/frontdesk/static/src/js/frontdesk.js',
        ],
        'web.assets_tests': [
            'frontdesk/static/tests/tours/**/*',
        ],
    },
}
