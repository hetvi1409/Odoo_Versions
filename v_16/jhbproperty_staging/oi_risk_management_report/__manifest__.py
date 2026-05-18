{
    'name': 'Risk Management Report',
    'version': '16.0.1.0.0',
    'category': 'Productivity',
    'author': '',
    'website': '',
    'sequence': 5,
    'summary': 'Risk Management Report',
    'description': """
    """,
    'depends': ['oi_risk_management', 'risk_strategy', 'risk_universe_update', 'internal_audit_management'],
    'data': [
        'report/risk_report.xml',
        'wizard/risk_report_wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}
