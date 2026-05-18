{
    'name': "asset_import",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',

    'depends': ['base','fixed_assets'],

    'data': [
        'demo/data.xml',

        'security/ir.model.access.csv',
        'wizard/asset_import.xml',
    ],
}

