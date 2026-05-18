# See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Management ',
    # test
    'version': '18.0.1.0.0',
    'category': 'Partner',
    'license': 'LGPL-3','version': '1.0',
    'author': 'Nated Systems (Pty) Ltd',
    'website': 'http://natedsystems.co.za',
    'category': 'Sales',
    'summary': 'Sale & sales management enhancements',
    'depends': [

        'sale_management','stock',
            ],
    'data': [
        'views/sales.xml',
        'views/sale_report.xml',
        'views/view_product_product.xml',
        'views/view_product_template.xml',
        'views/machinery_component_views.xml',

    ],    
    'installable': True,
}
