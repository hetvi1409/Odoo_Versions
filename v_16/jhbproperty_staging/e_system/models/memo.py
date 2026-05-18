from markupsafe import Markup
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta
from io import BytesIO
import io
import base64
from PyPDF2 import PdfReader
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from odoo.tools import pdf
import logging

_logger = logging.getLogger(__name__)


class Memo(models.Model):
    _name = 'memo.memo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Memo'

    name = fields.Char("Title", required=True, help="Title of the memo")
    memo_number = fields.Char("Memo Number", readonly=True, copy=False)
    date = fields.Date("Memo Date", default=fields.Date.today, help="Date when the memo is created")
    branch_id = fields.Many2one('hr.department', string='Department', required=True)
    subject = fields.Text("Subject", required=True)
    requester_id = fields.Many2one("res.users", string="Requester", default=lambda self: self.env.user,
                                   help="Memo creator")
    requester_sign = fields.Binary(string="Requester Signature", copy=False)
    target_group_ids = fields.Many2many("res.groups", string="Target Audience",
                                        help="User groups allowed to see the memo")

    # Approval roles
    approver_id = fields.Many2one("res.users", string="Approver", required=True,
                                  help="Person who must approve the memo")
    approver_sign = fields.Binary(string="Approver Signature", copy=False)
    quality_assurance_id = fields.Many2one("res.users", string="Quality Assurance",
                                           help="Person who must check memo quality")
    quality_assurance_ids = fields.One2many('memo.quality.assurance', 'memo_request_id',
                                            string="Quality Assurance Users",
                                            store=True, readonly=False)
    quality_assurance_required = fields.Boolean(string="Quality Assurance Required?", default=True)
    recommender_ids = fields.One2many('memo.approver', 'memo_request_id', string="Recommenders",
                                      store=True, readonly=False)
    recommender_required = fields.Boolean(string="Recommender Required?", default=True)
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
    ], default='draft', tracking=True, help="Workflow status")
    submission_type = fields.Selection([
        ('memo', 'Memo'),
        ('circular', 'Circular'),
        ('procurement', 'Procurement'),
    ], string="Submission Type", default='memo', store=True)

    change_reason = fields.Text("Change Request Reason", help="Comments if change is requested")
    rejection_reason = fields.Text("Rejection Reason")
    is_financial = fields.Boolean("Is Financial Detail Visible on Report", default=False,
                                  compute="_compute_is_financial", readonly=False)
    financial_sentence = fields.Html("Financial Sentences")
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
    template_id = fields.Many2one('memo.template', string="Template",
                                  domain="[('submission_type', '=', submission_type)]", tracking=True)
    version_ids = fields.One2many('memo.version', 'memo_id', string="Versions")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, domain="[]")
    submission_recommended = fields.Boolean("Submission Recommend", default=False,
                                            compute="_compute_submission_recommended")
    approve_date = fields.Datetime(string="Date")
    document_upload_ids = fields.One2many("memo.document.upload", "memo_id", string="Supporting documents", copy=False,
                                          required=True)

    memo_type = fields.Selection([
        ('general', 'General'),
        ('property', 'Property Memo'),
    ], string="Memo Type", default='general', required=True)
    building_id = fields.Many2one('building', string="Property")
    land_process = fields.Selection([
        ('instruction_request', 'Instruction/Request'),
        ('assessment', 'Assessment'),
        ('circulation_for_comment', 'Circulation for Comment'),
        ('valuation', 'Valuation'),
        ('transaction', 'Transaction'),
        ('committees', 'Committees'),
        ('section_79_notice', 'Section 79 Notice'),
        ('tender', 'Tender'),
        ('ptob', 'PTOB'),
        ('executive_adjudication_committee', 'Executive Adjudication Committee'),
        ('agreement', 'Agreement'),
        ('offer_to_purchase', 'Offer to Purchase'),
        ('expropriation', 'Expropriation'),
        ('conveyancing', 'Conveyancing'),
        ('tenant_contract_info', 'Tenant Contract Info (Take-on form)'),
    ], string="Land Process")
    property_type = fields.Selection([('social_lease', 'Social Lease/ Sale'),
                                      ('commercial_lease',
                                       'Commercial Lease/Sale (including residential)'),
                                      ('registration',
                                       'Registration/ cancellation of a servitude'),
                                      ('land', 'Land Regularisation Matter'),
                                      ('road', 'Road reserve'),
                                      ('user_agreement', 'User Agreement'),
                                      ('lanes', 'Sanatory Lanes'),
                                      ('outdoor', 'Outdoor Advertising')],
                                     string='Property Type')
    attachment_id = fields.Many2one('ir.attachment', string="Memo Document")
    folder_id = fields.Many2one('documents.folder', string="Document Folder", readonly=True)
    is_project_status = fields.Boolean("Is Project Status Visible on Report", default=False, readonly=False)
    project_status = fields.Html("Project Status")
    show_submit_qa = fields.Boolean("Show Submit QA Button",
                                    compute="_compute_show_submit_recommendation", default=False)
    show_complete_qa = fields.Boolean("Show Complete QA Button",
                                      compute="_compute_show_submit_recommendation", default=False)
    show_change_request = fields.Boolean("Show Change Request/Reject Button",
                                         compute="_compute_show_submit_recommendation", default=False)
    show_submit_recommendation = fields.Boolean("Show Submit Recommendation Button",
                                                compute="_compute_show_submit_recommendation", default=False)
    make_readonly = fields.Boolean("Make Readonly Button",
                                   compute="_compute_show_submit_recommendation", default=False)
    is_creator = fields.Boolean("Is Creator", compute="_compute_show_submit_recommendation", default=False)
    is_follower = fields.Boolean("Is Follower", compute="_compute_show_submit_recommendation", default=False)

    allowed_user_ids = fields.Many2many('res.users', 'memo_allowed_user_rel', 'memo_id', 'user_id',
                                        string='Turn-based Allowed Users', compute='_compute_allowed_user_ids',
                                        store=True, compute_sudo=True, )

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
            if rec.state in ['quality_assurance','change_requested']:
                pending_qas = rec.quality_assurance_ids.filtered(lambda q: not q.sign_initials).sorted('sequence')
                if pending_qas:
                    next_qa_user = pending_qas[0].user_id
                    if next_qa_user:
                        allowed.add(next_qa_user.id)

            # Recommenders: same logic
            rec_signed_users = rec.recommender_ids.filtered(lambda r: r.sign_initials).mapped('user_id')
            allowed.update(u.id for u in rec_signed_users)
            if rec.state in ['recommend','change_requested']:
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

    @api.constrains('requester_id', 'approver_id',
                    'quality_assurance_ids', 'recommender_ids', 'acknowledged_ids')
    def _check_unique_user_roles(self):
        for memo in self:
            role_users = []

            if memo.requester_id:
                role_users.append(('Requester', memo.requester_id.id))
            # if memo.quality_assurance_id:
            #     role_users.append(('Quality Assurance', memo.quality_assurance_id.id))
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
                    # image = Image.open(io.BytesIO(raw_data)).convert("RGB")
                    # output_buffer = io.BytesIO()
                    # image.save(output_buffer, format="PDF")
                    # output_buffer.seek(0)
                    # submission_report_pdfs.append(output_buffer.read())
                    pdf_data = self.image_to_a4_pdf(raw_data)
                    submission_report_pdfs.append(pdf_data)
                except Exception as e:
                    _logger.warning(f"[Image Convert Error] {attachment.name}: {e}")
            else:
                _logger.warning(f"[Skip] Unsupported file type: {attachment.name} ({mimetype})")

        if not submission_report_pdfs:
            raise UserError("No valid PDF documents found to merge.")

            # 3. Final merge
        try:
            final_pdf = pdf.merge_pdf(submission_report_pdfs)
        except Exception as e:
            raise UserError(f"Unexpected error during merge: {e}")

        base64_pdf = base64.b64encode(final_pdf)

        pdf_url = f"/web/content?model=memo.memo&id={self.id}&download=true&filename={filename}"

        # Use ir.attachment to temporarily store the file (or use a dummy field trigger)
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
            # Update existing document with correct folder and linkage
            document.sudo().write({
                'attachment_id': self.attachment_id.id,
                'folder_id': self.folder_id.id,
                'owner_id': self.requester_id.id,
                'res_model': self._name,
                'res_id': self.id,
                'name': self.name,
            })
        else:
            # Create a new document if it doesn’t exist
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
        if not vals.get('memo_number') and vals.get('submission_type') == 'memo':
            vals['memo_number'] = self.env['ir.sequence'].next_by_code('memo.memo')
        if not vals.get('memo_number') and vals.get('submission_type') == 'circular':
            vals['memo_number'] = self.env['ir.sequence'].next_by_code('circular.circular')
        if not vals.get('memo_number') and vals.get('submission_type') == 'procurement':
            vals['memo_number'] = self.env['ir.sequence'].next_by_code('procurement.procurement')
        res = super().create(vals)
        res.sudo()._assign_document_folder()
        return res

    def write(self, vals):
        for rec in self:
            restricted_fields = {'purpose_body', 'background_body', 'motivation_body'}
            if restricted_fields.intersection(vals.keys()):
                if rec.state in ['draft', 'quality_assurance', 'change_requested']:
                    allowed_users = [rec.create_uid.id, rec.requester_id.id] + rec.quality_assurance_ids.mapped(
                        'user_id').ids
                    if self.env.uid not in allowed_users:
                        raise ValidationError("You are not allowed to edit the memo body at this stage.")

            body_fields = {'purpose_body', 'background_body', 'motivation_body'}
            # Check if body content is being modified
            if body_fields.intersection(vals.keys()):
                has_signatures = bool(
                    rec.quality_assurance_ids.filtered("sign_initials") or
                    rec.recommender_ids.filtered("sign_initials") or
                    (rec.approver_id and rec.approver_sign) or
                    rec.acknowledged_sign
                )
                if has_signatures:
                    # Reset signatures
                    rec.quality_assurance_ids.write({
                        "sign_initials": False,
                        "status": False,
                        "comment": False,
                        "date": False,
                    })
                    rec.recommender_ids.write({
                        "sign_initials": False,
                        "status": False,
                        "comment": False,
                        "date": False,
                    })
                    if rec.approver_id:
                        rec.approver_sign = False
                        rec.approve_date = False

                    # Move to change_request stage
                    rec.sudo().state = "change_request"

                    # Log in audit trail
                    rec.sudo().message_post(body=_(
                        "Memo Content had been changed. Signatures have been cleared and process restarted."))

                    # Send notifications
                    recipients = (
                            rec.quality_assurance_ids.mapped("user_id.partner_id") +
                            rec.recommender_ids.mapped("user_id.partner_id") +
                            ([rec.approver_id.partner_id] if rec.approver_id else []) +
                            [rec.requester_id.partner_id]
                    )
                    template = self.env.ref("e_system.mail_template_memo_content_changed")
                    base_url = rec.get_base_url()
                    url = f"{base_url}/web#id={rec.id}&model=memo.memo&view_type=form"
                    if template:
                        template.with_context(url=url).send_mail(
                            rec.id, force_send=True, email_values={"recipient_ids": [(6, 0, recipients.ids)]}
                        )
        return super().write(vals)

    def _assign_document_folder(self):
        user = self.requester_id
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        if employee:
            dept_name = employee.department_id.name if employee.department_id else self.branch_id.name

            # Ensure root folder exists
            root_folder = self.env['documents.folder'].sudo().search([
                ('name', '=', 'Business Unit'), ('parent_folder_id', '=', False)
            ], limit=1)
            if not root_folder:
                root_folder = self.env['documents.folder'].sudo().create({'name': 'Business Unit'})

            # Department Folder
            dept_folder = self.env['documents.folder'].sudo().search([
                ('name', '=', dept_name), ('parent_folder_id', '=', root_folder.id)
            ], limit=1)
            if not dept_folder:
                dept_folder = self.env['documents.folder'].sudo().create({
                    'name': dept_name,
                    'parent_folder_id': root_folder.id
                })

            if self.submission_type == 'memo':
                # Memo Folder inside department
                memo_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Memos'), ('parent_folder_id', '=', dept_folder.id)
                ], limit=1)
                if not memo_folder:
                    memo_folder = self.env['documents.folder'].sudo().create({
                        'name': 'Memos',
                        'parent_folder_id': dept_folder.id
                    })

                self.sudo().write({'folder_id': memo_folder.id})
            if self.submission_type == 'circular':
                # Memo Folder inside department
                memo_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Circulars'), ('parent_folder_id', '=', dept_folder.id)
                ], limit=1)
                if not memo_folder:
                    memo_folder = self.env['documents.folder'].sudo().create({
                        'name': 'Circulars',
                        'parent_folder_id': dept_folder.id
                    })

                self.sudo().write({'folder_id': memo_folder.id})
            if self.submission_type == 'procurement':
                # Memo Folder inside department
                memo_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Procurements'), ('parent_folder_id', '=', dept_folder.id)
                ], limit=1)
                if not memo_folder:
                    memo_folder = self.env['documents.folder'].sudo().create({
                        'name': 'Procurements',
                        'parent_folder_id': dept_folder.id
                    })

                self.sudo().write({'folder_id': memo_folder.id})

    def _compute_submission_recommended(self):
        for submission in self:
            if submission.recommender_ids:
                remaining_approval = submission.recommender_ids.filtered(
                    lambda l: l.required and (l.status != 'Recommended' or not l.sign_initials))
                if remaining_approval:
                    submission.submission_recommended = False
                else:
                    if self.env.user.id == submission.approver_id.id:
                        submission.submission_recommended = True
                    else:
                        submission.submission_recommended = False
            else:
                if submission.submission_type in ['circular'] and self.env.user.id == submission.approver_id.id:
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
                                    memo.create_uid.id] and memo.state == 'complete_quality_assurance' and memo.recommender_required:
                memo.show_submit_recommendation = True
            else:
                memo.show_submit_recommendation = False
            if self.env.user.partner_id.id in memo.sudo().message_follower_ids.mapped(
                'partner_id.id') and self.env.user.id not in memo.sudo().quality_assurance_ids.mapped(
                'user_id.id') and self.env.user.id not in memo.sudo().recommender_ids.mapped(
                'user_id.id') and self.env.user.id not in [memo.requester_id.id, memo.create_uid.id,memo.approver_id.id]:
                memo.is_follower = True
            else:
                memo.is_follower = False

    @api.depends('acknowledged_ids')
    def _compute_read_count(self):
        for rec in self:
            rec.read_count = len(rec.acknowledged_ids)

    def action_sign_request(self):
        if not self.requester_id:
            if self.submission_type == 'memo':
                raise ValidationError("Please add Requester before sign the memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Please add Requester before sign the circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Please add Requester before sign the procurement.")
        if self.requester_id.id != self.env.user.id:
            raise ValidationError("Only Requester can sign.")
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
                lambda l: l.required and (l.status not in ('Recommended') or not l.sign_initials))
            if pending_recommenders:
                raise ValidationError("All Recommender user must be signed and Recommended document.")
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
            lambda r: not r.sign_initials or r.status not in ['Non-Completed'])
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
        template = self.env.ref('e_system.email_template_complete_quality_assurance')
        base_url = self.get_base_url()
        url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
        user = self.requester_id.name
        template.with_context(approve_user=user, url=url).send_mail(self.id, force_send=True,
                                                                    email_values={
                                                                        'email_to': self.requester_id.partner_id.email})
        self.state = 'complete_quality_assurance'
        # if self.submission_type == 'memo':
        #     self.sudo().message_post(
        #         body="Complete Quality Assurance: This memo is complete quality assurance.",
        #         # partner_ids=self.recommender_ids.mapped('user_id.partner_id.id')
        #         partner_ids=[self.requester_id.partner_id.id],
        #         message_type='comment',
        #     )
        # if self.submission_type == 'circular':
        #     self.sudo().message_post(
        #         body="Complete Quality Assurance: This circular is complete quality assurance.",
        #         # partner_ids=self.recommender_ids.mapped('user_id.partner_id.id')
        #         partner_ids=[self.requester_id.partner_id.id],
        #         message_type='comment',
        #     )
        # if self.submission_type == 'procurement':
        #     self.sudo().message_post(
        #         body="Complete Quality Assurance: This procurement is complete quality assurance.",
        #         # partner_ids=self.recommender_ids.mapped('user_id.partner_id.id')
        #         partner_ids=[self.requester_id.partner_id.id],
        #         message_type='comment',
        #     )

    def action_submit(self):
        if not self.recommender_ids:
            if self.submission_type == 'memo':
                raise ValidationError("Please add recommenders before submit the memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Please add recommenders before submit the circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Please add recommenders before submit the procurement.")
        if not self.requester_sign:
            raise ValidationError("Please add requester signature before submit for recommendation.")
        if self.create_uid != self.env.user and self.requester_id.id != self.env.user.id:
            raise ValidationError("Only memo document create user or requester user can submit for recommendation.")
        self.state = 'recommend'
        self._notify_next_recommender()

    def _notify_next_recommender(self):
        pending_recommenders = self.recommender_ids.filtered(
            lambda r: not r.sign_initials and r.status not in ['Recommended', 'Non-Recommended'])
        if pending_recommenders:
            next_recommender = pending_recommenders.sorted(key=lambda r: r.sequence)[0]
            next_recommender.sudo().action_send_mail()
        else:
            # All recommenders are done — now notify the approver
            self.state = 'pending_approval'
            self._notify_next_approver()

    def action_submit_for_approval(self):
        if not self.approver_id:
            raise ValidationError("Please add approver before submit for approval.")
        if self.submission_type == 'memo' and self.quality_assurance_required == False:
            self.state = 'pending_approval'
            template = self.env.ref('e_system.mail_template_memo_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})

        if self.submission_type == 'circular' and self.quality_assurance_required == False:
            self.state = 'pending_approval'
            template = self.env.ref('e_system.mail_template_circular_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})
        if self.submission_type == 'procurement' and self.quality_assurance_required == False:
            self.state = 'pending_approval'
            template = self.env.ref('e_system.mail_template_procurement_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})

    def _notify_next_approver(self):
        if self.submission_type == 'memo':
            template = self.env.ref('e_system.mail_template_memo_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})
        if self.submission_type == 'circular':
            template = self.env.ref('e_system.mail_template_circular_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})
        if self.submission_type == 'procurement':
            template = self.env.ref('e_system.mail_template_procurement_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            user = self.approver_id.name
            template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                           email_values={
                                                                                               'email_to': self.approver_id.partner_id.email})

    def action_approve_memo(self):
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
            if self.submission_type == 'memo':
                raise ValidationError("Only approver can approve memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Only approver can approve circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Only approver can approve procurement.")
        if not self.approver_sign:
            if self.submission_type == 'memo':
                raise ValidationError("Please add approver signature before approve memo.")
            if self.submission_type == 'circular':
                raise ValidationError("Please add approver signature before approve circular.")
            if self.submission_type == 'procurement':
                raise ValidationError("Please add approver signature before approve procurement.")
        if self.recommender_ids:
            remaining_approval = self.recommender_ids.filtered(
                lambda l: l.required and (l.status != 'Recommended' or not l.sign_initials))
            if remaining_approval:
                raise ValidationError("Recommender must be signed and recommended.")
        self.state = 'approved'
        self.submission_recommended = False
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
                    # image = Image.open(io.BytesIO(raw_data)).convert("RGB")
                    # output_buffer = io.BytesIO()
                    # image.save(output_buffer, format="PDF")
                    # output_buffer.seek(0)
                    # submission_report_pdfs.append(output_buffer.read())
                    pdf_data = self.image_to_a4_pdf(raw_data)
                    submission_report_pdfs.append(pdf_data)
                except Exception as e:
                    _logger.warning(f"[Image Convert Error] {attachment.name}: {e}")
            else:
                _logger.warning(f"[Skip] Unsupported file type: {attachment.name} ({mimetype})")

        if not submission_report_pdfs:
            raise UserError("No valid PDF documents found to merge.")

            # 3. Final merge
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
            template = self.env.ref('e_system.mail_template_memo_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
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
            template = self.env.ref('e_system.mail_template_circular_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
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
            template = self.env.ref('e_system.mail_template_procurement_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
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

    # def action_reject(self):
    #     if not self.rejection_reason:
    #         raise ValidationError(_("Please add rejection reason."))
    #     self.action_save_version()
    #     message = ''
    #     if self.submission_type == 'memo':
    #         message = Markup(
    #             "<p><strong>Memo is rejected</strong></p><p><b>By:</b> %(name)s</p><p><b>Reason:</b> %(reason)s</p>") % {
    #                       'name': self.env.user.name,
    #                       'reason': self.rejection_reason,
    #                   }
    #     if self.submission_type == 'circular':
    #         message = Markup(
    #             "<p><strong>Circular is rejected</strong></p><p><b>By:</b> %(name)s</p><p><b>Reason:</b> %(reason)s</p>") % {
    #                       'name': self.env.user.name,
    #                       'reason': self.rejection_reason,
    #                   }
    #     if self.submission_type == 'procurement':
    #         message = Markup(
    #             "<p><strong>Procurement is rejected</strong></p><p><b>By:</b> %(name)s</p><p><b>Reason:</b> %(reason)s</p>") % {
    #                       'name': self.env.user.name,
    #                       'reason': self.rejection_reason,
    #                   }
    #     self.message_post(
    #         body=message,
    #         partner_ids=[self.requester_id.partner_id.id],
    #         subject="Reject Notification",
    #     )
    #     self.state = 'rejected'

    # def action_request_change(self):
    #     if not self.change_reason:
    #         raise ValidationError(_("Please add change request reason."))
    #     self.action_save_version()
    #     message = Markup(
    #         "<p><strong>Change Request Submitted</strong></p><p><b>Requested By:</b> %(name)s</p><p><b>Reason:</b> %(reason)s</p>") % {
    #                   'name': self.env.user.name,
    #                   'reason': self.change_reason,
    #               }
    #     self.message_post(
    #         body=message,
    #         partner_ids=[self.requester_id.partner_id.id],
    #         subject="Change Request Notification",
    #     )
    #     self.state = 'change_requested'
    #     self.change_reason = ''

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
    #         template.send_mail(self.id, force_send=True, email_values={'email_to': user.partner_id.email})

    # def action_acknowledge(self):
    #     if self.env.user not in self.acknowledged_ids:
    #         self.acknowledged_ids = [(4, self.env.user.id)]

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
    # @api.model
    # def _send_reminder_emails(self):
    #     # 1. Memos signed but not published
    #     not_published = self.search([
    #         ('state', '=', 'approved'),
    #         ('date', '<=', (datetime.today() - timedelta(days=1)).date())
    #     ])
    #     for memo in not_published:
    #         if memo.submission_type == 'memo':
    #             memo.message_post(
    #                 body="Reminder: This memo is approved but not yet published.",
    #                 partner_ids=[memo.create_uid.partner_id.id]
    #             )
    #         if memo.submission_type == 'circular':
    #             memo.message_post(
    #                 body="Reminder: This circular is approved but not yet published.",
    #                 partner_ids=[memo.create_uid.partner_id.id]
    #             )
    #         if memo.submission_type == 'procurement':
    #             memo.message_post(
    #                 body="Reminder: This procurement is approved but not yet published.",
    #                 partner_ids=[memo.create_uid.partner_id.id]
    #             )
    #
    #     # 2. Memos published but not acknowledged
    #     unacknowledged = self.search([
    #         ('state', '=', 'published'),
    #         ('ack_required', '=', True),
    #     ])
    #     for memo in unacknowledged:
    #         not_ack_users = memo.target_group_ids.mapped('users') - memo.acknowledged_ids
    #         for user in not_ack_users:
    #             if memo.submission_type == 'memo':
    #                 memo.message_post(
    #                     body=f"Reminder: Please acknowledge memo: {memo.name}",
    #                     partner_ids=[user.partner_id.id]
    #                 )
    #             if memo.submission_type == 'circular':
    #                 memo.message_post(
    #                     body=f"Reminder: Please acknowledge circular: {memo.name}",
    #                     partner_ids=[user.partner_id.id]
    #                 )
    #             if memo.submission_type == 'procurement':
    #                 memo.message_post(
    #                     body=f"Reminder: Please acknowledge procurement: {memo.name}",
    #                     partner_ids=[user.partner_id.id]
    #                 )
    #
    #     # 3. Memos still not sign
    #     unsigned = self.search([('state', '=', 'recommend')])
    #     for memo in unsigned:
    #         # Send a reminder to approver or fallback user
    #         if memo.recommender_ids:
    #             if memo.submission_type == 'memo':
    #                 memo.message_post(body="Reminder: Memo still not signed.",
    #                                   partner_ids=self.recommender_ids.mapped('user_id.partner_id.id'))
    #             if memo.submission_type == 'circular':
    #                 memo.message_post(body="Reminder: Circular still not signed.",
    #                                   partner_ids=self.recommender_ids.mapped('user_id.partner_id.id'))
    #             if memo.submission_type == 'procurement':
    #                 memo.message_post(body="Reminder: Procurement still not signed.",
    #                                   partner_ids=self.recommender_ids.mapped('user_id.partner_id.id'))

    def action_load_template(self):
        for record in self:
            if record.template_id:
                record.purpose_body = record.template_id.purpose_body
                record.background_body = record.template_id.background_body
                record.motivation_body = record.template_id.motivation_body

    def action_save_as_template(self):
        for record in self:
            # template_id = self.env['memo.template'].sudo().search([('name','=',record.name)])
            # if template_id:
            #     raise ValidationError(_("With this name '%s' Template already exist!",record.name))
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

        # Create an in-memory PDF canvas
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        # Resize image to fit within A4 while preserving aspect ratio
        img_width, img_height = img.size
        ratio = min(a4_width / img_width, a4_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        # Convert resized image to bytes
        img_buffer = io.BytesIO()
        img = img.resize((new_width, new_height), Image.LANCZOS)
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Position image in center
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
        # attachment_ids = self.env['ir.attachment'].sudo().search(
        #     [('res_model', '=', 'memo.memo'), ('res_id', '=', self.id), ('mimetype', '=', 'application/pdf'),
        #      ('name', '!=', filename)])
        # for attachment in attachment_ids:
        #     if attachment.datas:
        #         submission_report_pdfs.append(base64.b64decode(attachment.datas))
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
                    # image = Image.open(io.BytesIO(raw_data)).convert("RGB")
                    # output_buffer = io.BytesIO()
                    # image.save(output_buffer, format="PDF")
                    # output_buffer.seek(0)
                    # submission_report_pdfs.append(output_buffer.read())
                    pdf_data = self.image_to_a4_pdf(raw_data)
                    submission_report_pdfs.append(pdf_data)
                except Exception as e:
                    _logger.warning(f"[Image Convert Error] {attachment.name}: {e}")
            else:
                _logger.warning(f"[Skip] Unsupported file type: {attachment.name} ({mimetype})")

        if not submission_report_pdfs:
            raise UserError("No valid PDF documents found to merge.")

            # 3. Final merge
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
            # Update existing document with correct folder and linkage
            document.sudo().write({
                'attachment_id': self.attachment_id.id,
                'folder_id': self.folder_id.id,
                'owner_id': self.requester_id.id,
                'res_model': self._name,
                'res_id': self.id,
                'name': self.name,
            })
        else:
            # Create a new document if it doesn’t exist
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
    status = fields.Selection([
        ('Recommended', 'Recommended'),
        ('Non-Recommended', 'Non-Recommended')], string="Status")
    memo_request_id = fields.Many2one('memo.memo', string="Memo Request",
                                      ondelete='cascade')
    required = fields.Boolean(default=True, readonly=True)
    sign_initials = fields.Binary(string="Digital Initials", copy=False)
    comment = fields.Text("Comment")
    date = fields.Datetime(string="Date")

    def _create_activity(self):
        for approver in self:
            approver.memo_request_id.activity_schedule(
                'e_system.mail_activity_memo_approval',
                user_id=approver.user_id.id)

    @api.depends('memo_request_id.recommender_ids.user_id')
    def _compute_existing_request_user_ids(self):
        for approver in self:
            approver.sudo().existing_request_user_ids = self.mapped(
                'memo_request_id.recommender_ids.user_id').sudo()._origin or False

    def write(self, vals):
        trigger_next = False
        for record in self:
            # if record.user_id.id != self.env.uid:
            #     raise ValidationError("You cannot sign on behalf of another user.")
            # if 'sign_initials' in vals:
            #     vals['date'] = fields.Datetime.now()
            #     trigger_next = True  # Flag to notify next recommender
            #     if not record.comment:
            #         if 'comment' not in vals
            #         raise ValidationError("Please add comment.")
            if 'sign_initials' in vals and record.sudo().user_id.id != self.env.uid:
                raise ValidationError("You cannot sign on behalf of another user.")
            # if 'sign_initials' in vals and 'comment' not in vals and not record.comment:
            #     raise ValidationError("Please add Recommendation Comment.")
            if 'sign_initials' in vals and ('comment' in vals and not record.comment) and (
                    'status' not in vals and record.status == ''):
                raise ValidationError("Please add Recommendation Status.")
            if 'sign_initials' in vals:
                vals['date'] = fields.Datetime.now()
                trigger_next = True  # Flag to notify next recommender
        result = super(MemoApprover, self).write(vals)
        for record in self:
            if record.status in ['Non-Recommended'] and record.sign_initials:
                trigger_next = False
                if record.memo_request_id.submission_type == 'memo':
                    template = self.env.ref('e_system.mail_template_memo_submit')
                    base_url = self.get_base_url()
                    url = f"{base_url}/web#id={record.memo_request_id.id}&model=memo.memo&view_type=form"
                    user = record.memo_request_id.create_uid.name
                    template.with_context(approve_user=user, request=record.status, url=url).sudo().send_mail(
                        record.memo_request_id.id, force_send=True,
                        email_values={
                            'email_to': record.memo_request_id.create_uid.partner_id.email})

                if record.memo_request_id.submission_type == 'circular':
                    template = self.env.ref('e_system.mail_template_circular_submit')
                    base_url = self.get_base_url()
                    url = f"{base_url}/web#id={record.memo_request_id.id}&model=memo.memo&view_type=form"
                    user = record.memo_request_id.create_uid.name
                    template.with_context(approve_user=user, request=record.status, url=url).sudo().send_mail(
                        record.memo_request_id.id, force_send=True,
                        email_values={
                            'email_to': record.memo_request_id.create_uid.partner_id.email})
                if record.memo_request_id.submission_type == 'procurement':
                    template = self.env.ref('e_system.mail_template_procurement_submit')
                    base_url = self.get_base_url()
                    url = f"{base_url}/web#id={record.memo_request_id.id}&model=memo.memo&view_type=form"
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
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.memo_request_id.id}&model=memo.memo&view_type=form"
            user = self.user_id.name
            template.with_context(approve_user=user, request='recommendation', url=url).send_mail(
                self.memo_request_id.id, force_send=True,
                email_values={
                    'email_to': self.user_id.partner_id.email})

        if self.memo_request_id.submission_type == 'circular':
            template = self.env.ref('e_system.mail_template_circular_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.memo_request_id.id}&model=memo.memo&view_type=form"
            user = self.user_id.name
            template.with_context(approve_user=user, request='recommendation', url=url).send_mail(
                self.memo_request_id.id, force_send=True,
                email_values={
                    'email_to': self.user_id.partner_id.email})
        if self.memo_request_id.submission_type == 'procurement':
            template = self.env.ref('e_system.mail_template_procurement_submit')
            base_url = self.get_base_url()
            url = f"{base_url}/web#id={self.memo_request_id.id}&model=memo.memo&view_type=form"
            user = self.user_id.name
            template.with_context(approve_user=user, request='recommendation', url=url).send_mail(
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
        if self.memo_request_id.recommender_ids:
            recommenders = self.memo_request_id.recommender_ids.sorted(key=lambda r: r.sequence)
            pending_recommenders = recommenders.filtered(lambda r: not r.sign_initials)
            if pending_recommenders and self in pending_recommenders:
                first_pending = pending_recommenders[0]
                if self != first_pending:
                    raise ValidationError("You cannot sign before the previous recommender has signed.")
        if not self.memo_request_id.requester_sign:
            raise ValidationError("Requester/Create user must be signed and submit for recommendation.")
        if not self.status:
            raise ValidationError("Please add Recommendation Status.")
        if not self.comment:
            raise ValidationError("Please add Recommendation Comment.")
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
            if rec.memo_request_id.create_uid != self.env.user:
                if rec.memo_request_id.submission_type == 'memo':
                    raise AccessError("Only the memo creator can delete recommenders.")
                if rec.memo_request_id.submission_type == 'circular':
                    raise AccessError("Only the circular creator can delete recommenders.")
                if rec.memo_request_id.submission_type == 'procurement':
                    raise AccessError("Only the procurement creator can delete recommenders.")
        return super(MemoApprover, self).unlink()


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
            # 1) re-point the attachment to memo.memo
            rec.attachment_id.write({
                "res_model": "memo.memo",
                "res_id": rec.memo_id.id,
            })

            # 2) log a message so the document shows in chatter
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
            # Update existing document with correct folder and linkage
            document.sudo().write({
                'attachment_id': self.attachment_id.id,
                'folder_id': self.memo_id.folder_id.id,
                'owner_id': self.memo_id.requester_id.id,
                'res_model': self._name,
                'res_id': self.id,
                'name': self.name,
            })
        else:
            # Create a new document if it doesn’t exist
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
            'favorited_ids': [(4, self.env.user.id)],
        })
        sign_template.write({'authorized_ids': [(4, self.env.user.id)]})
        self.sign_template_id = sign_template.id
        self.signature_status = 'sent'
        return {
            'type': 'ir.actions.client',
            'tag': 'sign.Template',
            'name': sign_template.name,
            'context': {
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
        return sign_request


class SignRequest(models.Model):
    _inherit = 'sign.request'

    def _sign(self):
        res = super()._sign()

        # Check if state changed to 'signed'
        for request in self:
            upload = self.env['memo.document.upload'].search([
                ('sign_request_id', '=', request.id)
            ], limit=1)

            if upload and request.completed_document_attachment_ids:
                # Link the signed PDF back to memo
                upload.attachment_id = request.completed_document_attachment_ids[0].id
                upload.signature_status = request.state
        return res

class SignTemplate(models.Model):
    _inherit = 'sign.template'

    def open_requests(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Sign requests"),
            "res_model": "sign.request",
            "res_id": self.id,
            "domain": [["template_id", "in", self.ids]],
            "views": [[False, 'list'],[False, 'kanban'], [False, "form"]],
            "context": {'search_default_signed': True},
            "view_mode": "list,form,kanban",
        }

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
        ('Non-Completed', 'Non-Completed')], string="Status", default="Completed")
    memo_request_id = fields.Many2one('memo.memo', string="Memo Request",
                                      ondelete='cascade')
    required = fields.Boolean(default=True, readonly=True)
    sign_initials = fields.Binary(string="Digital Initials", copy=False)
    comment = fields.Text("Comment")
    date = fields.Datetime(string="Date")

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
            # if 'sign_initials' in vals and 'comment' not in vals and not record.comment:
            #     raise ValidationError("Please add Quality Assurance Comment.")
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
        base_url = self.get_base_url()
        url = f"{base_url}/web#id={self.memo_request_id.id}&model=memo.memo&view_type=form"
        user = self.user_id.name
        template.with_context(approve_user=user, url=url).sudo().send_mail(self.memo_request_id.id, force_send=True,
                                                                           email_values={
                                                                               'email_to': self.user_id.partner_id.email})

    def action_sign_line(self):
        if not self.status:
            raise ValidationError("Please add Quality Assurance Status.")
        if self.memo_request_id.state != 'quality_assurance':
            raise ValidationError("You can sign this document only if document in 'Quality Assurance' stage.")
        if not self.comment:
            raise ValidationError("Please add Quality Assurance Comment.")
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
            if rec.memo_request_id.create_uid != self.env.user:
                if rec.memo_request_id.submission_type == 'memo':
                    raise AccessError("Only the memo creator can delete quality assurance user.")
                if rec.memo_request_id.submission_type == 'circular':
                    raise AccessError("Only the circular creator can delete quality assurance user.")
                if rec.memo_request_id.submission_type == 'procurement':
                    raise AccessError("Only the procurement creator can delete quality assurance user.")
        return super(MemoQualityAssurance, self).unlink()