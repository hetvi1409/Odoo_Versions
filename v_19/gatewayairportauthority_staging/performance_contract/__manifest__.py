{
    "name": "Annual Performance Contract",
    "version": "0.1",
    "category": "HR",
    "summary": "Performance Contracts linked with Appraisal & Sign",
    "depends": ["hr", "hr_appraisal", "sign"],
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "data/mail_template.xml",
        "views/performance_contract_template.xml",
        "views/performance_contract.xml",
        "views/approval_config.xml",
        "views/hr_appraisal_goal.xml",
        "wizard/multi_goal_managment.xml",
        "views/approval_team.xml",
        "views/approval_team_line.xml",
        "views/res_config_settings.xml",
        # "views/performance_contract_approval.xml",
        "views/menus.xml",
    ],

    'assets': {
        'web.assets_backend': [
            'performance_contract/static/src/views/contract_dashboard.xml',
            'performance_contract/static/src/js/contract_dashboard.js',
            'performance_contract/static/src/scss/contract_dashboard.scss',
            # 'performance_contract/static/src/js/lib/Chart.bundle.js'
        ],
    },

    "installable": True,
    "application": True,
}
