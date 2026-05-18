# -*- coding: utf-8 -*-
{
    'name': 'Risk Management',
    'summary': 'Risk, Risk Management, Global Risk, Business Risk, Company Risk, Financial '
               'Risk, Non-Financial Risk, Risk Profile, Risk Report, Risk Manager, Risk '
               'Analysis, Risk Assessment, Risk Tracking, Risk Evolution, Control '
               'Effectiveness, Likelihood, Severity, Risk Matrix',
    'description': 'Risk Management Module ',
    'images': ['static/description/cover.png'],
    'category': 'Extra Tools',
    'version': "19.0.1.0.0",
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends': ['base', 'hr', 'mail', 'oi_workflow'],
    'data': [
        'security/risk_security.xml',
         'security/ir.model.access.csv',
         'data/risk_criteria_data.xml',
         'data/category_data.xml',
         # 'data/approval_config.xml',
         'data/ir_config_parameter.xml',
         'views/activity.xml',
         'views/categories.xml',
         'views/risk.xml',
         'views/risk_treatment.xml',
         'views/risk_criteria.xml',
         'views/risk_dashboard.xml',
         'views/tags.xml',
         'views/actions.xml',
         'views/reports.xml',
         'views/res_config_settings_views.xml',
         'views/menus.xml',
         'wizard/list_of_risks_department.xml',
         'wizard/risk_dashboard_department.xml'
    ],

    # 'assets': {
    #     'web.assets_backend': [
    #         'oi_risk_management/static/src/js/list_view_expand_groups.js',
    #     ],
    #     'web.assets_frontend': [
    #         'oi_risk_management/static/src/js/list_view_expand_groups.js',
    #     ],
    # },
    'application': True,
    'license': 'OPL-1',
}
