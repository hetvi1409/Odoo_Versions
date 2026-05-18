# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        print('\n\n\n Action Confirm Called-->', self)
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            delivery = order.picking_ids
            print('\n\n\n Delivery -->', delivery)
            if delivery:
                # Pass all context values in a single call
                delivery = delivery.with_context(skip_sanity_check=True,skip_sms=True,skip_backorder=True)
                picking_line = delivery.move_ids_without_package
                print('\n\n\n Picking Line -->', picking_line)
                for picking in picking_line:
                    if not picking.quantity:
                        picking.write({'quantity': picking.product_uom_qty})
                print('\n\n\n Picking Line -->', picking_line)
                delivery.sudo().button_validate()
            invoice = order.sudo()._create_invoices()
            print('\n\n\n Invoice -->', invoice)
            invoice.sudo().action_post()
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for order in self:
            delivery = order.picking_ids
            print('\n\n\n Delivery -->', delivery)
            if delivery:
                for deli in delivery:
                    if deli.state != 'cancel':
                        if deli.state == 'done':
                            # Create returns for done pickings instead of canceling
                            return_picking = self.env['stock.return.picking'].create({'picking_id': deli.id})
                            return_picking.action_create_returns_all()
                        else:
                            deli.action_cancel()
                print('\n\n\n Delivery Line -->', deli)
            invoice = order.sudo().invoice_ids
            if invoice:
                for inv in invoice:
                    if inv.state != 'cancel':
                        inv.button_cancel()
                        # Create only one credit note per invoice
                        credit_note = inv.copy({
                            'move_type': 'out_refund',
                            'invoice_origin': inv.invoice_origin,
                            'ref': f"Reversal of: {inv.name}" ,
                            'date': fields.date.today(),
                        })
                        print('\n\n\n Credit Note -->', credit_note)

        return res