# -*- coding: utf-8 -*-
from odoo import api, fields, models , _
from odoo.fields import Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    unit_price_before_discount = fields.Float(_('Unit Price Before Discount'), related='product_id.lst_price')
    discount_amount = fields.Float(_('Discount Amount'), compute='_compute_discount_amount', store=True)
    total_before_discount = fields.Float(_('Total Before Discount'), compute='_compute_total_before_discount', store=True)
    # stock_location_id = fields.Many2one('stock.quant', _('Stock By Location'),store=True)

    @api.depends('product_uom_qty', 'product_id','product_id.lst_price','order_id.pricelist_id')
    def _compute_discount_amount(self):
        for line in self:
                line.discount_amount = (line.product_id.lst_price - line.price_unit) * line.product_uom_qty
                line.discount_amount = abs(line.discount_amount)

    @api.depends('unit_price_before_discount', 'product_uom_qty')
    def _compute_total_before_discount(self):
        for line in self:
            line.total_before_discount = line.product_id.lst_price * line.product_uom_qty



    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()

        if self.product_id.type == 'combo':
            # If the quantity to invoice is a whole number, format it as an integer (with no decimal point)
            qty_to_invoice = int(self.qty_to_invoice) if self.qty_to_invoice == int(self.qty_to_invoice) else self.qty_to_invoice
            return {
                'display_type': 'line_section',
                'sequence': self.sequence,
                'name': f'{self.product_id.name} x {qty_to_invoice}',
                'product_uom_id': self.product_uom.id,
                'quantity': self.qty_to_invoice,
                'unit_price_before_discount': self.unit_price_before_discount,
                'discount_amount': self.discount_amount,
                'total_before_discount': self.total_before_discount,
                'sale_line_ids': [Command.link(self.id)],
                **optional_values,
            }
        res = {
            'display_type': self.display_type or 'product',
            'sequence': self.sequence,
            'name': self.env['account.move.line']._get_journal_items_full_name(self.name, self.product_id.display_name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [Command.set(self.tax_id.ids)],
            'sale_line_ids': [Command.link(self.id)],
            'is_downpayment': self.is_downpayment,
            'unit_price_before_discount': self.unit_price_before_discount,
            'discount_amount': self.discount_amount,
            'total_before_discount': self.total_before_discount,
        }
        downpayment_lines = self.invoice_lines.filtered('is_downpayment')
        if self.is_downpayment and downpayment_lines:
            res['account_id'] = downpayment_lines.account_id[:1].id
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res



class SaleOrder(models.Model):
    _inherit = "sale.order"

