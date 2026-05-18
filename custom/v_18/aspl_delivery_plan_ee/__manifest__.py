# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'Delivery Plan (Enterprise)',
    'version': '18.0.1.0.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Warehouse',
    'description': 'Manage Delivery Plans',
    'website': 'http://www.acespritech.com',
    'price': 90,
    'currency': 'EUR',
    'depends': ['base', 'stock', 'base_geolocalize'],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_plan_filter_view.xml',
        'views/delivery_plan_menu.xml',
        'views/assign_delivery_line_views.xml',
        'views/res_config_settings.xml',
        'views/delivery_plan.xml',
        'views/stock_location.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'aspl_delivery_plan_ee/static/src/js/client_action/delivery_plan_filter.js',
            'aspl_delivery_plan_ee/static/src/js/client_action/delivery_template.xml',
            'aspl_delivery_plan_ee/static/src/js/dialog/assign_button.js',
            'aspl_delivery_plan_ee/static/src/js/dialog/assign_button.xml',
            'aspl_delivery_plan_ee/static/src/css/assign_driver_style.css',
            'aspl_delivery_plan_ee/static/src/css/delivery_template.css',
            'aspl_delivery_plan_ee/static/src/css/autocomplete.css',
            'aspl_delivery_plan_ee/static/src/js/jquery.min.js',
            'aspl_delivery_plan_ee/static/src/js/index.min.js',
            'aspl_delivery_plan_ee/static/src/js/autocomplete.js',
            'aspl_delivery_plan_ee/static/src/js/leaflet.js',
            'aspl_delivery_plan_ee/static/src/js/leaflet_routing_machine.js',
            'aspl_delivery_plan_ee/static/src/css/leaflet.css',
        ],
    },
    'images': ['static/description/main_screenshot.jpg'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
