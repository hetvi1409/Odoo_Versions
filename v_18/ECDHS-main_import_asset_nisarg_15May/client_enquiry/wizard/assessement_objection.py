from werkzeug import urls

from odoo import fields, models, _
from odoo.exceptions import UserError


class AssessmentObjection(models.TransientModel):
    _name = 'assessment.objection'
    _description = 'Assessment Objection'

    outcome = fields.Selection([('yes', 'Yes'), ('no', 'No')], required=True,
                               string="Any objection")
    assessment_id = fields.Many2one('enquiry.assessment')
    is_object_valid = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Is objection valid')
    # is_municipal_department = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Is Municipal Department')

    def action_submit(self):
        """Submit assessment"""
        for rec in self:
            rec.assessment_id.state = 'objection'
            rec.assessment_id.outcome = self.outcome
            rec.assessment_id.is_object_valid = self.is_object_valid

            if rec.outcome == 'yes':
                if not self.is_object_valid:
                    raise UserError(_("Please add the value for 'is objection valid'"))
                mail_content = _('Hi %s,<br>'
                                 'There are some objections on the assessment '
                                 '%s. Please Contact the team') % \
                               (self.assessment_id.partner_id.name,
                                self.assessment_id.name)
                main_content = {
                    'subject': _(
                        'Assessment Objections: %s' % self.assessment_id.name),
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': self.assessment_id.partner_id.email
                }
                mail_id = self.env['mail.mail'].sudo().create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.sudo().send()
                self.assessment_id.sudo().message_post(body=
                                         "There are some objections for this assessment")
                if self.is_object_valid == 'yes':
                    self.assessment_id.state = 'terminate'
                    self.assessment_id.enquiry_id.state = 'cancelled'
                if self.is_object_valid == 'no':
                    self.assessment_id.state = 'ownership'
            if rec.outcome == 'no':
                """Commented this code for remove the some workflow"""
                # rec.assessment_id.state = 'objection'
                # rec.assessment_id.is_municipal_department = rec.is_municipal_department
                # if rec.is_municipal_department == 'yes':
                #     rec.assessment_id.state = 'PTOB'
                #     self.assessment_id.enquiry_id.state = 'cancelled'
                #     self.assessment_id.message_post(
                #         body="Compile PTOB")
                # if rec.is_municipal_department == 'no':
                rec.assessment_id.state = 'objection'
                self.assessment_id.message_post(
                    body="Compile & sign the Valuation Form")
                mail_template = self.env.ref(
                    'client_enquiry.email_template_enquiry_assessment_request_valuation')
                recipient_ids = self.env.ref(
                    'client_enquiry.group_property_manager').users
                partner = recipient_ids.mapped('partner_id')
                email_values = {
                    'recipient_ids': [(6, 0, partner.ids)]
                }
                mail_template.send_mail(self.assessment_id.id, force_send=True,
                                        email_values=email_values)
