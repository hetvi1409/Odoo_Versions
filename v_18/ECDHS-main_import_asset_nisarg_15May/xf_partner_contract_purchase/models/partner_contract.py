# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import MissingError


class PartnerContract(models.Model):
    _inherit = 'xf.partner.contract'

    # Fields
    purchase_order_ids = fields.One2many(
        string='Purchase Orders',
        comodel_name='purchase.order',
        inverse_name='contract_id',
        readonly=True,
    )
    purchase_order_ids_count = fields.Integer(
        compute='_compute_purchase_order_ids_count',
        compute_sudo=True,
    )

    # Compute and search fields, in the same order of fields declaration
    @api.depends('purchase_order_ids')
    def _compute_purchase_order_ids_count(self):
        for record in self:
            record.purchase_order_ids_count = len(record.purchase_order_ids)

    # Constraints and onchanges
    # Built-in methods overrides
    # Action methods

    def action_create_purchase_order(self):
        self.ensure_one()
        purchase_order_vals = self._prepare_purchase_order()
        purchase_order = self.env['purchase.order'].create(purchase_order_vals)
        purchase_order.apply_contract_lines()
        return self.action_view_purchase_orders()

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = {
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }
        if self.purchase_order_ids_count == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.purchase_order_ids.id,
            })
        else:
            action.update({
                'name': _("Purchase Order generated from the contract %s", self.name),
                'domain': [('id', 'in', self.purchase_order_ids.ids)],
                'view_mode': 'tree,form',
            })
        return action

    # Business methods

    def _prepare_purchase_order(self):
        self.ensure_one()
        return {
            'contract_id': self.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'origin': self.ref,
            'notes': self.notes,
            'payment_term_id': self.payment_term_id.id,
        }


class PartnerContractLine(models.Model):
    _inherit = 'xf.partner.contract.line'

    def _prepare_purchase_order_line(self, order):
        self.ensure_one()
        if not self.product_id:
            raise MissingError('Please set product for each contract line as is required to generate purchase orders')
        vals = {
            'name': self.name,
            'sequence': self.sequence,
            'product_qty': self.quantity,
            'product_uom': self.product_uom_id.id or self.product_id.uom_po_id.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'taxes_id': [(6, 0, self.taxes_id.ids)],
            'analytic_distribution': self.analytic_distribution,
            'display_type': False,
        }
        if order:
            vals['order_id'] = order
        return vals
