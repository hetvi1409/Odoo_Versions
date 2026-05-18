{
    "name": "ECDHS OPMS",
    "version": "18.0.1.1.0",
    "summary": "Operational Performance Management System for ECDHS",
    "description": """
OPMS module for APP/Plan import and operational performance planning matrix.
Includes hierarchy from Plan -> Programme -> Sub-Programme -> Directorate -> Output -> Output Indicator,
with annual and quarterly target planning, narratives, evidence and reporting submissions.
    """,
    "category": "Productivity",
    "author": "ECDHS",
    "license": "LGPL-3",
    "depends": ["base", "mail", "account", "portal", "website", "documents_spreadsheet", "spreadsheet_dashboard"],
    "external_dependencies": {"python": ["openpyxl"]},
    "data": [
        "security/opms_groups.xml",
        "security/opms_access_rules.xml",
        "security/ir.model.access.csv",
        "data/opms_spreadsheet_dashboard_group.xml",
        "data/opms_fiscal_year_cron.xml",
        "data/opms_live_sync_cron.xml",
        "data/opms_submission_reminder_templates.xml",
        "views/opms_views.xml",
        "views/opms_import_wizard_views.xml",
        "views/opms_submission_period_wizard_views.xml",
        "views/opms_submission_reminder_wizard_views.xml",
        "views/opms_submission_notification_wizard_views.xml",
        "views/opms_rejection_reason_wizard_views.xml",
        "views/opms_user_groups_views.xml",
        "views/opms_menus.xml",
        "views/opms_app_annual_report_wizard_views.xml",
        "views/opms_sub_entity_report_wizard_views.xml",
        "views/opms_settings_views.xml",
        "views/opms_server_actions.xml",
        "reports/opms_app_annual_report_template.xml",
        "reports/opms_app_annual_report_action.xml",
        "reports/opms_sub_entity_report_template.xml",
        "reports/opms_sub_entity_report_action.xml",
        "views/portal_templates/opms_portal_submission_templates.xml",
        "views/portal_templates/opms_portal_all_submissions.xml",
        "demo/portal_user_demo.xml"
    ],
    "demo": [
        "demo/portal_user_demo.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "opms_ecdhs/static/src/css/opms_portal.css",
            "opms_ecdhs/static/src/js/opms_dynamic_labels_frontend.js",
            "opms_ecdhs/static/src/js/opms_searchable_selects_frontend.js",
        ],
        "web.assets_backend": [
            "opms_ecdhs/static/src/css/opms_backend.css",
            "opms_ecdhs/static/src/js/opms_dynamic_labels_backend.js",
        ],
    },
    "post_init_hook": "post_init_hook",
    "images": ['opms_ecdhs/static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}