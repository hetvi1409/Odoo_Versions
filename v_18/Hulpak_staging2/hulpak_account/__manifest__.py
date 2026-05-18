# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Cost Accounting - Cost of Sales Calculation',
    'version': '1.0',
    'author': 'Nated Systems (Pty) Ltd',
    'website': 'http://natedsystems.co.za',
    'category': 'Accounting',
    'description': 'Cost Accounting - Cost of Sales Calculation',
    'depends': ['base', 'account', 'accountant', 'analytic', 'base_vat', 'sale', ],
    'auto_install': ['account','hulpak_sales'],
    'data': [
                'security/product_cost_split_access.xml',
                'views/product_cost_split_views.xml',
                'views/account_account_view.xml',
                'views/account_move.xml',
                'views/purchase_order.xml',
                'views/invoice_report_templates.xml',
            ],

    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
# Part of Odoo. See LICENSE file for full copyright and licensing details.