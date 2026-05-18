{
    'name': 'Manufacturing - Serial Number',
    'version': '1.0',
    'author': 'Nated Systems (Pty) Ltd',
    'website': 'http://natedsystems.co.za',
    'category': 'Manufacturing',
    'description': 'Manufacturing - Serial Number',
    'depends': ['mrp','stock'],
    'data': [
        'report/manufacturing_order_report.xml',
        'report/serial_label_report.xml',
        "views/mrp_bom_views.xml",
        "views/stock_lot.xml",
        "views/mrp_production_views.xml",
        "wizard/mrp_batch_production.xml",
    ],

    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
