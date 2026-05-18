from odoo import models, fields, api
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo import exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('waiting_approval', 'Waiting Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        ondelete={
            'waiting_approval': 'set default',
            'approved': 'set default',
            'rejected': 'set default',
        }
    )

    rejection_reason = fields.Text(
        string='Rejection Reason',
        readonly=True
    )

    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True
    )

    def action_submit_for_approval(self):
        for order in self:
            order.state = 'waiting_approval'

    def action_approve(self):
        for order in self:
            # Check access rights
            if order.amount_total > 50000:
                if not self.env.user.has_group(
                    'view_customization.group_ceo_approval'
                ):
                    raise exceptions.UserError(
                        "Only CEO can approve orders above ₹50,000!"
                    )
            else:
                if not self.env.user.has_group(
                    'sales_team.group_sale_manager'
                ):
                    raise exceptions.UserError(
                        "Only Sales Manager can approve this order!"
                    )

            order.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
            })
            # Now confirm the sale order
            order.action_confirm()


    def action_reject(self, reason):
        return {
            'name': 'Rejection Reason',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        for order in self:
            print('\n\n\n CUSTOM=========order>>>>', order)
            pickings = order.picking_ids.filtered(
                lambda p: p.state not in ('done', 'cancel')
            )
            if pickings:
                print('pickings---->',pickings)
                for picking in pickings:
                    for move in picking.move_ids:
                        print('move---->', move)
                        print('move---->quantity:', move.quantity)
                        if move.quantity != move.product_uom_qty:
                            move.quantity = move.product_uom_qty
                        else:
                            pass
                pickings.sudo().button_validate()
                order._create_invoices()
        return res


    @api.depends('order_line.price_subtotal', 'order_line.discount_amount','currency_id', 'company_id', 'payment_term_id')
    def _compute_amounts(self):
        print('\n\n\n CUSTOM=========order>>>>', self)
        # add discount_amount in amount_total
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order._get_priced_lines()
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            base_lines += order._add_base_lines_for_early_payment_discount()
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            # Calculate total discount_amount from all order lines
            total_discount_amount = sum(line.discount_amount for line in order_lines)
            print('CUSTOM=========total_discount_amount>>>>', total_discount_amount)

            order.amount_untaxed = tax_totals['base_amount_currency'] - total_discount_amount
            order.amount_tax = tax_totals['tax_amount_currency'] - total_discount_amount
            order.amount_total = tax_totals['total_amount_currency'] - total_discount_amount


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_amount = fields.Float('Discount Amount')



    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_amount')
    def _compute_amount(self):
        for line in self:
            # Apply % discount first
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            # Apply fixed discount (per unit)
            if line.discount_amount:
                if line.product_uom_qty:
                    price -= (line.discount_amount / line.product_uom_qty)

            if price < 0:
                price = 0

            taxes = line.tax_id.compute_all(
                price,
                currency=line.order_id.currency_id,
                quantity=line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )

            line.update({
                'price_subtotal': taxes['total_excluded'],
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
            })