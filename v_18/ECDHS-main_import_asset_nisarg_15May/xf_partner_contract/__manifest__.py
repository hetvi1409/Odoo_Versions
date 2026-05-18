# -*- coding: utf-8 -*-
{
    'name': 'Contract Management',
    'version': '18.0.1.0.0',
    'summary': """
    This module helps to manage/approve/renew contracts
    , purchase contract
    , sale contract
    , recurring contract
    , contract recurring
    , approve contract document
    , contract approval process
    , contract workflow
    , contract approval workflow
    , sales contract management
    , partner contract repository
    , partner contract management
    , approve vendor contract
    , approve customer contract
    , approve supplier contract
    , customer invoice template
    , vendor bill template
    """,
'license': 'OPL-1',
    'price': 35,
    'currency': 'EUR',
    'description':
        """
Contract Management
===================
Manage, approve, renew contracts
        """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'data/ir_cron.xml',
        'data/contract_sequence.xml',
        'data/email_templates.xml',
        'data/mail_message_subtypes.xml',
        'views/menu.xml',
        'views/partner_contract.xml',
        'views/partner_contract_team.xml',
        'views/res_config_settings_views.xml',
        'views/account_move.xml',
        'views/res_province_views.xml',
        'views/contract_template_views.xml',
        'report/contract_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'xf_partner_contract/static/src/css/app_menu_wrap.css',
        ],
    },
    'depends': ['account', 'documents', 'mail', 'sale', 'project'],
    # stock_landed_costs
    'images': [
        'static/description/xf_partner_contract.png',
        'static/description/contract_approval_buttons.png',
        'static/description/approval_team_form_sale.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
