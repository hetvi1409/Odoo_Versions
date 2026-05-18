# -*- coding: utf-8 -*-
{
    'name': 'Contract Management',
    'version': '1.0.1',
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
    'category': 'Document Management,Accounting',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'license': 'OPL-1',
    'description':
        """
Contract Management
===================
Manage, approve, renew contracts
        """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/email_templates.xml',
        'data/mail_message_subtypes.xml',
        'data/ir_cron.xml',
        'views/menu.xml',
        'views/partner_contract.xml',
        'views/partner_contract_team.xml',
        'views/res_config_settings_views.xml',
        'views/account_move.xml',
    ],
    'depends': ['account', 'mail'],
    'qweb': [],
    'images': [
        'static/description/xf_partner_contract.png',
        'static/description/contract_approval_buttons.png',
        'static/description/approval_team_form_sale.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
