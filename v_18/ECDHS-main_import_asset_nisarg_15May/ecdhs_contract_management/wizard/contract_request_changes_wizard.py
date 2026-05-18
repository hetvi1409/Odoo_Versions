# -*- coding: utf-8 -*-

from odoo import fields, models


class EcdhsContractRequestChangesWizard(models.TransientModel):
    _name = 'ecdhs.contract.request.changes.wizard'
    _description = 'Contract Request Changes Wizard'

    contract_id = fields.Many2one('ecdhs.contract', string='Contract', required=True, readonly=True)
    section_reference = fields.Char(string='Draft Terms Section', required=True)
    requested_change = fields.Text(string='Requested Change', required=True)
    due_date = fields.Date(string='Response Due Date')

    def action_submit(self):
        self.ensure_one()
        self.contract_id.action_submit_change_request(
            section_reference=self.section_reference,
            requested_change=self.requested_change,
            due_date=self.due_date,
        )
        return {'type': 'ir.actions.act_window_close'}
