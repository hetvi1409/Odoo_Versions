from odoo import fields, models


class MailComposeMessage(models.TransientModel):
    """to send the message"""
    _inherit = 'mail.compose.message'

    def _action_send_mail(self, auto_commit=False):
        "Send the mail to the partners"
        if self.model == 'enquiry.assessment':
            self = self.with_context(mailing_document_based=True)
            if self.env.context.get('active_id'):
                enquiry = self.env['enquiry.assessment'].browse(
                    self.env.context.get('active_id'))
                if self.env.context.get('mark_assessment_as_sent'):
                    self = self.with_context(mail_notify_author=self.env.user.partner_id in self.partner_ids)
                    enquiry.state = 'compile'
                    enquiry.partner_ids = self.partner_ids
                # if self.env.context.get('mark_transaction_as_sent'):
                #     self = self.with_context(
                #         mail_notify_author=self.env.user.partner_id in self.partner_ids)
                #     enquiry.state = 'send_transition'
        if self.model == 'client.enquiry':
            self = self.with_context(mailing_document_based=True)
            if self.env.context.get('active_id'):
                if self.env.context.get('enquiry'):
                    self = self.with_context(
                        mail_notify_author=self.env.user.partner_id in self.partner_ids)
                    client = self.env['client.enquiry'].browse(self.env.context.get('active_id'))
                    client.state = 'cancelled'
        return super(MailComposeMessage, self)._action_send_mail(auto_commit=auto_commit)
