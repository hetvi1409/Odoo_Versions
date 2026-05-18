from odoo import models, fields, api
from odoo.exceptions import UserError

class MemoEmailWizard(models.TransientModel):
    _name = 'memo.memo.email.wizard'
    _description = 'Send Memo by Email Wizard'

    memo_id = fields.Many2one('memo.memo', required=True, readonly=True)
    subject = fields.Char('Subject', required=True)
    body_html = fields.Html('Email Body', required=True)
    recipient_ids = fields.Many2many('res.users', string="Recipients")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        memo = self.env['memo.memo'].browse(active_id)
        res.update({
            'memo_id': memo.id,
            'subject': memo.name,
            'recipient_ids': memo.recommender_ids.mapped('user_id').ids
        })
        return res

    def send_email(self):
        if not self.recipient_ids:
            raise UserError("No recipients selected!")

        for user in self.recipient_ids:
            if self.memo_id.submission_type == 'memo':
                template = self.env.ref('e_system.mail_template_memo_submit')
                template.with_context(email_to=user.email).send_mail(self.memo_id.id, force_send=True)
            if self.memo_id.submission_type == 'circular':
                template = self.env.ref('e_system.mail_template_memo_submit')
                template.with_context(email_to=user.email).send_mail(self.memo_id.id, force_send=True)
            if self.memo_id.submission_type == 'procurement':
                template = self.env.ref('e_system.mail_template_memo_submit')
                template.with_context(email_to=user.email).send_mail(self.memo_id.id, force_send=True)

        return {'type': 'ir.actions.act_window_close'}





