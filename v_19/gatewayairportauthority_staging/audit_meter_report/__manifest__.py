{
    "name": "Meter Audit Report",
    "version": "19.0.1.0.0",
    'summary': '',
    'author': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': '',
    "category": "Extra Tools",
    "depends": ['web','base'],
    "data": [
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'report/meter_audit_report.xml',
        'report/meter_audit_only_report.xml',
        'report/meter_audit_report_image.xml',
        'security/ir.model.access.csv',
        'views/audit_meter_views.xml',
        'views/res_partner_views.xml',
        'views/audit_line_views.xml'

    ],
    "assets": {
        "web.assets_backend": [
            'audit_meter_report/static/src/js/meter_audit_report.js',
            'audit_meter_report/static/src/js/meter_audit_only_report.js',
            'audit_meter_report/static/src/xml/meter_audit_report.xml',
            'audit_meter_report/static/src/xml/meter_audit_only_report.xml',
            'audit_meter_report/static/src/scss/report.scss',
        ],
    },
    'license': 'AGPL-3',
    "application": True,
    'installable': True,
}
