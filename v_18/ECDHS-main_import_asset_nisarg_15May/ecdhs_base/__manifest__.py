# -*- coding: utf-8 -*-
{
    "name": "ECDHS Base",
    "version": "18.0.0.0.3",
    "category": "Base",
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "base",
        "web",
        "web_studio",
        "sign"
    ],
    "data": [
        # "security/security.xml",
        # "data/data.xml",
        "views/menu.xml",
        "views/asset_action_inherit.xml",
        "views/sign_send_request_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ecdhs_base/static/src/js/custom_name_and_signature.js",
            ('remove', 'web_studio/static/src/systray_item/systray_item.js'),
            "ecdhs_base/static/src/custom_systray_item/custom_systray_item.xml",
            "ecdhs_base/static/src/custom_systray_item/custom_systray_item.js",
            "ecdhs_base/static/src/custom_sign_item/custom_sign_template_control_panel.xml",
            "ecdhs_base/static/src/custom_sign_item/custom_sign_template_control_panel.js",
            "ecdhs_base/static/src/custom_sign_item/custom_sign_request_control_panel.xml",
            "ecdhs_base/static/src/custom_sign_item/custom_sign_request_control_panel.js",
            "ecdhs_base/static/src/custom_sign_item/custom_sign_item_custom_popover.xml",
            "ecdhs_base/static/src/custom_sign_item/custom_signer_x2many.xml",
            "ecdhs_base/static/src/custom_sign_item/sign_disable_resize_handles.xml",
            "ecdhs_base/static/src/custom_sign_item/utils.js",

        ],
        "web.assets_frontend": [
            "ecdhs_base/static/src/js/custom_name_and_signature.js",
            "ecdhs_base/static/src/custom_sign_item/sign_disable_resize_handles.xml",
            "ecdhs_base/static/src/custom_sign_item/utils.js",
        ],
        "sign.assets_public_sign": [
            "ecdhs_base/static/src/js/custom_name_and_signature.js",
            "ecdhs_base/static/src/custom_sign_item/sign_disable_resize_handles.xml",
            "ecdhs_base/static/src/custom_sign_item/utils.js",
        ],
    },
    "demo": [
    ],
    "images": [
        "static/description/main.png"
    ],
}
