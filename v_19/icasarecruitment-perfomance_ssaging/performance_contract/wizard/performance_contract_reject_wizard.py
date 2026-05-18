# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class PerformanceContractRejectWizard(models.TransientModel):
    _name = "performance.contract.reject.wizard"
    _description = "Reject Performance Contract"

    contract_id = fields.Many2one('performance.contract', required=True)
    reason = fields.Text(string="Rejection Reason", required=True)

    def action_reject(self):
        """Reject the contract with the provided reason"""
        self.ensure_one()

        contract = self.contract_id
        current_line = contract._get_current_pending_line()

        if not current_line:
            raise UserError("No pending approvals found.")

        if self.env.user != current_line.user_id:
            raise UserError("You are not authorized to reject this contract.")

        # Mark current line as rejected
        current_line.write({
            'status': 'rejected',
            'approved': False,
            'approval_date': fields.Datetime.now(),
            'reason': self.reason,
        })

        # Update contract status
        contract.approval_status = 'rejected'
        contract.state = 'rejected'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Contract Rejected',
                'message': f"Contract has been rejected by {self.env.user.name}.\nReason: {self.reason}",
                'type': 'warning',
                'sticky': True,
            }
        }
