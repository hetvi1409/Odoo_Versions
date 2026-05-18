# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from collections import OrderedDict
from odoo.osv import expression
from odoo.exceptions import ValidationError, UserError
from markupsafe import Markup
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import clean_context
from dateutil.relativedelta import relativedelta
import re


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    document_verified = fields.Boolean(string='Is Verified?', default=False)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(DocumentsDocument, self).create(vals_list)

        for record, vals in zip(records, vals_list):
            res_model = vals.get("res_model")
            res_id = vals.get("res_id")

            if res_model == "physical.document.submission" and res_id and record.folder_id:
                submission = self.env["physical.document.submission"].browse(res_id)
                if submission.exists():
                    # --------------------
                    # Copy attachment
                    # --------------------
                    if record.attachment_id:
                        new_attach = record.attachment_id.copy({
                            "res_model": "physical.document.submission",
                            "res_id": submission.id,
                        })
                        submission.attachment_ids = [(4, new_attach.id)]
                        submission.document_id = new_attach.id

                    submission.main_document_id = record.id
                    submission.main_document_ids = [(4, record.id)]

                    breadcrumbs_links = submission._get_folder_breadcrumbs_links(record.folder_id)
                    breadcrumbs_plain = submission._get_folder_breadcrumbs_plain(record.folder_id)

                    # Chatter message
                    body = Markup(
                        f'📎 Attachment '
                        f'<a href="#" data-oe-model="documents.document" data-oe-id="{record.id}">{record.name}</a> '
                        f'was added in {breadcrumbs_links}'
                    )
                    submission.sudo().message_post(body=body, subtype_xmlid="mail.mt_note")
                    submission.breadcrumbs_text = breadcrumbs_plain
                    submission.folder_id = record.folder_id.id

        return records

    @staticmethod
    def year_range_selection(start_offset, end_offset, steps=1):
        current_year = fields.Datetime.now().year
        return [(str(year), str(year)) for year in range(current_year - start_offset, current_year + end_offset, steps)]

    reference_month = fields.Selection([
        ('january', 'January'),
        ('february', 'February'),
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December'),
    ], string='Month')
    reference_year = fields.Selection(
        string='Year',
        selection=lambda self: self.year_range_selection(50, 20),
        default=lambda self: str(fields.Datetime.now().year),
        help='Select the year for which you want to see file for which year.')
    description_1 = fields.Html("Description 1")
    description_2 = fields.Html("Description 2")
    sender_id = fields.Many2one("res.users", string="Sender", help="Person who send the file",
                                default=lambda self: self.env.user)
    receiver_id = fields.Many2one("res.users", string="Receiver", help="Person who receive the file")
    requestee_partner = fields.Many2one("res.partner")
    department_id = fields.Many2one('hr.department', string='Department', copy=True, )
    location_id = fields.Many2one('custom.physical.location', string='Location', copy=True, )
    d_number = fields.Char(string='Disposal Number', copy=False)
    umz_number = fields.Char(string='UMZ Number', copy=False)
    submission_date = fields.Datetime(string="Submission Date")
    is_submitted = fields.Boolean(string="Submitted", default=False)
    activity_note = fields.Html(string="Additional Comment")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', string="Submission Status")
    parent_folder_id = fields.Many2one('documents.document', related='folder_id.folder_id', string="Parent Folder", )
    attachment_ids = fields.Many2many('ir.attachment', 'document_ir_attachments_rel', 'document_id', 'attachment_id',
                                      string='Documents')
    show_approve_reject = fields.Boolean("Show Approve/Reject Button", compute="_compute_show_approve_reject")
    show_submit = fields.Boolean("Show Submit Button", compute="_compute_show_approve_reject")
    physical_submission_id = fields.Many2one('physical.document.submission', string="Physical Submission")
    submitted_text = fields.Char(string="Submitted (Y/N)", compute="_compute_submitted_text")
    edms_template = fields.Many2one('memo.template',string='EDMS Template')
    folder_name = fields.Char(string="Folder Name Backup",compute="_compute_folder_name",store=True)
    parent_folder_name = fields.Char(string="Folder Name Backup",compute="_compute_folder_name",store=True)

    @api.depends('folder_id')
    def _compute_folder_name(self):
        # if skip flag is on, keep existing stored value as-is
        if self.env.context.get('skip_folder_name_compute'):
            for rec in self:
                rec.folder_name = rec.folder_name  # preserve current value
                rec.parent_folder_name = rec.parent_folder_name  # preserve current value
            return

        for rec in self:
            rec.folder_name = rec.folder_id.name if rec.folder_id else ''
            rec.parent_folder_name = rec.folder_id.folder_id.name if rec.folder_id and rec.folder_id.folder_id else ''

    @api.depends('is_submitted')
    def _compute_submitted_text(self):
        for rec in self:
            rec.submitted_text = 'Y' if rec.is_submitted else 'N'

    def _compute_show_approve_reject(self):
        for doc in self:
            if self.env.user.id in [doc.sender_id.id, doc.create_uid.id] and doc.state == 'draft':
                doc.show_submit = True
            else:
                doc.show_submit = False
            if self.env.user.id in [doc.receiver_id.id] and doc.state == 'submitted':
                doc.show_approve_reject = True
            else:
                doc.show_approve_reject = False

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        if field_name == 'folder_id':
            enable_counters = kwargs.get('enable_counters', False)
            search_panel_fields = ['access_token', 'company_id', 'description', 'display_name', 'folder_id',
                                   'is_favorited', 'is_pinned_folder', 'owner_id', 'shortcut_document_id',
                                   'user_permission', 'active']
            if not self.env.user.share:
                search_panel_fields += ['alias_name', 'alias_domain_id', 'alias_tag_ids', 'partner_id',
                                        'create_activity_type_id', 'create_activity_user_id']
            domain = [('type', '=', 'folder')]

            if unique_folder_id := self.env.context.get('documents_unique_folder_id'):
                values = self.env['documents.document'].search_read(
                    expression.AND([domain, [('folder_id', 'child_of', unique_folder_id)]]),
                    search_panel_fields,
                    order='id asc',
                )
                accessible_folder_ids = {rec['id'] for rec in values}
                for record in values:
                    if record['folder_id'] not in accessible_folder_ids:
                        record['folder_id'] = False  # consider them as roots
                return {
                    'parent_field': 'folder_id',
                    'values': values,
                }

            records = self.env['documents.document'].search_read(domain, search_panel_fields, order='id asc')
            accessible_folder_ids = {rec['id'] for rec in records}
            alias_tag_data = {}
            if not self.env.user.share:
                alias_tag_ids = {alias_tag_id for rec in records for alias_tag_id in rec['alias_tag_ids']}
                alias_tag_data = {
                    alias_tag['id']: {
                        'id': alias_tag.id,
                        'color': alias_tag.color,
                        'display_name': alias_tag.display_name
                    } for alias_tag in self.env['documents.tag'].browse(alias_tag_ids)
                }
            domain_image = {}
            if enable_counters:
                model_domain = expression.AND([
                    kwargs.get('search_domain', []),
                    kwargs.get('category_domain', []),
                    kwargs.get('filter_domain', []),
                    [(field_name, '!=', False)]
                ])
                domain_image = self._search_panel_domain_image(field_name, model_domain, enable_counters)

            values_range = OrderedDict()
            shared_root_id = "SHARED" if not self.env.user.share else False
            for record in records:
                record_id = record['id']
                if not self.env.user.share:
                    record['alias_tag_ids'] = [alias_tag_data[tag_id] for tag_id in record['alias_tag_ids']]
                if enable_counters:
                    image_element = domain_image.get(record_id)
                    record['__count'] = image_element['__count'] if image_element else 0
                folder_id = record['folder_id']
                if folder_id:
                    folder_id = folder_id[0]
                    if folder_id not in accessible_folder_ids:
                        if record['shortcut_document_id']:
                            continue
                        folder_id = shared_root_id
                elif record['owner_id'][0] == self.env.user.id:
                    folder_id = "MY"
                elif record['owner_id'][0] != self.env.ref('base.user_root').id or self.env.user.share:
                    if record['shortcut_document_id']:
                        continue
                    folder_id = shared_root_id
                else:
                    folder_id = "COMPANY"

                record['folder_id'] = folder_id
                values_range[record_id] = record

            if enable_counters:
                self._search_panel_global_counters(values_range, 'folder_id')

            special_roots = []
            if not self.env.user.share:
                special_roots = [
                    {'bold': True, 'childrenIds': [], 'parentId': False, 'user_permission': 'edit'} | values
                    for values in [
                        {
                            'display_name': _("JHB File Plan"),
                            'id': 'COMPANY',
                            'description': _("Common roots for all company users."),
                            'user_permission': 'view',
                        }, {
                            'display_name': _("My Drive"),
                            'id': 'MY',
                            'user_permission': 'edit',
                            'description': _("Your individual space."),
                        }, {
                            'display_name': _("Shared with me"),
                            'id': 'SHARED',
                            'description': _("Additional documents you have access to."),
                        }, {
                            'display_name': _("Recent"),
                            'id': 'RECENT',
                            'description': _("Recently accessed documents."),
                        }, {
                            'display_name': _("Trash"),
                            'id': 'TRASH',
                            'description': _("Items in trash will be deleted forever after %s days.",
                                             self.get_deletion_delay()),
                        }]
                ]

            return {
                'parent_field': 'folder_id',
                'values': list(values_range.values()) + special_roots,
            }

        return super().search_panel_select_range(field_name)

    # File submission flow is not working with existing model documents so added new model physical document submission
    #
    # def create(self, vals):
    #     res = super(DocumentsDocument, self).create(vals)
    #     if res.sudo().child_folder_id and res.sudo().attachment_ids:
    #         for attachment in res.sudo().attachment_ids:
    #             attachment.sudo().write({'document_ids': [(6, 0, [res.sudo().child_folder_id.id])],
    #                                      'res_model': 'documents.document',
    #                                      'res_id': res.id,
    #                                      'public':True,
    #                                      })
    #     if not res.sudo().child_folder_id and res.sudo().folder_id and res.sudo().attachment_ids:
    #         for attachment in res.sudo().attachment_ids:
    #             attachment.sudo().write({'document_ids': [(6, 0, [res.sudo().folder_id.id])],
    #                                      'res_model': 'documents.document',
    #                                      'res_id': res.id,
    #                                      'public': True,
    #                                      })
    #     self.owner_id = self.sender_id.id
    #     self.partner_id = self.receiver_id.id
    #     self.favorited_ids = [(6,0,[self.sender_id.id,self.receiver_id.id])]
    #     return res
    #
    # def write(self, vals):
    #     res = super(DocumentsDocument, self).write(vals)
    #     if self.sudo().child_folder_id and self.sudo().attachment_ids:
    #         for attachment in self.sudo().attachment_ids:
    #             attachment.sudo().write({'document_ids': [(6, 0, [self.sudo().child_folder_id.id])],
    #                                      'res_model': 'documents.document',
    #                                      'res_id': self.id,
    #                                      'public': True,
    #                                      })
    #     if not self.sudo().child_folder_id and self.sudo().folder_id and self.sudo().attachment_ids:
    #         for attachment in self.sudo().attachment_ids:
    #             attachment.sudo().write({'document_ids': [(6, 0, [self.sudo().folder_id.id])],
    #                                      'res_model': 'documents.document',
    #                                      'res_id': self.id,
    #                                      'public': True,
    #                                      })
    #     return res

    def write(self, vals):
        res = super(DocumentsDocument, self).write(vals)
        # When the attachment_id is added/updated automatically
        if 'attachment_id' in vals:
            for record in self:
                if record.attachment_id:
                    record.submission_date = fields.Datetime.now()
                    record.is_submitted = True
        return res

    def action_submit(self):
        if not self.receiver_id:
            raise ValidationError("Please add receiver.")
        action = self.env['ir.actions.act_window']._for_xml_id('documents_file_plan.document_submission_action')
        base_url = self.get_base_url()
        # url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
        partner_ids = [self.receiver_id.partner_id.id]
        self.sudo().message_post(
            body=Markup(
                '<p>The File Submission application <strong>{name}</strong> has submitted.</p><p>You can view it by clicking the link below:</p><br/><p><a style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                name=self.name,
                # link=url
            ),
            partner_ids=partner_ids,
            subject="File Submission Application",
            email_from=self.env.user.partner_id.email or '',
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        access_id = self.env['documents.access'].sudo().search([('partner_id', '=', self.receiver_id.partner_id.id),('document_id','=',self.id)])
        if not access_id:
            access_id = self.env['documents.access'].sudo().create({
                'document_id': self.id,
                'partner_id': self.receiver_id.partner_id.id,
                'role': 'edit',
            })
        self.attachment_ids.sudo().check('read')
        self.receiver_id.share = True
        self.sudo().write({'state': 'submitted',
                           'access_ids': [(4, access_id.id)],
                           'user_permission':'edit',
                           'access_via_link':'edit',
                           'access_internal':'edit',
                           })

    def action_approve_submission(self):
        for doc in self:
            if not doc.folder_id:
                raise UserError("Please assign a folder before approving.")
            if not doc.location_id:
                raise UserError("Please assign a location before approving.")
            action = self.env['ir.actions.act_window']._for_xml_id('documents_file_plan.document_submission_action')
            base_url = doc.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(doc.id)
            partner_ids = [doc.sender_id.partner_id.id]
            doc.sudo().message_post(
                body=Markup(
                    '<p>The File Submission application <strong>{name}</strong> has Approved.</p><p>You can view it by clicking the link below:</p><br/><p><a style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                    name=self.name,
                    # link=url
                ),
                partner_ids=partner_ids,
                subject="File Submission Application Approved",
                email_from=self.env.user.partner_id.email or '',
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )
            access_id = self.env['documents.access'].sudo().search(
                [('partner_id', '=', self.sender_id.partner_id.id), ('document_id', '=', doc.id)])
            if not access_id:
                access_id = self.env['documents.access'].sudo().create({
                    'document_id': doc.id,
                    'partner_id': doc.sender_id.partner_id.id,
                    'role': 'edit',
                })
            doc.sudo().write({'state': 'approved',
                               'access_ids': [(4, access_id.id)]})

    def action_reject_submission(self):
        for doc in self:
            if not doc.is_file_submission:
                raise UserError("This is not a file submission.")
            action = self.env['ir.actions.act_window']._for_xml_id('documents_file_plan.document_submission_action')
            base_url = doc.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(doc.id)
            partner_ids = [doc.sender_id.partner_id.id]
            doc.sudo().message_post(
                body=Markup(
                    '<p>The File Submission application <strong>{name}</strong> has Rejected.</p><p>You can view it by clicking the link below:</p><br/><p><a style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                    name=self.name,
                    # link=url
                ),
                partner_ids=partner_ids,
                subject="File Submission Application Rejected",
                email_from=self.env.user.partner_id.email or '',
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )
            access_id = self.env['documents.access'].sudo().search(
                [('partner_id', '=', self.sender_id.partner_id.id), ('document_id', '=', doc.id)])
            if not access_id:
                access_id = self.env['documents.access'].sudo().create({
                    'document_id': doc.id,
                    'partner_id': doc.sender_id.partner_id.id,
                    'role': 'edit',
                })
            doc.sudo().write({'state': 'rejected',
                              'access_ids': [(4, access_id.id)]})
#

class RequestWizard(models.TransientModel):
    _inherit = "documents.request_wizard"

    department_id = fields.Many2one('hr.department', string='Department', copy=True, )
    location_id = fields.Many2one('custom.physical.location', string='Location', copy=True, )
    d_number = fields.Char(string='Disposal Number', copy=False)
    umz_number = fields.Char(string='UMZ Number', copy=False)
    requester_id = fields.Many2one("res.users", string="Requester", help="Person who request for the file",
                                   default=lambda self: self.env.user)
    request_date = fields.Datetime(string="Request Date")

    def request_document(self):
        self.ensure_one()
        document = self.env['documents.document'].create({
            'name': self.name,
            'folder_id': self.folder_id.id,
            'tag_ids': [(6, 0, self.tag_ids.ids if self.tag_ids else [])],
            'owner_id': self.env.user.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'requestee_partner_id': self.requestee_id.id,
            'requestee_partner': self.requestee_id.id,
            'res_model': self.res_model,
            'res_id': self.res_id,
        })

        activity_vals = {
            'user_id': self.requestee_id.user_ids[0].id if self.requestee_id.user_ids else self.env.user.id,
            'note': self.activity_note,
            'activity_type_id': self.activity_type_id.id if self.activity_type_id else False,
            'summary': self.name
        }

        if self.activity_date_deadline_range > 0:
            activity_vals['date_deadline'] = fields.Date.context_today(self) + relativedelta(
                **{self.activity_date_deadline_range_type: self.activity_date_deadline_range})

        request_by_mail = self.requestee_id and self.create_uid not in self.requestee_id.user_ids
        activity = document.with_context(mail_activity_quick_update=request_by_mail).activity_schedule(**activity_vals)
        document.request_activity_id = activity

        # Access rights: either user edit with expiration if the requestee has a user or access_via_link=edit otherwise
        # Note that when uploaded, access_via_link will be set to view automatically (if it was set to edit)
        if self.requestee_id.user_ids:
            document.action_update_access_rights('none', partners={
                self.env.user.partner_id.id: ('edit', False),
                self.requestee_id.id: ('edit', datetime.combine(activity.date_deadline, datetime.max.time())),
            })
        else:
            document.access_via_link = 'edit'
            document.action_update_access_rights('none', partners={
                self.env.user.partner_id.id: ('edit', False)
            })
        request_template = self.env.ref('documents.mail_template_document_request', raise_if_not_found=False)
        if request_template:
            document.with_context(clean_context(self.env.context)).message_mail_with_source(request_template)

        return document

class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    is_rejected = fields.Boolean(string="Rejected Attachment")