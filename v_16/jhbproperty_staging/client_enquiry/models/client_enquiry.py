import re
# from lib2to3.fixes.fix_input import context

from werkzeug import urls

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError
from random import randint

TICKET_PRIORITY = [
    ('0', 'Low priority'),
    ('1', 'Medium priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]


class ClientEnquiry(models.Model):
    """Client Enquiry"""
    _name = 'client.enquiry'
    _description = 'Client Enquiry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _inherits = {'helpdesk.ticket': 'ticket_id'}

    # ticket_id = fields.Many2one('helpdesk.ticket')
    def _get_default_company(self):
        """Method to get portfolio company."""
        company = self.env['res.company'].search([('name', '=', 'Portflolio')])
        return company.id

    name = fields.Char(string="Name", required=True, copy=False, default='New')
    partner_id = fields.Many2one('res.partner',
                                 string='Surname', tracking=True,required=True)
    team_id = fields.Many2one(
        'helpdesk.team',
        string='Channel',
        help='Channel details',
        domain="[('is_enquiry', '=', True)]",
        required=True,
        default=lambda self: self._default_team_id()
    )

    date = fields.Datetime(string="Date", default=fields.Datetime.now(), help="Date", readonly=True)
    asset_number = fields.Char(string="JMC number", help="JMC asset number")
    # ownership_id = fields.Many2one('check.ownership', string="Ownership Record")
    # state_assessment = fields.Selection([('draft', 'Draft'),
    #                           ('submit', 'Submitted'),
    #                           ('inprogress', 'In-Progress'),
    #                           ('assessment', 'Assessment Supported'),
    #                           ('ongoing', 'Assessment ongoing'),
    #                           ('completed', 'Assessment Completed'),
    #                           ('cancelled', 'Assessment Not Supported')], default='draft')
    state = fields.Selection([('draft', 'Enquiry'),
                              ('submit', 'Submitted'),
                              ('assessment', 'Assessment'),
                              ('land_regularisation', 'Land Regularisation'),
                              ('circulation_comments', 'Circulation for Comments'),
                              ('valuation', 'Valuation'),
                              ('transaction', 'Transaction'),
                              ('public_participation', 'Committees'),
                              ('section_advert', 'Section 79 Advert'),
                              ('bide_specification', 'Bid Specification'), ('scm_process', 'SCM Process'),
                              ('legal_agreement', 'Legal Agreements'), ('Take_on', 'Take-On')], default='draft', tracking=True)
    stand_number = fields.Char(string="Stand Number/ Portion number")
    region_id = fields.Many2one('regions', string="Region")
    township = fields.Char(string="Township /Farm Name")
    entire_property = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                       string="Does the enquiry relate to "
                                            "the entire property or a "
                                            "part thereof?",
                                       help="Does the enquiry relate to "
                                            "the entire property or a "
                                            "part thereof?")
    locality_map = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                       string="Locality Map Attached",
                                       help="Add the Locality Map attached.")
    size = fields.Float(string="Size of property", readonly=False)
    church_shop = fields.Selection([('church', 'Church'), ('shop','Shop')], string="Land Type")
    type = fields.Selection([('social_lease', 'Social Lease/ Sale'),
                             ('commercial_lease',
                              'Commercial Lease/Sale (including residential)'),
                             ('registration',
                              'Registration/ cancellation of a servitude'),
                             ('land', 'Land Regularisation Matter'),
                             ('road', 'Road reserve'),
                             ('user_agreement', 'User Agreement'),
                             ('ptob', 'PTOB'),
                             ('lanes', 'Sanatory Lanes'),
                             ('outdoor', 'Outdoor Advertising')],
                            string='Type of enquiry',required=1)
    adjacent_to = fields.Many2one('building', string='Adjacent To')
    proposed_use = fields.Char(string="Proposed use of the property")
    surname = fields.Char(string="Surname")
    # title = fields.Selection([('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'),
    #                           ('Miss', 'Miss')], string="Title")
    title = fields.Many2one('res.partner.title', string='Title')

    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0', tracking=True)
    first_name = fields.Char(string="First Name",required=1)
    cell_phone = fields.Char(string="Cell",required=1)
    zoning = fields.Char(string="Zoning")
    email = fields.Char(string="E-mail address")
    company_id = fields.Many2one('res.company', string="Company Name", default=_get_default_company)
    company_name = fields.Char(string="Company Name")
    registration_number = fields.Char(string="Registration number")
    street = fields.Char(string="Street",
                         help="Name of the street of the customer")
    street2 = fields.Char(string="Street",
                          help="Name of the street of the customer")
    zip = fields.Char(string="Zip", help="Zip code for the customer" )
    city = fields.Char(string="City", help="Name of the city of the customer")
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]",
                               help="Name of the State of the customer")
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict',
                                 help="Name of the country of the customer")
    support_state = fields.Selection([('supported', 'Supported'), ('not_supported', 'Not Supported')],
                                     string='Supporting Status', copy=False)
    telephone_numbers = fields.Char(string='Business Telephone Numbers')
    mobile = fields.Char(string='Mobile Number')
    windeed_search_attachment = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                       string="Windeed  SEarch Attachment",
                                       help="Add the Locality Map attached.")
    # stage = fields.Char(string='Status')
    stage = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted for Approval'),
                              ('free', 'Available'),
                              ('reserved', 'blocked'),
                              ('on_lease', 'Leased'),
                              ('sold', 'Sold'),
                              ('blocked', 'Blocked'),('reject','Rejected')],
                             default='draft', string="Status")
    assessment_id = fields.Many2one('enquiry.assessment', copy=False,
                                    string='Assessment', help="Assessment", tracking=True)
    land_regularisation_id = fields.Many2one('land.regularization',
                                             string='Land Regularization', tracking=True,copy=False)
    assessment_state = fields.Selection(related="assessment_id.state",  copy=False,
                                        string='Assessment State',
                                        help="Assessment State")
    property_id = fields.Many2one('building', "ERF Number")
    address = fields.Char(string="Postal Address", help="Address")
    nationality = fields.Char(string="Nationality",help="Enter the Nationality")
    passport_no = fields.Char(string="Identity Number /Passport No",help="Enter the identity/passport no",required=1)
    dob = fields.Char(string="Date of Birth",help="Enter the date if birth")
    race = fields.Char(string="Race",help="Enter the Race")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])
    user_id = fields.Many2one('res.users', string="Assignee",
                              domain = lambda self: [
                                  ('groups_id', 'in', self.env.ref('client_enquiry.group_cbo').id)])
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'),
                                               ('company', 'Company')],
                                    default='person')
    contact_person_id = fields.Many2one('res.partner', string='Contact Person Surname')
    contact_person_first_name = fields.Char(string='Trading Name')
    date_established = fields.Date(string='Date Established',help="Enter the date of establishment")
    vat_no = fields.Char(string='Vat No',help="Enter the Vat No")
    type_of_business = fields.Char(string='Type of Business',help="Enter the type of business")
    tax_no = fields.Char(string='SA Income Tax No.',help="Enter the Income Tax No")
    country_reg = fields.Char(string='Country where Registered',help="Enter the country where registered")
    first_name_title = fields.Many2one('res.partner.title', string='Title')
    attachment_ids = fields.Many2many('ir.attachment', string="GIS Report")
    enquiry_folder_id = fields.Many2one('documents.folder', string='Supporting documents')
    upload_document_report_ids = fields.One2many("upload.property.report", 'upload_document_id',string="Upload Document")
    upload_supporting_document_report_ids = fields.One2many("enquiry.assessment", 'upload_supporting_document_id',string="Upload Document")

    # SLA
    last_stage_updated = fields.Datetime('Last Stage Updated', readonly=True)
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

    circulation_id = fields.Many2one('circulation.comments',  copy=False,
                                     string="Circulation Comments",
                                     tracking=True)

    transaction_id = fields.Many2one('client.transaction', string="Transaction", copy=False,
                                     tracking=True)
    subject = fields.Char('Subject')
    description = fields.Char('Description')
    valuation_id = fields.Many2one('assessment.valuation',  copy=False,string="Valuation")
    eac_id = fields.Many2one('eac.process', string="EAC Process", copy=False)

    @api.model
    def _default_team_id(self):

        details=self.env['helpdesk.team'].search([('name', '=', 'Walk-in')])
        return details

    @api.onchange('attachment_ids')
    def _onchange_attachment_ids(self):
        # folder = self.env['documents.folder'].browse(document_enquiry_general_enquiry)
        folder = self.env.ref('document_update.document_enquiry_general_enquiry')

        for rec in self.attachment_ids:
            existing_document = self.env['documents.document'].sudo().search([
                ('attachment_id', '=', rec._origin.id),
                ('folder_id', '=', folder.id),
                ('name', '=', rec.name)
            ])

            if not existing_document:
                document = self.env['documents.document'].sudo().create({
                    'name': rec.name,
                    'attachment_id': rec._origin.id,
                    'folder_id': folder.id
                })

    def action_reset_to_draft_ownership(self):
        self.state = 'draft'

    def action_button_doc_view(self):
        folder = self.env.ref('document_update.document_enquiry_general_enquiry')
        return {
            'name': 'Document',
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'kanban',
             'target': 'current',
            'context': "{'searchpanel_default_folder_id': %s}" % folder.id
        }

    def action_circulation_comment(self):
        circulation_id = self.env['circulation.comments'].create({
            'enquiry_id': self.id,
            'assessment_id': self.assessment_id.id,
            'property_id': self.property_id.id,
            'address': self.property_id.address,
            'jmc_number': self.property_id.jmc_number,
            'township': self.property_id.township,
            'stand_number': self.property_id.stand_number,
            'zoning_id': self.property_id.zoning_id.id,
        })
        self.circulation_id = circulation_id.id
        self.state = 'circulation_comments'

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
                'view_mode': 'tree,form',
                'domain': [('id', 'in', valuation.ids)],
            })
        return action

    def action_reset_to_draft(self):
        self.state = 'draft'

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
                'view_mode': 'tree,form',
                'domain': [('id', 'in', valuation.ids)],
            })
        return action

    def action_view_eac(self):
        """View assessment valuation"""
        valuation = self.eac_id
        action = {
            'name': _('EAC Process'),
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
                'view_mode': 'tree,form',
                'domain': [('id', 'in', valuation.ids)],
            })
        return action

    @api.model
    def create(self, values):
        """Method for generating sequence"""
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code(
                'client.enquiry') or _('New')
        res = super(ClientEnquiry, self).create(values)
        res.state = 'draft'
        res.last_stage_updated = fields.Datetime.now()
        policy = self.env.ref('client_enquiry.one_day_for_submit')
        policy_status = self.env['client.enquiry.sla.policy.status'].create({
            'enquiry_id': res.id,
            'name': policy.name,
            'policy_id': policy.id
        })
        res.sla_policy_ids = [(4, policy_status.id)]
        # users = self.env.ref(
        #     'client_enquiry.group_cbo').users
        # for user in users:
        #     activity = self.env['mail.activity'].create({
        #         'display_name': 'New Enquiry',
        #         'summary': 'Please check and update it',
        #         'date_deadline': fields.Date.add(fields.Date.today(), days=1),
        #         'user_id': user.id,
        #         'res_id': res.id,
        #         'res_model_id': self.env.ref(
        #             'client_enquiry.model_client_enquiry').id,
        #         'activity_type_id': self.env.ref(
        #             'mail.mail_activity_data_todo').id
        #     })
        return res


    def action_create_assessment(self):
        """Method for creating assessment"""
        if not self.user_id:
            raise UserError(_('This enquiry have no assignee'))
        if self.env.user != self.user_id:
            raise UserError(_('You have no access to request the assessment'))
        else:
            asset = self.env.ref('client_enquiry.group_asset_evaluator').users
            assessment = self.env['enquiry.assessment'].sudo().create({
                'enquiry_id': self.id,
                'partner_id': self.partner_id.id,
                'jmc_number': self.asset_number,
                'stand_number': self.stand_number,
                'property_id': self.property_id.id,
                'first_name':self.first_name,
                'zoning':self.zoning,
                'title':self.title.name,
                'cell_phone':self.cell_phone,
                'email':self.email,
                'enquiry_name_id': self.partner_id.id,
                'user_domain_ids': asset.ids,
                'type': self.type,
                'land_type': self.church_shop,
                'upload_report_document_ids': self.attachment_ids

                # 'upload_report_document_ids': self._context['upload_report_document_ids']
            })
            self.assessment_id = assessment.id
            self.state = 'assessment'
            mail_template = self.env.ref(
                'client_enquiry.email_template_enquiry_assessment_created')
            recipient_ids = self.env.ref('client_enquiry.group_asset_evaluator').users
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_template.send_mail(self.id, force_send=True,
                                    email_values=email_values)
            if self.env.user in self.env.ref('client_enquiry.group_asset_evaluator').users:
                action = {
                    'name': _('Assessment'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'enquiry.assessment',
                    'context': {'create': False},
                    'view_mode': 'form',
                    'res_id': assessment.id,
                }
                return {
                    'name': _('Assessment'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'enquiry.assessment',
                    'context': {'create': False},
                    'view_mode': 'form',
                    'res_id': assessment.id,
                    'params': {
                        'type': 'success',
                        'message': _("Connection successfully established"),
                        'next': {
                            'type': 'ir.actions.client',
                            'tag': 'reload_context',
                        },
                    }
                }
            if self.env.user in self.env.ref('client_enquiry.group_cbo').users:
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Created the assessment',
                        'type': 'rainbow_man',
                    }
                }

    def action_view_assessment(self):
        """Method for view assessment"""
        if not self.property_id:
            raise UserError(_('No property attach to this enquiry'))
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
                'view_mode': 'tree,form',
                'domain': [('id', 'in', assessment.ids)],
            })
        return action

    def action_view_land_regularization(self):
        """Method for view Land Regularization"""
        land_regularisation = self.land_regularisation_id
        action = {
            'name': _('Land Regularization'),
            'type': 'ir.actions.act_window',
            'res_model': 'land.regularization',
            'context': {'create': False},
        }
        if len(land_regularisation) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': land_regularisation.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', land_regularisation.ids)],
            })
        return action

    def action_view_enquiry(self):
        """View enquiry from kanban card"""
        return {
            'name': self.name,
            'view_mode': 'form',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
        }

    def unlink(self):
        """To delete the draft stage enquiry"""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Can't delete an enquiry in this state. "
                                  "We can only delete draft state record."))
        return super().unlink()

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """Onchange the property id it will change some fields vales"""
        if self.property_id:
            self.region_id = self.property_id.region_id.id
            self.asset_number = self.property_id.jmc_number
            self.stage = self.property_id.state
            self.stand_number = self.property_id.stand_number
            # self.zoning = self.property_id.zoning_id.name
            self.township = self.property_id.address
            self.size = self.property_id.building_area
            self.address = self.property_id.address

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Onchange the customer details, it will auto-populate the
         values in the customer part"""
        self.first_name = self.partner_id.first_name
        self.surname = self.partner_id.name
        self.cell_phone = self.partner_id.mobile if self.partner_id.mobile else self.partner_id.phone
        self.email = self.partner_id.email
        self.title = self.partner_id.title.id

    @api.onchange('company_type')
    def _onchange_company_type(self):
        """Onchange the company type change the email fields values"""
        self.email = ""
        if self.company_type == 'person':
            self.email = self.partner_id.email
        if self.company_type == 'company':
            self.email = self.contact_person_id.email

    @api.onchange('contact_person_id')
    def _onchange_contact_person_id(self):
        """Onchange the contact person"""
        self.contact_person_first_name = self.contact_person_id.first_name
        self.first_name_title = self.contact_person_id.title.id
        self.email = self.contact_person_id.email

    def action_assigne_to_me(self):
        """Method for assign the enquiry to the users."""
        self.user_id = self.env.user.id

    def action_submit(self):
        """Method for submit"""
        if self.stage != 'free':
            raise ValidationError(_("Property is not available"))
        if not self.property_id:
            raise UserError(_("Please add the property"))
        if self.entire_property == 'no':
            if self.size == 0.00:
                raise UserError(_('Please add the size'))
        if not self.attachment_ids:
            raise UserError(_('Please add the documents'))
        # activites = self.env['mail.activity'].search([('res_id', '=', self.id),
        #             ('res_model_id', '=', self.env.ref('client_enquiry.model_client_enquiry').id),
        #             ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id),
        #             ('display_name', '=', 'New Enquiry')])
        # for activity in activites:
        #     if activity.user_id.id == self.env.uid:
        #         activity._action_done()
        #     else:
        #         activity.unlink()
        polices = self.env['client.enquiry.sla.policy.status'].search([
            ('enquiry_id', '=', self.id),
            ('status', '=', 'ongoing')
        ])
        for pol in polices:
            pol.reached_datetime = fields.Datetime.now()
        policy = self.env.ref('client_enquiry.two_days_for_document_upload')
        policy_status = self.env['client.enquiry.sla.policy.status'].create({
            'enquiry_id': self.id,
            'name': policy.name,
            'policy_id': policy.id
        })
        self.sla_policy_ids = [(4, policy_status.id)]
        self.state = 'submit'
        mail_template = self.env.ref(
            'client_enquiry.email_template_enquiry_submit')
        recipient_ids = self.env.ref(
            'client_enquiry.group_cbo').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True, email_values=email_values)
        mail_template = self.env.ref(
            'client_enquiry.email_template_enquiry_submitted')

        mail_template.send_mail(self.id, force_send=True)

    def write(self, vals):
        send = False
        state = ""
        assessment = self.assessment_id
        before_doc = self.attachment_ids

        if vals.get('user_id'):
            send = True
        if vals.get('state'):
            state = vals.get('state')
        if vals.get('assessment_id'):
            assessment = vals.get('assessment_id')

        res = super(ClientEnquiry, self).write(vals)

        after_doc = self.attachment_ids

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

        if state:
            self.last_stage_updated = fields.Datetime.now()
        if state == 'assessment':
            if not assessment:
                raise UserError(_("Please Create the assessment"))
        if send:
            mail_template = self.env.ref(
                'client_enquiry.email_template_enquiry_assigned')
            mail_template.send_mail(self.id, force_send=True)
        # Commeted this for solve the popup
        # if self.cell_phone:
        #     pattern = re.compile(r'^\0\d{9}$|^0\d{9}$')
        #     if not re.match(pattern, self.cell_phone):
        #         raise UserError(_('Please add the correct cellphone number'))
        # if self.telephone_numbers:
        #     pattern = re.compile(r'^\0\d{9}$|^0\d{9}$')
        #     if not re.match(pattern, self.telephone_numbers):
        #         raise UserError(_('Please add the correct business'
        #                           ' telephone number'))
        # if self.mobile:
        #     pattern = re.compile(r'^\0\d{9}$|^0\d{9}$')
        #     if not re.match(pattern, self.mobile):
        #         raise UserError(_('Please add the correct business mobile '
        #                           'phone number'))
        return res

    def get_list_url(self):
        """Returns the url for the list view"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,'web#id=%s&model=client.enquiry&view_type=form' % self.id)
        return Urls

    def get_list_assessment_url(self):
        """Return Assessment URL for the list view"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=enquiry.assessment&view_type=form' % self.assessment_id.id)
        return Urls

    def action_view_valuation(self):
        """View assessment valuation"""
        valuation = self.valuation_id
        action = {
            'name': _('Valuation'),
            'type': 'ir.actions.act_window',
            'res_model': 'assessment.valuation',
            'context': {'create': False},
        }
        if len(valuation) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': valuation.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', valuation.ids)],
            })
        return action

    def action_view_property(self):
        """View assessment valuation"""
        valuation = self.property_id
        action = {
            'name': _('Property'),
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
                'view_mode': 'tree,form',
                'domain': [('id', 'in', valuation.ids)],
            })
        return action

    def action_send_cancelled_mail(self):
        """To notify the users about the assessment is cancelled"""
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup(
                'client_enquiry.email_template_enquiry_cancelled')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                'mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': self._name,
            'active_model': self._name,
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': self.assessment_id.attachment_ids.ids if self.assessment_id and self.assessment_id.attachment_ids else None,
            'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
            'force_email': True,
            'mark_assessment_as_sent': True,
        })

        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model',
            'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(
                ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_lang([ctx['default_res_id']])[
                    ctx['default_res_id']]
        self = self.with_context(lang=lang)

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_send_assessment_started_mail(self):
        """To notify the users about the assessment is cancelled"""
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.state == 'assessment':

                template_id = ir_model_data._xmlid_lookup(
                    'client_enquiry.email_template_client_enquiry_supported')[2]
            if self.state == 'completed':
                template_id = ir_model_data._xmlid_lookup(
                    'client_enquiry.email_template_client_enquiry_assessment_completed')[2]

        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                'mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': self._name,
            'active_model': self._name,
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': self.assessment_id.attachment_ids.ids if self.assessment_id and self.assessment_id.attachment_ids else None,
            'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
            'force_email': True,
            'mark_assessment_as_sent': True,
        })

        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model',
            'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(
                ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_lang([ctx['default_res_id']])[
                    ctx['default_res_id']]
        self = self.with_context(lang=lang)

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    @api.depends('sla_policy_ids.deadline', 'sla_policy_ids.reached_datetime', 'sla_policy_ids')
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
