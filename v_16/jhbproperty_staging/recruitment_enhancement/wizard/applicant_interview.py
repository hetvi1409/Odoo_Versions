# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class ApplicantInterviewLetter(models.TransientModel):
    _name = 'applicant.interview.letter.wizard'
    _description = 'Applicant Interview Letter'

    subject = fields.Char('Subject', required=True)
    body_html = fields.Html('Body', required=True)
    applicant_id = fields.Many2one('hr.applicant', string='Applicant')

    def send_email(self):
        self.ensure_one()

        applicant = self.applicant_id.sudo()
        recipient_email = applicant.email_from or applicant.partner_id.email
        if not recipient_email:
            raise UserError(_('The applicant does not have an email address.'))

        mail = self.env['mail.mail'].sudo().create({
            'subject': self.subject,
            'body_html': self.body_html,
            'email_to': recipient_email,
            'author_id': self.env.user.partner_id.id,
            'auto_delete': True,
        })
        mail.send()
        return True
