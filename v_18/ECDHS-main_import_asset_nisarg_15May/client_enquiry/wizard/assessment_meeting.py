from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AssessmentMeeting(models.Model):
    """Class for assessment meeting"""
    _name = 'assessment.meeting'
    _description = 'Assessment Meeting'
    _rec_name = 'subject'

    assessment_id = fields.Many2one('enquiry.assessment',
                                    string="Assessment", help="Assessment",
                                    readonly=True)
    jmc_number = fields.Char(related='assessment_id.jmc_number',
                             string='JMC number', help='JMC number')

    committee_id = fields.Many2one('committee', string="Committee",
                                     help="Transaction and Boarding committee", required=True)
    meeting_id = fields.Many2one('committee.meeting', string="Meeting",)
    subject = fields.Char(string='Subject', help='Subject', required=True)
    date = fields.Datetime(required=True, string="Date", help="Date", default=fields.Datetime.now())
    is_single_meeting = fields.Boolean(string="Both board and transaction "
                                              "meeting")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, values):
        """Method for adding some values to the assessment"""
        res = super(AssessmentMeeting, self).create(values)
        if res.assessment_id:
            print(res.is_single_meeting, 'is_single_meeting')
            if self.env.context.get('transaction'):
                res.assessment_id.committee_transaction = True
                res.assessment_id.meeting_request_ids = [(4, res.id)]
            if self.env.context.get('board'):
                res.assessment_id.write({
                    'committee_board_meeting' : True
                })
                res.assessment_id.meeting_request_ids = [(4, res.id)]
            if res.assessment_id.committee_transaction and res.assessment_id.committee_board_meeting:
                res.assessment_id.state = "internal_meeting"
            if res.is_single_meeting == True:
                res.assessment_id.committee_transaction = True
                res.assessment_id.meeting_request_ids = [(4, res.id)]
                res.assessment_id.write({
                    'committee_board_meeting' : True
                })
                res.assessment_id.state = "internal_meeting"
            # else:
            #     print(res.assessment_id.meeting_request_ids)
            #     if len(res.assessment_id.meeting_request_ids.ids) == 2:
            #
            mail_template = self.env.ref(
                'client_enquiry.email_template_meeting_request')
            recipient_ids = self.env.ref(
                'oi_committee.group_committee').users
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(self.id, force_send=True,
                                    email_values=email_values)
        return res

    def create_meeting(self):
        """Create meeting"""
        committee_transaction = self.env.ref(
            'client_enquiry.committee_transaction').id
        committee_board_meeting = self.env.ref('client_enquiry.committee_board_meeting').id
        context = {
            'default_assessment_id': self.assessment_id.id,
            'default_committee_id': self.committee_id.id,
            'default_subject': self.subject,
            'assessment': True
        }
        if self.id == committee_transaction:
            context['default_is_transaction'] = True
        self.active = False
        return {
            'name': _('Committee Meeting'),
            'view_mode': 'form',
            'res_model': 'committee.meeting',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    def unlink(self):
        """To change spome values in assess,ent"""
        for rec in self:
            committee_transaction = self.env.ref(
                'client_enquiry.committee_transaction').id
            committee_board_meeting = self.env.ref(
                'client_enquiry.committee_board_meeting').id
            if self.assessment_id:
                if rec.committee_id.id == committee_transaction:
                    rec.assessment_id.committee_transaction = False
                if rec.committee_id.id == committee_board_meeting:
                    rec.assessment_id.committee_board_meeting = False
                rec.assessment_id.state = 'transition'
        return super().unlink()

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=assessment.meeting&view_type=tree' % self.id)
        print('urls', Urls)
        return Urls

