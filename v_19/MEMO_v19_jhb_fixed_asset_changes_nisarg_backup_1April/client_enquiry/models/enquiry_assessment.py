from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import requests

TICKET_PRIORITY = [
    ('0', 'Low priority'),
    ('1', 'Medium priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]
import xml.dom.minidom
from lxml import etree


# def dictlist(node):
#     res = {}
#     res[node.tag] = []
#     myxmltodict(node, res[node.tag])
#     reply = {}
#     reply[node.tag] = res[node.tag]
#     return reply
#
#
# def myxmltodict(node, res):
#     rep = {}
#     if len(node):
#         for n in list(node):
#             rep[node.tag] = []
#             value = myxmltodict(n, rep[node.tag])
#             if len(n):
#                 value = rep[node.tag]
#                 res.append({n.tag: value})
#             else:
#                 res.append(rep[node.tag][0])
#     else:
#         value = {}
#         value = node.text
#         res.append((node.tag, value))
#     return


class EnquiryAssessment(models.Model):
    """Enquiry Assessment"""
    _name = 'enquiry.assessment'
    _description = "Enquiry assessment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", copy=False)
    enquiry_id = fields.Many2one('client.enquiry', string='Enquiry',
                                 domain=[('state', '=', 'draft')])
    jmc_number = fields.Char(string="JMC Number", help="JMC number")
    # type = fields.Char(string="Types of Enquiry", help="Type of Enquiry")
    type = fields.Selection([('social_lease', 'Social Lease/ Sale'),
                             ('commercial_lease',
                              'Commercial Lease/Sale (including residential)'),
                             ('registration',
                              'Registration/ cancellation of a servitude'),
                             ('land', 'Land Regularisation Matter'),
                             ('road', 'Road reserve'),
                             ('user_agreement', 'User Agreement'),
                             ('ptob', 'PTOB'),
                             ('lanes','Sanatory Lanes'),
                             ('encroachment', 'Encroachment / Parking'),
                             ('outdoor', 'Outdoor Advertising')],
                            string='Reason of enquiry',default='encroachment')
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0', tracking=True)
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    property_id = fields.Many2one('building', domain=[('state', 'in', ['free', 'reserved'])])
    property_description = fields.Text(string='Property description')
    state = fields.Selection([('draft', 'In Progress'),
                              ('ownership', 'Assessment Completed'),
                              ('compile', 'Compile Assessment review'),
                              ('objection', 'Objection'),
                              ('negotiation', 'Negotiation'),
                              ('PTOB', 'PTOB'),
                              ('valuation', 'Waiting for Valuation Result'),
                              ('valuation_completed', 'Valuation Completed'),
                              ('terminate', 'Assessment Not Supported'),
                              ('transition', 'Transaction'),
                              ('send_transition', 'Send Transaction'),
                              ('approve', 'Approved'),
                              ('internal_meeting', 'Internal Meeting'),
                              ('internal_meeting_approved', "Board Approved"),
                              ('mayoral_approved', "Mayoral Approved"),
                              ('council_approved', 'Council Approved'),
                              ('technical_growth',
                               'Technical Growth Cluster Approved'),
                              ('sub_mayoral', 'Sub-Mayoral Approved'),
                              ('executive', 'Executive Management Team'),
                              ('council_79_approved', "Council 79 Approved"),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')],
                             default='draft', tracking=True)
    partner_id = fields.Many2one('res.partner',
                                 string='Customer', tracking=True)
    last_stage_updated = fields.Datetime('Last Stage Updated', readonly=True)
    stand_number = fields.Char(string="Stand Number/ Portion number")
    first_name = fields.Char(string="First Name")
    cell_phone = fields.Char(string="Cell")
    email = fields.Char(string="E-mail address")
    title = fields.Char(string="Tittle")
    upload_report_document_ids = fields.Many2many('ir.attachment',"upload_report_document_rel",string="Attachments",tracking=True)
    upload_document_name = fields.Char(string="Uploaded Document")
    enquiry_name_id = fields.Many2one('res.partner',
                                 string='Surname', tracking=True)
    zoning = fields.Char(string="Zoning",tracking=True)
    land_type = fields.Selection([('church', 'Church'), ('shop', 'Shop')],
                                 string="Land Type")

    # GIS
    # latitude = fields.Float(string="Latitude")
    # longitude = fields.Float(string="Longitude")

    # Compile report

    circulation_ids = fields.One2many('circulation.assessment', 'assessment_id')
    comments_receive_date = fields.Date(string="Date for circulation comments",
                                       help="Circulation comments will be "
                                            "receive before this date")
    # Objections
    outcome = fields.Selection([('yes', 'Yes'), ('no', 'No')], readonly=True)
    is_object_valid = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Is objection valid')
    # is_negotiation = fields.Boolean(string='Is there any negotiation required',
    #                                 readonly=True)
    # is_municipal_department = fields.Selection([('yes', 'Yes'), ('no', 'No')],
    #                                            string='Is Municipal Department',
    #                                            )
    valuation_ids = fields.Many2many('assessment.valuation')
    valuation_count = fields.Integer(compute="_compute_valuation_count")

    # SCM Valuation

    valuation_report = fields.Binary(string="Valuation report")
    # proceed_request = fields.Selection([('yes', 'Yes'), ('no', 'No')])

    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Assessment Report", readonly=True)

    transaction_report_ids = fields.Many2many('ir.attachment',
                                              'transaction_report_rel',
                                              string="Transaction Report",
                                              help="Transactions reports",
                                              readonly=True)
    transaction_sign_document_id = fields.Many2one('sign.request',
                                                string="Sign document",
                                                help="Sign document for the "
                                                     "transaction report")
    transaction_document_id = fields.Many2one('documents.document',
                                              string="Document", help="Documents")
    share_link = fields.Char(string="Share Link", compute='_compute_share_link')
    committee_transaction = fields.Boolean(string="Transaction meeting",
                                           help="Is the transaction meeting is created")
    committee_board_meeting = fields.Boolean(string="Board committee meeting",
                                             help="Is the board committee meeting is created")
    meeting_request_ids = fields.Many2many('assessment.meeting', string="Meeting request")
    committee_meeting_ids = fields.Many2many('committee.meeting',
                                             string="Meetings")
    internal_meeting_ids = fields.Many2many('committee.meeting',
                                            'internal_meeting_rel',
                                            string="Internal meeting")
    internal_meeting_document_ids = fields.Many2many('ir.attachment', 'internal_meeting_document_rel')
    mayoral_attachment_ids = fields.Many2many('ir.attachment',
                                              'mayoral_attachment',
                                              string="Mayoral Report")
    council_attachment_ids = fields.Many2many('ir.attachment',
                                              'council_attachment',
                                              string="Council Report")
    # details of the partner that they can only view the assessment in portal
    partner_ids = fields.Many2many('res.partner', string="Partner")
    assessment_documents_ids = fields.Many2many('documents.document',
                                                string="Assessment Document")
    assessment_folder_id = fields.Many2one('documents.document',
                                           string="Assessment Folder")
    circulation_documents_ids = fields.Many2many('documents.document', 'circulation_documents_rel', string="Circulation Documents")
    circulation_folder_id = fields.Many2one('documents.document', string="Circulation Folder")
    valuation_document_id = fields.Many2one('documents.document', string="Valuation Document")
    valuation_folder_id = fields.Many2one('documents.document', string='Valuation folder')
    transaction_folder_id = fields.Many2one('documents.document', string="Transaction folder")
    board_meeting_folder_id = fields.Many2one('documents.document', string='Board meeting folder')
    board_document_ids = fields.Many2many('documents.document',
                                          'board_document_rel', string='Board documents')
    mayoral_meeting_folder_id = fields.Many2one('documents.document',
                                              string='Mayoral meeting folder')
    mayoral_document_ids = fields.Many2many('documents.document',
                                          'mayoral_document_rel',
                                            string='Mayoral documents')
    council_meeting_folder_id = fields.Many2one('documents.document',
                                              string='Council meeting folder')
    council_document_ids = fields.Many2many('documents.document',
                                          'council_document_rel',
                                            string='Council documents')

    technical_growth_ids = fields.Many2many('ir.attachment',
                                              'technical_growth_rel',
                                              string="Technical Growth Report",
                                              help="Technical Growth reports",
                                              readonly=True)
    technical_growth_folder_id = fields.Many2one('documents.document',
                                              string='Technical growth folder')
    technical_growth_document_ids = fields.Many2many('documents.document',
                                          'technical_growth_document_rel',
                                            string='Executive management documents')
    executive_management_ids = fields.Many2many('ir.attachment',
                                              'executive_management_rel',
                                              string="Executive management Report",
                                              help="Executive management reports",
                                              readonly=True)
    executive_management_folder_id = fields.Many2one('documents.document',
                                              string='Executive Management Folder')
    executive_management_document_ids = fields.Many2many('documents.document',
                                          'executive_management_document_rel',
                                            string='Executive management documents')

    council_79_attachment_ids = fields.Many2many('ir.attachment',
                                                 'council_79_attachment',
                                                 string="Council 79 Section "
                                                        "Report")
    council_79_folder_id = fields.Many2one('documents.document',
                                              string='Council 79 Section folder')
    council_79_document_ids = fields.Many2many('documents.document',
                                          'executive_management_document_rel',
                                            string='Council 79 Section documents')
    sub_mayoral_attachment_ids = fields.Many2many('ir.attachment',
                                                 'sub_mayoral_attachment_rel',
                                                 string="Sub-mayoral Report")
    sub_mayoral_folder_id = fields.Many2one('documents.document',
                                              string='Sub-mayoral folder')
    sub_mayoral_document_ids = fields.Many2many('documents.document',
                                          'sub_mayoral_document_rel',
                                            string='Sub-mayoral documents')
    user_id = fields.Many2one('res.users', string='Assignee', help="Assignee details")
    user_domain_ids = fields.Many2many('res.users', string='Team Members',
                              help="Assignee details", compute="_depends_state")
    section_79_section_ids = fields.Many2many('documents.document', 'section_79_notice_rel',
                                              string='Section 79 Section')
    section_79_folder_id = fields.Many2one('documents.document', string='Section 79 Folder')
    upload_supporting_document_id = fields.Many2one(comodel_name='client.enquiry',help="Add the audit universe")
    land_regularisation_id = fields.Many2one('land.regularization',string='Land Regularization')
    is_supported = fields.Selection([('supported', 'Supported'), ('not_supported', 'Not Supported')],  string="Assessment Result")

    # SLA

    sla_policy_ids = fields.Many2many('client.enquiry.sla.policy.status')
    sla_reached_late = fields.Boolean("Has SLA reached late",
                                      compute='_compute_sla_reached_late',
                                      compute_sudo=True, store=True)
    sla_reached = fields.Boolean("Has SLA reached",
                                 compute='_compute_sla_reached',
                                 compute_sudo=True, store=True)
    sla_deadline = fields.Datetime("SLA Deadline",
                                   compute='_compute_sla_deadline',
                                   compute_sudo=True, store=True)
    # sla_deadline_hours = fields.Float("Hours to SLA Deadline",
    #                                   compute='_compute_sla_deadline',
    #                                   compute_sudo=True, store=True)
    sla_fail = fields.Boolean("Failed SLA Policy", compute='_compute_sla_fail')
    sla_success = fields.Boolean("Success SLA Policy",
                                 compute='_compute_sla_success')
    circulation_id = fields.Many2one('circulation.comments', string="Circulation Comments")
    transaction_id = fields.Many2one('client.transaction', string="Transaction")




    @api.depends('transaction_sign_document_id')
    def _compute_share_link(self):
        if self.transaction_sign_document_id:
            self.share_link = "%s/sign/document/mail/%s/%s" % (
            self.get_base_url(), self.transaction_sign_document_id.id,
            self.transaction_sign_document_id.request_item_ids[0].sudo().access_token)
        else:
            self.share_link = ''

    booking_id = fields.Many2one('unit.reservation', string="Property Booking", help="Booking")


    def action_button_doc_view(self):
        folder = self.env.ref('__custom__.dd')
        return {
            'name': 'Document',
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'kanban',
            'target': 'current',
            'context': "{'searchpanel_default_folder_id': %s}" % folder.id
        }

    @api.depends('state')
    def _depends_state(self):
        """Methode for set the assessment"""
        self.user_domain_ids = []
        if self.state == 'draft' or self.state == 'valuation':
            asset = self.env.ref('client_enquiry.group_asset_evaluator').user_ids
            self.user_domain_ids = asset
        if self.state in ['ownership', 'transition', 'internal_meeting',
                          'internal_meeting_approved', 'technical_growth',
                          'executive', 'council_79_approved', 'sub_mayoral',
                          'mayoral_approved', 'council_approved']:
            property = self.env.ref(
                'client_enquiry.group_property_manager').user_ids
            self.user_domain_ids = property
        if self.state == 'compile' or self.state == 'objection' or self.state == 'valuation_completed':
            property = self.env.ref(
                'client_enquiry.group_property_manager').user_ids
            self.user_domain_ids = property

    @api.model
    def create(self, values):
        """Method for generating sequence"""
        values['name'] = self.env['ir.sequence'].next_by_code(
            'enquiry.assessment') or _('New')
        if not values['property_id']:
            raise ValidationError(_('Please provide a property'))
        res = super(EnquiryAssessment, self).create(values)
        res.enquiry_id.assessment_id = res.id
        res.last_stage_updated = fields.Datetime.now()
        res.enquiry_id.state = 'assessment'
        return res


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'enquiry.assessment'
            vals['name'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(EnquiryAssessment, self).create(vals_list)
        res.enquiry_id.assessment_id = res.id
        res.last_stage_updated = fields.Datetime.now()
        res.enquiry_id.state = 'assessment'
        return res

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """Onchange the property"""
        self.jmc_number = self.property_id.jmc_number

    def check_ownership(self):
        """Check ownership of an existing property"""
        if not self.jmc_number:
            raise ValidationError(_('Please add the JMC number'))
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Assessment report'),
            'view_mode': 'form',
            'res_model': 'check.ownership',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'default_jmc_number': self.property_id.jmc_number,
                'default_land_type': self.land_type
            }
        }

    def create_land_regularization(self):
        land_regularisation_id = self.env['land.regularization'].create({
            'enquiry_id': self.enquiry_id.id,
            'assessment_id': self.id,
            'assessment_result': self.is_supported,
            'type': self.enquiry_id.church_shop,
            'state': 'requested_doc',
            'requester_infos': self.user_id.id,
        })
        self.land_regularisation_id = land_regularisation_id.id
        mail_template = self.env.ref(
            'client_enquiry.email_template_request_document')
        mail_template.send_mail(self.land_regularisation_id.id, force_send=True)
        if self.enquiry_id:
            self.enquiry_id.land_regularisation_id = land_regularisation_id.id
            self.enquiry_id.state = 'land_regularisation'

    def send_compile_report(self):
        """Methode to send the compile reports to all users"""
        circulation_id = self.env['circulation.comments'].create({
            'assessment_id': self.id,
            'enquiry_id': self.enquiry_id.id,
            'property_id': self.property_id.id,
            'address': self.property_id.address,
            'jmc_number': self.property_id.jmc_number,
            'township': self.property_id.township,
            'stand_number': self.property_id.stand_number,
            # 'zoning_id': self.property_id.zoning_id.id,
        })
        self.circulation_id = circulation_id.id
        # self.state = 'compile'
        if self.enquiry_id:
            self.enquiry_id.circulation_id = circulation_id.id
            self.enquiry_id.state = 'circulation_comments'

    def action_objection(self):
        """Method for action objection"""
        if self.circulation_documents_ids:
            pass
        return {
            'name': _('Review'),
            'view_mode': 'form',
            'res_model': 'assessment.objection',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id
            }
        }

        # else:
        #     raise UserError(_('Need to add the circulation documents'))

    def action_create_valuation_form(self):
        """Method to create a valuation form"""
        attachment = self.env['ir.attachment'].search([('res_model', '=', self._name),
                                                       ('res_id', '=', self.id)])
        return {
            'name': _('Valuation'),
            'view_mode': 'form',
            'res_model': 'assessment.valuation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'default_property_id': self.property_id.id,
                'default_property_number': self.property_id.code,
                'default_property_description': self.property_id.description,
                'default_address': self.property_id.address,
                'default_jmc_number': self.jmc_number,
                'default_attachment_ids': attachment.ids
                # 'default_circulation_comments': self.circulation_comments,
            }
        }

    @api.depends('valuation_ids')
    def _compute_valuation_count(self):
        for rec in self:
            # rec.valuation_count = len(rec.valuation_ids)
            rec.valuation_count = len(self.env['assessment.valuation'].search(
                [('assessment_id', '=', self.id)]))

    def action_open_valuation(self):
        """Method to open the valuation"""
        valuation = self.env['assessment.valuation'].search([('assessment_id', '=', self.id)])
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


    def action_scm_assessment(self):
        """Open a wizard to attach the assessment valuation"""
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the documents'))
        return {
            'name': _('Valuation'),
            'view_mode': 'form',
            'res_model': 'scm.valuation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
            }
        }

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

    # def action_send_valuation_report(self):
    #     """This method for send the Transaction report."""
    #     self.ensure_one()
    #     ir_model_data = self.env['ir.model.data']
    #     try:
    #         template_id = ir_model_data._xmlid_lookup(
    #             'client_enquiry.email_template_transaction_report')[2]
    #     except ValueError:
    #         template_id = False
    #     try:
    #         compose_form_id = ir_model_data._xmlid_lookup(
    #             'mail.email_compose_message_wizard_form')[2]
    #     except ValueError:
    #         compose_form_id = False
    #     ctx = dict(self.env.context or {})
    #     ctx.update({
    #         'default_model': self._name,
    #         'active_model': self._name,
    #         'active_id': self.ids[0],
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
    #         'force_email': True,
    #         'mark_transaction_as_sent': True,
    #     })
    #
    #     lang = self.env.context.get('lang')
    #     if {'default_template_id', 'default_model',
    #         'default_res_id'} <= ctx.keys():
    #         template = self.env['mail.template'].browse(
    #             ctx['default_template_id'])
    #         if template and template.lang:
    #             lang = template._render_lang([ctx['default_res_id']])[
    #                 ctx['default_res_id']]
    #
    #     self = self.with_context(lang=lang)
    #     ctx.update({
    #         # 'default_partner_ids': partner.ids,
    #         'default_attachment_ids': self.transaction_report_ids.ids
    #     })
    #     return {
    #         'name': _('Compose Email'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form_id, 'form')],
    #         'view_id': compose_form_id,
    #         'target': 'new',
    #         'context': ctx,
    #     }

    # def action_approve(self):
    #     """Method for approve the transaction report"""
    #     self.state = 'approve'
    #
    # def action_refuse(self):
    #     """Method for approve the transaction report"""
    #     self.state = 'valuation_completed'

    def unlink(self):
        """Super this method to add a condition in deleting the record"""
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('We can only delete the assessment in draft state.'))
            if rec.state == 'draft':
                if rec.enquiry_id:
                    rec.enquiry_id.state = 'draft'
        return super().unlink()

    def action_open_enquiry(self):
        """Methode to open enquiry"""
        return {
            'name': _('Enquiry'),
            'view_mode': 'form',
            'res_model': 'client.enquiry',
            'type': 'ir.actions.act_window',
            'res_id': self.enquiry_id.id,
        }

    def action_view_land_regularization(self):
        """Methode to open land regularization"""
        return {
            'name': _('Land Regularization'),
            'view_mode': 'form',
            'res_model': 'land.regularization',
            'type': 'ir.actions.act_window',
            'res_id': self.land_regularisation_id.id,
        }

    def action_assigne_to_me(self):
        """Method for assign the enquiry to the users."""
        if self.env.user.id in self.user_domain_ids.ids:
            self.user_id = self.env.user.id
            mail_template = self.env.ref('client_enquiry.email_template_enquiry_assessment_assigned')
            mail_template.send_mail(self.id, force_send=True)
        else:
            raise UserError (_('You are not allowed to access this enquiry now.'))

    def action_open_booking(self):
        """Methode to open booking"""
        return {
            'name': _('Booking'),
            'view_mode': 'form',
            'res_model': 'unit.reservation',
            'type': 'ir.actions.act_window',
            'res_id': self.booking_id.id,
        }

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

    def action_receive_transition_report(self):
        """Method for to attach the transaction report"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to upload the documents'))

        return {
            'name': _('Transaction Report'),
            'view_mode': 'form',
            'res_model': 'assessment.transaction',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
            }
        }

    def write(self, vals):
        send = False
        if vals.get('user_id'):
            send = True
        before_doc = self.upload_report_document_ids

        res = super(EnquiryAssessment, self).write(vals)
        after_doc = self.upload_report_document_ids
        newly_added = after_doc - before_doc
        removed = before_doc - after_doc

        for attachment in removed:
            if not attachment.exists():
                continue

            document = self.env['documents.document'].search([
                ('attachment_id', '=', attachment.id)
            ])
            if document:
                document.unlink()

        if send:
            mail_template = self.env.ref(
                'client_enquiry.email_template_enquiry_assessment_assigned')
            mail_template.send_mail(self.id, force_send=True)
        if vals.get('internal_meeting_ids'):
            if len(self.internal_meeting_ids) > 1:
                mail_template = self.env.ref(
                    'client_enquiry.email_template_enquiry_assessment_upload_meeting_report')
                recipient_ids = self.env.ref(
                    'client_enquiry.group_property_manager').users
                partner = recipient_ids.mapped('partner_id')
                email_values = {
                    'recipient_ids': [(6, 0, partner.ids)]
                }
                mail_template.send_mail(self.id, force_send=True,
                                        email_values=email_values)
        return res

    def action_create_committee_meeting_for_transaction(self):
        """Method for create the meeting for internal users."""
        # sign = self.env['sign.template'].sudo().search([('name', '=', self.transaction_document_id.name)])
        # if not sign:
        #     raise UserError(_('Sign Template is not created.'))
        # if sign:
        #     request = sign.sign_request_ids
        #     if request:
        #         for req in request:
        #             if not req.nb_closed:
        #                 raise UserError(_('Sign Request is not signed.'))
        #     else:
        #         raise UserError(_('Sign Request is not created.'))
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to create the meeting'))
        context = {}
        if not self.committee_transaction:
            context = {
                    'default_assessment_id': self.id,
                    'default_committee_id': self.env.ref('client_enquiry.committee_transaction').id,
                    'transaction': True
                }
        if not self.committee_board_meeting:
            context = {
                'default_assessment_id': self.id,
                'default_committee_id': self.env.ref(
                    'client_enquiry.committee_board_meeting').id,
                'board': True
            }
        return {
            'name': _('Committee Meeting'),
            'view_mode': 'form',
            'res_model': 'assessment.meeting',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('client_enquiry.assessment_meeting_view_form').id,
            'target': 'new',
            'context': context
        }
        # if self.committee_transaction:
        #     commitee = [self.env.ref('client_enquiry.committee_board_meeting').id]
        # elif self.committee_board_meeting:
        #     commitee = [self.env.ref('client_enquiry.committee_transaction').id]
        # elif not self.committee_transaction and not self.committee_transaction:
        #     commitee = [self.env.ref('client_enquiry.committee_transaction').id, self.env.ref('client_enquiry.committee_board_meeting').id]
        # return {
        #     'name': _('Committee Meeting'),
        #     'view_mode': 'form',
        #     'res_model': 'assessment.meeting',
        #     'type': 'ir.actions.act_window',
        #     'view_id': self.env.ref('client_enquiry.assessment_meeting_view_form').id,
        #     'target': 'new',
        #     'context': {
        #         'default_assessment_id': self.id,
        #         'default_available_committee_ids': commitee
        #     }
        # }

    def action_sign_document(self):
        """Method for open the document"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.transaction_folder_id.id
            }
        }

    def action_signed_document(self):
        """Method for open the document"""
        folder = self.env['documents.document'].sudo().search([('folder_id', '=', self.transaction_folder_id.id)])
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,list,form',
            'context': {
                'searchpanel_default_folder_id': folder.id
            }
        }

    def action_upload_the_report(self):
        """Method for upload the report"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        for req in self.meeting_request_ids:
            if not req.meeting_id:
                raise UserError(
                    _('The meeting is not in created for meeting request %s meeting') % req.subject)
        for rec in self.committee_meeting_ids:
            if rec.state == 'approved':
                if not rec.is_completed:
                    raise UserError(_('The meeting %s has not completed') % rec.name)
                else:
                    return {
                        'name': _('Attach Report'),
                        'view_mode': 'form',
                        'res_model': 'upload.meeting.report',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': {
                            'default_assessment_id': self.id,
                            'internal_meeting': True
                        }
                    }
            else:
                raise UserError(_('The meeting %s is not in approved state') %rec.name)

    # def action_approve_internal_meeting(self):
    #     """Methode for approve the internal meetings"""
    #     if self.internal_meeting_document_ids:
    #         self.state = "internal_meeting_approved"
    #     else:
    #         raise UserError(_('Upload the documents'))

    # def action_refuse_internal_meeting(self):
    #     """Methode for approve the internal meetings"""
    #     if self.internal_meeting_document_ids:
    #         self.state = "approve"
    #     else:
    #         raise UserError(_('Upload the documents'))

    def action_open_mayoral(self):
        """Methode for open mayoral"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Mayoral report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'mayoral': True
            }
        }

    # def action_approve_mayoral_report(self):
    #     """Methode for approve mayoral report"""
    #     if self.mayoral_attachment_ids:
    #         self.state = "mayoral_approved"
    #     else:
    #         raise UserError(_('Upload the Mayoral Reports'))
    #
    # def action_refuse_mayoral_report(self):
    #     """Methode for approve mayoral report"""
    #     if self.mayoral_attachment_ids:
    #         self.state = "terminate"
    #     else:
    #         raise UserError(_('Upload the Mayoral Reports'))

    def action_upload_council(self):
        """Methode for open mayoral"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Council report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'council': True
            }
        }

    def action_executive_management_team(self):
        """Methode for Executive Management team"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Executive management report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'executive_management_team': True
            }
        }

    def action_technical_growth_cluster(self):
        """Methode for technical growth cluster"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Technical Growth Cluster'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'technical': True
            }
        }

    # def action_approve_council_report(self):
    #     """Methode for approve mayoral report"""
    #     if self.council_attachment_ids:
    #         self.state = "council_approved"
    #     else:
    #         raise UserError(_('Upload the Council Reports'))
    #
    # def action_refuse_council_report(self):
    #     """Method for approve mayoral report"""
    #     if self.council_attachment_ids:
    #         self.state = "terminate"
    #     else:
    #         raise UserError(_('Upload the Council Reports'))

    def action_council_section_79(self):
        """Method for council section 79"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Council Section 79 report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'council_section_79': True
            }
        }

    def action_sub_mayoral(self):
        """Method for sub-mayoral"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise ValidationError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Council section 79 report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'sub_mayoral': True
            }
        }
    # def action_approve_council_section_79_report(self):
    #     """Methode for approve mayoral report"""
    #     if self.council_79_attachment_ids:
    #         self.state = "council_79_approved"
    #     else:
    #         raise UserError(_('Upload the Council Reports'))
    #
    # def action_refuse_council_section_79_report(self)9:
    #     """Method for approve mayoral report"""
    #     if self.council_79_attachment_ids:
    #         self.state = "mayoral_approved"
    #     else:
    #         raise UserError(_('Upload the Council Reports'))

    def action_open_meetings(self):
        """Methode for open meetings"""
        meeting = self.committee_meeting_ids
        action = {
            'name': _('Meetings'),
            'type': 'ir.actions.act_window',
            'res_model': 'committee.meeting',
            'context': {'create': False},
        }
        if len(meeting) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': meeting.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', meeting.ids)],
            })
        return action

    def action_open_meeting_request(self):
        """Methode for open meetings"""
        meeting = self.meeting_request_ids
        action = {
            'name': _('Meeting Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'assessment.meeting',
            'context': {'create': False},
        }
        if len(meeting) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': meeting.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', meeting.ids)],
            })
        return action

    def action_open_assessment_documents(self):
        """Method for open assessment documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.assessment_documents_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.assessment_folder_id.id
            }
        }

    def action_open_circulation_documents(self):
        """Method for open circuit documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.circulation_documents_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.circulation_folder_id.id
            }
        }

    def action_open_valuation_documents(self):
        """Method for open valuation documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.valuation_document_id.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.valuation_folder_id.id
            }
        }

    def action_open_board_document(self):
        """Method to open the board document"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.board_document_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.board_meeting_folder_id.id
            }
        }

    def action_open_mayoral_document(self):
        """Method to open the mayoral document"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.mayoral_document_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.mayoral_meeting_folder_id.id
            }
        }

    def action_open_council_document(self):
        """Method to open the council documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.council_document_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.council_meeting_folder_id.id
            }
        }

    def action_open_technical_growth_document(self):
        """Method to open the council documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.technical_growth_document_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.technical_growth_folder_id.id
            }
        }

    def action_open_executive_management_document(self):
        """Method to open the executive management documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.executive_management_document_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.executive_management_folder_id.id
            }
        }

    def action_open_council_79_document(self):
        """Method to open the executive management documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.council_79_document_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.council_79_folder_id.id
            }
        }

    def action_open_sub_mayoral_document(self):
        """Method to open the executive management documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.sub_mayoral_document_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.sub_mayoral_folder_id.id
            }
        }

    # @api.onchange('upload_report_document_ids')
    # def _onchange_upload_report_document_ids(self):
    #     # folder = self.env['documents.document'].browse(document_enquiry_general_enquiry)
    #     folder = self.env.ref('__custom__.dd')
    #
    #     for rec in self.upload_report_document_ids:
    #         existing_document = self.env['documents.document'].sudo().search([
    #             ('attachment_id', '=', rec._origin.id),
    #             ('folder_id', '=', folder.id),
    #             ('name', '=', rec.name)
    #         ])
    #
    #         if not existing_document:
    #             self.env['documents.document'].sudo().create({
    #                 'name': rec.name,
    #                 'attachment_id': rec._origin.id,
    #                 'folder_id': folder.id
    #             })

    def action_view_assessment(self):
        """View assessment from kanban card"""
        return {
            'name': self.name,
            'view_mode': 'form',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
        }

    def action_section_179_report(self):
        """Add section 179 report"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Section 79 Notice Report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'section_179': True
            }
        }

    def action_open_section_79_notice_document(self):
        """Open a new section 79 notice documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),
                       ('id', 'in', self.section_79_section_ids.ids)],
            'view_mode': 'kanban,list,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.section_79_folder_id.id
            }
        }

    def action_upload_board_document(self):
        """Upload board document"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Upload Internal Meeting Report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('client_enquiry.upload_meeting_report_view_form_uploading').id,
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'internal_meeting': True
            }
        }

    def action_upload_executive_management_document(self):
        """Re upload the executive management document"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Executive Management Report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('client_enquiry.upload_meeting_report_view_form_uploading').id,
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'executive_management_team': True
            }
        }

    def action_upload_council_79_document(self):
        """Re-upload the documents"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Council Section 79 Report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('client_enquiry.upload_meeting_report_view_form_uploading').id,
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'council_section_79': True
            }
        }

    def action_upload_sub_mayoral_document(self):
        """Re-upload the sub mayoral documents"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Sub Mayoral Report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('client_enquiry.upload_meeting_report_view_form_uploading').id,
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'sub_mayoral': True
            }
        }

    def action_upload_mayoral_document(self):
        """Re-upload the mayoral documents"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Mayoral Report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('client_enquiry.upload_meeting_report_view_form_uploading').id,
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'mayoral': True
            }
        }

    def action_upload_council_document(self):
        """Re-upload the council documents"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Attach Mayoral Report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('client_enquiry.upload_meeting_report_view_form_uploading').id,
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'council': True
            }
        }

    def action_upload_technical_growth_document(self):
        """Upload the technical growth documents"""
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Upload the document'))
        return {
            'name': _('Upload Technical Growth Cluster Report'),
            'view_mode': 'form',
            'res_model': 'upload.meeting.report',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('client_enquiry.upload_meeting_report_view_form_uploading').id,
            'target': 'new',
            'context': {
                'default_assessment_id': self.id,
                'technical': True
            }
        }

    def get_list_url(self):
        """Returns the url for the list view"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,'web#id=%s&model=enquiry.assessment&view_type=form' % self.id)
        return Urls

    def action_windeed_authentication(self):
        """Authentication for windeed"""
        url = "http://server.windeed.co.za/windeedengine3/deedsoffice.asmx"

        payload = ("<?xml version=\"1.0\" encoding=\"utf-8\"?>"
                   "\n<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\n  <soap12:Header>\n    <EmailCredentials xmlns=\"http://server.windeed.co.za/windeedengine/\">\n      "
                   "<EmailAddress>%s</EmailAddress>\n"
                   "<Password>%s</Password>\n"
                   "<Requester>%s</Requester>\n"
                   "</EmailCredentials>\n"
                   "</soap12:Header>\n"
                   "<soap12:Body>\n"
                   "<Authenticate xmlns=\"http://server.windeed.co.za/windeedengine/\" />\n"
                   "</soap12:Body>\n</soap12:Envelope>") %( 'jpcpims@jhbproperty.co.za', 'JPCWindeed01', 'oodo')
        headers = {
            'Content-Type': 'application/soap+xml',
            'SOAPAction': 'http://server.windeed.co.za/windeedengine/Authenticate',
            'charset': 'utf-8'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        xml_data = xml.dom.minidom.parseString(response.content)
        xml_string = xml_data.toprettyxml()
        tree = etree.fromstring(xml_string)
        # dic = dictlist(tree)
        raise UserError(_(response.text))

    @api.onchange('internal_meeting_ids')
    def _onchange_internal_meeting_ids(self):
        """Change the internal meeting IDs"""
        print('aaaaaaaaaaa _onchange_internal_meeting_ids')

    @api.depends('sla_policy_ids.deadline', 'sla_policy_ids.reached_datetime',
                 'sla_policy_ids')
    def _compute_sla_reached_late(self):
        """ Required to do it in SQL since we need to compare 2 columns value """
        for rec in self:
            policy_status = rec.sla_policy_ids.mapped('status')
            if 'failed' in policy_status:
                rec.sla_reached_late = True
            else:
                rec.sla_reached_late = False

    @api.depends('sla_policy_ids.deadline', 'sla_policy_ids.reached_datetime')
    def _compute_sla_reached(self):
        for rec in self:
            policy_status = list(set(rec.sla_policy_ids.mapped('status')))
            if 'ongoing' in policy_status:
                rec.sla_reached = False
            else:
                rec.sla_reached = True

    @api.depends('sla_policy_ids.deadline', 'sla_policy_ids.reached_datetime')
    def _compute_sla_deadline(self):
        """ Keep the deadline for the last stage (closed one), so a closed ticket can have a status failed.
            Note: a ticket in a closed stage will probably have no deadline
        """
        now = fields.Datetime.now()
        for ticket in self:
            min_deadline = False
            for status in ticket.sla_policy_ids:
                if status.reached_datetime or not status.deadline:
                    continue
                if not min_deadline or status.deadline < min_deadline:
                    min_deadline = status.deadline
            ticket.update({
                'sla_deadline': min_deadline,
                # 'sla_deadline_hours':
                #     ticket.team_id.resource_calendar_id.get_work_duration_data \
                #         (now, min_deadline, compute_leaves=True)[
                #         'hours'] if min_deadline else 0.0,
            })

    @api.depends('sla_deadline', 'sla_reached_late')
    def _compute_sla_fail(self):
        now = fields.Datetime.now()
        for ticket in self:
            if ticket.sla_deadline:
                ticket.sla_fail = (ticket.sla_deadline < now) or ticket.sla_reached_late
            else:
                ticket.sla_fail = ticket.sla_reached_late

    @api.depends('sla_deadline', 'sla_reached_late')
    def _compute_sla_success(self):
        now = fields.Datetime.now()
        for ticket in self:
            ticket.sla_success = (
                    ticket.sla_deadline and ticket.sla_deadline > now)


class AssessmentCirculation(models.Model):
    """Model for assessment Circulation"""
    _name = 'circulation.assessment'
    _description = "Circulation Assessment"

    assessment_id = fields.Many2one('enquiry.assessment')
    attachment_ids = fields.Many2many('ir.attachment',
                                     string="Documents", help="Documents")
    date = fields.Datetime(string="Date", default=fields.Datetime.now())
    user_id = fields.Many2one('res.users', string="User")
    group_ids = fields.Many2many('res.groups')
