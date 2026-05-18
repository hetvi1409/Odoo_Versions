# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    item_number = fields.Integer('#', compute='_set_sequence', default=0)
    sequence = fields.Integer(default=1)

    @api.depends('move_id.invoice_line_ids')
    def _set_sequence(self):
        for rec in self:
            index = 1
            for line in rec.move_id.invoice_line_ids.sorted('sequence'):
                if not line.display_type or line.display_type == 'product':
                    line.item_number = index
                    index = index+1
                else:
                    line.item_number = 0


class AccountMove(models.Model):
    _inherit = 'account.move'

    full_payment_date = fields.Date(string="Payment Date", compute="_set_full_payment_date", store=True, default=False)

    @api.depends('matched_payment_ids', 'matched_payment_ids.state', 'matched_payment_ids.date', 'payment_state')
    def _set_full_payment_date(self):
        for rec in self:
            payments = rec.matched_payment_ids.filtered(lambda payment: payment.state == 'paid').mapped('date')
            rec.full_payment_date = max(payments) if payments and rec.status_in_payment == 'paid' else False
