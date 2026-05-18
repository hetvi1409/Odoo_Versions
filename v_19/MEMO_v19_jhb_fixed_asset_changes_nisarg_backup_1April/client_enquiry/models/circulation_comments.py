from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class CirculationComments(models.Model):
    """Circulation Comments"""
    _name = 'circulation.comments'
    _description = "Circulation Comments"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", copy=False )
    enquiry_id = fields.Many2one('client.enquiry', string="Enquiry")
    assessment_id = fields.Many2one('enquiry.assessment', string="Assessment")

    user_id = fields.Many2one('res.users', string="Assignee",
                              domain = lambda self: [
                                  ('id', 'in', self.env.ref('base.group_user').user_ids.ids)])

    property_id = fields.Many2one('building', string="Property", required=True)
    address = fields.Char(string="Address")
    jmc_number = fields.Char(string="JMC Number")
    township = fields.Char(string="Township Name")
    stand_number = fields.Char(string="Stand Number")
    # zoning_id = fields.Many2one(string='Zoning',
    #                             related='property_id.zoning_id')
    proposal = fields.Char(string="Proposal", required=False)
    attachment_ids = fields.Many2many('ir.attachment', string="Supporting Documents")
    state = fields.Selection([('draft', 'Draft'), ('send', 'Send for Comments'),
                              ('objection', 'Objection'),
                              ('create_ptob', 'Create PTOB'),
                              ('valuation', 'Valuation'),
                              ('terminate', 'Terminated'),],
                             default="draft")
    last_stage_updated = fields.Datetime('Last Stage Updated', readonly=True)
    partner_ids = fields.Many2many('res.partner', string="Partner")
    line_ids = fields.One2many('circulation.comment.line', 'circulation_id', string="Comment")
    objection = fields.Selection([('yes', 'Yes'), ('no', 'No')], copy=False)
    is_municipal_department = fields.Selection([('yes', 'Municipal'), ('no', 'Private')], string='Municipal/Private Land', copy=False)
    is_negotiation = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Is There Any Negotiation', copy=False)

    valuation_id = fields.Many2one('assessment.valuation', string="Valuation")
    transaction_id = fields.Many2one('client.transaction', string="Transaction")

    def send_compile_report(self):
        """Methode to send the compile reports to all users"""
        # Commented this to sset the workflow
        self.ensure_one()
        if not self.user_id:
            raise ValidationError(_('Please add the assignee'))
        if self.user_id != self.env.user:
            raise UserError(_('You have no access to Send the documents'))

        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref('client_enquiry.email_template_circulation_comments_report')
        except ValueError:
            template_id = False
        try:
            compose_form_id = self.env['ir.model.data']._xmlid_to_res_id('mail.email_compose_message_wizard_form')
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': self._name,
            'active_model': self._name,
            # 'active_id': self.ids[0],
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
            'force_email': True,
            'mark_assessment_as_sent': True,
        })

        lang = self.env.context.get('lang')
        # if {'default_template_id', 'default_model',
        #     'default_res_id'} <= ctx.keys():
        #     template = self.env['mail.template'].browse(
        #         ctx['default_template_id'])
        #     if template and template.lang:
        #         lang = template._render_lang([ctx['default_res_id']])[
        #             ctx['default_res_id']]
        # self = self.with_context(lang=lang)

        recipient_ids = self.property_id.sudo().region_id.user_ids
        partner = []
        for recipient in recipient_ids:
            partner.append(recipient.partner_id.id)

        # partner = self.env['res.partner'].browse(recipient_ids)
        ctx.update({
            'default_partner_ids': partner,
            'default_attachment_ids': self.attachment_ids.ids
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

    def action_button_doc_view(self):
        folder = self.env.ref('document_update.portfolio_city_interventions_circulation')
        return {
            'name': 'Document',
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'kanban',
            'target': 'current',
            'context': "{'searchpanel_default_folder_id': %s}" % folder.id
        }

    @api.onchange('attachment_ids')
    def _onchange_attachment_ids(self):
        # folder = self.env['documents.document'].browse(document_enquiry_general_enquiry)
        folder = self.env.ref('document_update.portfolio_city_interventions_circulation')

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


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'circulation.comments'
            vals['name'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(CirculationComments, self).create(vals_list)

        res.last_stage_updated = fields.Datetime.now()

        return res

    @api.onchange('jmc_number')
    def _onchange_jmc_number(self):
        if self.jmc_number != self.property_id.jmc_number:
            raise ValidationError(_("The JMC number doesn't match with ERF number"))

    def write(self, vals):
        send = False
        if vals.get('user_id'):
            send = True
        before_doc = self.attachment_ids
        res = super(CirculationComments, self).write(vals)
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
        if send:
            mail_template = self.env.ref(
                'client_enquiry.email_template_circulation_comments_assigned')
            mail_template.send_mail(self.id, force_send=True)
        return res

    @api.onchange('property_id')
    def onchange_property(self):
        """Onchange property Details"""
        self.address = self.property_id.address
        self.jmc_number = self.property_id.jmc_number
        self.township = self.property_id.township
        self.stand_number = self.property_id.stand_number
        # self.zoning_id = self.property_id.zoning_id.id

    def action_move_to_ptob(self):
        """Move to ptob"""
        self.state = 'create_ptob'
        self.sudo().message_post(body="Need to do PTOB")

    def action_move_to_request_valuation(self):
        """Move to ptob"""
        self.state = 'valuation'
        self.sudo().message_post(body="Need to do Valuation")

    def action_negotiation(self):
        if self.is_negotiation == 'yes':
            self.state = 'send'
            self.is_negotiation = False
            self.is_municipal_department = False
            self.objection = False
        elif self.is_negotiation == 'no':

            mail_template = self.env.ref(
                'client_enquiry.email_template_circulation_comments_objection')
            recipient_ids = self.user_id.partner_id
            recipient_ids += self.enquiry_id.partner_id
            recipient_ids += self.assessment_id.enquiry_name_id
            email_values = {
                'recipient_ids': [(6, 0, recipient_ids.ids)]
            }
            mail_template.send_mail(self.id, force_send=True,
                                    email_values=email_values)
            self.state = 'terminate'

    def action_create_valuation(self):
        """Create Valuation"""
        valuation = self.env['assessment.valuation'].create({
            'property_id': self.property_id.id,
            'assessment_id': self.assessment_id.id,
            'enquiry_id': self.enquiry_id.id,
            'circulation_id': self.id,
            'property_number': self.property_id.code,
            'size': self.property_id.building_area,
            'jmc_number': self.property_id.jmc_number,
            'address': self.property_id.address,
            'attachment_ids': self.attachment_ids
        })
        self.state = 'valuation'
        self.valuation_id = valuation.id
        if self.enquiry_id:
            self.enquiry_id.valuation_id = valuation.id
            self.enquiry_id.state = 'valuation'

    def action_objection(self):
        """Method for action objection"""
        if self.line_ids:
            return {
                'name': _('Review'),
                'view_mode': 'form',
                'res_model': 'assessment.objection',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_circulation_id': self.id,
                'default_assessment_id': self.assessment_id.id
                }
            }
        else:
            raise UserError(_("Please add Circulation Comments"))

    def get_list_url(self):
        """Returns the url for the list view"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,'web#id=%s&model=circulation.comments&view_type=form' % self.id)
        return Urls

    def action_assigne_to_me(self):
        """Method for assign the enquiry to the users."""
        self.user_id = self.env.user.id

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
            'name': _('Enquiry'),
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


class CirculationCommentsLines(models.Model):
    """Circulation comments Lines"""
    _name = 'circulation.comment.line'

    circulation_id = fields.Many2one('circulation.comments')
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Documents", help="Documents")
    date = fields.Datetime(string="Date", default=fields.Datetime.now())
    comments = fields.Char(string="Comments")
    user_id = fields.Many2one('res.users', string="User",
                              default=lambda self: self.env.user)
    author_id = fields.Many2one('res.partner', string="User",)
    department_id = fields.Many2many('hr.department', string="Department")
    group_ids = fields.Many2many('res.groups')
    name = fields.Html(string="Comments")
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)

