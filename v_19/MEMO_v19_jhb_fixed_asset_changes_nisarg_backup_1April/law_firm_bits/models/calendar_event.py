# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, Command
import ast
from datetime import datetime, date
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Meeting(models.Model):
    _inherit = 'calendar.event'

    customer_id = fields.Many2one("res.partner")
    consultation_amount = fields.Float()
    is_consultation = fields.Boolean(default=False)
    count_invoice = fields.Integer(compute="_compute_count_invoice")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('start', False):
                if datetime.strptime(str(vals.get('start')), '%Y-%m-%d %H:%M:%S') < datetime.today():
                    raise UserError("You are not allowed to past entries.")

        return super(Meeting, self).create(vals_list)

    def write(self, vals):
        if vals.get('start', False):
            if datetime.strptime(str(vals.get('start')), '%Y-%m-%d %H:%M:%S') < datetime.today():
                raise UserError("You are not allowed to past entries.")

        return super(Meeting, self).write(vals)

    def _compute_count_invoice(self):
        for rec in self:
            rec.count_invoice = len(self.env['account.move'].search([('calendar_id', '=', rec.id)]))

    @api.depends("customer_id")
    def _compute_is_consultation(self):
        for rec in self:
            is_consultation = False
            if rec.customer_id:
                is_consultation = True
            rec.is_consultation = is_consultation

    def action_create_invoice(self):
        action = self.env.ref('law_firm_bits.wizard_create_matter_invoice_action').sudo().read()[0]
        action['context'] = {'default_amount': self.consultation_amount}
        return action

    def open_invoice_view(self):
        action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        domain = ast.literal_eval(action['domain'])
        domain.append(('calendar_id', '=', self.id))
        action['domain'] = domain
        return action
