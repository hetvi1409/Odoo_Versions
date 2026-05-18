# -*- coding: utf-8 -*-
# Copyright 2022 seta PT Solusi Usaha Mudah
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# noinspection PyUnresolvedReferences,SpellCheckingInspection
{
    "name": """SETA Dashboard with AI""",
    "summary": """
        Beautiful Analytic Dashboard by SETA.
        You can create a Sales Dashboard, Inventory Dashboard, Finance Dashboard, or Others dynamically with this module.
        You can explore data with AI too!
    """,
    "category": "Reporting",
    "version": "18.0.5.2.3",
    "development_status": "Production",  # Options: Alpha|Beta|Production/Stable|Mature
    "auto_install": False,
    "installable": True,
    "application": True,
    "author": "SETA PT Solusi Usaha Mudah",
    "support": "admin@iziapp.id",
    "website": "https://www.iziapp.id",
    "license": "OPL-1",
    "images": [
        'static/description/banner.gif'
    ],

    "price": 385,
    "currency": "USD",

    "depends": [
        # odoo addons
        'base',
        'web',
        # third party addons

        # developed addons
        'seta_data',
    ],
    "data": [
        # group
        'security/res_groups.xml',

        # data
        'data/seta_visual_type.xml',
        'data/seta_visual_config.xml',
        'data/seta_visual_config_value.xml',
        'data/seta_dashboard_theme.xml',
        'data/seta_data_template.xml',

        # global action
        # 'views/action/action.xml',

        # view
        'views/common/seta_dashboard.xml',
        'views/common/seta_analysis.xml',
        'views/common/seta_lab_api_key_wizard.xml',
        'views/common/res_company.xml',

        # wizard
        'views/wizard/seta_dashboard_config_wizard.xml',

        # report paperformat
        # 'data/report_paperformat.xml',

        # report template
        # 'views/report/report_template_model_name.xml',

        # report action
        # 'views/action/action_report.xml',

        # assets
        # 'views/assets.xml',

        # onboarding action
        # 'views/action/action_onboarding.xml',

        # action menu
        'views/action/action_menu.xml',

        # action onboarding
        # 'views/action/action_onboarding.xml',

        # menu
        'views/menu.xml',

        # security
        'security/ir.model.access.csv',
        # 'security/ir.rule.csv',

        # template
        'views/template/seta_dashboard.xml',
        'views/template/seta_dashboard_slide.xml',
    ],
    "demo": [
        # 'demo/demo.xml',
    ],
    "qweb": [

    ],

    "post_load": None,
    # "pre_init_hook": "pre_init_hook",
    # "post_init_hook": "post_init_hook",
    "uninstall_hook": None,

    "external_dependencies": {"python": [], "bin": []},
    "live_test_url": "https://demo.iziapp.id/web/login",
    # "demo_title": "{MODULE_NAME}",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    "demo_url": "https://demo.iziapp.id/web/login",
    # "demo_summary": "{SHORT_DESCRIPTION_OF_THE_MODULE}",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]

    'assets': {
        'web.assets_backend': [
            # Odoo
            'web/static/src/legacy/js/core/class.js',
            'web/static/src/core/dialog/dialog.js',
            'web/static/src/core/dialog/dialog.xml',
            'web/static/src/legacy/js/public/minimal_dom.js',
            # 'web/static/src/legacy/js/core/dom.js',
            # 'web/static/src/legacy/js/core/mixins.js',
            # 'web/static/src/legacy/js/core/service_mixins.js',
            'web/static/src/legacy/js/public/public_widget.js',
            'web/static/lib/jquery/jquery.js',
            # QWeb
            # Generic
            'seta_dashboard/static/src/xml/component/seta_dialog.xml',
            # Component
            'seta_dashboard/static/src/xml/component/seta_view_dashboard.xml',
            'seta_dashboard/static/src/xml/component/seta_view_dashboard_block.xml',
            'seta_dashboard/static/src/xml/component/seta_view_analysis.xml',
            'seta_dashboard/static/src/xml/component/seta_config_analysis.xml',
            'seta_dashboard/static/src/xml/component/seta_view_table.xml',
            'seta_dashboard/static/src/xml/component/seta_view_visual.xml',
            'seta_dashboard/static/src/xml/component/seta_config_dashboard.xml',
            'seta_dashboard/static/src/xml/component/seta_select_analysis.xml',
            'seta_dashboard/static/src/xml/component/seta_select_dashboard.xml',
            'seta_dashboard/static/src/xml/component/seta_select_metric.xml',
            'seta_dashboard/static/src/xml/component/seta_select_dimension.xml',
            'seta_dashboard/static/src/xml/component/seta_select_sort.xml',
            'seta_dashboard/static/src/xml/component/seta_select_filter_temp.xml',
            'seta_dashboard/static/src/xml/component/seta_select_filter.xml',
            # Component > QWeb
            'seta_dashboard/static/src/xml/component/qweb/seta_select_analysis_item.xml',
            'seta_dashboard/static/src/xml/component/qweb/seta_select_dashboard_item.xml',
            'seta_dashboard/static/src/xml/component/qweb/seta_select_metric_item.xml',
            'seta_dashboard/static/src/xml/component/qweb/seta_select_dimension_item.xml',
            'seta_dashboard/static/src/xml/component/qweb/seta_select_filter_item.xml',
            'seta_dashboard/static/src/xml/component/qweb/seta_select_sort_item.xml',
            # Base
            'seta_dashboard/static/src/xml/seta_dashboard.xml',
            'seta_dashboard/static/src/xml/seta_analysis.xml',
            'seta_dashboard/static/src/xml/seta_analysis_widget.xml',

            # CSS
            'seta_dashboard/static/lib/select2/select2.css',
            'seta_dashboard/static/lib/select2-bootstrap-css/select2-bootstrap.css',
            'seta_dashboard/static/lib/gridstack/gridstack.min.css',
            'seta_dashboard/static/lib/grid/mermaid.min.css',
            'seta_dashboard/static/lib/google/icon.css',
            'seta_dashboard/static/lib/jquery.ui/jquery-ui.css',
            'seta_dashboard/static/lib/bootstrap-datepicker/css/bootstrap-datepicker3.min.css',
            'seta_dashboard/static/lib/bootstrap-datepicker/css/bootstrap-datepicker.min.css',
            'seta_dashboard/static/lib/tempusdominus/tempusdominus.min.css',
            'seta_dashboard/static/lib/google/icon.css',

            'seta_dashboard/static/src/css/font.css',
            'seta_dashboard/static/src/css/component/general/seta_bootstrap.min.css',
            'seta_dashboard/static/src/css/component/general/seta_layout.css',
            'seta_dashboard/static/src/css/component/general/seta_dialog.css',
            'seta_dashboard/static/src/css/component/general/seta_button.css',
            'seta_dashboard/static/src/css/component/general/seta_select.css',
            'seta_dashboard/static/src/css/component/general/seta_accordion.css',
            'seta_dashboard/static/src/css/component/general/seta_chart.css',
            'seta_dashboard/static/src/css/component/general/seta_replace.css',

            'seta_dashboard/static/src/css/component/main/seta_view.css',
            'seta_dashboard/static/src/css/component/main/seta_view_table.css',
            'seta_dashboard/static/src/css/component/main/seta_view_dashboard.css',
            'seta_dashboard/static/src/css/component/main/seta_config_analysis.css',
            'seta_dashboard/static/src/css/component/main/seta_config_dashboard.css',
            'seta_dashboard/static/src/css/component/main/seta_select_analysis.css',
            'seta_dashboard/static/src/css/component/main/seta_select_metric.css',
            'seta_dashboard/static/src/css/component/main/seta_select_dimension.css',
            'seta_dashboard/static/src/css/component/main/seta_select_sort.css',
            'seta_dashboard/static/src/css/component/main/seta_select_filter_temp.css',
            'seta_dashboard/static/src/css/component/main/seta_select_filter.css',
            'seta_dashboard/static/src/css/component/main/seta_description_page.css',

            'seta_dashboard/static/src/css/component/toggle-switchy.css',

            # JS
            'seta_dashboard/static/lib/jquery.ui/jquery-ui.js',
            'seta_dashboard/static/lib/select2/select2.js',
            'seta_dashboard/static/lib/moment/moment.js',
            'seta_dashboard/static/lib/ace-1.3.1/ace.js',
            'seta_dashboard/static/lib/ace-1.3.1/mode-javascript.js',
            'seta_dashboard/static/lib/ace-1.3.1/worker-javascript.js',
            'seta_dashboard/static/lib/ace-1.3.1/theme-chrome.js',
            'seta_dashboard/static/lib/ace-1.3.1/mode-sql.js',
            'seta_dashboard/static/lib/ace-1.3.1/theme-chrome.js',
            'seta_dashboard/static/lib/amcharts/core.js',
            'seta_dashboard/static/lib/amcharts/charts.js',
            'seta_dashboard/static/lib/amcharts/maps.js',
            'seta_dashboard/static/lib/amcharts/regression.js',
            'seta_dashboard/static/lib/amcharts/geodata/indonesiaLow.js',
            'seta_dashboard/static/lib/amcharts/geodata/usaLow.js',
            'seta_dashboard/static/lib/amcharts/geodata/worldLow.js',
            'seta_dashboard/static/lib/amcharts/geodata/countries2.js',
            'seta_dashboard/static/lib/amcharts/themes/animated.js',
            'seta_dashboard/static/lib/amcharts/themes/frozen.js',
            'seta_dashboard/static/lib/gridstack/gridstack-h5.js',
            # 'seta_dashboard/static/lib/gridstack/gridstack-poly.js',
            # 'seta_dashboard/static/lib/gridstack/gridstack-all.js',
            'seta_dashboard/static/lib/sweetalert/sweetalert.min.js',
            'seta_dashboard/static/lib/xlsx/xlsx.full.min.js',
            'seta_dashboard/static/lib/grid/gridjs.umd.js',
            'seta_dashboard/static/lib/jspdf/html2canvas.min.js',
            'seta_dashboard/static/lib/jspdf/jspdf.umd.min.js',
            'seta_dashboard/static/lib/jquery.ui/jquery-ui.js',
            'seta_dashboard/static/lib/bootstrap-datepicker/js/bootstrap-datepicker.min.js',
            'seta_dashboard/static/lib/bootstrap-datepicker/js/bootstrap-datepicker-conflict.js',
            'seta_dashboard/static/lib/jscolor/jscolor.min.js',

            'seta_dashboard/static/lib/tempusdominus/tempusdominus.min.js',
            'seta_dashboard/static/src/js/component/chart/amcharts_theme.js',
            'seta_dashboard/static/src/js/component/chart/amcharts_component_old.js',
            'seta_dashboard/static/src/js/component/chart/amcharts_component.js',
            'seta_dashboard/static/src/js/component/general/seta_autocomplete.js',
            'seta_dashboard/static/src/js/component/general/seta_tags.js',
            'seta_dashboard/static/src/js/component/general/seta_dialog.js',
            'seta_dashboard/static/src/js/component/general/seta_field_icon.js',
            'seta_dashboard/static/src/js/component/general/seta_dropdown.js',
            'seta_dashboard/static/src/js/component/main/seta_view_dashboard.js',
            'seta_dashboard/static/src/js/component/main/seta_view_dashboard_block.js',
            'seta_dashboard/static/src/js/component/main/seta_view_analysis.js',
            'seta_dashboard/static/src/js/component/main/seta_view_table.js',
            'seta_dashboard/static/src/js/component/main/seta_view_visual.js',
            'seta_dashboard/static/src/js/component/main/seta_config_dashboard.js',
            'seta_dashboard/static/src/js/component/main/seta_config_analysis.js',
            'seta_dashboard/static/src/js/component/main/seta_select_analysis.js',
            'seta_dashboard/static/src/js/component/main/seta_select_dashboard.js',
            'seta_dashboard/static/src/js/component/main/seta_select_metric.js',
            'seta_dashboard/static/src/js/component/main/seta_select_dimension.js',
            'seta_dashboard/static/src/js/component/main/seta_select_sort.js',
            'seta_dashboard/static/src/js/component/main/seta_select_filter_temp.js',
            'seta_dashboard/static/src/js/component/main/seta_select_filter.js',
            'seta_dashboard/static/src/js/component/main/seta_add_analysis.js',
            'seta_dashboard/static/src/js/seta_analysis_controller.js',
            'seta_dashboard/static/src/js/seta_analysis_view.js',
            'seta_dashboard/static/src/js/seta_dashboard_controller.js',
            'seta_dashboard/static/src/js/seta_dashboard_view.js',
            'seta_dashboard/static/src/js/seta_analysis_widget.js',
            'seta_dashboard/static/src/js/seta_slide.js',
        ]
    }
}
