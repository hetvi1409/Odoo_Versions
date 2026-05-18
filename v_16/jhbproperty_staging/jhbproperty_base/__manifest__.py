# -*- coding: utf-8 -*-
{
    "name": "Jhb Property Base",
    "version": "16.0.0.0.2",
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
        "hr_attendance",
        "seta_data",
        "crm",
        "helpdesk",
        "project",
        "contacts",
        "planning",
        "stock",
        "hr_holidays",
        "itsys_real_estate",
        "social",
        "mass_mailing",
        "survey",
        "hr_work_entry_contract_enterprise",
        "utm",
        "event",
        "fleet",
        "cloud_base",
        "spreadsheet_dashboard",
        "network_drives",
        "law_firm_bits",
        "web_studio",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data_powered_by_brand_promotion_login.xml",
        # "data/data.xml",
        "views/menu.xml",
        "views/asset_action_inherit.xml"
    ],
    "assets": {
        "web.assets_backend": [
            ('remove', 'web_studio/static/src/systray_item/systray_item.js'),
            'jhbproperty_base/static/src/custom_systray_item/custom_systray_item.xml',
            "jhbproperty_base/static/src/custom_systray_item/custom_systray_item.js",
        ],
        "web.assets_frontend": [
            "jhbproperty_base/static/src/brand_promotion/brand_promotion.scss",
        ],
    },
    "demo": [
    ],
    "images": [
        "static/description/main.png"
    ],
}