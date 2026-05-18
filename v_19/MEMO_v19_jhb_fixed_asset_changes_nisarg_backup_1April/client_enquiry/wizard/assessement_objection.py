from werkzeug import urls

from odoo import fields, models, _
from odoo.exceptions import UserError


class AssessmentObjection(models.TransientModel):
    _name = 'assessment.objection'
    _description = 'Assessment Objection'

    outcome = fields.Selection([('yes', 'Yes'), ('no', 'No')], required=True,
                               string="Any objection")
    assessment_id = fields.Many2one('enquiry.assessment')
    circulation_id = fields.Many2one('circulation.comments', string="Circulation")
    is_object_valid = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Is objection valid')
    is_municipal_department = fields.Selection([('yes', 'Municipal'), ('no', 'Private')], string='Municipal/Private Land')

    def action_submit(self):
        """Submit assessment"""
        if self.circulation_id:
            self.circulation_id.objection = self.outcome
            self.circulation_id.is_municipal_department = self.is_municipal_department
            if self.outcome == 'no':
                self.circulation_id.sudo().message_post(body="There is no objections for this assessment")
                if self.is_municipal_department == 'yes':
                    self.circulation_id.action_move_to_ptob()
                if self.is_municipal_department == 'no':
                    self.circulation_id.action_move_to_request_valuation()
            if self.outcome == 'yes':
                self.circulation_id.sudo().message_post(body=
                                                       "There are some objections for this assessment")
                mail_template = self.env.ref(
                    'client_enquiry.email_template_circulation_comments_objection')
                recipient_ids = self.circulation_id.user_id.partner_id
                recipient_ids += self.circulation_id.enquiry_id.partner_id
                recipient_ids += self.circulation_id.assessment_id.enquiry_name_id
                email_values = {
                    'recipient_ids': [(6, 0, recipient_ids.ids)]
                }
                mail_template.send_mail(self.circulation_id.id, force_send=True,
                                        email_values=email_values)
                self.circulation_id.state = 'objection'

        else:
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


class AssessmentAccept(models.TransientModel):
    _name = 'assessment.accept'
    _description = 'Assessment Objection'

    endorse = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                               required=True,
                               string="Endorse")
    assessment_id = fields.Many2one('enquiry.assessment')
    transaction_id = fields.Many2one('client.transaction', 'Transaction')
    comments = fields.Char('Comments', required=True)

    def action_submit(self):
        """Submit"""
        self.transaction_id.endorse_comments = self.comments
        self.transaction_id.sudo().message_post(
            body="Comments: %s" % self.comments)

        if self.endorse == 'no':
            self.transaction_id.state = 'terminated'
            self.transaction_id.sudo().message_post(body="The process was terminated, due to Endure process")
        else:
            self.transaction_id.state = 'to_do_section_79'

class AssessmentSpecDevelopment(models.TransientModel):
    _name = 'assessment.spec'

    endorse = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                               required=True,
                               string="Spec Development Required")
    assessment_id = fields.Many2one('enquiry.assessment')
    transaction_id = fields.Many2one('client.transaction', 'Transaction')
    comments = fields.Char('Comments', required=True)

    def action_submit(self):
        """Submit"""
        self.transaction_id.bid_comments = self.comments
        self.transaction_id.sudo().message_post(
            body="Comments: %s" % self.comments)
        if self.transaction_id.enquiry_id:
            self.transaction_id.enquiry_id.state = 'section_advert'
        if self.endorse == 'no':
            self.transaction_id.state = 'eac'
            self.transaction_id.sudo().message_post(
                body="The process was terminated, due to Endure process")
        else:
            self.transaction_id.state = 'bid'


class EACReview(models.TransientModel):
    _name = 'eac.review'

    type = fields.Selection([('approve', 'Approve'), ('refuse', 'Refuse')],
                               string="Type")
    types = fields.Selection([('approve', 'Approve'), ('refuse', 'Refuse')],
                               string="Type")
    eac_id = fields.Many2one('eac.process', 'EAC Process')
    comments = fields.Char('Comments', required=True)

    def action_submit(self):
        """Submit"""
        if self.type:
            self.eac_id.eac_comments = self.comments
            self.eac_id.sudo().message_post(
                body="Comments: %s" % self.comments)
        if self.types:
            self.eac_id.review_comments = self.comments
            self.eac_id.sudo().message_post(
                body="Review Comments: %s" % self.comments)
        if self.type == 'approve':
            self.eac_id.state = 'eac_approve'
        else:
            self.eac_id.state = 'draft'
            self.eac_id.sudo().message_post(
                body="The process was terminated, Please do the Meetings")
            self.eac_id.eac_committee_id = False
        if self.types == 'approve':
            self.eac_id.state = 'approve'
        if self.types == 'refuse':
            self.eac_id.state = 'eac_meeting'
            self.eac_id.sudo().message_post(
                body="The process was terminated, Please do the Meetings")
