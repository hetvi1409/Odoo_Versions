from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from markupsafe import Markup
import io
import base64
import re
from PyPDF2 import PdfReader
from odoo.tools import pdf
import logging

_logger = logging.getLogger(__name__)


class MemoActionWizard(models.TransientModel):
    _name = 'memo.action.wizard'
    _description = 'Memo Action Wizard'

    memo_id = fields.Many2one('memo.memo', string="Memo", required=True)
    action_type = fields.Selection([('reject', 'Reject'), ('change', 'Change Request')], required=True)
    reject_reason = fields.Text("Rejection Reason")
    change_reason = fields.Text("Change Request Reason")

    def confirm_action(self):
        self.ensure_one()
        memo = self.memo_id

        if self.action_type == 'reject':
            if not self.reject_reason:
                raise ValidationError("Please provide a rejection reason.")
            if not self.reject_reason or not re.search(r'\w+', self.reject_reason):
                raise UserError("You must provide a valid comment before rejecting.")
            memo.sudo().action_save_version()
            if memo.attachment_id:
                memo.attachment_id.sudo().unlink()
                memo.attachment_id = False  # reset before reuse
            Report = self.env['ir.actions.report']
            submission_report_pdfs = []
            report_pdf, _ = Report._render_qweb_pdf('e_system.action_report_memo_management', memo.id)
            if report_pdf:
                submission_report_pdfs.append(report_pdf)
            filename = f"Memo_{memo.name or memo.id}.pdf"
            for doc in memo.sudo().document_upload_ids.sorted("sequence"):
                attachment = doc.sudo().attachment_id
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
                        pdf_data = memo.image_to_a4_pdf(raw_data)
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
                'res_id': memo.id,
                'mimetype': 'application/pdf',
            })
            memo.sudo().write({'attachment_id': attachment.id})
            if memo.submission_type == 'memo':
                base_url = memo.get_base_url()
                url = f"{base_url}/web#id={memo.id}&model=memo.memo&view_type=form"
                partner_ids = [memo.create_uid.partner_id.id]
                if memo.requester_id:
                    partner_ids.extend([memo.requester_id.partner_id.id])
                if memo.quality_assurance_ids:
                    partner_ids.extend(memo.quality_assurance_ids.mapped('user_id.partner_id.id'))
                if memo.recommender_ids:
                    partner_ids.extend(memo.recommender_ids.mapped('user_id.partner_id.id'))
                if memo.acknowledged_ids:
                    partner_ids.extend(memo.acknowledged_ids.mapped('user_id.partner_id.id'))
                memo.message_post(
                    body=Markup(
                        '<p>The e-submission memo application <strong>{name}</strong> has rejected.</p><p><b>Requested By:</b> {user}</p><p><b>Reason:</b> {reason}</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                        name=memo.name,
                        user=self.env.user.name,
                        reason=self.reject_reason,
                        link=url
                    ),
                    partner_ids=partner_ids,
                    subject="Memo Document Rejected",
                    email_from=self.env.user.partner_id.email or '',
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                    attachment_ids=memo.attachment_id.ids,
                )
            if memo.submission_type == 'circular':
                base_url = memo.get_base_url()
                url = f"{base_url}/web#id={memo.id}&model=memo.memo&view_type=form"
                partner_ids = [memo.create_uid.partner_id.id]
                if memo.requester_id:
                    partner_ids.extend([memo.requester_id.partner_id.id])
                if memo.quality_assurance_ids:
                    partner_ids.extend(memo.quality_assurance_ids.mapped('user_id.partner_id.id'))
                if memo.recommender_ids:
                    partner_ids.extend(memo.recommender_ids.mapped('user_id.partner_id.id'))
                if memo.acknowledged_ids:
                    partner_ids.extend(memo.acknowledged_ids.mapped('user_id.partner_id.id'))
                memo.message_post(
                    body=Markup(
                        '<p>The e-submission circular application <strong>{name}</strong> has rejected.</p><p><b>Requested By:</b> {user}</p><p><b>Reason:</b> {reason}</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                        name=memo.name,
                        user=self.env.user.name,
                        reason=self.reject_reason,
                        link=url
                    ),
                    partner_ids=partner_ids,
                    subject="Circular Document Rejected",
                    email_from=self.env.user.partner_id.email or '',
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                    attachment_ids=memo.attachment_id.ids,
                )
            if memo.submission_type == 'procurement':
                base_url = memo.get_base_url()
                url = f"{base_url}/web#id={memo.id}&model=memo.memo&view_type=form"
                partner_ids = [memo.create_uid.partner_id.id]
                if memo.requester_id:
                    partner_ids.extend([memo.requester_id.partner_id.id])
                if memo.quality_assurance_ids:
                    partner_ids.extend(memo.quality_assurance_ids.mapped('user_id.partner_id.id'))
                if memo.recommender_ids:
                    partner_ids.extend(memo.recommender_ids.mapped('user_id.partner_id.id'))
                if memo.acknowledged_ids:
                    partner_ids.extend(memo.acknowledged_ids.mapped('user_id.partner_id.id'))
                memo.message_post(
                    body=Markup(
                        '<p>The e-submission procurement application <strong>{name}</strong> has rejected.</p><p><b>Requested By:</b> {user}</p><p><b>Reason:</b> {reason}</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                        name=memo.name,
                        user=self.env.user.name,
                        reason=self.reject_reason,
                        link=url
                    ),
                    partner_ids=partner_ids,
                    subject="Procurement Document Rejected",
                    email_from=self.env.user.partner_id.email or '',
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                    attachment_ids=memo.attachment_id.ids,
                )
            memo.state = 'rejected'
            memo.rejection_reason = self.reject_reason

        if self.action_type == 'change':
            if not self.change_reason:
                raise ValidationError(_("Please provide a change request reason."))
            if not self.change_reason or not re.search(r'\w+', self.change_reason):
                raise UserError("You must provide a valid comment before change request.")
            memo.action_save_version()
            if memo.sudo().attachment_id:
                memo.attachment_id.sudo().unlink()
                memo.attachment_id = False  # reset before reuse
            Report = self.env['ir.actions.report']
            submission_report_pdfs = []
            report_pdf, _ = Report._render_qweb_pdf('e_system.action_report_memo_management', memo.id)
            if report_pdf:
                submission_report_pdfs.append(report_pdf)
            filename = f"Memo_{memo.name or memo.id}.pdf"
            for doc in memo.sudo().document_upload_ids.sorted("sequence"):
                attachment = doc.sudo().attachment_id
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
                        pdf_data = memo.image_to_a4_pdf(raw_data)
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
                'res_id': memo.id,
                'mimetype': 'application/pdf',
            })
            memo.sudo().write({'attachment_id': attachment.id})
            if memo.submission_type == 'memo':
                base_url = memo.get_base_url()
                url = f"{base_url}/web#id={memo.id}&model=memo.memo&view_type=form"
                partner_ids = [memo.create_uid.partner_id.id]
                if memo.requester_id:
                    partner_ids.extend([memo.requester_id.partner_id.id])
                if memo.quality_assurance_ids:
                    partner_ids.extend(memo.quality_assurance_ids.mapped('user_id.partner_id.id'))
                if memo.recommender_ids:
                    partner_ids.extend(memo.recommender_ids.mapped('user_id.partner_id.id'))
                if memo.acknowledged_ids:
                    partner_ids.extend(memo.acknowledged_ids.mapped('user_id.partner_id.id'))
                memo.sudo().message_post(
                    body=Markup(
                        '<p>The e-submission memo application <strong>{name}</strong> has change request.</p><p><b>Requested By:</b> {user}</p><p><b>Reason:</b> {reason}</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                        name=memo.name,
                        user=self.env.user.name,
                        reason=self.change_reason,
                        link=url
                    ),
                    partner_ids=partner_ids,
                    subject="Memo Document Change Request",
                    email_from=self.env.user.partner_id.email or '',
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                    attachment_ids=memo.attachment_id.ids,
                )
            if memo.submission_type == 'circular':
                base_url = memo.get_base_url()
                url = f"{base_url}/web#id={memo.id}&model=memo.memo&view_type=form"
                partner_ids = [memo.create_uid.partner_id.id]
                if memo.requester_id:
                    partner_ids.extend([memo.requester_id.partner_id.id])
                if memo.quality_assurance_ids:
                    partner_ids.extend(memo.quality_assurance_ids.mapped('user_id.partner_id.id'))
                if memo.recommender_ids:
                    partner_ids.extend(memo.recommender_ids.mapped('user_id.partner_id.id'))
                if memo.acknowledged_ids:
                    partner_ids.extend(memo.acknowledged_ids.mapped('user_id.partner_id.id'))
                memo.sudo().message_post(
                    body=Markup(
                        '<p>The e-submission circular application <strong>{name}</strong> has change request.</p><p><b>Requested By:</b> {user}</p><p><b>Reason:</b> {reason}</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                        name=memo.name,
                        user=self.env.user.name,
                        reason=self.change_reason,
                        link=url
                    ),
                    partner_ids=partner_ids,
                    subject="Circular Document Change Request",
                    email_from=self.env.user.partner_id.email or '',
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                    attachment_ids=memo.attachment_id.ids,
                )
            if memo.submission_type == 'procurement':
                base_url = memo.get_base_url()
                url = f"{base_url}/web#id={memo.id}&model=memo.memo&view_type=form"
                partner_ids = [memo.create_uid.partner_id.id]
                if memo.requester_id:
                    partner_ids.extend([memo.requester_id.partner_id.id])
                if memo.quality_assurance_ids:
                    partner_ids.extend(memo.quality_assurance_ids.mapped('user_id.partner_id.id'))
                if memo.recommender_ids:
                    partner_ids.extend(memo.recommender_ids.mapped('user_id.partner_id.id'))
                if memo.acknowledged_ids:
                    partner_ids.extend(memo.acknowledged_ids.mapped('user_id.partner_id.id'))
                memo.sudo().message_post(
                    body=Markup(
                        '<p>The e-submission procurement application <strong>{name}</strong> has change request.</p><p><b>Requested By:</b> {user}</p><p><b>Reason:</b> {reason}</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                        name=memo.name,
                        user=self.env.user.name,
                        reason=self.change_reason,
                        link=url
                    ),
                    partner_ids=partner_ids,
                    subject="Procurement Document Change Request",
                    email_from=self.env.user.partner_id.email or '',
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                    attachment_ids=memo.attachment_id.ids,
                )

            memo.sudo().state = 'change_requested'
            memo.sudo().change_reason = self.change_reason