{
    'name': 'Risk Workflow',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'author': '',
    'website': '',
    'sequence': 5,
    'summary': 'Risk Workflow',
    'description': """
    """,
    'depends': ['oi_risk_management', 'risk_universe_update','internal_audit_management'],
    'data': [
        'data/mail_template.xml',
        'data/audit_revert_data.xml',
        'data/risk_register_criteria_data.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/oi_risk_management_views.xml',
        'views/activity_view.xml',
        'views/oi_risk_register_view.xml',
        'wizard/risk_revert_wizard_views.xml',
        'wizard/risk_register_import_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}
