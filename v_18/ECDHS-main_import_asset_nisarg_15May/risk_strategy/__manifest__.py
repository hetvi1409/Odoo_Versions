{
    'name': 'Risk Strategy Update',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'author': '',
    'website': '',
    'sequence': 5,
    'summary': 'Business Governance',
    'description': """
    """,
    'depends': ['oi_risk_management', 'governance', 'risk_universe_update', 'internal_audit_management'],
    'data': [
        'views/risk_strategy_menus.xml',
        'views/risk_identification_views.xml',
        'views/strategic_planning_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}
