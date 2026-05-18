# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Analytic Data Query""",
    "summary": """seta Module to Handle Data Query. Dependency For seta Dashboard by seta""",
    "category": "Reporting",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",  # Options: Alpha|Beta|Production/Stable|Mature
    "auto_install": False,
    "installable": True,
    "application": False,
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "license": "OPL-1",
    "images": [
        'static/description/banner.jpg'
    ],
    "depends": [
        # odoo addons
        'base',
        # third party addons

        # developed addons
    ],
    "data": [
        # group
        'security/res_groups.xml',

        # data
        'data/seta_table_field_mapping_db_odoo.xml',
        'data/seta_analysis_filter_operator_db_odoo.xml',

        # global action
        # 'views/action/action.xml',

        # view
        'views/common/seta_data_source.xml',
        'views/common/seta_table.xml',
        'views/common/seta_analysis.xml',
        'views/common/ir_attachment.xml',
        'views/common/ir_cron.xml',
        'views/common/seta_kpi.xml',
        'views/common/seta_kpi_line.xml',

        # action menu
        'views/action/action_menu.xml',

        # menu
        'views/menu.xml',

        # security
        'security/ir.model.access.csv',
        # 'security/ir.rule.csv',

    ],

    "external_dependencies": {"python": [
        "pandas",
        "openpyxl",
        "requests",
        "xlsxwriter",
        "sqlparse",
    ], "bin": []},
}
