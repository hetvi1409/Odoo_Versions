from markupsafe import Markup
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta
from io import BytesIO
import io
import base64
import re
from PyPDF2 import PdfReader
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from odoo.tools import pdf, format_list, is_html_empty
import logging

_logger = logging.getLogger(__name__)


class Memo(models.Model):
    _name = 'memo.memo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Memo'

    name = fields.Char("Title", required=True, help="Title of the memo")
    memo_number = fields.Char("Memo Number", readonly=True, copy=False)
    date = fields.Date("Memo Date", default=fields.Date.today, help="Date when the memo is created")
    branch_id = fields.Many2one('res.municipality', string='Branch', tracking=True)
    subject = fields.Text("Subject")
    requester_id = fields.Many2one("res.users", string="Responsible Officer", default=lambda self: self.env.user,
                                   help="Memo creator", tracking=True)
    requester_sign = fields.Binary(string="Responsible Officer Signature", copy=False)
    target_group_ids = fields.Many2many("res.groups", string="Target Group Audience",
                                        help="User groups allowed to see the memo")
    target_audience_ids = fields.Many2many("hr.job", string="Target Audience")

    # Approval roles
    approver_id = fields.Many2one("res.users", string="Approver", help="Person who must approve the memo",
                                  tracking=True)
    approver_sign = fields.Binary(string="Approver Signature", copy=False)
    quality_assurance_ids = fields.One2many('memo.quality.assurance', 'memo_request_id',
                                            string="Quality Assurance Users",
                                            store=True, readonly=False)
    quality_assurance_required = fields.Boolean(string="Quality Assurance Required?", default=True)
    recommender_ids = fields.One2many('memo.approver', 'memo_request_id', string="Recommenders",
                                      store=True, readonly=False)
    recommendation = fields.Html("Recommendation")
    user_ids = fields.Many2many('res.users', string="Users",
                                compute='_compute_user_ids', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('quality_assurance', 'Quality Assurance'),
        ('complete_quality_assurance', 'Complete Quality Assurance'),
        ('change_requested', 'Change Requested'),
        ('recommend', 'Recommend'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('locked', 'Locked'),
    ], default='draft', tracking=True, help="Workflow status")
    submission_type = fields.Selection([
        ('general', 'General'),
        ('memo', 'Memo'),
        ('circular', 'Circular'),
        ('procurement', 'Procurement'),
    ], string="Submission Type", default='memo', store=True)

    change_reason = fields.Text("Change Request Reason", help="Comments if change is requested")
    rejection_reason = fields.Text("Rejection Reason")
    is_financial = fields.Boolean("Is Financial Detail Visible on Report", default=False,
                                  compute="_compute_is_financial", readonly=False)
    financial_sentence = fields.Text("Financial Sentences")
    under_grant_management = fields.Selection([
        ('hsdg', 'HSDG'),
        ('isopg', 'ISOPG'),
    ], string="Under Grant Management")
    dg_financial = fields.Boolean("Is Financial Detail Visible on Report", default=False,
                                  compute="_compute_is_financial", readonly=False)
    funds = fields.Char("Funds")
    responsibility = fields.Char("Responsibility")
    objective = fields.Char("Objective")
    item = fields.Char("Item")
    project = fields.Char("Project")
    asset = fields.Char("Asset")
    regional_identifier = fields.Char("Regional Identifier")
    amount_paid = fields.Char("Amount Paid")
    service_provider = fields.Char("Service Provider")
    infrastructure = fields.Char("Infrastructure")
    purpose_body = fields.Html("Purpose")
    background_body = fields.Html("Background")
    motivation_body = fields.Html("Motivation")
    ack_required = fields.Boolean("Require Acknowledgment")
    acknowledged_ids = fields.Many2many("res.users", relation='memo_acknowledged_rel', column1='memo_id',
                                        column2='user_id', string="Acknowledged By")
    read_count = fields.Integer("Read Count", compute="_compute_read_count")
    acknowledged_body = fields.Html("Acknowledgment")
    acknowledged_sign = fields.Binary(string="Acknowledged Signature", copy=False)
    acknowledged_date = fields.Datetime(string="Acknowledged Date")
    template_id = fields.Many2one('memo.template', string="Template",
                                  domain="[('submission_type', '=', submission_type)]", tracking=True)
    version_ids = fields.One2many('memo.version', 'memo_id', string="Versions")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, domain="[]")
    submission_recommended = fields.Boolean("Submission Recommend", default=False,
                                            compute="_compute_submission_recommended")
    approve_date = fields.Datetime(string="Date")
    approve_comment = fields.Text(string="Comment")
    document_upload_ids = fields.One2many("memo.document.upload", "memo_id", string="Supporting documents", copy=False,
                                          required=True)
    attachment_id = fields.Many2one('ir.attachment', string="Memo Document")
    folder_id = fields.Many2one('documents.document', string="Document Folder", readonly=True,
                                domain="[('type', '=', 'folder')]")

    chief_directorate_id = fields.Many2one('hr.department', string="Chief Directorate", required=True, tracking=True)
    directorate_id = fields.Many2one('hr.department', string="Directorate",
                                     domain="[('parent_id', '=', chief_directorate_id)]", tracking=True)

    department_detail_street = fields.Char(string='Street', readonly=False)
    department_detail_street2 = fields.Char(string='Street2', readonly=False)
    department_detail_zip = fields.Char(string='Zip', readonly=False)
    department_detail_city = fields.Char(string='City', readonly=False)
    department_detail_state_id = fields.Many2one('res.country.state', string='State', readonly=False)
    department_detail_country_id = fields.Many2one('res.country', string='Country', readonly=False)
    department_detail_email = fields.Char(string='Email', readonly=False)
    department_detail_phone = fields.Char(string='Phone', readonly=False)
    department_detail_mobile = fields.Char(string='Mobile', readonly=False)
    recipient = fields.Text("Recipient", tracking=True)
    enquiries = fields.Text("Enquiries", tracking=True)
    record_security = fields.Selection([
        ('private', 'Private'),
        ('confidential', 'Confidential'),
        ('public', 'Public'),
    ], string="Record Security", help="Visibility of the Memo")
    is_project_status = fields.Boolean("Is Project Status Visible on Report", default=False, readonly=False)
    project_status = fields.Html("Project Status")
    show_submit_qa = fields.Boolean("Show Submit QA Button",
                                    compute="_compute_show_submit_recommendation", default=False)
    show_complete_qa = fields.Boolean("Show complete QA Button",
                                      compute="_compute_show_submit_recommendation", default=False)
    show_change_request = fields.Boolean("Show Change Request/Reject Button",
                                         compute="_compute_show_submit_recommendation", default=False)
    show_submit_recommendation = fields.Boolean("Show Submit Recommendation Button",
                                                compute="_compute_show_submit_recommendation", default=False)
    make_readonly = fields.Boolean("Make Readony Button",
                                   compute="_compute_show_submit_recommendation", default=False)
    is_creator = fields.Boolean("Is Createor", compute="_compute_show_submit_recommendation", default=False)
    allowed_user_ids = fields.Many2many('res.users', 'memo_allowed_user_rel', 'memo_id', 'user_id',
                                        string='Turn-based Allowed Users', compute='_compute_allowed_user_ids',
                                        store=True, compute_sudo=True, )
    acting_letter_id = fields.Many2one('ir.attachment', string="Acting Letter Evidence",
                                       help="Upload acting letter when changing/deleting QA or recommender",
                                       copy=False, )
    acting_letter_name = fields.Char(related="acting_letter_id.name", store=True, readonly=False)
    datas = fields.Binary(related='acting_letter_id.datas', readonly=False)
    show_acting_letter = fields.Boolean(
        compute="_compute_acting_letter_visibility", store=False)

    @api.onchange('datas')
    def _onchange_datas(self):
        if self.acting_letter_name:
            vals = {'name': self.acting_letter_name, 'datas': self.datas}
            if not self.acting_letter_id:
                attachment = self.env['ir.attachment'].sudo().create(vals)
                self.acting_letter_id = attachment.id
            else:
                self.acting_letter_id.sudo().write(vals)

    @api.depends('state')
    def _compute_acting_letter_visibility(self):
        for memo in self:
            user = self.env.user
            can_see = False
            if user.has_group('e_system.group_it_team') or user.id in [memo.create_uid.id, memo.requester_id.id]:
                if memo.state not in ['draft']:
                    can_see = True
            memo.show_acting_letter = can_see

    @api.constrains('memo_number')
    def _check_memo_number_unique(self):
        for memo in self:
            if memo.memo_number and self.env['memo.memo'].search_count([('memo_number', '=', memo.memo_number)]) > 1:
                raise ValidationError(_('Another memo already has this memo number'))

    @api.depends(
        'create_uid', 'requester_id', 'state',
        'quality_assurance_ids.user_id', 'quality_assurance_ids.sign_initials', 'quality_assurance_ids.sequence',
        'recommender_ids.user_id', 'recommender_ids.sign_initials', 'recommender_ids.sequence',
        'approver_id', 'approver_sign',
        'ack_required', 'acknowledged_ids',
    )
    def _compute_allowed_user_ids(self):
        for rec in self:
            allowed = set()

            # Always: creator + requester
            if rec.create_uid:
                allowed.add(rec.create_uid.id)
            if rec.requester_id:
                allowed.add(rec.requester_id.id)

            # QA: all who already signed keep access; the next in sequence gets access
            qa_signed_users = rec.quality_assurance_ids.filtered(lambda q: q.sign_initials).mapped('user_id')
            allowed.update(u.id for u in qa_signed_users)
            if rec.state == 'quality_assurance':
                pending_qas = rec.quality_assurance_ids.filtered(lambda q: not q.sign_initials).sorted('sequence')
                if pending_qas:
                    next_qa_user = pending_qas[0].user_id
                    if next_qa_user:
                        allowed.add(next_qa_user.id)

            # Recommenders: same logic
            rec_signed_users = rec.recommender_ids.filtered(lambda r: r.sign_initials).mapped('user_id')
            allowed.update(u.id for u in rec_signed_users)
            if rec.state == 'recommend':
                pending_recs = rec.recommender_ids.filtered(lambda r: not r.sign_initials).sorted('sequence')
                if pending_recs:
                    next_rec_user = pending_recs[0].user_id
                    if next_rec_user:
                        allowed.add(next_rec_user.id)

            # Approver: only when it’s due; after signing, keep access
            if rec.state == 'pending_approval' and rec.approver_id:
                allowed.add(rec.approver_id.id)
            if rec.approver_sign and rec.approver_id:
                allowed.add(rec.approver_id.id)

            # Acknowledgers: only after approver signed (so not before their time)
            if rec.approver_sign and rec.ack_required:
                allowed.update(rec.acknowledged_ids.ids)

            rec.allowed_user_ids = [(6, 0, list(allowed))]

    @api.constrains('memo_number')
    def _check_memo_number_unique(self):
        for memo in self:
            if memo.memo_number and self.env['memo.memo'].search_count([('memo_number', '=', memo.memo_number)]) > 1:
                raise ValidationError(_('Another memo already has this memo number'))

    @api.constrains('requester_id', 'approver_id',
                    'quality_assurance_ids', 'recommender_ids', 'acknowledged_ids')
    def _check_unique_user_roles(self):
        for memo in self:
            role_users = []

            if memo.requester_id:
                role_users.append(('Requester', memo.requester_id.id))
            if memo.approver_id and memo.submission_type != 'general':
                role_users.append(('Approver', memo.approver_id.id))

            qa_user_ids = memo.quality_assurance_ids.mapped('user_id.id')
            for uid in qa_user_ids:
                role_users.append(('Quality Assurance Team', uid))

            recommender_user_ids = memo.recommender_ids.mapped('user_id.id')
            for uid in recommender_user_ids:
                role_users.append(('Recommender', uid))

            if memo.acknowledged_ids:
                for uid in memo.acknowledged_ids.ids:
                    role_users.append(('Acknowledged', uid))

            # Check for duplicates
            seen = {}
            for role, uid in role_users:
                if uid in seen:
                    raise ValidationError(
                        f"User '{self.env['res.users'].browse(uid).name}' is assigned multiple roles "
                        f"('{seen[uid]}' and '{role}') in the same memo. Roles must be unique per user."
                    )
                seen[uid] = role

    @api.onchange('company_id')
    def _onchange_company(self):
        if self.company_id:
            self.department_detail_street = self.company_id.street or ''
            self.department_detail_street2 = self.company_id.street2 or ''
            self.department_detail_zip = self.company_id.zip or ''
            self.department_detail_city = self.company_id.city or ''
            self.department_detail_state_id = self.company_id.state_id.id or False
            self.department_detail_country_id = self.company_id.country_id.id or False
            self.department_detail_email = self.company_id.email or ''
            self.department_detail_phone = self.company_id.phone or ''
            self.department_detail_mobile = self.company_id.mobile or ''

    def action_preview_report(self):
        self.ensure_one()
        if self.attachment_id:
            self.attachment_id.sudo().unlink()
            self.attachment_id = False  # reset before reuse
        Report = self.env['ir.actions.report']
        submission_report_pdfs = []
        report_pdf, _ = Report._render_qweb_pdf('e_system.action_report_memo_management', self.id)
        if report_pdf:
            submission_report_pdfs.append(report_pdf)
        filename = f"Memo_{self.name or self.id}.pdf"
        for doc in self.document_upload_ids.sorted("sequence"):
            attachment = doc.attachment_id
            if not attachment or not attachment.datas:
                _logger.warning(f"[Skip] Missing or empty attachment in document ID {doc.id}")
                continue

            try:
                raw_data = base64.b64decode(attachment.datas)
            except Exception as e:
                _logger.warning(f"[Decode Error] {attachment.name}: {e}")
                continue

            mimetype = attachment.mimetype or ''
            _logger.info(f"[Process] {attachment.name} (type={mimetype}, size={len(raw_data)} bytes)")
            # Handle PDFs
            if mimetype == 'application/pdf':
                submission_report_pdfs.append(raw_data)

            # Handle images
            elif mimetype in ['image/jpeg', 'image/png', 'image/jpg']:
                try:
                    pdf_data = self.image_to_a4_pdf(raw_data)
                    submission_report_pdfs.append(pdf_data)
                except Exception as e:
                    _logger.warning(f"[Image Convert Error] {attachment.name}: {e}")
            else:
                _logger.warning(f"[Skip] Unsupported file type: {attachment.name} ({mimetype})")

        if not submission_report_pdfs:
            raise UserError("No valid PDF documents found to merge.")

        try:
            final_pdf = pdf.merge_pdf(submission_report_pdfs)
        except Exception as e:
            raise UserError(f"Unexpected error during merge: {e}")

        base64_pdf = base64.b64encode(final_pdf)

        attachment = self.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': base64_pdf,
            'res_model': 'memo.memo',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        self.sudo().write({'attachment_id': attachment.id})
        if not self.folder_id:
            self.sudo()._assign_document_folder()
        document = self.env['documents.document'].sudo().search([
            ('attachment_id', '=', self.attachment_id.id)
        ], limit=1)

        if document:
            document.sudo().write({
                'attachment_id': self.attachment_id.id,
                'folder_id': self.folder_id.id,
                'owner_id': self.requester_id.id,
                'res_model': self._name,
                'res_id': self.id,
                'name': self.name,
            })
        else:
            self.env['documents.document'].sudo().create({
                'attachment_id': self.attachment_id.id,
                'folder_id': self.folder_id.id,
                'owner_id': self.requester_id.id,
                'res_model': self._name,
                'res_id': self.id,
                'name': self.name,
            })
        preview_url = f'/web/content/{self.attachment_id.id}?download=false'
        if not preview_url:
            raise ValidationError("Preview not supported for this file type.")
        return {
            'type': 'ir.actions.act_url',
            'url': preview_url,
            'target': 'new',
        }

    def _compute_is_financial(self):
        for memo in self:
            if memo.financial_sentence or memo.funds or memo.responsibility or memo.objective or memo.item or memo.project or memo.asset or memo.regional_identifier or memo.amount_paid or memo.service_provider or memo.infrastructure:
                memo.is_financial = True
            else:
                memo.is_financial = False

    @api.depends('recommender_ids')
    def _compute_user_ids(self):
        for request in self:
            request.sudo().write({'user_ids': [(6, 0, [request.recommender_ids.mapped('user_id.id')])]})

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.purpose_body = self.template_id.purpose_body
            self.background_body = self.template_id.background_body
            self.motivation_body = self.template_id.motivation_body

    @api.model
    def create(self, vals):
        sequence_codes = {
            "general": "general.general",
            "memo": "memo.memo",
            "circular": "circular.circular",
            "procurement": "procurement.procurement",
        }

        submission_type = vals.get("submission_type") or self.env.context.get("default_submission_type")
        if not vals.get("memo_number"):
            seq_code = sequence_codes.get(submission_type)
            if seq_code:
                next_number = self.env["ir.sequence"].sudo().next_by_code(seq_code)
                vals["memo_number"] = next_number or "/"
            else:
                _logger.warning(f"No sequence code defined for submission_type: {submission_type}")

        res = super().create(vals)
        res.sudo()._assign_document_folder()
        return res

    def _is_structure_change(self,cmds, safe_fields):
        """
        Return True if o2m command list contains structural changes:
        - (0) create a new line (new person)      -> structure
        - (2)/(3) unlink/clear a line             -> structure
        - (6) replace full set                    -> structure
        - (1) update: if user_id/sequence or any field not in safe_fields -> structure
          Otherwise (status/comment/sign/sign_date) -> NOT structure.
        """
        if not cmds:
            return False
        for cmd in cmds:
            if not isinstance(cmd, (list, tuple)) or not cmd:
                continue
            op = cmd[0]
            # (0) create, (2)/(3) unlink, (6) replace set
            if op in (0, 2, 3, 6):
                return True
            # (1) update – check which fields are updated
            if op == 1:
                vals = (cmd[2] or {})
                if 'user_id' in vals or 'sequence' in vals:
                    return True
                unknown = set(vals.keys()) - safe_fields
                if unknown:
                    return True
        return False

    def write(self, vals):
        safe_fields = {'status', 'comment', 'sign_initials', 'date'}
        for rec in self:
            structure_change = False

            # Detect O2M structure changes
            if 'recommender_ids' in vals and self._is_structure_change(vals['recommender_ids'], safe_fields):
                structure_change = True

            if 'quality_assurance_ids' in vals and self._is_structure_change(vals['quality_assurance_ids'],
                                                                             safe_fields):
                structure_change = True

            # Detect Approver change
            if 'approver_id' in vals and vals.get('approver_id') != (
                    rec.approver_id.id if rec.approver_id else False):
                structure_change = True

            if not structure_change:
                continue  # no critical structural change — proceed

            # -----------------------------------------------------------------
            # Stage restriction check
            # -----------------------------------------------------------------
            protected_states = ['quality_assurance', 'recommend', 'pending_approval', 'approved']
            if rec.state in protected_states:
                if not self.env.user.has_group('e_system.group_it_team'):
                    raise ValidationError(
                        _("Only the I.T Team can change QA, Recommenders, or Approver once the memo is submitted.")
                    )

            elif rec.state not in ['draft', 'change_requested']:
                # Allow only Creator or Author before submission
                if self.env.user not in (rec.create_uid, rec.requester_id):
                    raise ValidationError(
                        _("Only the Creator or Author can change roles before QA/Recommendation.")
                    )

            # -----------------------------------------------------------------
            # Acting letter validation
            # -----------------------------------------------------------------
            evidence = vals.get('acting_letter_id') or rec.acting_letter_id
            if not evidence:
                # Try to find acting letter in affected child lines
                evidence_found = False

                def _check_child(cmds, model_name):
                    for cmd in cmds or []:
                        if not isinstance(cmd, (list, tuple)):
                            continue
                        op = cmd[0]
                        if op == 0 and cmd[2].get('acting_letter_id'):
                            return True
                        if op == 1:
                            vals_line = cmd[2] or {}
                            if vals_line.get('acting_letter_id'):
                                return True
                            rid = cmd[1]
                            if rid:
                                rrec = self.env[model_name].browse(rid)
                                if rrec.acting_letter_id:
                                    return True
                        if op in (2, 3):
                            rid = cmd[1]
                            if rid:
                                rrec = self.env[model_name].browse(rid)
                                if rrec.acting_letter_id:
                                    return True
                    return False

                if _check_child(vals.get('recommender_ids'), 'memo.approver'):
                    evidence_found = True
                elif _check_child(vals.get('quality_assurance_ids'), 'memo.quality.assurance'):
                    evidence_found = True
                    
                if not evidence_found and rec.state != 'draft':
                    raise ValidationError(_(
                        "You must upload an Acting Letter (evidence) on the Memo or on the affected line(s) "
                        "before changing, removing, or replacing QA, Recommenders, or Approver."
                    ))

        return super(Memo, self).write(vals)

    def _assign_document_folder(self):
        user = self.requester_id
        if self.chief_directorate_id:
            dept_name = self.chief_directorate_id.name
            root_folder = self.env['documents.document'].sudo().search([
                ('name', '=', 'Business Unit'), ('folder_id', '=', False), ('type', '=', 'folder')
            ], limit=1)
            if not root_folder:
                root_folder = self.env['documents.document'].sudo().create({'name': 'Business Unit', 'type': 'folder'})

            dept_folder = self.env['documents.document'].sudo().search([
                ('name', '=', dept_name), ('folder_id', '=', root_folder.id), ('type', '=', 'folder')
            ], limit=1)
            if not dept_folder:
                dept_folder = self.env['documents.document'].sudo().create({
                    'name': dept_name,
                    'folder_id': root_folder.id,
                    'type': 'folder'
                })

            if self.submission_type == 'general':
                memo_folder = self.env['documents.document'].sudo().search([
                    ('name', '=', 'General'), ('folder_id', '=', dept_folder.id), ('type', '=', 'folder')
                ], limit=1)
                if not memo_folder:
                    memo_folder = self.env['documents.document'].sudo().create({
                        'name': 'General',
                        'folder_id': dept_folder.id,
                        'type': 'folder'
                    })
                self.sudo().write({'folder_id': memo_folder.id})

            if self.submission_type == 'memo':
                memo_folder = self.env['documents.document'].sudo().search([
                    ('name', '=', 'Memos'), ('folder_id', '=', dept_folder.id), ('type', '=', 'folder')
                ], limit=1)
                if not memo_folder:
                    memo_folder = self.env['documents.document'].sudo().create({
                        'name': 'Memos',
                        'folder_id': dept_folder.id,
                        'type': 'folder'
                    })
                self.sudo().write({'folder_id': memo_folder.id})

            if self.submission_type == 'circular':
                memo_folder = self.env['documents.document'].sudo().search([
                    ('name', '=', 'Circulars'), ('folder_id', '=', dept_folder.id), ('type', '=', 'folder')
                ], limit=1)
                if not memo_folder:
                    memo_folder = self.env['documents.document'].sudo().create({
                        'name': 'Circulars',
                        'folder_id': dept_folder.id,
                        'type': 'folder'
                    })
                self.sudo().write({'folder_id': memo_folder.id})

            if self.submission_type == 'procurement':
                memo_folder = self.env['documents.document'].sudo().search([
                    ('name', '=', 'Procurements'), ('folder_id', '=', dept_folder.id), ('type', '=', 'folder')
                ], limit=1)
                if not memo_folder:
                    memo_folder = self.env['documents.document'].sudo().create({
                        'name': 'Procurements',
                        'folder_id': dept_folder.id,
                        'type': 'folder'
                    })
                self.sudo().write({'folder_id': memo_folder.id})
        else:
            raise ValidationError("Please add department under Responsible Officer profile.")

    def _compute_submission_recommended(self):
        for submission in self:
            if submission.sudo().recommender_ids:
                remaining_approval = submission.sudo().recommender_ids.filtered(
                    lambda l: l.status not in ('Recommended', 'Funds Available', 'Supported') and not l.sign_initials)
                if remaining_approval:
                    submission.submission_recommended = False
                else:
                    if self.env.user.id == submission.approver_id.id:
                        submission.submission_recommended = True
                    else:
                        submission.submission_recommended = False
            else:
                if submission.submission_type in ['general',
                                                  'circular'] and self.env.user.id == submission.approver_id.id:
                    submission.submission_recommended = True
                else:
                    submission.submission_recommended = False

    def _compute_show_submit_recommendation(self):
        for memo in self:
            if self.env.user.id not in [memo.requester_id.id, memo.create_uid.id]:
                memo.make_readonly = True
                memo.is_creator = True
            else:
                memo.make_readonly = False
                memo.is_creator = False
            if self.env.user.id in [memo.requester_id.id, memo.create_uid.id] and memo.state in ['draft',
                                                                                                 'change_requested'] and memo.quality_assurance_required == True:
                memo.show_submit_qa = True
            else:
                memo.show_submit_qa = False
            if memo.sudo().quality_assurance_ids:
                remaining_approval = memo.sudo().quality_assurance_ids.filtered(
                    lambda l: l.required and (l.status != 'Completed' or not l.sign_initials))
                if not remaining_approval and self.env.user.id in memo.quality_assurance_ids.mapped(
                        'user_id.id') and memo.state in ['quality_assurance']:
                    memo.show_complete_qa = True
                else:
                    memo.show_complete_qa = False
            else:
                memo.show_complete_qa = False
            if (self.env.user.id in memo.sudo().quality_assurance_ids.mapped(
                    'user_id.id') and memo.state == 'quality_assurance') or (
                    self.env.user.id in memo.sudo().recommender_ids.mapped('user_id.id') and memo.state == 'recommend'):
                memo.show_change_request = True
            else:
                memo.show_change_request = False
            if self.env.user.id in [memo.requester_id.id,
                                    memo.create_uid.id] and memo.state == 'complete_quality_assurance':
                memo.show_submit_recommendation = True
            else:
                memo.show_submit_recommendation = False

    @api.depends('acknowledged_ids')
    def _compute_read_count(self):
        for rec in self:
            rec.read_count = len(rec.acknowledged_ids)

    def action_sign_request(self):
        if not self.requester_id:
            if self.submission_type == 'memo':
                raise ValidationError("Please add Responsible Officer before sign the memo.")
            if self.submission_type == 'procurement':
                raise ValidationError("Please add Responsible Officer before sign the procurement.")
        if self.requester_id.id != self.env.user.id:
            raise ValidationError("Only Responsible Officer can sign.")
        return {
            'name': 'Sign Request',
            'type': 'ir.actions.act_window',
            'res_model': 'memo.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_memo_id': self.id,
                'default_field': 'requester_sign',
                'default_user_id': self.requester_id.id,
                'default_mode': 'memo',
            }
        }

    def action_sign_approver(self):
        if not self.approver_id:
            if self.submission_type == 'memo':
                raise ValidationError("Please add Approver before sign the memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Please add Approver before sign the circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Please add Approver before sign the procurement.")
        if self.approver_id.id != self.env.user.id:
            if self.submission_type == 'memo':
                raise ValidationError("Only approver can sign approve memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Only approver can sign approve circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Only approver can sign approve procurement.")
        if self.sudo().quality_assurance_ids:
            remaining_approval = self.sudo().quality_assurance_ids.filtered(
                lambda l: l.required and (l.status != 'Completed' or not l.sign_initials))
            if remaining_approval:
                raise ValidationError(
                    "All Quality Assurance users must be signed and Quality Assurance Status marked as Completed.")
        if self.sudo().recommender_ids:
            pending_recommenders = self.sudo().recommender_ids.filtered(
                lambda l: l.required and (
                        l.status not in ('Recommended', 'Funds Available', 'Supported') or not l.sign_initials))
            if pending_recommenders:
                raise ValidationError("All Recommender user must be signed and Recommended document.")
        if self.approve_comment and not re.search(r'\w+', self.approve_comment):
            raise UserError("You must provide a valid comment before approving (not just spaces or symbols).")
        return {
            'name': 'Sign Approver',
            'type': 'ir.actions.act_window',
            'res_model': 'memo.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_memo_id': self.id,
                'default_field': 'approver_sign',
                'default_user_id': self.approver_id.id,
                'default_mode': 'memo',
            }
        }

    def action_sign_acknowledged(self):
        if not self.acknowledged_ids:
            if self.submission_type == 'general':
                raise ValidationError("Please add acknowledged person before sign the general memo.")
            if self.submission_type == 'memo':
                raise ValidationError("Please add acknowledged person before sign the memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Please add acknowledged person before sign the circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Please add acknowledged person before sign the procurement.")
        if self.acknowledged_ids[0].id != self.env.user.id:
            if self.submission_type == 'general':
                raise ValidationError("Only acknowledged person can sign general memo.")
            if self.submission_type == 'memo':
                raise ValidationError("Only acknowledged person can sign memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Only acknowledged person can sign circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Only acknowledged person can sign procurement.")
        if not self.approver_sign:
            raise ValidationError("First Approver must be sign this document.")
        return {
            'name': 'Sign Acknowledgment',
            'type': 'ir.actions.act_window',
            'res_model': 'memo.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_memo_id': self.id,
                'default_field': 'acknowledged_sign',
                'default_user_id': self.acknowledged_ids[0].id,
                'default_mode': 'memo',
            }
        }

    def action_quality_assurance(self):
        if self.quality_assurance_required and not self.quality_assurance_ids:
            if self.submission_type == 'memo':
                raise ValidationError("Please add Quality Assurance before submit the memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Please add Quality Assurance before submit the circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Please add Quality Assurance before submit the procurement.")
        self.state = 'quality_assurance'
        self._notify_quality_assurance()

    def _notify_quality_assurance(self):
        pending_quality_assurance = self.quality_assurance_ids.filtered(
            lambda r: not r.sign_initials or r.status not in ['Completed', 'Non-Completed'])
        if pending_quality_assurance:
            next_quality_assurance = pending_quality_assurance.sorted(key=lambda r: r.sequence)[0]
            next_quality_assurance.sudo().action_send_mail()

    def action_done_quality_assurance(self):
        if self.sudo().quality_assurance_ids:
            remaining_approval = self.sudo().quality_assurance_ids.filtered(
                lambda l: l.required and (l.status != 'Completed' or not l.sign_initials))
            if remaining_approval:
                raise ValidationError(
                    "All Quality Assurance users must be signed and Quality Assurance Status marked as Completed.")
        if self.env.user.id not in self.sudo().quality_assurance_ids.mapped('user_id.id'):
            if self.submission_type == 'general':
                raise ValidationError("Only Quality Assurance User can complete quality assurance general.")
            if self.submission_type == 'memo':
                raise ValidationError("Only Quality Assurance User can complete quality assurance memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Only Quality Assurance User can complete quality assurance circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Only Quality Assurance User can complete quality assurance procurement.")

        if self.submission_type not in ['general', 'circular']:
            template = self.env.ref('e_system.email_template_complete_quality_assurance')
            if self.submission_type == 'memo':
                action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_memo_dashboard')
            if self.submission_type == 'circular':
                action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
            if self.submission_type == 'procurement':
                action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_procurement_dashboard')
            base_url = self.sudo().get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            user = self.sudo().requester_id.name
            template.with_context(approve_user=user, url=url).sudo().send_mail(self.id, force_send=True,
                                                                               email_values={
                                                                                   'email_to': self.sudo().requester_id.partner_id.email})
            self.state = 'complete_quality_assurance'
        if self.submission_type in ['general', 'circular']:
            if self.submission_type == 'circular':
                action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
            if self.submission_type == 'general':
                action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_general_dashboard')
            template_1 = self.env.ref('e_system.email_template_complete_quality_assurance')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            user = self.sudo().requester_id.name
            template_1.with_context(approve_user=user, url=url).sudo().send_mail(self.id, force_send=True,
                                                                                 email_values={
                                                                                     'email_to': self.sudo().requester_id.partner_id.email})
            self.state = 'complete_quality_assurance'
            template = self.env.ref('e_system.mail_template_general_submit')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            user = self.sudo().approver_id.name
            template.with_context(approve_user=user, url=url).sudo().send_mail(self.id, force_send=True,
                                                                               email_values={
                                                                                   'email_to': self.sudo().approver_id.partner_id.email})
            self.state = 'pending_approval'

    def action_submit(self):
        if not self.recommender_ids:
            if self.submission_type == 'memo':
                raise ValidationError("Please add recommenders before submit the memo.")
            if self.submission_type == 'procurement':
                raise ValidationError("Please add recommenders before submit the procurement.")
        if not self.requester_sign:
            raise ValidationError("Please add Responsible Officer signature before submit for recommendation.")
        if self.create_uid != self.env.user and self.requester_id.id != self.env.user.id:
            raise ValidationError(
                "Only memo document create user or Responsible Officer user can submit for recommendation.")
        self.state = 'recommend'
        self._notify_next_recommender()

    def _notify_next_recommender(self):
        pending_recommenders = self.recommender_ids.filtered(
            lambda r: not r.sign_initials and r.status not in ['Recommended', 'Non-Recommended', 'Funds Available',
                                                               'Funds Not Available', 'Supported', 'Not Supported'])
        if pending_recommenders:
            next_recommender = pending_recommenders.sorted(key=lambda r: r.sequence)[0]
            next_recommender.sudo().sent_date = fields.Date.today()
            next_recommender.sudo().action_send_mail()
        else:
            # All recommenders are done — now notify the approver
            self.state = 'pending_approval'
            self._notify_next_approver()

    def action_submit_for_approval(self):
        if not self.approver_id:
            raise ValidationError("Please add approver before submit for approval.")
        if self.submission_type == 'general' and self.quality_assurance_required == False:
            self.state = 'pending_approval'
            template = self.env.ref('e_system.mail_template_general_submit')
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_general_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            user = self.approver_id.name
            template.with_context(approve_user=user, url=url).send_mail(self.id, force_send=True,
                                                                        email_values={
                                                                            'email_to': self.approver_id.partner_id.email})
        if self.submission_type == 'circular' and self.quality_assurance_required == False:
            self.state = 'pending_approval'
            template = self.env.ref('e_system.mail_template_circular_submit')
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})

    def _notify_next_approver(self):
        if self.submission_type == 'memo':
            template = self.env.ref('e_system.mail_template_memo_submit')
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_memo_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})
        if self.submission_type == 'circular':
            template = self.env.ref('e_system.mail_template_circular_submit')
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})
        if self.submission_type == 'procurement':
            template = self.env.ref('e_system.mail_template_procurement_submit')
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_procurement_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})

    def action_approve_memo(self):
        if self.recommender_ids:
            remaining_approval = self.recommender_ids.filtered(
                lambda l: l.required and (
                        l.status not in ('Recommended', 'Funds Available', 'Supported') or not l.sign_initials))
            if remaining_approval:
                raise ValidationError("Recommender must be signed and recommended.")
        if self.create_uid == self.env.user:
            if self.submission_type == 'memo':
                raise ValidationError(
                    "You are not allowed to approve your own memo document. Please contact your approvers."
                )
            if self.submission_type == 'circular':
                raise ValidationError(
                    "You are not allowed to approve your own circular document. Please contact your approvers."
                )
            if self.submission_type == 'procurement':
                raise ValidationError(
                    "You are not allowed to approve your own procurement document. Please contact your approvers."
                )
        if self.approver_id.id != self.env.user.id:
            if self.submission_type == 'general':
                raise ValidationError("Only approver can approve memo.")
            if self.submission_type == 'memo':
                raise ValidationError("Only approver can approve memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Only approver can approve circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Only approver can approve procurement.")
        if not self.approver_sign:
            if self.submission_type == 'general':
                raise ValidationError("Please add approver signature before approve general memo.")
            if self.submission_type == 'memo':
                raise ValidationError("Please add approver signature before approve memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Please add approver signature before approve circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Please add approver signature before approve procurement.")
        self.state = 'approved'
        self.submission_recommended = False
        if self.sudo().attachment_id:
            self.sudo().attachment_id.unlink()
            self.sudo().attachment_id = False  # reset before reuse
        Report = self.env['ir.actions.report']
        submission_report_pdfs = []
        report_pdf, _ = Report._render_qweb_pdf('e_system.action_report_memo_management', self.id)
        if report_pdf:
            submission_report_pdfs.append(report_pdf)
        filename = f"Memo_{self.name or self.id}.pdf"
        for doc in self.document_upload_ids.sorted("sequence"):
            attachment = doc.attachment_id
            if not attachment or not attachment.datas:
                _logger.warning(f"[Skip] Missing or empty attachment in document ID {doc.id}")
                continue

            try:
                raw_data = base64.b64decode(attachment.datas)
            except Exception as e:
                _logger.warning(f"[Decode Error] {attachment.name}: {e}")
                continue

            mimetype = attachment.mimetype or ''
            _logger.info(f"[Process] {attachment.name} (type={mimetype}, size={len(raw_data)} bytes)")
            # Handle PDFs
            if mimetype == 'application/pdf':
                submission_report_pdfs.append(raw_data)

            # Handle images
            elif mimetype in ['image/jpeg', 'image/png', 'image/jpg']:
                try:
                    pdf_data = self.image_to_a4_pdf(raw_data)
                    submission_report_pdfs.append(pdf_data)
                except Exception as e:
                    _logger.warning(f"[Image Convert Error] {attachment.name}: {e}")
            else:
                _logger.warning(f"[Skip] Unsupported file type: {attachment.name} ({mimetype})")

        if not submission_report_pdfs:
            raise UserError("No valid PDF documents found to merge.")

        try:
            final_pdf = pdf.merge_pdf(submission_report_pdfs)
        except Exception as e:
            raise UserError(f"Unexpected error during merge: {e}")

        base64_pdf = base64.b64encode(final_pdf)
        attachment = self.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': base64_pdf,
            'res_model': 'memo.memo',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        self.sudo().write({'attachment_id': attachment.id})
        if self.submission_type == 'memo':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_memo_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            partner_ids = [self.create_uid.partner_id.id]
            if self.requester_id:
                partner_ids.extend([self.requester_id.partner_id.id])
            if self.quality_assurance_ids:
                partner_ids.extend(self.quality_assurance_ids.mapped('user_id.partner_id.id'))
            if self.recommender_ids:
                partner_ids.extend(self.recommender_ids.mapped('user_id.partner_id.id'))
            if self.acknowledged_ids:
                partner_ids.extend(self.acknowledged_ids.mapped('user_id.partner_id.id'))
            self.message_post(
                body=Markup(
                    '<p>The e-submission memo application <strong>{name}</strong> has approved.</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                    name=self.name,
                    link=url
                ),
                partner_ids=partner_ids,
                subject="Circular Document Approved",
                email_from=self.env.user.partner_id.email or '',
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                attachment_ids=self.attachment_id.ids,
            )
        if self.submission_type == 'circular':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            partner_ids = [self.create_uid.partner_id.id]
            if self.requester_id:
                partner_ids.extend([self.requester_id.partner_id.id])
            if self.quality_assurance_ids:
                partner_ids.extend(self.quality_assurance_ids.mapped('user_id.partner_id.id'))
            if self.recommender_ids:
                partner_ids.extend(self.recommender_ids.mapped('user_id.partner_id.id'))
            if self.acknowledged_ids:
                partner_ids.extend(self.acknowledged_ids.mapped('user_id.partner_id.id'))
            self.message_post(
                body=Markup(
                    '<p>The e-submission circular application <strong>{name}</strong> has approved.</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                    name=self.name,
                    link=url
                ),
                partner_ids=partner_ids,
                subject="Circular Document Approved",
                email_from=self.env.user.partner_id.email or '',
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                attachment_ids=self.attachment_id.ids,
            )
        if self.submission_type == 'procurement':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_procurement_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
            partner_ids = [self.create_uid.partner_id.id]
            if self.requester_id:
                partner_ids.extend([self.requester_id.partner_id.id])
            if self.quality_assurance_ids:
                partner_ids.extend(self.quality_assurance_ids.mapped('user_id.partner_id.id'))
            if self.recommender_ids:
                partner_ids.extend(self.recommender_ids.mapped('user_id.partner_id.id'))
            if self.acknowledged_ids:
                partner_ids.extend(self.acknowledged_ids.mapped('user_id.partner_id.id'))
            self.message_post(
                body=Markup(
                    '<p>The e-submission procurement application <strong>{name}</strong> has approved.</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                    name=self.name,
                    link=url
                ),
                partner_ids=partner_ids,
                subject="Circular Document Approved",
                email_from=self.env.user.partner_id.email or '',
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                attachment_ids=self.attachment_id.ids,
            )

    def action_open_reject_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'memo.action.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_memo_id': self.id,
                'default_action_type': 'reject'
            }
        }

    def action_open_change_request_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'memo.action.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_memo_id': self.id,
                'default_action_type': 'change'
            }
        }

    # def action_publish(self):
    #     if self.state != 'approved':
    #         if self.submission_type == 'memo':
    #             raise ValidationError(_("Please approve memo before publish."))
    #         if self.submission_type == 'circular':
    #             raise ValidationError(_("Please approve circular before publish."))
    #         if self.submission_type == 'procurement':
    #             raise ValidationError(_("Please approve procurement before publish."))
    #     self.state = 'published'
    #     for group in self.target_group_ids:
    #         users = self.env['res.users'].search([('groups_id', 'in', group.id)])
    #         for user in users:
    #             if self.submission_type == 'memo':
    #                 self.message_post(body=f"Memo published for your group: {group.name}",
    #                                   partner_ids=[user.partner_id.id])
    #             if self.submission_type == 'circular':
    #                 self.message_post(body=f"Circular published for your group: {group.name}",
    #                                   partner_ids=[user.partner_id.id])
    #             if self.submission_type == 'procurement':
    #                 self.message_post(body=f"Procurement published for your group: {group.name}",
    #                                   partner_ids=[user.partner_id.id])
    #
    #     if self.submission_type == 'memo':
    #         template = self.env.ref('e_system.email_template_memo_published')
    #     if self.submission_type == 'circular':
    #         template = self.env.ref('e_system.email_template_circular_published')
    #     if self.submission_type == 'procurement':
    #         template = self.env.ref('e_system.email_template_procurement_published')
    #     for user in self.get_target_users():
    #         action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_general_dashboard')
    #         base_url = self.get_base_url()
    #         url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
    #         user = user.name
    #         template.with_context(approve_user=user, url=url).send_mail(self.id, force_send=True,
    #                                                                     email_values={
    #                                                                         'email_to': user.partner_id.email})

    def action_acknowledge(self):
        if self.env.user.id != self.create_uid.id:
            raise ValidationError(_("Create user can submit for the acknowledgement."))
        template = self.env.ref('e_system.mail_template_submit_acknowledgment')
        action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_general_dashboard')
        base_url = self.get_base_url()
        url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
        user = self.acknowledged_ids[0].name
        template.with_context(approve_user=user, url=url).send_mail(self.id, force_send=True,
                                                                    email_values={
                                                                        'email_to': self.acknowledged_ids[
                                                                            0].partner_id.email})

    def action_save_version(self):
        for record in self:
            version_count = self.env['memo.version'].search_count([('memo_id', '=', record.id)])
            new_version = f"v{version_count + 1}"
            self.env['memo.version'].create({
                'memo_id': record.id,
                'memo_name': record.name,
                'comment': record.change_reason or 'Save Version',
                'version_number': new_version,
                'subject': record.subject,
                'purpose_body': record.purpose_body,
                'background_body': record.background_body,
                'motivation_body': record.motivation_body,
                'project_status': record.project_status,
            })

    def get_target_users(self):
        self.ensure_one()
        groups = self.target_group_ids
        users = self.env['res.users'].search([('groups_id', 'in', groups.ids)])
        return users

    # Scheduled Reminder Method
    @api.model
    def _send_reminder_emails(self):
        # 1. Memos signed but not published
        # not_published = self.search([
        #     ('state', '=', 'approved'),
        #     ('date', '<=', (datetime.today() - timedelta(days=1)).date())
        # ])
        # for memo in not_published:
        #     if memo.submission_type == 'memo':
        #         memo.message_post(
        #             body="Reminder: This memo is approved but not yet published.",
        #             partner_ids=[memo.create_uid.partner_id.id]
        #         )
        #     if memo.submission_type == 'circular':
        #         memo.message_post(
        #             body="Reminder: This circular is approved but not yet published.",
        #             partner_ids=[memo.create_uid.partner_id.id]
        #         )
        #     if memo.submission_type == 'procurement':
        #         memo.message_post(
        #             body="Reminder: This procurement is approved but not yet published.",
        #             partner_ids=[memo.create_uid.partner_id.id]
        #         )

        # 2. Memos not acknowledged
        # unacknowledged = self.search([
        #     ('state', '=', 'published'),
        #     ('ack_required', '=', True),
        # ])
        # for memo in unacknowledged:
        #     not_ack_users = memo.target_group_ids.mapped('users') - memo.acknowledged_ids
        #     for user in not_ack_users:
        #         if memo.submission_type == 'memo':
        #             memo.message_post(
        #                 body=f"Reminder: Please acknowledge memo: {memo.name}",
        #                 partner_ids=[user.partner_id.id]
        #             )
        #         if memo.submission_type == 'circular':
        #             memo.message_post(
        #                 body=f"Reminder: Please acknowledge circular: {memo.name}",
        #                 partner_ids=[user.partner_id.id]
        #             )
        #         if memo.submission_type == 'procurement':
        #             memo.message_post(
        #                 body=f"Reminder: Please acknowledge procurement: {memo.name}",
        #                 partner_ids=[user.partner_id.id]
        #             )

        # 3. Memos still not sign
        unsigned = self.search([('state', '=', 'recommend')])
        for memo in unsigned:
            # Send a reminder to approver or fallback user
            if memo.recommender_ids:
                if memo.submission_type == 'memo':
                    memo.message_post(body="Reminder: Memo still not signed.",
                                      partner_ids=self.recommender_ids.mapped('user_id.partner_id.id'))
                if memo.submission_type == 'circular':
                    memo.message_post(body="Reminder: Circular still not signed.",
                                      partner_ids=self.recommender_ids.mapped('user_id.partner_id.id'))
                if memo.submission_type == 'procurement':
                    memo.message_post(body="Reminder: Procurement still not signed.",
                                      partner_ids=self.recommender_ids.mapped('user_id.partner_id.id'))

    def _cron_recommender_followup(self):
        today = fields.Date.today()
        memos = self.search([('state', '=', 'recommend')])
        for memo in memos:
            pending = memo.recommender_ids.filtered(lambda r: not r.sign_initials and r.sent_date)

            for rec in pending:
                days_passed = (today - rec.sent_date).days

                # Day 2 → Reminder to this recommender only
                if days_passed == 2:
                    rec.send_reminder("Day 2 Reminder: Please sign the memo")

                # Day 5 → Reminder to all recommenders
                elif days_passed == 5:
                    rec.send_reminder(
                        f"Day 5 Reminder: Memo '{memo.name}' still has pending signatures"
                    )

                # Day 7 → Escalation to all recommenders + approver
                elif days_passed == 7:
                    recipients = memo.recommender_ids.mapped("user_id.partner_id.email")
                    if memo.approver_id:
                        recipients.append(memo.approver_id.partner_id.email)

                    template = self.env.ref("e_system.mail_template_memo_escalation")
                    if self.submission_type == 'memo':
                        action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_memo_dashboard')
                    if self.submission_type == 'circular':
                        action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
                    if self.submission_type == 'procurement':
                        action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_procurement_dashboard')
                    base_url = self.sudo().get_base_url()
                    url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
                    template.with_context(
                        memo_name=memo.name,
                        pending_names=", ".join(pending.mapped("user_id.name")),
                        url=url
                    ).sudo().send_mail(
                        memo.id,
                        force_send=True,
                        email_values={'email_to': ",".join(filter(None, recipients))}
                    )
                    memo.state = "locked"
                    memo.message_post(
                        body=f"Memo has been locked on Day 7 due to no action from pending recommenders: {', '.join(pending.mapped('user_id.name'))}."
                    )

    def action_load_template(self):
        for record in self:
            if record.template_id:
                record.purpose_body = record.template_id.purpose_body
                record.background_body = record.template_id.background_body
                record.motivation_body = record.template_id.motivation_body

    def action_save_as_template(self):
        for record in self:
            template_id = self.env['memo.template'].sudo().create({
                'name': record.name,
                'submission_type': record.submission_type,
                'purpose_body': record.purpose_body,
                'background_body': record.background_body,
                'motivation_body': record.motivation_body,
                'project_status': record.project_status,
            })
            record.template_id = template_id.id

    def image_to_a4_pdf(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        a4_width, a4_height = A4

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        img_width, img_height = img.size
        ratio = min(a4_width / img_width, a4_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        img_buffer = io.BytesIO()
        img = img.resize((new_width, new_height), Image.LANCZOS)
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        x = (a4_width - new_width) / 2
        y = (a4_height - new_height) / 2
        c.drawImage(ImageReader(img_buffer), x, y, width=new_width, height=new_height)
        c.showPage()
        c.save()

        buffer.seek(0)
        return buffer.read()

    def action_download_memo(self):
        if self.attachment_id:
            self.attachment_id.sudo().unlink()
            self.attachment_id = False  # reset before reuse
        Report = self.env['ir.actions.report']
        submission_report_pdfs = []
        report_pdf, _ = Report._render_qweb_pdf('e_system.action_report_memo_management', self.id)
        if report_pdf:
            submission_report_pdfs.append(report_pdf)
        filename = f"Memo_{self.name or self.id}.pdf"
        for doc in self.document_upload_ids.sorted("sequence"):
            attachment = doc.attachment_id
            if not attachment or not attachment.datas:
                _logger.warning(f"[Skip] Missing or empty attachment in document ID {doc.id}")
                continue

            try:
                raw_data = base64.b64decode(attachment.datas)
            except Exception as e:
                _logger.warning(f"[Decode Error] {attachment.name}: {e}")
                continue

            mimetype = attachment.mimetype or ''
            _logger.info(f"[Process] {attachment.name} (type={mimetype}, size={len(raw_data)} bytes)")
            # Handle PDFs
            if mimetype == 'application/pdf':
                submission_report_pdfs.append(raw_data)

            # Handle images
            elif mimetype in ['image/jpeg', 'image/png', 'image/jpg']:
                try:
                    pdf_data = self.image_to_a4_pdf(raw_data)
                    submission_report_pdfs.append(pdf_data)
                except Exception as e:
                    _logger.warning(f"[Image Convert Error] {attachment.name}: {e}")
            else:
                _logger.warning(f"[Skip] Unsupported file type: {attachment.name} ({mimetype})")

        if not submission_report_pdfs:
            raise UserError("No valid PDF documents found to merge.")

        try:
            final_pdf = pdf.merge_pdf(submission_report_pdfs)
        except Exception as e:
            raise UserError(f"Unexpected error during merge: {e}")

        base64_pdf = base64.b64encode(final_pdf)
        attachment = self.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': base64_pdf,
            'res_model': 'memo.memo',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        self.sudo().write({'attachment_id': attachment.id})
        if not self.folder_id:
            self._assign_document_folder()
        document = self.env['documents.document'].sudo().search([
            ('attachment_id', '=', self.attachment_id.id)
        ], limit=1)

        if document:
            document.sudo().write({
                'attachment_id': self.attachment_id.id,
                'folder_id': self.folder_id.id,
                'owner_id': self.requester_id.id,
                'res_model': self._name,
                'res_id': self.id,
                'name': self.name,
            })
        else:
            self.env['documents.document'].sudo().create({
                'attachment_id': self.attachment_id.id,
                'folder_id': self.folder_id.id,
                'owner_id': self.requester_id.id,
                'res_model': self._name,
                'res_id': self.id,
                'name': self.name,
            })

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{attachment.id}?download=true",
            'target': 'new',
        }


class MemoApprover(models.Model):
    _name = 'memo.approver'
    _description = 'Memo Approver'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence', default=1)
    user_id = fields.Many2one('res.users', string="User", required=True,
                              domain="['|', ('id', 'not in', existing_request_user_ids), ('id', '=', user_id)]")
    display_name = fields.Char(related='user_id.name', readonly=True, store=True)
    existing_request_user_ids = fields.Many2many('res.users', compute='_compute_existing_request_user_ids')
    status = fields.Selection(
        [('Recommended', 'Recommended'), ('Non-Recommended', 'Non-Recommended'), ('Funds Available', 'Funds Available'),
         ('Funds Not Available', 'Funds Not Available'), ('Supported', 'Supported'),
         ('Not Supported', 'Not Supported'), ], string="Status", default='')
    memo_request_id = fields.Many2one('memo.memo', string="Memo Request",
                                      ondelete='cascade')
    required = fields.Boolean(default=True, readonly=True)
    sign_initials = fields.Binary(string="Digital Initials", copy=False)
    comment = fields.Text("Comment")
    date = fields.Datetime(string="Date")
    sent_date = fields.Date(string="Sent Date", help="Date when this recommender was asked to sign.")
    acting_letter_id = fields.Many2one('ir.attachment', string="Acting Letter Evidence",
                                       help="Upload acting letter when changing/deleting this QA line",
                                       copy=False)
    acting_letter_name = fields.Char(related="acting_letter_id.name", store=True, readonly=False)
    datas = fields.Binary(related='acting_letter_id.datas', readonly=False)

    @api.onchange('datas')
    def _onchange_datas(self):
        if self.acting_letter_name:
            vals = {'name': self.acting_letter_name, 'datas': self.datas}
            if not self.acting_letter_id:
                attachment = self.env['ir.attachment'].sudo().create(vals)
                self.acting_letter_id = attachment.id
            else:
                self.acting_letter_id.sudo().write(vals)

    def _create_activity(self):
        for approver in self:
            approver.memo_request_id.activity_schedule(
                'e_system.mail_activity_memo_approval',
                user_id=approver.user_id.id)

    @api.depends('memo_request_id.recommender_ids.user_id')
    def _compute_existing_request_user_ids(self):
        for approver in self:
            approver.existing_request_user_ids = self.mapped('memo_request_id.recommender_ids.user_id')._origin or False

    def write(self, vals):
        trigger_next = False
        for record in self:
            if 'sign_initials' in vals and record.sudo().user_id.id != self.env.uid:
                raise ValidationError("You cannot sign on behalf of another user.")
            if 'sign_initials' in vals and ('comment' in vals and not record.comment) and (
                    'status' not in vals and record.status == ''):
                raise ValidationError("Please add Recommendation Status.")
            if 'sign_initials' in vals:
                vals['date'] = fields.Datetime.now()
                trigger_next = True  # Flag to notify next recommender
        result = super(MemoApprover, self).write(vals)
        for record in self:
            if record.status in ('Non-Recommended', 'Funds Not Available', 'Not Supported') and record.sign_initials:
                trigger_next = False
                if record.memo_request_id.submission_type == 'memo':
                    template = self.env.ref('e_system.mail_template_memo_submit')
                    action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_memo_dashboard')
                    base_url = self.get_base_url()
                    url = base_url + '/odoo/' + action.get('path') + '/' + str(self.memo_request_id.id)
                    user = record.memo_request_id.create_uid.name
                    template.with_context(approve_user=user, request=record.status, url=url).sudo().send_mail(
                        record.memo_request_id.id, force_send=True,
                        email_values={
                            'email_to': record.memo_request_id.create_uid.partner_id.email})

                if record.memo_request_id.submission_type == 'circular':
                    template = self.env.ref('e_system.mail_template_circular_submit')
                    action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
                    base_url = self.get_base_url()
                    url = base_url + '/odoo/' + action.get('path') + '/' + str(self.memo_request_id.id)
                    user = record.memo_request_id.create_uid.name
                    template.with_context(approve_user=user, request=record.status, url=url).sudo().send_mail(
                        record.memo_request_id.id, force_send=True,
                        email_values={
                            'email_to': record.memo_request_id.create_uid.partner_id.email})
                if record.memo_request_id.submission_type == 'procurement':
                    template = self.env.ref('e_system.mail_template_procurement_submit')
                    action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_procurement_dashboard')
                    base_url = self.get_base_url()
                    url = base_url + '/odoo/' + action.get('path') + '/' + str(self.memo_request_id.id)
                    user = record.memo_request_id.create_uid.name
                    template.with_context(approve_user=user, request=record.status, url=url).sudo().send_mail(
                        record.memo_request_id.id, force_send=True,
                        email_values={
                            'email_to': record.memo_request_id.create_uid.partner_id.email})
                remaining_approval = record.memo_request_id.sudo().quality_assurance_ids.filtered(
                    lambda l: l.required and (l.status != 'Completed' or not l.sign_initials))
                if remaining_approval:
                    record.memo_request_id.state = 'draft'
                else:
                    record.memo_request_id.state = 'complete_quality_assurance'
            if trigger_next:
                record.memo_request_id.state = 'recommend'
                record.memo_request_id.sudo()._notify_next_recommender()
        return result

    def action_send_mail(self):
        if self.memo_request_id.submission_type == 'memo':
            template = self.env.ref('e_system.mail_template_memo_submit')
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_memo_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.memo_request_id.id)
            user = self.user_id.name
            template.with_context(approve_user=user, request='recommendation', url=url).sudo().send_mail(
                self.memo_request_id.id, force_send=True,
                email_values={
                    'email_to': self.user_id.partner_id.email})

        if self.memo_request_id.submission_type == 'circular':
            template = self.env.ref('e_system.mail_template_circular_submit')
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.memo_request_id.id)
            user = self.user_id.name
            template.with_context(approve_user=user, request='recommendation', url=url).sudo().send_mail(
                self.memo_request_id.id, force_send=True,
                email_values={
                    'email_to': self.user_id.partner_id.email})
        if self.memo_request_id.submission_type == 'procurement':
            template = self.env.ref('e_system.mail_template_procurement_submit')
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_procurement_dashboard')
            base_url = self.get_base_url()
            url = base_url + '/odoo/' + action.get('path') + '/' + str(self.memo_request_id.id)
            user = self.user_id.name
            template.with_context(approve_user=user, request='recommendation', url=url).sudo().send_mail(
                self.memo_request_id.id, force_send=True,
                email_values={
                    'email_to': self.user_id.partner_id.email})

    def action_sign_line(self):
        if self.memo_request_id.sudo().quality_assurance_ids:
            remaining_approval = self.memo_request_id.sudo().quality_assurance_ids.filtered(
                lambda l: l.required and (l.status != 'Completed' or not l.sign_initials))
            if remaining_approval:
                raise ValidationError(
                    "All Quality Assurance users must be signed and Quality Assurance Status marked as Completed.")
        if not self.memo_request_id.requester_sign:
            raise ValidationError("Requester/Create user must be signed and submit for recommendation.")
        recommenders = self.memo_request_id.recommender_ids.sorted(key=lambda r: r.sequence)
        pending_recommenders = recommenders.filtered(lambda r: not r.sign_initials)
        if pending_recommenders and self in pending_recommenders:
            first_pending = pending_recommenders[0]
            if self != first_pending:
                raise ValidationError("You cannot sign before the previous recommender has signed.")
        if not self.status:
            raise ValidationError("Please add Recommendation Status.")
        if not self.comment or not re.search(r'\w+', self.comment):
            raise UserError("You must provide a valid comment before sign (not just spaces or symbols).")
        return {
            'name': 'Sign',
            'type': 'ir.actions.act_window',
            'res_model': 'memo.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_memo_id': self.memo_request_id.id,
                'default_user_id': self.user_id.id,
                'default_mode': 'approver',
            }
        }

    def unlink(self):
        for rec in self:
            # If memo is beyond draft (submitted), require acting_letter and permission
            if rec.memo_request_id.state not in ('draft', 'change_requested'):
                # allow unlink only for IT team or creator/requester with acting letter
                allowed = False
                if self.env.user in (rec.memo_request_id.create_uid, rec.memo_request_id.requester_id):
                    allowed = True
                if self.env.user.has_group('e_system.group_it_team'):
                    allowed = True
                if not allowed:
                    raise AccessError(_("You do not have permission to delete this Recommender line."))

                # require evidence
                if not rec.acting_letter_id:
                    raise ValidationError(_("Upload acting letter before deleting a Recommender line."))

        return super(MemoApprover, self).unlink()

    def send_reminder(self, subject):
        """Resend reminder email to this approver."""
        self.ensure_one()
        template = self.env.ref("e_system.mail_template_memo_submit")
        if self.submission_type == 'memo':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_memo_dashboard')
        if self.submission_type == 'circular':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
        if self.submission_type == 'procurement':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_procurement_dashboard')
        base_url = self.get_base_url()
        url = f"{base_url}/odoo/{action.get('path')}/{self.memo_request_id.id}"
        template.with_context(
            approve_user=self.user_id.name,
            request=subject,
            url=url,
        ).sudo().send_mail(
            self.memo_request_id.id,
            force_send=True,
            email_values={'email_to': self.user_id.partner_id.email},
        )


