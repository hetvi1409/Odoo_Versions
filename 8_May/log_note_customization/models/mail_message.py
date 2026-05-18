# -*- coding: utf-8 -*-

from markupsafe import Markup
from odoo import models, fields, _
from odoo.exceptions import UserError


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_update_content(self, message, /, *, body, **kwargs):
        # if non-admin user can erase the content then will give us validation
        if body is not None and not body:
            if not self.env.user.has_group('base.group_system'):
                raise UserError("You are not allowed to delete messages.")

            if message.model and message.res_id:
                try:
                    record = self.env[message.model].browse(message.res_id)
                    original = message.body or '<em>(empty)</em>'
                    reason = kwargs.get('deletion_reason')
                    note_body = self.env['ir.qweb']._render(
                        'log_note_customization.message_delete_log_template',
                        {
                            'deleted_by': self.env.user.name,
                            'deleted_on': fields.Date.to_string(fields.Date.context_today(self)),
                            'reason': reason,
                            'original_content': Markup(original),
                        },
                    )
                    if isinstance(note_body, bytes):
                        note_body = note_body.decode('utf-8')
                    record.message_post(
                        body=note_body,
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
                except Exception:
                    pass

        return super()._message_update_content(message, body=body, **kwargs)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def action_open_delete_reason_wizard(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise UserError("You are not allowed to delete messages.")

        view = self.env.ref('log_note_customization.view_delete_reason_wizard_form')

        return {
            'type': 'ir.actions.act_window',
            'name': _('Delete Log Note'),
            'res_model': 'delete.reason.wizard',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_message_id': self.id,
            },
        }
