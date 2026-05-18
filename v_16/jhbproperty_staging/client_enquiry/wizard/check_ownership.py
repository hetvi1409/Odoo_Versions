from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CheckOwnership(models.TransientModel):
    """Class for to check the ownership"""
    _name = 'check.ownership'
    _description = "Check ownership"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    assessment_id = fields.Many2one('enquiry.assessment')
    acquisition_id = fields.Many2one('property.acquisition')
    property_id = fields.Many2one('building')
    comments = fields.Html(string="Comments",help="Add the Comments")
    jmc_number = fields.Char( string='JMC number', help='JMC number')
    attachment_ids = fields.Many2many('ir.attachment', store=True,
                                      string="Assessment Report", required=True)
    attachment_image_ids = fields.Many2many('ir.attachment', relation="attachment_image_rel",
                                      string="Add Image", tracking=True)
    upload_document_name = fields.Char(string="Name")
    type = fields.Selection([('supported', 'Supported'), ('not_supported', 'Not Supported')], required=True, string="Assessment Result")
    land_type = fields.Selection([('church', 'Church'), ('shop','Shop')], string="Land Type")
    department_id = fields.Many2one('hr.department', string='Department')
    document_type = fields.Char(string='Document Type')
    church_const_doc = fields.Many2many('ir.attachment','church_const_attach_rel', string='Constitution')
    church_photo_doc = fields.Many2many('ir.attachment','church_photo_attach_rel', string='Photos')
    church_corner_doc = fields.Many2many('ir.attachment','church_corner_attach_rel', string='Cornerstone')
    church_bishop_doc = fields.Many2many('ir.attachment','church_bishop_attach_rel', string="Bishop's letter")
    shop_license_doc = fields.Many2many('ir.attachment','shop_license_attach_rel', string="License")
    shop_permit_doc = fields.Many2many('ir.attachment','shop_permit_attach_rel', string="Permit")
    shop_id_doc = fields.Many2many('ir.attachment','shop_id_attach_rel', string="ID")
    shop_death_doc = fields.Many2many('ir.attachment','shop_death_attach_rel', string="Death Certificate")
    shop_affidavit_doc = fields.Many2many('ir.attachment','shop_affidavit_attach_rel', string="Affidavit")

    def action_submit(self):
        # folder = self.env['documents.folder'].browse(document_enquiry_general_enquiry)
        folder = self.env.ref('__custom__.dd')

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

        """Submit the form"""
        # To add the documents into document module
        if not self.attachment_ids:
            raise UserError(_('Please attach the documents'))
        if self.assessment_id.enquiry_id:
            polices = self.env['client.enquiry.sla.policy.status'].search([
                ('enquiry_id', '=', self.assessment_id.sudo().enquiry_id.id),
                ('status', '=', 'ongoing')
            ])
            for pol in polices:
                pol.reached_datetime = fields.Datetime.now()
        if self.type == 'supported':
            policy = self.env.ref('client_enquiry.nine_months_for_document_upload')
            if self.assessment_id.enquiry_id:
                policy_status = self.env['client.enquiry.sla.policy.status'].create(
                    {
                        'enquiry_id': self.assessment_id.sudo().enquiry_id.id,
                        'name': policy.name,
                        'policy_id': policy.id
                    })
                self.assessment_id.sudo().enquiry_id.sla_policy_ids = [(4, policy_status.id)]
                self.assessment_id.sla_policy_ids = [(4, policy_status.id)]
            self.assessment_id.sudo().is_supported = 'supported'

            attachments = []
            documents = []
            for rec in self.attachment_ids:
                #     assessment_folder = self.env.ref('client_enquiry.document_enquiry')
                attachment = rec
                attachment.sudo().write({
                    'res_id': self.assessment_id.id,
                    'res_model': self.assessment_id._name
                })
                attachments.append(attachment.id)
            #     if self.assessment_id.property_id.sudo().region_id:
            #         region = self.env['documents.folder'].sudo().search([
            #             ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
            #             ('parent_folder_id', '=', assessment_folder.id)
            #         ])
            #         if not region:
            #             region = self.env['documents.folder'].sudo().create({
            #                 'name': self.assessment_id.property_id.sudo().region_id.name,
            #                 'parent_folder_id': assessment_folder.id
            #             })
            #     else:
            #         region = self.env['documents.folder'].sudo().search([
            #             ('name', '=', "Undefined Region"),
            #             ('parent_folder_id', '=', assessment_folder.id)
            #         ])
            #         if not region:
            #             region = self.env['documents.folder'].sudo().create({
            #                 'name': 'Undefined Region',
            #                 'parent_folder_id': assessment_folder.id
            #             })
            #     jmc = self.env['documents.folder'].sudo().search([
            #             ('name', '=', self.jmc_number),
            #             ('parent_folder_id', '=', region.id)
            #         ])
            #     if not jmc:
            #         jmc = self.env['documents.folder'].sudo().create({
            #             'name': self.jmc_number,
            #             'parent_folder_id': region.id,
            #         })
            #     enquiry_folder = self.env['documents.folder'].sudo().search([
            #             ('name', '=', self.assessment_id.name),
            #             ('parent_folder_id', '=', jmc.id)
            #         ])
            #     if not enquiry_folder:
            #         enquiry_folder = self.env['documents.folder'].sudo().create({
            #             'name': self.assessment_id.name,
            #             'parent_folder_id': jmc.id,
            #         })
            #     assessment = self.env['documents.folder'].sudo().search([
            #         ('name', '=', 'Assessment'),
            #         ('parent_folder_id', '=', enquiry_folder.id)
            #     ])
            #     if not assessment:
            #         assessment = self.env['documents.folder'].sudo().create({
            #             'name': 'Assessment',
            #             'parent_folder_id': enquiry_folder.id,
            #         })
            #     document = self.env['documents.document'].sudo().create({
            #             'name': attachment.name,
            #             'attachment_id': attachment.id,
            #             'folder_id': assessment.id
            #         })
            #     documents.append(document.id)
            self.assessment_id.attachment_ids = self.env['ir.attachment'].browse(attachments)
            # self.assessment_id.assessment_documents_ids = self.env['documents.document'].browse(documents)
            # To send mail
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            Urls = urls.url_join(base_url, '/my/enquiry')
            mail_content = _('Hi,<br>'
                             'The Assessment for the enquiry %s was started. You can check the status from the portal'
                             '<div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                             'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                             'border-color:#875A7B;text-decoration: none; display: inline-block; '
                             'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                             'cursor: pointer; white-space: nowrap; background-image: none; '
                             'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                             'My Account</a></div>'
                             ) % (self.assessment_id.enquiry_id.name, Urls,)
            partner = self.assessment_id.partner_id
            main_content = {
                'subject': _(
                    'Enquiry: %s' % self.assessment_id.enquiry_id.name),
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'recipient_ids': [(6, 0, partner.ids)],
                'attachment_ids': self.attachment_ids
            }
            mail_id = self.env['mail.mail'].sudo().create(main_content)
            mail_id.mail_message_id.body = mail_content
            mail_id.sudo().send()
            self.assessment_id.state = 'ownership'
            self.assessment_id.sudo().message_post(
                body=_('Uploaded the documents for the enquiry %s by %s') %
                     (self.assessment_id.name, self.env.user.name))
            mail_template = self.env.ref(
                'client_enquiry.email_template_enquiry_assessment_send_for_circulation')
            recipient_ids = self.env.ref(
                'client_enquiry.group_property_manager').users
            partner = recipient_ids.mapped('partner_id')
            self.assessment_id.enquiry_id.state = 'assessment'
            self.assessment_id.enquiry_id.support_state = 'supported'
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)],
                'attachment_ids': self.attachment_ids
            }
            mail_template.send_mail(self.assessment_id.id, force_send=True,
                                    email_values=email_values)
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Uploaded the assessment report',
                               'type': 'rainbow_man',
                    }
                }
        if self.type == 'not_supported':
            attachments = []
            documents = []
            for rec in self.attachment_ids:
            #     assessment_folder = self.env.ref(
            #         'client_enquiry.document_enquiry')
                attachment = rec
                attachment.sudo().write({
                    'res_id': self.assessment_id.id,
                    'res_model': self.assessment_id._name
                })
                attachments.append(attachment.id)
            #     if self.assessment_id.property_id.sudo().region_id:
            #         region = self.env['documents.folder'].sudo().search([
            #             ('name', '=',
            #              self.assessment_id.property_id.sudo().region_id.name),
            #             ('parent_folder_id', '=', assessment_folder.id)
            #         ])
            #         if not region:
            #             region = self.env['documents.folder'].sudo().create({
            #                 'name': self.assessment_id.property_id.sudo().region_id.name,
            #                 'parent_folder_id': assessment_folder.id
            #             })
            #     else:
            #         region = self.env['documents.folder'].sudo().search([
            #             ('name', '=', "Undefined Region"),
            #             ('parent_folder_id', '=', assessment_folder.id)
            #         ])
            #         if not region:
            #             region = self.env['documents.folder'].sudo().create({
            #                 'name': 'Undefined Region',
            #                 'parent_folder_id': assessment_folder.id
            #             })
            #     jmc = self.env['documents.folder'].sudo().search([
            #         ('name', '=', self.jmc_number),
            #         ('parent_folder_id', '=', region.id)
            #     ])
            #     if not jmc:
            #         jmc = self.env['documents.folder'].sudo().create({
            #             'name': self.jmc_number,
            #             'parent_folder_id': region.id,
            #         })
            #     enquiry_folder = self.env['documents.folder'].sudo().search([
            #             ('name', '=', self.assessment_id.name),
            #             ('parent_folder_id', '=', jmc.id)
            #         ])
            #     if not enquiry_folder:
            #         enquiry_folder = self.env['documents.folder'].sudo().create({
            #             'name': self.assessment_id.name,
            #             'parent_folder_id': jmc.id,
            #         })
            #     assessment = self.env['documents.folder'].sudo().search([
            #         ('name', '=', 'Assessment'),
            #         ('parent_folder_id', '=', enquiry_folder.id)
            #     ])
            #     if not assessment:
            #         assessment = self.env['documents.folder'].sudo().create({
            #             'name': 'Assessment',
            #             'parent_folder_id': enquiry_folder.id,
            #         })
            #     document = self.env['documents.document'].sudo().create({
            #         'name': attachment.name,
            #         'attachment_id': attachment.id,
            #         'folder_id': assessment.id
            #     })
            #     documents.append(document.id)
            self.assessment_id.attachment_ids = self.env[
                'ir.attachment'].browse(attachments)
            # self.assessment_id.assessment_documents_ids = self.env[
            #     'documents.document'].browse(documents)
            self.assessment_id.state = 'terminate'
            # self.assessment_id.enquiry_id.state = 'cancelled'
            self.assessment_id.sudo().message_post(
                body=_('The assessment %s is not supported.') %
                     (self.assessment_id.name))
            mail_template = self.env.ref(
                'client_enquiry.email_template_enquiry_assessment_not_supported')
            recipient_ids = self.env.ref(
                'client_enquiry.group_cbo').users
            partner = recipient_ids.mapped('partner_id')
            email_values = {
                'recipient_ids': [(6, 0, partner.ids)],
                'attachment_ids': self.attachment_ids
            }
            mail_template.send_mail(self.assessment_id.id, force_send=True,
                                    email_values=email_values)
            mail_template = self.env.ref(
                'client_enquiry.email_template_enquiry_cancelled')
            email_values = {
                'attachment_ids': self.attachment_ids
            }
            mail_template.send_mail(self.assessment_id.enquiry_id.id, force_send=True,
                                    email_values=email_values)
            self.assessment_id.enquiry_id.support_state = 'not_supported'
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Assessment is not supported in JPC',
                    'type': 'rainbow_man',
                }
            }

    def action_submit_acquisition(self):
        """Submit acquisition"""
        if not self.attachment_ids:
            raise UserError(_('Please attach the documents'))
        if not self.comments:
            raise UserError(_('Please attach the comments'))
        self.acquisition_id.attachment_ids = self.attachment_ids
        self.acquisition_id.comments = self.comments
        if self.type == 'supported':
            self.acquisition_id.state = 'submit'
        if self.type == 'not_supported':
            self.acquisition_id.state = 'terminate'



