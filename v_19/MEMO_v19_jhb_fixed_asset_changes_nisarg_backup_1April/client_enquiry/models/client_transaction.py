from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import Command


class ClientTransaction(models.Model):
    """Client transaction"""
    _name = 'client.transaction'
    _description = "Client Transaction"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Client Transaction", copy=False)
    enquiry_id = fields.Many2one('client.enquiry', string="Enquiry")
    assessment_id = fields.Many2one('enquiry.assessment', string="Assessment")

    user_id = fields.Many2one('res.users', string="Assignee", tracking=True,
                              domain=lambda self: [
                                  ('group_ids', 'in',
                                   self.env.ref('base.group_user').id)])

    property_id = fields.Many2one('building', string="Property", required=True)
    valuation_id = fields.Many2one('assessment.valuation', string="Valuation")
    address = fields.Char(string="Address")
    jmc_number = fields.Char(string="JMC Number")
    stand_number = fields.Char(string="Stand Number")
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submit'),
                              ('approve', 'Approve'),
                              ('send_to', 'Send for Signature'),
                              ('signed', 'Signed'),
                              ('to_do_section_79', 'To Do Section 79'),
                              ('eac', 'EAC Process'),
                              ('bid', 'Develop Bid'),
                              ('terminated', 'Terminated'),
                              ('reject', 'Rejected'),
                              ], default='draft', tracking=True)
    valuation_attachment_ids = fields.Many2many('ir.attachment', string="Valuation Documents")
    circulation_id = fields.Many2one('circulation.comments', string="Circulation Comments")
    transaction_type = fields.Selection([('social_lease', 'Social Lease/ Sale'),
                             ('commercial_lease',
                              'Commercial Lease/Sale (including residential)'),
                             ('registration',
                              'Registration/ cancellation of a servitude'),
                             ('land', 'Land Regularisation Matter'),
                             ('road', 'Road reserve'),
                             ('user_agreement', 'User Agreement'),
                             ('ptob', 'PTOB'),
                             ('lanes', 'Sanatory Lanes'),
                             ('outdoor', 'Outdoor Advertising'),
                            ('other', 'Other')], tracking=True, string="Property Type")
    transaction_attachment_ids = fields.Many2many('ir.attachment', 'transaction_attachment_rel', string="Transaction Documents")
    continue_process = fields.Selection([('yes', 'Yes'), ('no', 'No')], tracking=True,
                                        string="The customer will continue the process")
    board_committee_id = fields.Many2one('calendar.event', string="Transaction/Board Commitee Meeting")
    board_committee_attachment_ids = fields.Many2many('ir.attachment',
                                                     'board_committee_attachment_rel',
                                                     string="Reports")
    emt_committee_id = fields.Many2one('calendar.event', string="Technical Cluster/ EMT Committee")
    emt_committee_attachment_ids = fields.Many2many('ir.attachment',
                                                     'emt_committee_attachment_rel',
                                                     string="Reports")
    section_79_committee_id = fields.Many2one('calendar.event', string="Section 79 Committee")
    section_79_committee_attachment_ids = fields.Many2many('ir.attachment',
                                                     'section_79_committee_attachment_rel',
                                                     string="Reports")
    mayoral_committee_id = fields.Many2one('calendar.event', string="Sub Mayoral/Mayoral Committee")
    mayoral_committee_attachment_ids = fields.Many2many('ir.attachment',
                                                     'mayoral_committee_attachment_rel',
                                                     string="Reports")
    last_stage_updated = fields.Datetime('Last Stage Updated', readonly=True)
    council_committee_id = fields.Many2one('calendar.event', string="Council Committee")
    council_committee_attachment_ids = fields.Many2many('ir.attachment',
                                                     'council_committee_attachment_rel',
                                                     string="Reports")
    endorse_comments = fields.Char(string="Endorse Comments", readonly=True)
    bid_comments = fields.Char(string="Sepc Development Comments", readonly=True)
    eac_id = fields.Many2one('eac.process', string="EAC Process", copy=False)
    amount = fields.Float(string="Amount")
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')
    receiver_user_id = fields.Many2one('res.users', string='Receiver User',
                                       domain=lambda
                                           self: self._get_general_manager_domain())

    @api.model
    def _get_general_manager_domain(self):
        group = self.env.ref('client_enquiry.group_general_manager')
        if group:
            user_ids = group.user_ids.ids
            return [('id', 'in', user_ids)]
        return []

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'client.transaction'
            vals['name'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
            vals['last_stage_updated'] = fields.Datetime.now()
        res = super(ClientTransaction, self).create(vals_list)

        return res


    @api.onchange('valuation_id')
    def _onchange_valuation(self):
        """Change of valuation"""
        self.property_id = self.valuation_id.property_id.id
        self.enquiry_id = self.valuation_id.enquiry_id.id
        self.assessment_id = self.valuation_id.assessment_id.id
        self.circulation_id = self.valuation_id.circulation_id.id
        self.address = self.valuation_id.address
        self.jmc_number = self.valuation_id.jmc_number
        # self.stand_number = self.valuation_id.stand_number

    @api.onchange('enquiry_id')
    def _onchange_enquiry_id(self):
        """Onchange enquiry"""
        if self.enquiry_id:
            self.transaction_type = self.enquiry_id.type

    def action_submit(self):
        """Submit Transaction"""
        if not self.transaction_type:
            raise UserError(_('Please add a transaction type'))
        if self.transaction_type == 'other':
            if not self.transaction_attachment_ids:
                raise UserError(_('Please add a transaction document'))
            mail_template = self.env.ref(
                'client_enquiry.email_template_transaction_send_to_sign_report')
            recipient_ids = self.user_id.partner_id
            email_values = {
                'recipient_ids': [(6, 0, recipient_ids.ids)],
                'attachment_ids': self.transaction_attachment_ids
            }
            mail_template.send_mail(self.id, force_send=True,
                                    email_values=email_values)
            self.state = 'submit'
        else:
            if not self.continue_process:
                raise UserError(_('The customer will continue the process'))
            if self.continue_process == 'yes':
                if not self.transaction_attachment_ids:
                    raise UserError(_('Please add a transaction document'))
                mail_template = self.env.ref(
                    'client_enquiry.email_template_transaction_send_to_sign_report')
                recipient_ids = self.user_id.partner_id
                email_values = {
                    'recipient_ids': [(6, 0, recipient_ids.ids)],
                'attachment_ids': self.transaction_attachment_ids
                }
                mail_template.send_mail(self.id, force_send=True,
                                        email_values=email_values)
                self.state = 'submit'
            if self.continue_process == 'no':
                self.state = 'terminated'
                self.sudo().message_post(body="The process was terminated. ")

    def action_send_for_signing(self):
        self.ensure_one()
        if not self.transaction_attachment_ids:
            raise UserError(
                "Please upload at least one PDF file before sending for signing.")
        attachments = self.transaction_attachment_ids.filtered(
            lambda a: a.mimetype == 'application/pdf'
        )
        # document = self.env['documents.document'].create({
        #     'name': attachment.name,
        #     'attachment_id': attachment.id,
        #     'res_model': self._name,
        #     'res_id': self.id,
        # })
        sign_template = self.env['sign.template'].create({
            'document_ids': [
                Command.create({
                    'attachment_id': attachment.id,
                })
                for attachment in attachments
            ],
            'name': self.name,
        })
        print(sign_template, 'sign_template')
        group_users = self.receiver_user_id
        for document in sign_template.document_ids:
            sign_item = self.env['sign.item'].create([{
                'type_id': self.env.ref('sign.sign_item_type_signature').id,
                'required': True,
                'responsible_id': self.env.ref('sign.sign_item_role_default').id,
                'page': 1,
                'posX': 0.85,
                'posY': 0.84,
                'document_id': document.id,
                'width': 0.10,
                'height': 0.05,
            }])
            sign_item = self.env['sign.item'].create([{
                'type_id': self.env.ref('sign.sign_item_type_initial').id,
                'required': True,
                'responsible_id': self.env.ref('sign.sign_item_role_default').id,
                'page': 1,
                'posX': 0.73,
                'posY': 0.86,
                'document_id': document.id,
                'width': 0.10,
                'height': 0.03,
            }])

        sign_request = self.env['sign.request'].create({
            'template_id': sign_template.id,
            'reference': self.name,
            'subject': 'Signature Request - ' + self.name,
            'request_item_ids': [(0, 0, {
                'partner_id': self.receiver_user_id.partner_id.id,
                'role_id': self.env.ref('sign.sign_item_role_default').id
            })]
        })
        self.sign_request_id = sign_request.id
        self.state = 'send_to'

    def sign_the_report(self):
        """Signed the report"""
        self.state = 'signed'
        self.sudo().message_post(body="Signed the report")

    def action_approve(self):
        """Signed the report"""
        self.state = 'approve'
        self.sudo().message_post(body="Transaction is Approved")
        self.create_board_meeting()
        if self.enquiry_id:
            self.enquiry_id.state = 'public_participation'

    def action_refuse(self):
        """Signed the report"""
        self.state = 'reject'
        self.sudo().message_post(body="Transaction is rejected.")

    def action_accept(self):
        """Action Accept"""
        return {
            'name': _('Accept'),
            'view_mode': 'form',
            'res_model': 'assessment.accept',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_transaction_id': self.id,
                'default_assessment_id': self.assessment_id.id
            }
        }

    def action_approve_section_79(self):
        """Approve section 79"""
        return {
            'name': _('Spect Development'),
            'view_mode': 'form',
            'res_model': 'assessment.spec',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_transaction_id': self.id,
                'default_assessment_id': self.assessment_id.id
            }
        }

    def create_board_meeting(self):
        """Create a new board meeting"""
        board_committee_id = self.env['calendar.event'].create({
            'name': 'Transaction / Board Committee',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.board_committee_id = board_committee_id.id

    def create_emt_meeting(self):
        """Create a new board meeting"""
        emt_committee_id = self.env['calendar.event'].create({
            'name': 'Technical Cluster/ EMT Committee',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.emt_committee_id = emt_committee_id.id

    def create_section_79_meeting(self):
        """Create a new board meeting"""
        section_79_committee_id = self.env['calendar.event'].create({
            'name': 'Section Committee',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.section_79_committee_id = section_79_committee_id.id

    def create_mayoral_meeting(self):
        """Create a new board meeting"""
        mayoral_committee_id = self.env['calendar.event'].create({
            'name': 'Sub-Mayoral/Mayoral',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.mayoral_committee_id = mayoral_committee_id.id

    def create_council_meeting(self):
        """Create a new board meeting"""
        council_committee_id = self.env['calendar.event'].create({
            'name': 'Council',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.council_committee_id = council_committee_id.id

    def action_create_eac(self):
        """Create a EAC"""
        eac = self.env['eac.process'].create({
            'valuation_id': self.valuation_id.id,
            'property_id': self.property_id.id,
            'enquiry_id': self.enquiry_id.id,
            'assessment_id': self.assessment_id.id,
            'circulation_id': self.circulation_id.id,
            'transaction_id': self.id,
            'transaction_attachment_ids': self.transaction_attachment_ids,
            'address': self.address,
            'jmc_number': self.jmc_number,
            'stand_number': self.stand_number,
        })
        self.eac_id = eac.id
        if self.enquiry_id:
            self.enquiry_id.eac_id = eac.id


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
                'view_mode': 'list,form',
                'domain': [('id', 'in', valuation.ids)],
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
                'view_mode': 'list,form',
                'domain': [('id', 'in', valuation.ids)],
            })
        return action

    def action_view_emt_meeting(self):
        """View assessment valuation"""
        meeting = self.emt_committee_id
        action = {
            'name': _('Meeting'),
            'type': 'ir.actions.act_window',
            'res_model': meeting._name,
            'context': {'create': False},
            'view_mode': 'form',
            'target' : 'new',
            'res_id': meeting.id,
            }
        return action

    def action_view_board_meeting(self):
        """View assessment valuation"""
        meeting = self.board_committee_id
        action = {
            'name': _('Meeting'),
            'type': 'ir.actions.act_window',
            'res_model': meeting._name,
            'context': {'create': False},
            'view_mode': 'form',
            'target' : 'new',
            'res_id': meeting.id,
            }
        return action

    def action_view_section_79_meeting(self):
        """View assessment valuation"""
        meeting = self.section_79_committee_id
        action = {
            'name': _('Meeting'),
            'type': 'ir.actions.act_window',
            'res_model': meeting._name,
            'context': {'create': False},
            'view_mode': 'form',
            'target' : 'new',
            'res_id': meeting.id,
            }
        return action

    def action_view_mayoral_meeting(self):
        """View assessment valuation"""
        meeting = self.mayoral_committee_id
        action = {
            'name': _('Meeting'),
            'type': 'ir.actions.act_window',
            'res_model': meeting._name,
            'context': {'create': False},
            'view_mode': 'form',
            'target' : 'new',
            'res_id': meeting.id,
            }
        return action

    def action_view_council_meeting(self):
        """View assessment valuation"""
        meeting = self.council_committee_id
        action = {
            'name': _('Meeting'),
            'type': 'ir.actions.act_window',
            'res_model': meeting._name,
            'context': {'create': False},
            'view_mode': 'form',
            'target' : 'new',
            'res_id': meeting.id,
            }
        return action

    def get_list_url(self):
        """Returns the url for the list view"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        from werkzeug import urls
        Urls = urls.url_join(base_url,'web#id=%s&model=client.transaction&view_type=form' % self.id)
        return Urls

    def send_section_79_advert(self):
        """Section 79"""
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup(
                'client_enquiry.email_template_transaction_send_to_section_79')[2]
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
        partner = []
        ctx.update({
            'default_partner_ids': partner,
            'default_attachment_ids': self.transaction_attachment_ids.ids
        })
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

    def action_create_scm(self):
        """Create SCM"""
        return {
            'name': _('RFQ Memo'),
            'view_mode': 'form',
            'res_model': 'bsc.memo',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_transaction_id': self.id,
                'default_circulation_id': self.circulation_id.id,
                'default_enquiry_id': self.enquiry_id.id,
                'default_assessment_id': self.assessment_id.id,
                'default_property_id': self.property_id.id,
                'default_valuation_id': self.valuation_id.id,
                'default_total_amount': self.amount
            }
        }


class SignRequest(models.Model):
    _inherit = 'sign.request'

    def write(self, vals):
        res = super(SignRequest, self).write(vals)
        if 'state' in vals and vals['state'] == 'signed':
            # Find the related client.transaction record
            transaction = self.env['client.transaction'].search(
                [('sign_request_id', '=', self.id)], limit=1)
            if transaction:
                transaction.state = 'signed'
        return res
