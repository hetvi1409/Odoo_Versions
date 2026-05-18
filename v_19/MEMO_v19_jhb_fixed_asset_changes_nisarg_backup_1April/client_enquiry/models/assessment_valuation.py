from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssessmentValuation(models.Model):
    """Valuation"""
    _name = 'assessment.valuation'
    _description = 'Valuation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    property_id = fields.Many2one('building', string="Property", required=True)
    assessment_id = fields.Many2one('enquiry.assessment', string="Assessment",
                                    domain="[('state', 'in', ['valuation', 'objection'])]",
                                    )
    property_number = fields.Char(string="Property Number")
    property_description = fields.Char(string="Property Description")
    address = fields.Char(string="Address", required=False)
    contract_ids = fields.Many2many('rental.contract',
                                    string="Lease")
    only_portion = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                    required=False,
                                    string="Only Portion need to be valued",
                                    help="If only a portion need to be valued")
    size = fields.Char(string="Size to be valued")
    property_category = fields.Selection([('commercial', 'Commercial'),
                                          ('industrial', 'Industrial'),
                                          ('residential', 'residential'),
                                          ('retail', 'Retail/Shop'),
                                          ('vacant', 'Vacant Land')],
                                         string="Property Category")
    purpose_valuation = fields.Selection(
        [('development', 'Possible Development'),
         ('sale', 'Sale')],
        string="Purpose of valuation")

    attachment_ids = fields.Many2many('ir.attachment', string="Assessment Documents")
    jmc_number = fields.Char(string="JMC Number", help="JMC number")
    circulation_id = fields.Many2one('circulation.comments', string="Circulation Comments")
    comments = fields.Char(string="Comments")
    is_recommended = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    transaction_id = fields.Many2one('client.transaction', string="Transaction")
    valuation_attachment_ids = fields.Many2many('ir.attachment', 'valuation_attachment_rel', string="Valuation Documents")
    enquiry_id = fields.Many2one('client.enquiry', string='Enquiry')
    acquisition_id = fields.Many2one('property.acquisition', string="Acquisition")
    valuation_date = fields.Date(string="Valuation Date", defualt=fields.Date.today())
    user_id = fields.Many2one('res.users', string='Assignee')
    last_stage_updated = fields.Datetime('Last Stage Updated', readonly=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'assessment.valuation'
            vals['name'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(AssessmentValuation, self).create(vals_list)
        res.last_stage_updated = fields.Datetime.now()
        return res

    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'),
                              ('scm', 'SCM'), ('transaction', 'create Transaction'),
                              ('terminate', 'Terminated'),
                              ('transaction_created', 'Transaction'),
                              ], default='draft')



    @api.onchange( 'circulation_id')
    def onchange_property_circulation(self):
        """Onchange property Details"""
        self.property_id = self.circulation_id.property_id.id

    @api.onchange('property_id')
    def onchange_property(self):
        """Onchange property Details"""
        self.address = self.property_id.address
        self.jmc_number = self.property_id.jmc_number
        self.property_number = self.property_id.code
        self.size = self.property_id.building_area

    def action_submit(self):
        """Submit new assessment valuation"""
        self.state = 'submit'

    def action_submit_scm(self):
        """Submit new assessment valuation"""
        self.state = 'scm'

    def action_recommend(self):
        """Recommend"""
        if self.is_recommended == 'yes':
            self.state = 'transaction'
        elif self.is_recommended == 'no':
            self.state = 'terminate'

    def action_create_transaction(self):
        """Create a new assessment"""
        transaction = self.env['client.transaction'].create({
            'valuation_id': self.id,
            'property_id': self.property_id.id,
            'enquiry_id': self.assessment_id.enquiry_id.id,
            'assessment_id': self.assessment_id.id,
            'circulation_id': self.circulation_id.id,
            'address': self.address,
            'jmc_number': self.jmc_number,
            'transaction_type': self.enquiry_id.type if self.enquiry_id else '',
            'stand_number': self.property_id.stand_number,
            'valuation_attachment_ids': self.valuation_attachment_ids
        })
        self.state = 'transaction_created'
        self.transaction_id = transaction.id
        if self.enquiry_id:
            self.enquiry_id.transaction_id = transaction.id
            self.enquiry_id.state = 'transaction'
        if self.assessment_id:
            self.assessment_id.transaction_id = transaction.id
        if self.circulation_id:
            self.circulation_id.transaction_id = transaction.id
        if self.acquisition_id:
            self.acquisition_id.transaction_id = transaction.id
            self.acquisition_id.state = 'transaction_created'

    def action_view_transaction(self):
        """View assessment valuation"""
        valuation = self.transaction_id
        action = {
            'name': _('Transaction'),
            'type': 'ir.actions.act_window',
            'res_model': valuation._name,
            'context': {'create': False},
        }
        if len(valuation) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': valuation.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', valuation.ids)],
            })
        return action

    def action_view_enquiry(self):
        """View assessment"""
        assessment = self.enquiry_id
        action = {
            'name': _('Enquiry'),
            'type': 'ir.actions.act_window',
            'res_model': 'client.enquiry',
            'context': {'create': False},
        }
        if len(assessment) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': assessment.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', assessment.ids)],
            })
        return action

    def action_view_circulation(self):
        """View assessment valuation"""
        valuation = self.circulation_id
        action = {
            'name': _('Circulation'),
            'type': 'ir.actions.act_window',
            'res_model': valuation._name,
            'context': {'create': False},
        }
        if len(valuation) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': valuation.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', valuation.ids)],
            })
        return action

    def action_view_assessment(self):
        """View assessment"""
        assessment = self.assessment_id
        action = {
            'name': _('Assessment'),
            'type': 'ir.actions.act_window',
            'res_model': 'enquiry.assessment',
            'context': {'create': False},
        }
        if len(assessment) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': assessment.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', assessment.ids)],
            })
        return action

    def action_view_acquisition(self):
        """View assessment"""
        assessment = self.acquisition_id
        action = {
            'name': _('Acquisition'),
            'type': 'ir.actions.act_window',
            'res_model': 'enquiry.assessment',
            'context': {'create': False},
        }
        if len(assessment) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': assessment.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', assessment.ids)],
            })
        return action

    # def action_approve(self):
    #     """Method for approve the assessment valuation"""
    #     for rec in self:
    #         rec.state = 'approve'
    #         base_url = self.env['ir.config_parameter'].sudo().get_param(
    #             'web.base.url')
    #         Urls = urls.url_join(base_url,
    #                              'web#id=%s&model=assessment.valuation&view_type=form' % rec.id)
    #         mail_content = _('Hi,<br>'
    #                          'Valuation %s was approved.'
    #                          '<div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
    #                          'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
    #                          'border-color:#875A7B;text-decoration: none; display: inline-block; '
    #                          'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
    #                          'cursor: pointer; white-space: nowrap; background-image: none; '
    #                          'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
    #                          'View %s</a></div>'
    #                          ) % (rec.name, Urls,
    #                               rec.name)
    #         # recipient_ids = self.env.ref(
    #         #     'client_enquiry.group_property_manager').users
    #         partner = rec.assessment_id.partner_id
    #         main_content = {
    #             'subject': _(
    #                 'Valuation Approved: %s' % self.assessment_id.name),
    #             'author_id': self.env.user.partner_id.id,
    #             'body_html': mail_content,
    #             'recipient_ids': [(6, 0, partner.ids)]
    #         }
    #         mail_id = self.env['mail.mail'].sudo().create(main_content)
    #         mail_id.mail_message_id.body = mail_content
    #         mail_id.sudo().send()
    #         rec.assessment_id.state = 'valuation_completed'
    #
    # def action_refuse(self):
    #     """Method for refuse the assessment valuation"""
    #     for rec in self:
    #         rec.state = 'refuse'
    #         base_url = self.env['ir.config_parameter'].sudo().get_param(
    #             'web.base.url')
    #         Urls = urls.url_join(base_url,
    #                              'web#id=%s&model=assessment.valuation&view_type=form' % rec.id)
    #         mail_content = _('Hi,<br>'
    #                          'Valuation %s was Refused.'
    #                          '<div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
    #                          'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
    #                          'border-color:#875A7B;text-decoration: none; display: inline-block; '
    #                          'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
    #                          'cursor: pointer; white-space: nowrap; background-image: none; '
    #                          'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
    #                          'View %s</a></div>'
    #                          ) % (rec.name, Urls,
    #                               rec.name)
    #         # recipient_ids = self.env.ref(
    #         #     'client_enquiry.group_property_manager').users
    #         partner = rec.assessment_id.partner_id
    #         main_content = {
    #             'subject': _(
    #                 'Valuation Refused: %s' % self.assessment_id.name),
    #             'author_id': self.env.user.partner_id.id,
    #             'body_html': mail_content,
    #             'recipient_ids': [(6, 0, partner.ids)]
    #         }
    #         mail_id = self.env['mail.mail'].sudo().create(main_content)
    #         mail_id.mail_message_id.body = mail_content
    #         mail_id.sudo().send()

    # def unlink(self):
    #     """Super this method to add a condition in deleting the record"""
    #     for rec in self:
    #         if rec.state != 'draft':
    #             raise ValidationError(_('We can only delete the valuation'
    #                                     ' in draft state.'))
    #     return super().unlink()
