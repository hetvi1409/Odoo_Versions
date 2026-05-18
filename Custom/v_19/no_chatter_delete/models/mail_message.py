from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MailMessage(models.Model):
    _inherit = 'mail.message'

    # Stores the reason when an admin deletes a log note
    delete_reason = fields.Char(string='Delete Reason')
    deleted_by = fields.Many2one('res.users', string='Deleted By', readonly=True)
    deleted_on = fields.Datetime(string='Deleted On', readonly=True)

    def unlink(self):
        # Only users with the group_system (admin) group can delete messages
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_(
                "You are not allowed to delete log notes or messages. "
                "Please contact your system administrator."
            ))

        for msg in self:
            if not (msg.delete_reason and msg.delete_reason.strip()):
                raise UserError(_(
                    "Deletion reason is required. "
                    "Use the delete wizard from chatter to provide a reason."
                ))

        # Record audit info before actually deleting
        for msg in self:
            self.env['mail.message.delete.log'].sudo().create({
                'message_id_ref': msg.id,
                'message_body': msg.body or '',
                'message_type': msg.message_type,
                'author_id': msg.author_id.id,
                'res_model': msg.model,
                'res_id': msg.res_id,
                'deleted_by': self.env.uid,
                'deleted_on': fields.Datetime.now(),
                'delete_reason': msg.delete_reason or '',
            })

        return super().unlink()
