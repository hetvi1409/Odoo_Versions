# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError


class DeleteReasonWizard(models.TransientModel):
    _name = 'delete.reason.wizard'
    _description = 'Log Note Delete Reason Wizard'

    message_id = fields.Many2one('mail.message', required=True, ondelete='cascade')
    reason = fields.Text(string='Reason', required=True)

    def action_confirm_delete(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise UserError("You are not allowed to delete messages.")

        message = self.message_id.sudo()
        if not message:
            raise UserError("The message no longer exists.")
        if message.model and message.res_id:
            thread = self.env[message.model].browse(message.res_id)
            thread._message_update_content(message, body='', deletion_reason=self.reason)
        else:
            message.write({'body': ''})

        return {'type': 'ir.actions.act_window_close'}
