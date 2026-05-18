{
    'name': "asset_verification_import",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','asset_import'],

    'data': [
        # 'demo/data.xml',

        # 'security/ir.model.access.csv',
        'wizard/asset_verification_import.xml',
    ],
}

