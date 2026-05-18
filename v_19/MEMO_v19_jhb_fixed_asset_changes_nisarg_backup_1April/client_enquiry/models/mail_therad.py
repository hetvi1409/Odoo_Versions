from odoo import api, models


class MailMessage(models.Model):
    """inherit Mail messages to connect messages to circulation comments"""
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, values_list):
        res = super(MailMessage, self).create(values_list)
        for ress in res:
            if ress.model == 'circulation.comments':
                record = self.env[res.model].sudo().browse(int(res.res_id))
                subject = ' ' + record.name + ' :  Add Circulation Comments'
                if record.state == 'send' and ress.message_type == 'email':
                    if ress.subject == subject:
                        pass
                    else:
                        email_content = ress.body
                        vals = {
                            'name': email_content,
                            'circulation_id': record.id,
                            'author_id': ress.author_id.sudo().id,
                            'attachment_ids': ress.attachment_ids.ids
                        }
                        self.env['circulation.comment.line'].sudo().create(vals)
        return res

