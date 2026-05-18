from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.image import image_process
import base64


class DocumentsApproval(models.Model):
    """Document approval model"""
    _name = 'documents.approval'
    _description = "Documents Approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    attachment_id = fields.Many2one('ir.attachment', copy=False,
                                    string="Attachment")
    name = fields.Char('Name', copy=True, store=True, compute='_compute_name',
                       inverse='_inverse_name')
    folder_id = fields.Many2one('documents.document',domain=[("type", "=", "folder")],
                                string="Workspace", ondelete="restrict",
                                tracking=True, required=True, index=True)
    partner_id = fields.Many2one('res.partner', string="Contact",
                                 tracking=True)
    user_id = fields.Many2one('res.users',
                              string="Owner")
    owner_id = fields.Many2one('res.users',
                               default=lambda self: self.env.user.id,
                               string="Owner",
                               tracking=True)
    datas = fields.Binary(string="File", required=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'), ('send', 'Send for Approval'),
        ('approved', 'Approved'), ('reject', 'Rejected')],
        string='Status', required=True, readonly=True,
        copy=False, tracking=True, default='draft')
    general_type = fields.Selection([('general_file', 'General File'),
                                     ('property', 'Property')],default='general_file',
                                    string="Document Type", required=True)

    redirect_url = fields.Char(compute="_compute_redirect_url", store=True)
    document_id = fields.Many2one('documents.document', string="Document")
    # thumbnail = fields.Binary(readonly=False, store=True, compute='_compute_thumbnail')
    jmc_number = fields.Char(string="JMC Number")
    erf_number = fields.Char(string="Erf Number")
    address = fields.Char(string="Address")
    jmc_property_id = fields.Many2one(comodel_name='building',
                                      string="JMC Number", tracking=True,
                                      context={'list_view_ref':'property_update.building_list'})
    work_to_do = fields.Char(string="Work To Do")

    @api.depends('state')
    def _compute_redirect_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')

            # / odoo / mailing.mailing / {self.id}
            if record.state != 'approved':
                base_url += '/odoo/%s/%s' % (record._name, record.id)
                record.redirect_url = base_url
            else:
                asset_id = self.env['building'].search(
                    [('approval_request_id', '=', record.id)])
                base_url += '/odoo/%s/%s' % ('documents.document',asset_id.id)
                record.redirect_url = base_url

    @api.depends('attachment_id.name')
    def _compute_name(self):
        for record in self:
            if record.attachment_id.name:
                record.name = record.attachment_id.name

    def _inverse_name(self):
        for record in self:
            if record.attachment_id:
                record.attachment_name = record.name

    @api.model_create_multi
    def create(self, vals_list):
        """Create A New Attachment"""
        documents = super().create(vals_list)
        for vals in vals_list:
            if vals['datas']:
                attachment = self.env['ir.attachment'].create({
                    'datas': vals['datas'],
                    'name': vals['name'],
                })
                documents.attachment_id = attachment.id
        return documents


    def write(self, values):
        res = super().write(values)
        for rec in self:
            if rec.attachment_id:
                rec.attachment_id.write({
                    'datas': rec.datas,
                    'name': rec.name,
                })
        return res

    def action_submit_for_approval(self):
        """ Submit the asset for approval """
        self.write({'state': 'send'})
        manager_group = self.env.ref(
            'document_approval.group_document_approval_manager')

        # Get partner objects
        mail_values = {}

        partners = manager_group.user_ids.mapped('partner_id')

        for partner in partners:
            if partner.email:  # Ensure the partner has an email address
                mail_values = {
                    'email_to': partner.email,
                    # Other values can be set as needed
                }
        template = self.env.ref('document_approval.email_template_to_confirm')
        template.send_mail(self.id, force_send=True, email_values=mail_values)

        # Send an in-app notification
        for document in self:
            message_body = (
                f" Asset {document.name} has been submitted for approval. "
            )
            # Send to all followers and specifically to the Impairment Manager group
            manager_group = self.env.ref(
                'document_approval.group_document_approval_manager')

            partner_ids = manager_group.user_ids.mapped('partner_id.id')

            document.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=partner_ids,
            )

    @api.onchange('jmc_property_id')
    def onchange_jmc_number(self):
        """Onchange JMC Number"""
        property_name = self.jmc_property_id
        self.jmc_number = property_name.jmc_number
        self.erf_number = property_name.name
        self.address = property_name.address

    def action_approve(self):
        for record in self:
            record.state = 'approved'
            message_body = (
                f" Asset {record.name} has been approved. "
            )
            mail_values = {}

            if record.partner_id.email:  # Ensure the partner has an email address
                mail_values = {
                    'email_to': record.partner_id.email,
                    # Other values can be set as needed
                }
            # Send to all followers and specifically to the Impairment Manager group
            vals = {
                'name': record.name,
                'general_type': record.general_type,
                'datas': record.datas,
                'attachment_id': record.attachment_id.id if record.attachment_id else False,
                'partner_id': record.partner_id.id if record.partner_id else False,
                'folder_id': record.folder_id.id if record.folder_id else False,
                'owner_id': record.owner_id.id if record.owner_id else False,
                'jmc_property_id': record.jmc_property_id.id if record.jmc_property_id else False,
                'erf_number': record.erf_number,
                'address': record.address,
            }

            document_id = self.env['documents.document'].create(vals)

            record.document_id = document_id.id

            template = self.env.ref(
                'document_approval.email_template_approval_confirmed')
            template.send_mail(record.id, force_send=True,
                               email_values=mail_values)

            record.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.owner_id.partner_id.id],
            )

    def action_reject(self):
        for record in self:
            record.state = 'reject'
            message_body = (
                f" Asset {record.name} has been rejected. "
            )
            mail_values = {}

            if record.partner_id.email:  # Ensure the partner has an email address
                mail_values = {
                    'email_to': record.partner_id.email,
                    # Other values can be set as needed
                }
            # Send to all followers and specifically to the Impairment Manager group
            template = self.env.ref('document_approval.email_template_rejected')
            template.send_mail(record.id, force_send=True,
                               email_values=mail_values)

            record.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.partner_id.id],
            )


    # @api.depends('datas',)
    # def _compute_thumbnail(self):
    #     for record in self:
    #         if record.attachment_id:
    #             if record.attachment_id.mimetype == 'application/pdf':
    #                 # Thumbnails of pdfs are generated by the client. To force the generation, we invalidate the thumbnail.
    #                 record.thumbnail = False
    #             else:
    #                 try:
    #                     record.thumbnail = base64.b64encode(image_process(record.datas, size=(200, 140), crop='center'))
    #                 except (UserError, TypeError):
    #                     record.thumbnail = False
    #         else:
    #             record.thumbnail = False