{
    'name': "Asset Maintenance",
    'description': """Asset Maintenance""",
    'summary': """Asset Maintenance""",
    'version': '16.0.1.0.0',
    'sequence': '20',
    'category': 'Accounting,Manufacturing',
    'depends': ['asset_registration', 'maintenance', 'helpdesk', 'fleet'],
    'data': [
        'data/maintenance_stage_data.xml',
        'data/maintenance_team_data.xml',
        'security/ir.model.access.csv',
        'views/account_asset_views.xml',
        'views/maintenance_request_views.xml',
        'views/helpdesk_ticket_views.xml',
        # 'views/job_cad_views.xml',
        'views/maintenance_team_views.xml',
        'wizard/import_maintenance_views.xml',
        'wizard/maintenance_job_card_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            # 'asset_registration/static/src/js/action_manager.js',
        ],
    },

    'external_dependencies': {
        # 'python': ['openpyxl'],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,

}