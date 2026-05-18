from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DeleteReasonWizard(models.TransientModel):
    _name = 'mail.message.delete.reason.wizard'
    _description = 'Wizard to capture reason before deleting a log note'

    message_id = fields.Many2one('mail.message', string='Message', required=True)
    reason = fields.Char(string='Reason for Deletion', required=True)

    def action_confirm_delete(self):
        # Admin must give a reason before deletion is allowed
        if not self.reason or not self.reason.strip():
            raise UserError(_("Please provide a reason before deleting this log note."))

        # Attach reason to message so the unlink() method can log it
        self.message_id.sudo().write({'delete_reason': self.reason})
        self.message_id.sudo().unlink()

        return {'type': 'ir.actions.act_window_close'}
