# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ApplicantInterviewFeedback(models.TransientModel):
    _name = 'applicant.interview.feedback.wizard'
    _description = 'Applicant Interview Feedback'

    subject = fields.Char('Subject', required=True)
    body_html = fields.Html('Body', required=True)
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")

    def send_email(self):
        """ Send the email using a template """
        template = self.env.ref(
            'recruitment_enhancement.email_template_applicant_feedback')
        template.write({
            'subject': self.subject,
            'body_html': self.body_html,
        })
        template.send_mail(self.applicant_id.id, force_send=True)
        return True


class ApplicantInterviewLetter(models.TransientModel):
    _name = 'applicant.interview.letter.wizard'
    _description = 'Applicant Interview Letter'

    subject = fields.Char('Subject', required=True)
    body_html = fields.Html('Body', required=True)
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")

    def send_email(self):
        """ Send the email using a template """
        template = self.env.ref('recruitment_enhancement.email_template_applicant_letter')
        template.write({
            'subject': self.subject,
            'body_html': self.body_html,
        })
        template.send_mail(self.applicant_id.id, force_send=True)
        return True