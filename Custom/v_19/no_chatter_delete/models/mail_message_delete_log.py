from odoo import models, fields


class MailMessageDeleteLog(models.Model):
    _name = 'mail.message.delete.log'
    _description = 'Audit Log for Deleted Chatter Messages'
    _order = 'deleted_on desc'

    # Snapshot of the deleted message content
    message_id_ref = fields.Integer(string='Original Message ID', readonly=True)
    message_body = fields.Html(string='Message Content', readonly=True)
    message_type = fields.Char(string='Message Type', readonly=True)
    author_id = fields.Many2one('res.users', string='Original Author', readonly=True)
    res_model = fields.Char(string='Related Model', readonly=True)
    res_id = fields.Integer(string='Related Record ID', readonly=True)

    # Audit fields
    deleted_by = fields.Many2one('res.users', string='Deleted By',
                                  default=lambda self: self.env.uid, readonly=True)
    deleted_on = fields.Datetime(string='Deleted On',
                                  default=fields.Datetime.now, readonly=True)
    delete_reason = fields.Char(string='Reason for Deletion', readonly=True)
