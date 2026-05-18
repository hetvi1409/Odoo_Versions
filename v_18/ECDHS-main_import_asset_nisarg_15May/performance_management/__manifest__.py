# -*- coding: utf-8 -*-
{
    'name': 'Performance Management',
    'version': '18.0.1.1.2',
    'category': 'Management',
    'summary': 'Track and manage organizational performance indicators and targets with international UoM standards',
    'description': '''
        Performance Management System
        ==========================================

        This module provides comprehensive performance tracking capabilities including:
        * Programme management with Outcome Outputs
        * Performance indicators tracking with Output Indicators
        * Target setting and monitoring with quarterly breakdown
        * Achievement recording and analysis with variance calculation
        * Performance reporting and dashboards
        * International Units of Measure (UoM) standards

        Based on Annual Performance Plan requirements.

        Features:
        - Outcome Output tracking per programme
        - Output Indicator specification per performance indicator
        - International UoM standards (SI units, Imperial, etc.)
        - Mail integration for tracking changes
    ''',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': "https://natedsystems.co.za",
    'depends': ['base', 'mail', 'governance', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/app_report_wizard_view.xml',
        'wizard/app_quarterly_report_wizard_view.xml',
        'views/performance_outcome_views.xml',
        'views/performance_views.xml',
        'views/programme_views.xml',
        'views/target_targets_views.xml',
        'views/performance_output_views.xml',
        'views/output_indicator_views.xml',
        'views/long_term_planing_views.xml',
        'views/medium_term_planing_views.xml',
        'views/short_term_planing_views.xml',
        'views/indicator_dimension_views.xml',
        'views/indicator_target_views.xml',
        'views/indicator_target_quarter_views.xml',
        'views/reporting_collection_views.xml',
        'views/activities_views.xml',
        'reports/app_report.xml',
        'reports/report_template.xml',
        'reports/app_quaterely_action.xml',
        'reports/report_quaterly_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'performance_management/static/src/css/style.css',
        ],
    },
    'images': ['static/description/icon.png'],
    'demo': [
        'data/app_2025_26_portfolio_seed.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}