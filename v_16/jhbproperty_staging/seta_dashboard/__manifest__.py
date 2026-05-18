# -*- coding: utf-8 -*-
{
    "name": """Analytic Dashboard & KPI""",
    "summary": """
        Beautiful Analytic Dashboard Builder for SETA's.
    """,
    "category": "Reporting",
    "version": "15.0.0.1.0",
    "development_status": "Production",  # Options: Alpha|Beta|Production/Stable|Mature
    "auto_install": False,
    "installable": True,
    "application": True,
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    "license": "OPL-1",
    "images": [
        'static/description/banner.gif'
    ],
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

        # view
        'views/common/seta_dashboard.xml',
        'views/common/seta_analysis.xml',

        # action menu
        'views/action/action_menu.xml',

        # menu
        'views/menu.xml',

        # security
        'security/ir.model.access.csv',

    ],

    "external_dependencies": {"python": [], "bin": []},

    'assets': {
        # 'web.assets_qweb': [
        #     # Generic
        #     'seta_dashboard/static/src/xml/component/seta_dialog.xml',
        #     # Component
        #     'seta_dashboard/static/src/xml/component/seta_view_dashboard.xml',
        #     'seta_dashboard/static/src/xml/component/seta_view_dashboard_block.xml',
        #     'seta_dashboard/static/src/xml/component/seta_view_analysis.xml',
        #     'seta_dashboard/static/src/xml/component/seta_config_analysis.xml',
        #     'seta_dashboard/static/src/xml/component/seta_view_table.xml',
        #     'seta_dashboard/static/src/xml/component/seta_view_visual.xml',
        #     'seta_dashboard/static/src/xml/component/seta_config_dashboard.xml',
        #     'seta_dashboard/static/src/xml/component/seta_select_analysis.xml',
        #     'seta_dashboard/static/src/xml/component/seta_select_dashboard.xml',
        #     'seta_dashboard/static/src/xml/component/seta_select_metric.xml',
        #     'seta_dashboard/static/src/xml/component/seta_select_dimension.xml',
        #     'seta_dashboard/static/src/xml/component/seta_select_sort.xml',
        #     'seta_dashboard/static/src/xml/component/seta_select_filter_temp.xml',
        #     'seta_dashboard/static/src/xml/component/seta_select_filter.xml',
        #     # Component > QWeb
        #     'seta_dashboard/static/src/xml/component/qweb/seta_select_analysis_item.xml',
        #     'seta_dashboard/static/src/xml/component/qweb/seta_select_dashboard_item.xml',
        #     'seta_dashboard/static/src/xml/component/qweb/seta_select_metric_item.xml',
        #     'seta_dashboard/static/src/xml/component/qweb/seta_select_dimension_item.xml',
        #     'seta_dashboard/static/src/xml/component/qweb/seta_select_filter_item.xml',
        #     'seta_dashboard/static/src/xml/component/qweb/seta_select_sort_item.xml',
        #     # Base
        #     'seta_dashboard/static/src/xml/seta_dashboard.xml',
        #     'seta_dashboard/static/src/xml/seta_analysis.xml',
        # ],
        'web.assets_backend': [
# Generic
#             "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",
#             "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/dom-to-image/2.6.0/dom-to-image.min.js",
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

            'seta_dashboard/static/lib/gridstack/gridstack.min.css',
            'seta_dashboard/static/lib/grid/mermaid.min.css',
            'seta_dashboard/static/lib/google/icon.css',

            'seta_dashboard/static/src/css/font.css',
            'seta_dashboard/static/src/css/component/general/seta_layout.css',
            'seta_dashboard/static/src/css/component/general/seta_dialog.css',
            'seta_dashboard/static/src/css/component/general/seta_button.css',
            'seta_dashboard/static/src/css/component/general/seta_select.css',
            'seta_dashboard/static/src/css/component/general/seta_accordion.css',
            'seta_dashboard/static/src/css/component/general/seta_chart.css',
            'seta_dashboard/static/src/css/component/general/seta_replace.css',
            'seta_dashboard/static/src/css/component/general/seta_bootstrap.min.css',

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
            'seta_dashboard/static/lib/sweetalert/sweetalert.min.js',
            'seta_dashboard/static/lib/grid/gridjs.umd.js',
            'seta_dashboard/static/lib/jspdf/html2canvas.min.js',
            'seta_dashboard/static/lib/jspdf/jspdf.umd.min.js',

            'seta_dashboard/static/src/js/component/chart/amcharts_theme.js',
            'seta_dashboard/static/src/js/component/chart/amcharts_component_old.js',
            'seta_dashboard/static/src/js/component/chart/amcharts_component.js',
            'seta_dashboard/static/src/js/component/general/seta_autocomplete.js',
            'seta_dashboard/static/src/js/component/general/seta_tags.js',
            'seta_dashboard/static/src/js/component/general/seta_dialog.js',
            'seta_dashboard/static/src/js/component/general/seta_field_icon.js',
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
            'seta_dashboard/static/src/js/seta_analysis_model.js',
            'seta_dashboard/static/src/js/seta_analysis_controller.js',
            'seta_dashboard/static/src/js/seta_analysis_renderer.js',
            'seta_dashboard/static/src/js/seta_analysis_view.js',
            'seta_dashboard/static/src/js/seta_dashboard_model.js',
            'seta_dashboard/static/src/js/seta_dashboard_controller.js',
            'seta_dashboard/static/src/js/seta_dashboard_renderer.js',
            'seta_dashboard/static/src/js/seta_dashboard_view.js',
        ]
    }
}
