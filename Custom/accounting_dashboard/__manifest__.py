# accounting_dashboard_custom/__manifest__.py
{
    "name": "Accounting Dashboard (Custom)",
    "summary": "Custom accounting dashboard with client-server action and charts",
    "version": "1.0.0",
    "author": "Your Company",
    "license": "OPL-1",
    "category": "Accounting",
    "depends": ["account", "web","base","account_reports","account"],
    "data": [
        # "security/ir.model.access.csv",
        "views/ir_actions_client.xml",
        # "views/assets.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "accounting_dashboard/static/src/js/client_action/dashboard_account.js",
            "accounting_dashboard/static/src/js/client_action/template.xml",
            "accounting_dashboard/static/lib/Chart/Chart.js"
        ],
    },

    "installable": True,
    "application": True,
}
