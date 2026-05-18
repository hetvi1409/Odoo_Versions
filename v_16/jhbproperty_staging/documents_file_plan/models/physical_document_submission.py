from odoo import api, fields, models, _
from collections import OrderedDict
from odoo.osv import expression
from odoo.exceptions import ValidationError, AccessError, UserError
from markupsafe import Markup
import base64
import logging

_logger = logging.getLogger(__name__)


class PhysicalDocumentSubmission(models.Model):
    _name = 'physical.document.submission'
    _description = 'Physical Document Submission'
    _inherit = ['mail.thread.cc',
                'mail.thread.blacklist',
                'mail.activity.mixin',
                'utm.mixin',
                'format.address.mixin',
                ]
    _primary_email = 'email_from'
    _check_company_auto = True

    @staticmethod
    def year_range_selection(start_offset, end_offset, steps=1):
        current_year = fields.Datetime.now().year
        return [(str(year), str(year)) for year in range(current_year - start_offset, current_year + end_offset, steps)]

    @api.model
    def _get_default_receiver(self):
        """Return user S Dlamini if exists, otherwise fallback to current user."""
        group = self.env.ref("documents_file_plan.group_physical_record_registry", raise_if_not_found=False)
        if group:
            users = group.users - self.env.user
            print("\n\n\n===default===users====", users)
            return users[:1].id if users else False
        # Final fallback
        return False

    @api.model
    def _get_receiver_domain(self):
        """Return domain for users in group_physical_record_registry excluding the current user."""
        group = self.env.ref("documents_file_plan.group_physical_record_registry", raise_if_not_found=False)
        if not group:
            return [("id", "=", 0)]  # empty fallback

        user_ids = group.users.ids
        if self.env.user.id in user_ids:
            user_ids.remove(self.env.user.id)

        return [("id", "in", user_ids)]

    name = fields.Char(string="Title", required=True, tracking=True)
    active = fields.Boolean(default=True)
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
    description_1 = fields.Html("Description")
    sender_id = fields.Many2one("res.users", string="Sender", default=lambda self: self.env.user,
                                help="Person who sent the file")
    receiver = fields.Selection(
        [('Registry clerk', 'Registry clerk'), ('Registry Administrator', 'Registry Administrator'),
         ('Records Management officer', 'Records Management officer')], default="Records Management officer",
        required=True, string = "Receiver Role")
    allowed_receiver_ids = fields.Many2many(
        'res.users',
        string='Allowed Receivers',
        compute='_compute_allowed_receiver_ids',
        compute_sudo=True,
        store=False,
    )
    receiver_id = fields.Many2one("res.users", string="Receiver Name", help="Person who received the file",
                                  required=True, domain="[('id', 'in', allowed_receiver_ids)]")
    # default=lambda self: self._get_default_receiver(),
    # domain=lambda self: self._get_receiver_domain())
    department_id = fields.Many2one('hr.department', string="Department", tracking=True)
    sub_department_id = fields.Many2one('hr.department', string="Sub Department",
                                        domain="[('parent_id', '=', department_id)]", tracking=True)
    location_id = fields.Many2one('custom.physical.location', string='Location', copy=True)
    d_number = fields.Char(string='Disposal Number', copy=False)
    umz_number = fields.Char(string='UMZ Number', default='K-UMZ001', copy=False)
    submission_date = fields.Datetime(string="Submission Date", default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('filed', 'Filed'),
        ('requested_document', 'Requested Document'),
        ('collected', 'Collected'),
        ('not_found', 'Not Found'),
        ('rejected', 'Rejected'),
        ('packed', 'Packed'),
        ('dispatched', 'Dispatched'),
        ('in_transit', 'In Transit'),
        ('at_warehouse', 'At Warehouse'),
    ], default='draft', string="Submission Status", tracking=True)
    # attachment_ids = fields.Many2many(
    #     'ir.attachment',
    #     'physical_document_submission_ir_attachment_rel',
    #     'submission_id',
    #     'attachment_id',
    #     string='Documents'
    # )
    physical_document_ids = fields.One2many(
        'physical.document.upload',
        'physical_submission_id',
        string='Documents'
    )
    show_approve_reject = fields.Boolean("Show Approve/Reject Button", compute="_compute_show_approve_reject")
    show_submit = fields.Boolean("Show Submit Button", compute="_compute_show_approve_reject")

    attachment_ids = fields.Many2many(
        "ir.attachment",
        "submission_attachment_rel",
        "submission_id",
        "attachment_id",
        string="Attachments", readonly=True, copy=False
    )
    document_id = fields.Many2one('ir.attachment', string='Document Attachment', readonly=True, copy=False)
    document = fields.Binary(string='Attachment', related='document_id.datas', readonly=True)

    breadcrumbs_text = fields.Text(
        string="Folder Breadcrumbs",
        readonly=True, copy=False,
        help="Path of the folder where the last attachment was added",
    )

    main_document_id = fields.Many2one(
        'documents.document',
        string='Main Document',
        readonly=True,
        copy=False
    )
    main_document_ids = fields.Many2many(
        'documents.document',
        'physical_documents_submission_rel',  # relation table name
        'submission_id',  # current model’s column
        'document_id',  # target model’s column
        string='Documents',
        help='Documents linked from the Documents app.'
    )
    email_from = fields.Char(
        string="Email From",
        help="Email address of the sender who submitted this document."
    )
    document_type = fields.Selection([
        ('at_warehouse', 'At Warehouse'),
        ('at_location', 'At Location'),
    ], string='Document Type', default='at_location', tracking=True)
    folder_id = fields.Many2one(
        'documents.document',
        string="Folder",
        domain="[('type', '=', 'folder')]")
    at_warehouse = fields.Boolean(string="At Warehouse", default=False)
    warehouse_id = fields.Many2one('metro.file', string="Warehouse Reference")
    transfer_batch_id = fields.Many2one('document.transfer.batch', string='Transfer Batch', copy=False)
    box_number = fields.Char(string='Box Number', copy=False)
    has_accessible_folders = fields.Boolean(
        compute="_compute_has_accessible_folders",
        store=False
    )

    @api.depends('receiver')
    def _compute_allowed_receiver_ids(self):
        xmlid_map = {
            'Registry clerk': 'documents_file_plan.group_physical_record_user',
            'Registry Administrator': 'physical_document_records_manage.group_physical_record_custom',
            'Records Management officer': 'documents_file_plan.group_physical_record_registry',
        }
        empty_users = self.env['res.users']
        for rec in self:
            xmlid = xmlid_map.get((rec.receiver or '').strip())
            group = self.env.ref(xmlid, raise_if_not_found=False) if xmlid else False
            rec.allowed_receiver_ids = group.users if group else empty_users

    @api.constrains('receiver', 'receiver_id')
    def _check_receiver_in_allowed_list(self):
        for rec in self:
            if rec.receiver and rec.receiver_id and rec.receiver_id not in rec.allowed_receiver_ids:
                raise ValidationError("Selected Receiver must belong to selected Receiver Role.")

    @api.depends()
    def _compute_has_accessible_folders(self):
        Folder = self.env['documents.document']
        for rec in self:
            # record rules apply automatically here
            count = Folder.search_count([('type', '=', 'folder')])
            rec.has_accessible_folders = bool(count)

    @api.constrains('state')
    def _check_state_flow(self):
        # Prevent illegal jumps, e.g., direct draft -> at_warehouse
        for rec in self:
            if rec.state == 'at_warehouse' and not rec.transfer_batch_id:
                raise ValidationError(_("Cannot mark as 'At Warehouse' without a transfer batch."))

    @api.onchange('document_type')
    def _onchange_document_type(self):
        for rec in self:
            if rec.document_type == 'at_warehouse':
                rec.location_id = False  # clear location if not needed

    def _get_folder_chain(self, folder):
        """Return full folder chain [root ... leaf] following folder_id only."""
        chain = []
        seen = set()
        current = folder.sudo()
        while current and current.exists() and current.id not in seen:
            chain.append(current)
            seen.add(current.id)
            # in documents.document the parent is always folder_id when type == 'folder'
            current = current.folder_id
        return list(reversed(chain))

    def _get_folder_breadcrumbs_links(self, folder):
        chain = self._get_folder_chain(folder)
        return " / ".join(
            f'<a href="#" data-oe-model="documents.document" data-oe-id="{f.id}">{f.name}</a>'
            for f in chain
        )

    def _get_folder_breadcrumbs_plain(self, folder):
        chain = self._get_folder_chain(folder)
        return " / ".join(f.name for f in chain)

    def action_open_department_folders(self):
        """Open the sender's department folder, all its descendants, and show files too"""
        self.ensure_one()
        if not self.department_id:
            raise UserError("PLease add department value.")
        if not self.reference_month:
            raise UserError("PLease add month value.")
        if not self.reference_year:
            raise UserError("PLease add year value.")
        # if not self.d_number:
        #     raise UserError("PLease add Disposal Number value.")
        if not self.description_1:
            raise UserError("PLease add description for your file submission.")
        # department_folder = False
        # department = self.sender_id.sudo().employee_id.department_id
        # if not department:
        #     raise UserError("No department found for the sender.")
        #
        # if self.sub_department_id:
        #     department_folder = self.env['documents.document'].search([
        #         ('type', '=', 'folder'),
        #         ('folder_id', '=', False),  # only root level
        #         ('name', '=', self.sub_department_id.name),
        #     ], limit=1)
        # else:
        #     # Department folder must exist in documents.document (root folder)
        #     department_folder = self.env['documents.document'].search([
        #         ('type', '=', 'folder'),
        #         ('folder_id', '=', False),  # only root level
        #         ('name', '=', department.name),
        #     ], limit=1)
        #
        # if not department_folder:
        #     raise UserError(
        #         _("No root folder found for department '%s'. Please create a folder with this department name.") % self.sub_department_id.name if self.sub_department_id else department.name
        #     )
        #
        # return {
        #     'name': f"{department.name} Documents",
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'documents.document',
        #     # ✅ include both folders and files in kanban/tree/form views
        #     'view_mode': 'kanban,list',
        #     'domain': [
        #         ('folder_id', 'child_of', department_folder.id),  # include files + all descendant folders
        #     ],
        #     'context': {
        #         **self.env.context,
        #         'default_physical_submission_id': self.id,
        #         'default_res_model': 'physical.document.submission',
        #         'default_res_id': self.id,
        #     },
        # }

        self.ensure_one()
        employee = self.env.user.employee_id
        domain = [('id', '=', False)]

        if employee:
            domain = [
                '|',
                '&',
                ('access_level', '=', 'department'),
                ('department_id', '=', employee.department_id.id),
                '&',
                ('access_level', '=', 'sub_department'),
                ('sub_department_id', '=', employee.department_id.id),
            ]
        return {
            'name': _('Documents'),
            # 'domain': [('partner_id', '=', self.sender_id.partner_id.id)],
            'domain': domain,
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'views': [(False, 'kanban')],
            'view_mode': 'kanban',
            'context': {
                "default_partner_id": self.sender_id.partner_id.id,
                "searchpanel_default_folder_id": False,
                'default_physical_submission_id': self.id,
                'default_res_model': 'physical.document.submission',
                'default_res_id': self.id,
                'default_reference_month': self.reference_month,
                'default_reference_year': self.reference_year,
                'default_sender_id': self.sender_id.id,
                'default_receiver_id': self.receiver_id.id,
                'default_location_id': self.location_id.id if self.location_id else False,
                'default_department_id': self.department_id.id,
                'default_sub_department_id': self.sub_department_id.id,
            },
        }

    def _compute_show_approve_reject(self):
        for doc in self:
            if self.env.user.id in [doc.sender_id.id, doc.create_uid.id] and doc.state == 'draft':
                doc.show_submit = True
            else:
                doc.show_submit = False
            if self.env.user.id in [doc.receiver_id.id] and doc.state == 'submitted':
                doc.show_approve_reject = True
            else:
                if self.env.user.has_group('base.group_system') and doc.state == 'submitted':
                    doc.show_approve_reject = True
                else:
                    doc.show_approve_reject = False

    @api.model
    def year_range_selection(self, past=50, future=20):
        current_year = fields.Date.today().year
        years = [(str(y), str(y)) for y in range(current_year - past, current_year + future + 1)]
        return years

    @api.model_create_multi
    def create(self, vals):
        res = super(PhysicalDocumentSubmission, self).create(vals)
        return res

    @api.onchange('sender_id', 'receiver_id')
    def _onchange_sender_receiver(self):
        for rec in self:
            if rec.sender_id and rec.receiver_id and rec.sender_id.id == rec.receiver_id.id:
                raise ValidationError(_("Sender and Receiver cannot be the same user. %s", rec))

    @api.onchange('sender_id')
    def _onchange_sender_id(self):
        for doc in self:
            if doc.sender_id and doc.sender_id.sudo().employee_id:
                department_id = doc.sender_id.sudo().employee_id.department_id.id if doc.sender_id.sudo().employee_id.department_id else False
                if department_id:
                    if doc.sender_id.sudo().employee_id.department_id.parent_id:
                        doc.department_id = doc.sender_id.sudo().employee_id.department_id.parent_id.id
                        doc.sub_department_id = department_id
                    else:
                        doc.department_id = department_id

    def action_submit(self):
        if not self.receiver_id:
            raise ValidationError("Please add receiver.")
        # for document in self.sudo().submission_documents_ids:
        #     if document.attachment_id:
        #         document.sudo().attachment_id.write({'public':True})
        #         document.sudo().write({'type':'binary'})
        #     document.sudo().write({'partner_id': self.receiver_id.partner_id.id,
        #                            'owner_id': self.sender_id.partner_id.id,
        #                            'user_permission': 'edit'})
        #     self.env['documents.access'].sudo().create([{
        #         'document_id': document.id,
        #         'partner_id': self.receiver_id.partner_id.id,
        #         'role': 'edit',
        #     }])
        action = self.env['ir.actions.act_window']._for_xml_id('documents_file_plan.physical_document_submission_action')
        base_url = self.get_base_url()
        url = base_url + '/web/content/?model=physical.document.submission&id='  + str(self.id)
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
        # self.attachment_ids.sudo().check('read')
        # self.receiver_id.share = True
        self.sudo().write({'state': 'submitted'})
        # else:
        #     raise ValidationError("Please Add Attachment.")

    def action_request_file(self):
        self.ensure_one()
        if not self.location_id and self.document_type == 'at_location':
            raise ValidationError(_("Please assign a location before requesting a file."))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Request File',
            'res_model': 'request.file.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_submission_id': self.id,
                'default_location_id': self.location_id.id if self.location_id else False,
                'default_receiver_id': self.receiver_id.id,
            }
        }

    def action_mark_collected(self):
        for rec in self:
            rec.sudo().write({'state': 'collected'})
            rec.message_post(
                body=_("📂 The requested document <strong>%s</strong> has been marked as <b>Collected</b>.") % rec.name,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )

    def action_mark_not_found(self):
        for rec in self:
            rec.sudo().write({'state': 'not_found'})
            rec.message_post(
                body=_("❌ The requested document <strong>%s</strong> has been marked as <b>Not Found</b>.") % rec.name,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )

    def action_approve_submission(self):
        for doc in self:
            if doc.physical_document_ids.filtered(lambda l:l.folder_id == False):
                raise UserError("Please assign a folder before approving.")
            if not doc.location_id:
                raise UserError("Please assign a location before approving.")
            # for document in self.sudo().submission_documents_ids:
            #     if document.folder_id and document.child_folder_id:
            #         document.sudo().attachment_id.write({'public': True})
            #         document.sudo().write({'folder_id': 'binary'})
            #     document.sudo().write({'partner_id': self.receiver_id.partner_id.id,
            #                            'owner_id': self.sender_id.partner_id.id,
            #                            'user_permission': 'edit'})
            #     self.env['documents.access'].sudo().create([{
            #         'document_id': document.id,
            #         'partner_id': self.receiver_id.partner_id.id,
            #         'role': 'edit',
            #     }])
            action = self.env['ir.actions.act_window']._for_xml_id('documents_file_plan.physical_document_submission_action')
            base_url = doc.get_base_url()
            url = base_url + '/web/content/?model=physical.document.submission&id=' + str(doc.id)
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

            # for attachment in doc.sudo().attachment_ids:
            #     document = self.env['documents.document'].sudo().create({
            #         'name': attachment.name,
            #         'attachment_id': attachment.id,
            #         'folder_id': doc.sudo().child_folder_id.id or doc.sudo().folder_id.id,
            #         'owner_id': doc.sender_id.id,
            #         'partner_id': doc.receiver_id.partner_id.id if doc.receiver_id else False,
            #         'tag_ids': [(6, 0, [])],
            #         'reference_month':doc.reference_month,
            #         'reference_year':doc.reference_year
            #     })
            #     self.env['documents.access'].sudo().create([{
            #         'document_id': document.id,
            #         'partner_id': doc.receiver_id.partner_id.id,
            #         'role': 'edit',
            #     }])
            doc.sudo().write({'state': 'approved'})
            if doc.document_type == 'at_warehouse':
                for document in doc.sudo().main_document_ids:
                    document_warehouse = self.env['metro.file'].sudo().create({
                        'document_id': document.id,
                        'metro_d_number': self.d_number or '',
                        'umz_number': self.umz_number or '',
                        'date_sent': fields.Date.today(),
                        'responsible_id': self.env.user.id,
                        'submission_ids': [(6, 0, [doc.id])],
                    })
                    attachments = doc.attachment_ids.sudo()
                    for attachment in attachments:
                        # copy attachment to point to warehouse (keep original untouched)
                        new_attachment = attachment.sudo().copy({
                            'res_model': 'metro.file',
                            'res_id': document_warehouse.id,
                        })
                        document_warehouse.sudo().write({'attachment_ids': [(4, new_attachment.id)]})

                doc.sudo().write({'at_warehouse': True,
                                  'warehouse_id': document_warehouse.id,
                                  'state': 'filed',
                                  'document_type': 'at_warehouse'})

    def action_reject_submission(self):
        for doc in self:
            if not doc.document_id:
                raise UserError(_("No uploaded documents found to reject."))

            reason = getattr(doc, "rejection_reason", False) or _("No reason provided")

            # Archive all linked documents
            if doc.document_id:
                doc.document_id.sudo().write({'is_rejected': True})
                # Clear the reference
                doc.sudo().write({'document_id': False})

            if doc.main_document_id:
                doc.main_document_id.sudo().write({'active': False})
                # Clear the reference
                doc.sudo().write({'main_document_id': False})

                # Reject & clear all related attachments
            if doc.attachment_ids:
                latest_attachment = doc.attachment_ids.sorted("create_date")[-1]  # newest one
                latest_attachment.sudo().write({'is_rejected': True})
                doc.sudo().write({
                    'attachment_ids': [(3, latest_attachment.id)]  # remove only this one
                })

            # Post chatter message
            # doc.sudo().message_post(
            #     body=Markup(
            #         _("❌ The file submission <strong>%s</strong> has been rejected.<br/><br/><strong>Reason:</strong> %s")
            #         % (doc.name, reason)
            #     ),
            #     message_type='notification',
            #     subtype_xmlid='mail.mt_comment',
            # )
            action = self.env['ir.actions.act_window']._for_xml_id(
                'documents_file_plan.physical_document_submission_action')
            base_url = doc.get_base_url()
            # url = base_url + '/odoo/' + action.get('path') + '/' + str(doc.id)
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
            doc.sudo().write({'state': 'rejected'})

    def action_filed(self):
        for doc in self:
            # if not doc.d_number:
            #     raise UserError("Please add D Number")
            # if not doc.umz_number:
            #     raise UserError("Please add UMZ Number")
            doc.sudo().write({'state': 'filed'})

    def action_sync_attachments(self):
        """Move attachments from O2M -> M2M and set res_model/res_id"""
        for submission in self:
            attachments_to_link = self.env['ir.attachment']

            for doc in submission.physical_document_ids:
                if doc.attachment_id:
                    # update res_model and res_id
                    doc.attachment_id.sudo().write({
                        'res_model': 'physical.document.submission',
                        'res_id': submission.id,
                    })
                    attachments_to_link |= doc.attachment_id

            # link to many2many field
            if attachments_to_link:
                submission.sudo().write({
                    'attachment_ids': [(6, 0, attachments_to_link.ids)]
                })

        # 🧩 Handle incoming email and create record + attachments
        @api.model
        def message_new(self, msg_dict, custom_values=None):
            """Triggered when a new record is created from incoming mail."""
            custom_values = dict(custom_values or {})
            # Get sender info
            sender_email = msg_dict.get("email_from")
            sender_user = self.env["res.users"].search(
                [("login", "ilike", sender_email)], limit=1
            )

            # Set defaults
            custom_values.setdefault("sender_id", sender_user.id if sender_user else self.env.user.id)
            custom_values.setdefault("receiver_id", self._get_default_receiver())
            custom_values.setdefault("name", msg_dict.get("subject") or "Incoming Mail")

            # Create the physical submission record
            record = super(PhysicalDocumentSubmission, self).message_new(msg_dict, custom_values)

            # 🔹 Handle attachments and create linked document records
            attachments = msg_dict.get("attachments") or []
            for attach_name, attach_content in attachments:
                try:
                    # Save to ir.attachment
                    attachment = self.env["ir.attachment"].create({
                        "name": attach_name,
                        "datas": base64.b64encode(attach_content),
                        "res_model": self._name,
                        "res_id": record.id,
                        "type": "binary",
                    })

                    # Create a document in Odoo Documents app (if module installed)
                    self.env["documents.document"].create({
                        "name": attach_name,
                        "datas": attachment.datas,
                        "owner_id": record.receiver_id.id,
                        "submission_id": record.id,  # link back if you added this field
                        "attachment_id": attachment.id,
                    })
                except Exception as e:
                    _logger.warning(f"Attachment creation failed: {e}")

            return record


