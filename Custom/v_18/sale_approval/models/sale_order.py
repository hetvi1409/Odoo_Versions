# -*- coding: utf-8 -*-
from odoo import fields, models, api ,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approval_state= fields.Selection([
        ('draft', 'Draft'),
        ('to_approved', 'To Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Approval Status', default='draft')


    def action_confirm(self):
        for order in self:
            # Block if already waiting for approval
            if order.approval_state == 'to_approved':
                raise ValidationError(
                    _('This order is pending manager approval. You cannot confirm it until the discount is approved.')
                )

            # Check if any line exceeds 20% discount
            if any(line.discount > 20 for line in order.order_line):
                if order.approval_state != 'approved':
                    order.approval_state = 'to_approved'
                    raise ValidationError(
                        _('One or more order lines have a discount greater than 20%%. '
                          'Please contact your Sales Manager to approve before confirming.')
                    )

        return super().action_confirm()

    def approve_discount(self):
        self.approval_state = 'approved'
