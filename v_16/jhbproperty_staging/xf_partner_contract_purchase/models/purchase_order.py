# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Fields
    use_purchase_contract = fields.Selection(
        string='Use Contract',
        related='company_id.use_purchase_contract',
        readonly=True,
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='xf.partner.contract',
        ondelete='restrict',
        domain=[('state', '=', 'running'), ('type', '=', 'purchase')],
    )

    # Compute and search fields, in the same order of fields declaration
    # Constraints and onchanges

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if self.contract_id:
            self.partner_id = self.contract_id.partner_id

    # Built-in methods overrides
    # Action methods

    def action_apply_contract(self):
        self.apply_contract()

    # Business methods

    def apply_contract(self):
        for order in self:
            if not order.contract_id:
                continue
            po_vals = order.contract_id._prepare_purchase_order()
            order.write(po_vals)
            order.apply_contract_lines()

    def apply_contract_lines(self):
        for order in self:
            if not order.contract_id:
                continue
            lines = self.env['purchase.order.line']
            for line in order.contract_id.line_ids:
                po_line_vals = line._prepare_purchase_order_line(order)
                po_line = lines.new(po_line_vals)
                lines |= po_line
            order.order_line = lines

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        if self.contract_id:
            invoice_vals['contract_id'] = self.contract_id.id
        return invoice_vals