class CheckProperty(models.Model):
    _name = 'check.property'
    _description = 'Check Property'

    enquiry_id = fields.Many2one('client.enquiry', string="Enquiry")
    available = fields.Boolean(string="Is available in JPC",
                               help="Is available in JPC")
    property_id = fields.Many2one('building', "Property Name")

    asset_number = fields.Char(string="JMC number", help="JMC asset number")
    stand_number = fields.Char(string="Stand Number/ Portion number")

    @api.onchange('property_id')
    def _onchange_property(self):
        """Change the property"""
        if self.property_id:
            self.asset_number = self.property_id.jmc_number
            self.stand_number = self.property_id.stand_number

    def action_submit(self):
        """Method to submit the form"""
        if self.available:
            self.enquiry_id.property_id = self.property_id.id
            self.enquiry_id.asset_number = self.asset_number
            self.enquiry_id.stand_number = self.stand_number
        if not self.available:
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data._xmlid_lookup(
                    'client_enquiry.email_template_enquiry')[2]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data._xmlid_lookup(
                    'mail.email_compose_message_wizard_form')[2]
            except ValueError:
                compose_form_id = False
            ctx = dict(self.env.context or {})
            ctx.update({
                'default_model': self.enquiry_id._name,
                'active_model': self.enquiry_id._name,
                'active_id': self.enquiry_id.id,
                'default_res_id': self.enquiry_id.id,
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
                'force_email': True,
                'enquiry': True,
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

            ctx.update({
                'default_partner_ids': self.enquiry_id.partner_id.ids,
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
