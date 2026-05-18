# -*- coding: utf-8 -*-
{
    'name': 'Purchase Contract Management',
    'version': '19.0.1.0.0',
    'summary': """
    This module helps to manage/approve/renew purchase contracts
    , purchase contract 
    , purchase order contract 
    , rfq contract 
    , quotation contract 
    , purchase contract approval process
    , approve purchasing contract
    , approve contract purchase
    , order contract approval workflow
    , purchase contract management
    , vendor contract approval
    , supplier contract
    , purchase order template
    , vendor bill template
    , recurring purchases
    , purchase recurring
    , purchase order recurring
    , po recurring
    , recurring quotation
    , recurring rfq
    """,
    'category': 'Purchases,Accounting,Document Management',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'license': 'OPL-1',
    'description':
        """
Purchase Contract Management
============================
Manage, approve, renew purchase contracts
        """,
    'data': [
        'views/partner_contract.xml',
        'views/res_config_settings_views.xml',
        'views/purchase_order.xml',
    ],
    'depends': ['xf_partner_contract', 'purchase'],
    'qweb': [],
    'images': [
        'static/description/xf_partner_contract_purchase.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
