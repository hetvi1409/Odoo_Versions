{
    'name': 'Risk Universe Update',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'author': '',
    'website': '',
    'sequence': 5,
    'summary': 'Business Governance',
    'description': """
    """,
    'depends': ['oi_risk_management'],
    'data': [
        'data/risk_type_data.xml',
        'security/ir.model.access.csv',
        'views/oi_risk_management_risk_views.xml',
        'views/risk_type_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}
