# -*- coding: utf-8 -*-
{
    "name": "Inventory Adjustments from Excel (Production Template)",
    'version': '1.0',
    'author': 'Nated Systems (Pty) Ltd',
    'website': 'http://natedsystems.co.za',    
    "category": "Inventory/Inventory",
    "summary": "Import production template Excel, normalize per SKU, and apply inventory at a chosen location.",    
    'description': 'Import production template Excel, normalize per SKU, and apply inventory at a chosen location.',
    'depends': ['stock'],
    "data": [
    "security/inventory_production_access.xml",

    "views/import_inventory_wizard_views.xml",  # <-- load first
    "views/inventory_batch_views.xml",           # <-- then the form that references it
            ],
 
    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
# Part of Odoo. See LICENSE file for full copyright and licensing details.