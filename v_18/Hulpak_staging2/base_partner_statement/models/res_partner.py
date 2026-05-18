# Copyright 2018 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import logging

from odoo import api, fields, models, _
from datetime import datetime

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_invoice_payment = fields.Boolean('Invoice / Payment')
    is_invoice_payment_set = fields.Boolean()
    statement_with_dr_cr = fields.Boolean()

    def update_invoice_payment(self):
        for partner in self.search([]).filtered(lambda l: (l.credit - l.debit) != 0):
            invoice_payment_ids = self.env['account.move'].search([('partner_id', '=', partner.id)])
            partner.is_invoice_payment = True if len(invoice_payment_ids) else False
            partner.is_invoice_payment_set = True

    def update_statement_sent(self):
        config_id = self.env['ir.config_parameter'].sudo().get_param('partner_statement.cron_next_call_date')
        if int(int(config_id) - 1) == int(datetime.now().day):
            partners = self.search([('statement_sent', '=', True)])
            for partner_id in partners:
                partner_id.write({'statement_sent': False,
                                  'is_invoice_payment_set': False,
                                  'is_invoice_payment': False})
            for partner in self.search([]).filtered(lambda l: (l.credit - l.debit) != 0):
                invoice_payment_ids = self.env['account.move'].search([('partner_id', '=', partner.id)])
                partner.is_invoice_payment = True if len(invoice_payment_ids) else False
                partner.is_invoice_payment_set = True

    def open_activity_statement_wizard(self):
        action = self.env["ir.actions.actions"]._for_xml_id("base_partner_statement.action_partner_activity_statement")
        action['context'] = {
            'active_ids': (self._context.get('active_ids')),
            'default_show_aging_buckets': True,
            'statement_type': 'Activity Statement',
            'default_aging_type': 'months',
        }
        return action
    
    def open_activity_outgoing_statement_wizard(self):
        action = self.env["ir.actions.actions"]._for_xml_id("base_partner_statement.action_partner_outgoing_activity_statement")
        action['context'] = {
            #'active_ids': [self._context.get('active_id')]
            'active_ids': (self._context.get('active_ids')),
            'default_show_aging_buckets': True,
            'statement_type': 'Outstanding Statement',
            'default_aging_type': 'months',
        }
        return action