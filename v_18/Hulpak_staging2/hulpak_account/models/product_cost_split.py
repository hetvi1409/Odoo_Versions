# models/product_cost_split.py

from odoo import models, fields
# from odoo import models
# from odoo.exceptions import UserError

class ProductCostSplit(models.Model):
    _name = "product.cost.split"
    _description = "Cost Split per Product"
    _rec_name = 'main_product_id'

    main_product_id = fields.Many2one('product.product', string='Main Product', required=True)    
    machine = fields.Many2one('machinery.component', string='Attached to Machine')
    

    line_ids = fields.One2many('product.cost.split.line', 'split_id', string='Split Lines')

class ProductCostSplitLine(models.Model):
    _name = "product.cost.split.line"
    _description = "Cost Split Line"
    _rec_name = 'component_product_id'

    split_id = fields.Many2one('product.cost.split', required=True, ondelete='cascade')
    component_product_id = fields.Many2one('product.product', string='Component Product', required=True)
    amount = fields.Float(string='Amount', required=True)
    account_id = fields.Many2many('account.account', string='COS Accounts')



