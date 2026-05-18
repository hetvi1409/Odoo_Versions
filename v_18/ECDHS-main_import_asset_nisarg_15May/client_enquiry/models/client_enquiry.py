import re

from werkzeug import urls

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
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
                                 string='Surname', tracking=True)
    team_id = fields.Many2one('helpdesk.team', string='Channel',
                              help='Channel details',
                              domain="[('is_enquiry', '=', True)]", required=True)
    date = fields.Datetime(string="Date", default=fields.Datetime.now(), help="Date")
    asset_number = fields.Char(string="JMC number", help="JMC asset number")
    stand_number = fields.Char(string="Stand Number/ Portion number")
    # region_id = fields.Many2one('regions', string="Region")
    township = fields.Char(string="Township /Farm Name")
    entire_property = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                       string="Relate to entire property",
                                       help="Does the enquiry relate to "
                                            "the entire property or a "
                                            "part thereof?")
    size = fields.Float(string="Size of property")
    type = fields.Selection([('social_lease', 'Social Lease/ Sale'),
                             ('commercial_lease',
                              'Commercial Lease/Sale (including residential)'),
                             ('registration',
                              'Registration/ cancellation of a servitude'),
                             ('land', 'Land Regularisation Matter'),
                             ('road', 'Road reserve'),
                             ('user_agreement', 'User Agreement'),
                             ('encroachment', 'Encroachment / Parking'),
                             ('outdoor', 'Outdoor Advertising')],
                            string='Type of enquiry')
    proposed_use = fields.Char(string="Proposed use of the property")
    surname = fields.Char(string="Surname")
    # title = fields.Selection([('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'),
    #                           ('Miss', 'Miss')], string="Title")
    title = fields.Many2one('res.partner.title', string='Title')

    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0', tracking=True)
    first_name = fields.Char(string="First Name")
    cell_phone = fields.Char(string="Cell")
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
    telephone_numbers = fields.Char(string='Business Telephone Numbers')
    mobile = fields.Char(string='Mobile Number')
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted to CBO department'),
                              ('assessment', 'Assessment Started'),
                              ('ongoing', 'Assessment ongoing'),
                              ('completed', 'Assessment Completed'),
                              ('cancelled', 'Assessment Cancelled')],
                             default='draft', string="Status")
    assessment_id = fields.Many2one('enquiry.assessment',
                                    string='Assessment', help="Assessment")
    assessment_state = fields.Selection(related="assessment_id.state",
                                        string='Assessment State',
                                        help="Assessment State")
    # property_id = fields.Many2one('building', "Property Name")
    address = fields.Char(string="Address", help="Address")
    user_id = fields.Many2one('res.users', string="Assignee",
                              domain = lambda self: [
        ('groups_id', 'in', self.env.ref('client_enquiry.group_property_manager').id)])
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'),
                                               ('company', 'Company')],
                                    default='person')
    contact_person_id = fields.Many2one('res.partner', string='Contact Person Surname')
    contact_person_first_name = fields.Char(string='First Name')
    first_name_title = fields.Many2one('res.partner.title', string='Title')
    attachment_ids = fields.Many2many('ir.attachment', string="Supporting Documents")
    # enquiry_folder_id = fields.Many2one('documents.folder', string='Supporting documents')
    # SLA
    last_stage_updated = fields.Datetime('Last Stage Updated',)
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

    # rental_id = fields.Many2one('rental.contract', readonly=True, string="Rental contract")

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
        users = self.env.ref(
            'client_enquiry.group_cbo').users
        for user in users:
            activity = self.env['mail.activity'].create({
                'display_name': 'New Enquiry',
                'summary': 'Please check and update it',
                'date_deadline': fields.Date.add(fields.Date.today(), days=1),
                'user_id': user.id,
                'res_id': res.id,
                'res_model_id': self.env.ref(
                    'client_enquiry.model_client_enquiry').id,
                'activity_type_id': self.env.ref(
                    'mail.mail_activity_data_todo').id
            })
        return res

    def action_view_rental(self):
        """to view the rental contracts"""
        return {
            'res_model': 'rental.contract',
            'type': 'ir.actions.act_window',
            'name': _("Lease Contract"),
            'view_mode': 'form',
            # 'res_id': self.rental_id.id
        }

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
                'user_domain_ids': asset.ids
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

    def action_check_ownership(self):
        """Check if the property is for the jpc or not"""
        if not self.user_id:
            raise UserError(_('This enquiry have no assignee'))
        return {
            'name': _('Check the property'),
            'view_mode': 'form',
            'res_model': 'check.property',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_enquiry_id': self.id,
            }
        }

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
            # self.region_id = self.property_id.region_id.id
            self.asset_number = self.property_id.jmc_number
            self.stand_number = self.property_id.stand_number
            self.township = self.property_id.address
            # self.size = self.property_id.building_area
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
        if not self.property_id:
            raise UserError(_("Please add the property"))
        if self.entire_property == 'no':
            if self.size == 0.00:
                raise UserError(_('Please add the size'))
        activites = self.env['mail.activity'].search([('res_id', '=', self.id),
                    ('res_model_id', '=', self.env.ref('client_enquiry.model_client_enquiry').id),
                    ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id),
                    ('display_name', '=', 'New Enquiry')])
        for activity in activites:
            print(activity)
            if activity.user_id.id == self.env.uid:
                activity._action_done()
            else:
                activity.unlink()
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
        if vals.get('user_id'):
            send = True
        if vals.get('state'):
            state = vals.get('state')
        if vals.get('assessment_id'):
            assessment = vals.get('assessment_id')
        res = super(ClientEnquiry, self).write(vals)
        if state:
            self.last_stage_updated = fields.Datetime.now()
        if state == 'assessment':
            if not assessment:
                raise UserError(_("Please Create the assessment"))
        if send:
            mail_template = self.env.ref(
                'client_enquiry.email_template_enquiry_assigned')
            mail_template.send_mail(self.id, force_send=True)
        if self.cell_phone:
            pattern = re.compile(r'^\0\d{9}$|^0\d{9}$')
            if not re.match(pattern, self.cell_phone):
                raise UserError(_('Please add the correct cellphone number'))
        if self.telephone_numbers:
            pattern = re.compile(r'^\0\d{9}$|^0\d{9}$')
            if not re.match(pattern, self.telephone_numbers):
                raise UserError(_('Please add the correct business'
                                  ' telephone number'))
        if self.mobile:
            pattern = re.compile(r'^\0\d{9}$|^0\d{9}$')
            if not re.match(pattern, self.mobile):
                raise UserError(_('Please add the correct business mobile '
                                  'phone number'))
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


    def action_open_document(self):
        """Method to open the council documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self._name),
                       ('res_id', 'in', self.ids),],
            'view_mode': 'kanban,tree,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.enquiry_folder_id.id
            }
        }

    @api.depends('sla_policy_ids.deadline', 'sla_policy_ids.reached_datetime', 'sla_policy_ids')
    def _compute_sla_reached_late(self):
        """ Required to do it in SQL since we need to compare 2 columns value """
        for rec in self:
            policy_status = rec.sla_policy_ids.mapped('status')
            print(policy_status, 'status')
            if 'failed' in policy_status:
                rec.sla_reached_late = True
            else:
                rec.sla_reached_late = False

    @api.depends('sla_policy_ids.deadline', 'sla_policy_ids.reached_datetime')
    def _compute_sla_reached(self):
        for rec in self:
            policy_status = list(set(rec.sla_policy_ids.mapped('status')))
            print(policy_status, 'status')
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