class PhysicalDocumentUpload(models.Model):
    _name = "physical.document.upload"
    _description = 'Physical Document Upload'

    attachment_id = fields.Many2one('ir.attachment', ondelete='cascade', auto_join=True, copy=False)
    attachment_name = fields.Char('Attachment Name', related='attachment_id.name', readonly=False)
    # name = fields.Char('Name', copy=True, store=True,readonly=False)
    name = fields.Char('Name', copy=True, store=True,compute="_compute_name_and_preview",readonly=False)
    folder_id = fields.Many2one('documents.folder', string="Folder",domain="[('folder_id', '=', False)]")
    child_folder_id = fields.Many2one('documents.folder', string="Subfolder",domain="[('folder_id', '=', folder_id)]")
    datas = fields.Binary(related='attachment_id.datas', related_sudo=True, readonly=False)
    document_id = fields.Many2one('documents.document', string="Document")
    physical_submission_id = fields.Many2one('physical.document.submission', string="Physical Submission")
    available_subfolders = fields.Many2many(
        'documents.document',
        compute="_compute_available_subfolders",
        store=False
    )

    def _compute_available_subfolders(self):
        for rec in self:
            subfolders = self.env['documents.document']
            if rec.folder_id:
                # collect all descendants of folder_id
                subfolders |= rec._get_all_descendants(rec.folder_id)
                # exclude the folder itself
                subfolders -= rec.folder_id
            rec.available_subfolders = subfolders

    def _get_all_descendants(self, folder):
        """Recursively collect all descendant folders"""
        result = self.env['documents.document']
        children = self.env['documents.document'].search([
            ('folder_id', '=', folder.id)
        ])
        result |= children
        for child in children:
            result |= self._get_all_descendants(child)
        return result
    @api.depends('attachment_id')
    def _compute_name_and_preview(self):
        for record in self:
            if record.attachment_id:
                record.name = record.attachment_id.name

    @api.onchange('folder_id','child_folder_id')
    def _onchange_folders(self):
        for rec in self:
            if not rec.document_id:
                existing_doc = self.env['documents.document'].sudo().search([
                    ('attachment_id', '=', rec.attachment_id.id)
                ], limit=1)
                if existing_doc:
                    rec.document_id = existing_doc.id
                    if rec.child_folder_id.id or rec.folder_id.id:
                        existing_doc.write({
                            'folder_id': rec.child_folder_id.id or rec.folder_id.id,
                        })
                    # existing_doc.folder_id = rec.child_folder_id.id or rec.folder_id.id
                else:
                    rec.sudo().attachment_id.write({'public': True})
                    document = self.env['documents.document'].sudo().create({
                        'name': rec.attachment_id.name,
                        'attachment_id': rec.attachment_id.id,
                        'folder_id': rec.sudo().child_folder_id.id or rec.sudo().folder_id.id,
                        'owner_id': rec.physical_submission_id.sender_id.id,
                        'partner_id': rec.physical_submission_id.receiver_id.partner_id.id if rec.physical_submission_id.receiver_id else False,
                        'tag_ids': [(6, 0, [])],
                        'reference_month': rec.physical_submission_id.reference_month,
                        'reference_year': rec.physical_submission_id.reference_year,
                        'sender_id': rec.physical_submission_id.sender_id.id,
                        'receiver_id': rec.physical_submission_id.receiver_id.id,
                        'location_id': rec.physical_submission_id.location_id.id if rec.physical_submission_id.location_id else False,
                        'department_id': rec.physical_submission_id.department_id.id,
                        'sub_department_id': rec.physical_submission_id.sub_department_id.id,
                    })
                    rec.document_id = document.id
                    Access = self.env['documents.access'].sudo()

                    # For the main document
                    if rec.physical_submission_id.receiver_id.partner_id:
                        if not Access.search([
                            ('document_id', '=', document.id),
                            ('partner_id', '=', rec.physical_submission_id.receiver_id.partner_id.id)
                        ], limit=1):
                            Access.create({
                                'document_id': document.id,
                                'partner_id': rec.physical_submission_id.receiver_id.partner_id.id,
                                'role': 'edit',
                            })

                    # For folder_id
                    if rec.folder_id and rec.physical_submission_id.sender_id.partner_id:
                        if not Access.search([
                            ('document_id', '=', rec.folder_id.id),
                            ('partner_id', '=', rec.physical_submission_id.sender_id.partner_id.id)
                        ], limit=1):
                            Access.create({
                                'document_id': rec.folder_id.id,
                                'partner_id': rec.physical_submission_id.sender_id.partner_id.id,
                                'role': 'edit',
                            })

                    # For child_folder_id
                    if rec.child_folder_id and rec.physical_submission_id.sender_id.partner_id:
                        if not Access.search([
                            ('document_id', '=', rec.child_folder_id.id),
                            ('partner_id', '=', rec.physical_submission_id.sender_id.partner_id.id)
                        ], limit=1):
                            Access.create({
                                'document_id': rec.child_folder_id.id,
                                'partner_id': rec.physical_submission_id.sender_id.partner_id.id,
                                'role': 'edit',
                            })

            else:
                rec.document_id.sudo().write({'folder_id': rec.sudo().child_folder_id.id or rec.sudo().folder_id.id, })