class MemoDocumentUpload(models.Model):
    _name = "memo.document.upload"
    _description = "Memo – supporting document"
    _order = "sequence, id"

    sequence = fields.Integer(default=1)
    attachment_id = fields.Many2one("ir.attachment", string="Document",
                                    domain=[("mimetype", "=", "application/pdf")],
                                    ondelete="cascade",
                                    )
    memo_id = fields.Many2one("memo.memo", string="Memo", required=True, ondelete="cascade", )
    name = fields.Char(related="attachment_id.name", store=True, required=True, readonly=False)
    datas = fields.Binary(related='attachment_id.datas', required=True, readonly=False)
    sign_required = fields.Boolean(string="Is Sign Required", default=False)
    sign_template_id = fields.Many2one('sign.template', readonly=False, store=True, string="New Document Template")
    signature_status = fields.Selection([
        ("shared", "Shared"),
        ("sent", "To Sign"),
        ("signed", "Fully Signed"),
        ("canceled", "Cancelled"),
        ("expired", "Expired"),
    ], default='sent', string="Signature Status")
    sign_request_id = fields.Many2one('sign.request', string="Signature Request")

    def compute_sign_request_id(self):
        for doc in self:
            if doc.sign_template_id:
                request_ids = self.env['sign.request'].sudo().search([('template_id', '=', doc.sign_template_id.id)])
                if request_ids:
                    doc.sign_request_id = request_ids[0].id
                else:
                    doc.sign_request_id = False
            else:
                doc.sign_request_id = False

    @api.depends('sign_request_id', 'sign_request_id.state')
    def check_signature_status(self):
        for doc in self:
            if doc.sign_request_id.state == 'shared':
                doc.signature_status = 'shared'
            elif doc.sign_request_id.state == 'sent':
                doc.signature_status = 'sent'
            elif doc.sign_request_id.state == 'canceled':
                doc.signature_status = 'cancelled'
            elif doc.sign_request_id and doc.sign_request_id.state == 'signed':
                doc.signature_status = 'signed'
            elif doc.sign_request_id and doc.sign_request_id.state == 'expired':
                doc.signature_status = 'expired'

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        vals = {'name': rec.name, 'datas': rec.datas}
        if not rec.attachment_id:
            attachment = self.env['ir.attachment'].sudo().create(vals)
            rec.attachment_id = attachment.id
        else:
            rec.attachment_id.sudo().write(vals)
        if rec.attachment_id:
            rec.attachment_id.write({
                "res_model": "memo.memo",
                "res_id": rec.memo_id.id,
            })
            rec.memo_id.message_post(
                body=_("Added supporting document: %s") % rec.attachment_id.name,
                attachment_ids=[rec.attachment_id.id],
            )
            if not rec.memo_id.folder_id:
                rec.memo_id._assign_document_folder()
            self.env['documents.document'].sudo().create({
                'attachment_id': rec.attachment_id.id,
                'folder_id': rec.memo_id.folder_id.id,
                'owner_id': rec.memo_id.requester_id.id,
                'res_model': rec._name,
                'res_id': rec.id,
                'name': rec.name,
            })
        return rec

    def action_preview_document(self):
        self.ensure_one()
        if not self.attachment_id:
            raise ValidationError("Please first upload document")
        if not self.memo_id.folder_id:
            self.memo_id._assign_document_folder()
        document = self.env['documents.document'].sudo().search([
            ('attachment_id', '=', self.attachment_id.id)
        ], limit=1)

        if document:
            document.sudo().write({
                'attachment_id': self.attachment_id.id,
                'folder_id': self.memo_id.folder_id.id,
                'owner_id': self.memo_id.requester_id.id,
                'res_model': self._name,
                'res_id': self.id,
                'name': self.name,
            })
        else:
            self.env['documents.document'].sudo().create({
                'attachment_id': self.attachment_id.id,
                'folder_id': self.memo_id.folder_id.id,
                'owner_id': self.memo_id.requester_id.id,
                'res_model': self._name,
                'res_id': self.id,
                'name': self.name,
            })
        preview_url = f'/web/content/{self.attachment_id.id}?download=false'
        if not preview_url:
            raise ValidationError("Preview not supported for this file type.")
        return {
            'type': 'ir.actions.act_url',
            'url': preview_url,
            'target': 'new',
        }

    def action_doc_sign_request(self):
        sign_template = self.env['sign.template'].sudo().create({
            'name': self.name,
            'attachment_id': self.attachment_id.id,
        })
        sign_template.write({'authorized_ids': [(4, self.env.user.id)]})
        self.sign_template_id = sign_template.id
        self.signature_status = 'sent'
        return {
            'type': 'ir.actions.client',
            'tag': 'sign.Template',
            'name': sign_template.name,
            'params': {
                'sign_edit_call': 'sign_send_request',
                'id': sign_template.id,
                'sign_directly_without_mail': False
            }
        }

    def action_doc_sign_now(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sign.action_sign_send_request')
        sign_template = self.env['sign.template'].sudo().create({
            'name': self.name,
            'attachment_id': self.attachment_id.id,
        })
        sign_template.write({'authorized_ids': [(4, self.env.user.id)]})
        self.sign_template_id = sign_template.id
        self.signature_status = 'sent'
        action["context"] = {
            "active_id": sign_template.id,
            "sign_directly_without_mail": True,
            "default_res_model": "memo.memo",
            "default_res_id": self.memo_id.id,
            "default_reference_doc": f"memo.memo,{self.memo_id.id}",
            "default_signer_id": self.env.user.partner_id.id
        }
        return action


class SignSendRequest(models.TransientModel):
    _inherit = "sign.send.request"

    def create_request(self):
        sign_request = super(SignSendRequest, self).create_request()
        upload = self.env['memo.document.upload'].search([
            ('sign_template_id', '=', self.template_id.id)
        ], limit=1)
        if upload:
            upload.sign_request_id = sign_request.id
            upload.attachment_id = sign_request.completed_document_attachment_ids[
                0].id if sign_request.completed_document_attachment_ids else self.template_id.attachment_id.id
            # Ensure the created sign.request has a reference_doc pointing to the memo document upload
            try:
                if not sign_request.reference_doc:
                    sign_request.reference_doc = upload
            except Exception as e:
                _logger.warning("Could not set sign_request.reference_doc for sign_request %s: %s", sign_request.id, e)
        return sign_request

    @api.onchange('template_id', 'set_sign_order')
    def _onchange_template_id(self):
        self.signer_id = False
        self.filename = self.template_id.display_name
        self.subject = _("Signature Request - %s", self.template_id.attachment_id.name or '')
        roles = self.template_id.mapped('sign_item_ids.responsible_id').sorted()
        signer_ids = []
        if roles:
            signer_ids = [(0, 0, {
                'role_id': role.id,
                'partner_id': role.user_id.partner_id if role.user_id and role.user_id.partner_id else False,
                'mail_sent_order': default_signing_order + 1 if self.set_sign_order else 1
            }) for default_signing_order, role in enumerate(roles)]

        sign_item_role_user = self.env.ref('sign.sign_item_role_user', raise_if_not_found=False)
        if self.env.context.get('sign_directly_without_mail') or sign_item_role_user:
            default_signer = self.env.context.get("default_signer_id", self.env.user.partner_id.id)
            if len(roles) == 1 and signer_ids:
                signer_ids[0][2]['partner_id'] = roles[0].user_id.partner_id if roles[0].user_id and roles[0].user_id.partner_id else default_signer
            elif not roles:
                self.signer_id = default_signer
            user_role = sign_item_role_user and sign_item_role_user.id
            if user_role:
                for signer_val in signer_ids:
                    current_role = signer_val[2].get('role_id')
                    # user_role can't be deleted if already used.
                    if len(signer_val) == 3 and isinstance(current_role, int) and current_role == user_role:
                        signer_val[2]['partner_id'] = default_signer
                        break
        self.signer_ids = [(5, 0, 0)] + signer_ids
        self.signers_count = len(roles)


class SignRequest(models.Model):
    _inherit = 'sign.request'

    def _sign(self):
        """ Sign a SignRequest. It can only be used in the SignRequestItem._sign """
        self.ensure_one()
        if self.state != 'sent' or any(sri.state != 'completed' for sri in self.request_item_ids):
            raise UserError(_("This sign request cannot be signed"))
        self.write({'state': 'signed'})
        if not self._check_is_encrypted():
            # if the file is encrypted, we must wait that the document is decrypted
            self._send_completed_document()

            if not self.reference_doc:
                _logger.warning("SignRequest %s: reference_doc is missing after _send_completed_document(); skipping record posting/linking.", self.id)
            else:
                # Only try message_post/linking when reference_doc exists
                try:
                    if self.reference_doc._name != 'memo.document.upload':
                        model = self.env['ir.model']._get(self.reference_doc._name)
                        if model.is_mail_thread:
                            self.reference_doc.message_post_with_source(
                                "sign.message_signature_link",
                                render_values={"request": self, "salesman": self.env.user.partner_id},
                                subtype_xmlid='mail.mt_note',
                            )
                            # attach a copy of the signed document to the record for easy retrieval
                            attachment_values = []
                            for att in self.completed_document_attachment_ids:
                                attachment_values.append({
                                    "name": att['name'],
                                    "datas": att['datas'],
                                    "type": "binary",
                                    "res_model": self.reference_doc._name,
                                    "res_id": self.reference_doc.id
                                })
                            if attachment_values:
                                self.env["ir.attachment"].create(attachment_values)
                except Exception as e:
                    _logger.exception("SignRequest %s: error while posting signed document to reference_doc: %s", self.id, e)

        for request in self:
            upload = self.env['memo.document.upload'].search([
                ('sign_request_id', '=', request.id)
            ], limit=1)

            if upload and request.completed_document_attachment_ids:
                # Link the signed PDF back to memo
                upload.attachment_id = request.completed_document_attachment_ids[0].id
                upload.signature_status = request.state

    def _send_completed_document(self):
        """ Send the completed document to signers and Contacts in copy with emails
        """
        self.ensure_one()
        if self.state != 'signed':
            raise UserError(_('The sign request has not been fully signed'))
        self._check_senders_validity()

        if not self.completed_document:
            self._generate_completed_document()

        signers = [{'name': signer.partner_id.name, 'email': signer.signer_email, 'id': signer.partner_id.id} for signer
                   in self.request_item_ids]
        request_edited = any(log.action == "update" for log in self.sign_log_ids)
        for sign_request_item in self.request_item_ids:
            self._send_completed_document_mail(signers, request_edited, sign_request_item.partner_id,
                                               access_token=sign_request_item.sudo().access_token,
                                               with_message_cc=False, force_send=True)

        cc_partners_valid = self.cc_partner_ids.filtered(lambda p: p.email_formatted)
        for cc_partner in cc_partners_valid:
            self._send_completed_document_mail(signers, request_edited, cc_partner)
        if cc_partners_valid:
            body = _(
                "The mail has been sent to contacts in copy: %(contacts)s",
                contacts=format_list(self.env, cc_partners_valid.mapped("name")),
            )
            if not is_html_empty(self.message_cc):
                body += self.message_cc
            self.message_post(body=body,
                              attachment_ids=self.attachment_ids.ids + self.completed_document_attachment_ids.ids)

        if not self.reference_doc:
            _logger.warning("SignRequest %s: reference_doc missing when sending completed document; skipping record post.", self.id)
        else:
            try:
                if self.reference_doc._name != 'memo.document.upload':
                    record_body = _("The document %s has been fully signed.", self._get_html_link())
                    self.reference_doc.message_post(
                        body=record_body,
                        attachment_ids=self.completed_document_attachment_ids.ids,
                        partner_ids=cc_partners_valid.ids,
                    )
            except Exception as e:
                _logger.exception("SignRequest %s: error while messaging reference_doc: %s", self.id, e)


class MemoQualityAssurance(models.Model):
    _name = 'memo.quality.assurance'
    _description = 'Memo Quality Assurance'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence', default=1)
    user_id = fields.Many2one('res.users', string="User", required=True,
                              domain="['|', ('id', 'not in', existing_request_user_ids), ('id', '=', user_id)]")
    display_name = fields.Char(related='user_id.name', readonly=True, store=True)
    existing_request_user_ids = fields.Many2many('res.users', compute='_compute_existing_request_user_ids')
    status = fields.Selection([
        ('Completed', 'Completed'),
        ('Non-Completed', 'Non-Completed')], string="Status", default="")
    memo_request_id = fields.Many2one('memo.memo', string="Memo Request",
                                      ondelete='cascade')
    required = fields.Boolean(default=True, readonly=True)
    sign_initials = fields.Binary(string="Digital Initials", copy=False)
    comment = fields.Text("Comment")
    date = fields.Datetime(string="Date")
    acting_letter_id = fields.Many2one('ir.attachment', string="Acting Letter Evidence",
                                       help="Upload acting letter when changing/deleting this QA line",
                                       copy=False)
    acting_letter_name = fields.Char(related="acting_letter_id.name", store=True, readonly=False)
    datas = fields.Binary(related='acting_letter_id.datas', readonly=False)

    @api.onchange('datas')
    def _onchange_datas(self):
        if self.acting_letter_name:
            vals = {'name': self.acting_letter_name, 'datas': self.datas}
            if not self.acting_letter_id:
                attachment = self.env['ir.attachment'].sudo().create(vals)
                self.acting_letter_id = attachment.id
            else:
                self.acting_letter_id.sudo().write(vals)

    def _create_activity(self):
        for quality_assurance in self:
            quality_assurance.memo_request_id.activity_schedule(
                'e_system.mail_activity_memo_approval',
                user_id=quality_assurance.user_id.id)

    @api.depends('memo_request_id.quality_assurance_ids.user_id')
    def _compute_existing_request_user_ids(self):
        for quality_assurance in self:
            quality_assurance.existing_request_user_ids = self.mapped(
                'memo_request_id.quality_assurance_ids.user_id')._origin or False

    def write(self, vals):
        trigger_next = False
        for record in self:
            if 'sign_initials' in vals and record.sudo().user_id.id != self.env.uid:
                raise ValidationError("You cannot sign on behalf of another user.")
            if 'sign_initials' in vals and ('comment' in vals and not record.comment) and (
                    'status' not in vals and record.status == ''):
                raise ValidationError("Please add Quality Assurance Status.")
            if 'sign_initials' in vals:
                vals['date'] = fields.Datetime.now()
                trigger_next = True  # Flag to notify next recommender
        result = super(MemoQualityAssurance, self).write(vals)
        if trigger_next:
            self.memo_request_id.sudo()._notify_quality_assurance()
        return result

    def action_send_mail(self):
        template = self.env.ref('e_system.email_template_submit_quality_assurance')
        if self.memo_request_id.submission_type == 'memo':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_memo_dashboard')
        if self.memo_request_id.submission_type == 'circular':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_circular_dashboard')
        if self.memo_request_id.submission_type == 'procurement':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_procurement_dashboard')
        if self.memo_request_id.submission_type == 'general':
            action = self.env['ir.actions.act_window']._for_xml_id('e_system.action_general_dashboard')
        base_url = self.get_base_url()
        url = base_url + '/odoo/' + action.get('path') + '/' + str(self.memo_request_id.id)
        user = self.user_id.name
        template.with_context(approve_user=user, url=url).sudo().send_mail(self.memo_request_id.id, force_send=True,
                                                                           email_values={
                                                                               'email_to': self.user_id.partner_id.email})

    def action_sign_line(self):
        if self.memo_request_id.sudo().quality_assurance_ids:
            remaining_qas = self.memo_request_id.sudo().quality_assurance_ids.sorted(key=lambda r: r.sequence)
            pending_qas = remaining_qas.filtered(lambda r: not r.sign_initials)
            if pending_qas and self in pending_qas:
                first_pending = pending_qas[0]
                if self != first_pending:
                    raise ValidationError("You cannot sign before the previous quality assurance has signed.")
        if not self.status:
            raise ValidationError("Please add Quality Assurance Status.")
        if self.memo_request_id.state != 'quality_assurance':
            raise ValidationError("You can sign this document only if document in 'Quality Assurance' stage.")
        if not self.comment or not re.search(r'\w+', self.comment):
            raise UserError("You must provide a valid comment before sign (not just spaces or symbols).")
        return {
            'name': 'Sign',
            'type': 'ir.actions.act_window',
            'res_model': 'memo.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_memo_id': self.memo_request_id.id,
                'default_user_id': self.user_id.id,
                'default_mode': 'quality_assurance',
            }
        }

    def unlink(self):
        for rec in self:
            # Only allow deletion in Draft (simple case) OR with permission + evidence after submit
            if rec.memo_request_id.state not in ('draft', 'change_requested'):
                allowed = False
                if self.env.user in (rec.memo_request_id.create_uid, rec.memo_request_id.requester_id):
                    allowed = True
                if self.env.user.has_group('e_system.group_it_team'):
                    allowed = True
                if not allowed:
                    raise AccessError(_("You do not have permission to delete this Quality Assurance line."))

                # require evidence
                if not rec.acting_letter_id:
                    raise ValidationError(_("Upload acting letter before deleting a Quality Assurance line."))

        return super(MemoQualityAssurance, self).unlink()