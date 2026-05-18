{
    'name': 'Assets Disposal',
    'version': '19.0.1.0.0',
    'summary': 'Manage the disposal of fixed assets including calculations and journal entries',
    'description': """
        This module allows users to manage the disposal of fixed assets, including handling different disposal methods (Sale, Donation, Scrapping, Other), calculating depreciation, and generating necessary journal entries.
    """,
    'category': 'Accounting/Assets',
    'depends': ['web','accountant','account_asset','asset_update'],
    'data': [
        'data/approval_template.xml',
        'security/ir.model.access.csv',
        'security/client_enquiry_security.xml',
        'views/account_asset.xml',
        'views/asset_removal_approval.xml',

    ],
'assets': {

'web.assets_backend': [
    'assets_disposal/static/src/core/signature/signature.xml'
        ],
},
    'installable': True,
    'application': True,
}

