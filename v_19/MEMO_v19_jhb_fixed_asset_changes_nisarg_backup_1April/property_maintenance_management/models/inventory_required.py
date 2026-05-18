from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InventoryRequired(models.Model):
    _name = 'inventory.required'
    _description = 'Inventory Required'

    product_id = fields.Many2one('product.product', string="Product")
    product_uom_qty = fields.Float(
        string="Quantity", store=True)

    # price_unit = fields.Float(
    #     string="Unit Price", compute="_compute_price_unit")
    # def _default_currency_id(self):
    #     return self.env.user.company_id.currency_id
    # currency_id = fields.Many2one('res.currency', string='Currency',
    #                               required=True, default=lambda
    #         self: self._default_currency_id())
    # price_subtotal = fields.Monetary(compute="_compute_price_subtotal",
    #     string="Subtotal")

    required_inventory_job = fields.Many2one('job.card')

    # @api.depends('product_id')
    # def _compute_price_unit(self):
    #     for line in self:
    #         line.price_unit = False
    #         if line.product_id.lst_price:
    #             line.price_unit = line.product_id.lst_price
    #
    # @api.depends('product_id', 'product_uom_qty')
    # def _compute_price_subtotal(self):
    #     for line in self:
    #         line.price_subtotal = False
    #         price_unit = line.product_id.lst_price
    #         product_uom_qty = line.product_uom_qty
    #         line.price_subtotal = price_unit * product_uom_qty
