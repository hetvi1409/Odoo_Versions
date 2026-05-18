from odoo import api, fields, models, _, modules

class DefaultAnswers(models.Model):
    _name = 'chat.answers'

    name = fields.Char('Name')
    active = fields.Boolean(string='Active')
    show = fields.Boolean(string='Show')
    type = fields.Selection([('image', 'Image'), ('text', 'Text'), ('location', 'Location')], default='text')
    text = fields.Text(string='Text')
    file = fields.Many2one('ir.attachment', 'Attachment ', readonly=True)
    attachment_data = fields.Binary(related='file.datas', string='Attachment', help="Download attachment")
    attachment_ids = fields.Many2many('ir.attachment', 'whatsapp_answer_ir_attachments_rel', 'model_id', 'attachment_id', 'Attachments', tracking=True)