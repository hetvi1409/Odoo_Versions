from email.policy import default
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class WhatsappMessages(models.Model):
    _inherit = 'whatsapp.messages'
    _description = "Whatsapp Messages"

    name=fields.Char('Name', readonly=True)
    message_body = fields.Char('Message', readonly=True)
    message_id = fields.Text('Message Id', readonly=True)
    fromMe = fields.Boolean('From Me', readonly=True)
    to = fields.Char('To', readonly=True)
    chatId = fields.Char('Chat ID', readonly=True)
    msg_status = fields.Selection([('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read')], default="sent")
    is_sent = fields.Boolean(string="Sent")
    time_sent = fields.Datetime(string="Time sent")
    is_delivered = fields.Boolean(string="Delivered")
    time_delivered = fields.Datetime(string="Time Delivered")
    is_read = fields.Boolean(string="Read")
    time_read = fields.Datetime(string="Time read")
    type = fields.Char('Type', readonly=True)
    msg_image = fields.Binary('Image', readonly=True)
    senderName = fields.Char('Sender Name', readonly=True)
    chatName = fields.Char('Chat Name', readonly=True)
    author = fields.Char('Author', readonly=True)
    time = fields.Datetime('Date and time', readonly=True)
    partner_id = fields.Many2one('res.partner','Partner', readonly=True)
    user_default_partner = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id)
    state= fields.Selection([('sent', 'Sent'),('received', 'Received')], readonly=True)
    attachment_id = fields.Many2one('ir.attachment', 'Attachment ', readonly=True)
    attachment_data = fields.Binary(related='attachment_id.datas', string='Attachment', readonly=True)
    whatsapp_instance_id = fields.Many2one('whatsapp.instance', string='Whatsapp instance', help="From this instance message is sent on whatsapp")
