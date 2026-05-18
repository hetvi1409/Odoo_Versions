# -*- coding: utf-8 -*-

import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EcdhsContractDocumentUpload(models.Model):
    _name = 'ecdhs.contract.document.upload'
    _description = 'Contract Supporting Document Upload'
    _order = 'sequence, id'

    sequence = fields.Integer(default=1)
    contract_id = fields.Many2one('ecdhs.contract', string='Contract', ondelete='cascade')
    monitoring_id = fields.Many2one('ecdhs.contract.monitoring', string='Contract Review', ondelete='cascade')
    document_type = fields.Selection([
        ('annexure', 'Annexure / Appendix'),
        ('supporting', 'Supporting Document'),
        ('monitoring_letter_report', 'Letter / Report'),
    ], string='Document Type', required=True)
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Document',
        domain=[('mimetype', '=', 'application/pdf')],
        ondelete='cascade',
    )
    name = fields.Char(string='Document Name', readonly=True, copy=False)
    file_name = fields.Char(string='File Name')
    annexure_sequence_name = fields.Char(string='Annexure / Appendices', readonly=True, copy=False)
    source_document = fields.Selection([
        ('manual', 'Manual'),
        ('jbcc', 'JBCC Upload'),
        ('gcc', 'GCC Upload'),
    ], string='Source', default='manual', copy=False)
    datas = fields.Binary(related='attachment_id.datas', required=True, readonly=False)

    # -------------------------------------------------------------------------
    # Document Filing System
    # -------------------------------------------------------------------------
    folder_id = fields.Many2one(
        'documents.document',
        string='Document Folder',
        readonly=True,
        domain="[('type', '=', 'folder')]",
        help='Folder for storing this document, linked to parent contract.'
    )

    @staticmethod
    def _alpha_index(index):
        """Convert 1-based index to alphabetic label (A..Z, AA..ZZ, ...)."""
        if index <= 0:
            return 'A'
        chars = []
        while index:
            index, rem = divmod(index - 1, 26)
            chars.append(chr(65 + rem))
        return ''.join(reversed(chars))

    @staticmethod
    def _document_prefix(document_type):
        if document_type == 'annexure':
            return 'Annexure'
        elif document_type == 'monitoring_letter_report':
            return 'Letter / Report'
        else:
            return 'Supporting Document'

    def _get_subfolder_name_for_document_type(self, document_type):
        """Map document_type to the appropriate contract subfolder."""
        mapping = {
            'annexure': 'Annexures',
            'supporting': 'Supporting Documents',
            'monitoring_letter_report': 'Monthly Reports',
        }
        return mapping.get(document_type, 'Other Documents')

    def _next_document_name(self, parent_id, document_type, parent_field='contract_id'):
        domain = [
            (parent_field, '=', parent_id),
            ('document_type', '=', document_type),
        ]
        count = self.search_count(domain)
        return '%s %s' % (self._document_prefix(document_type), self._alpha_index(count + 1))

    def _renumber_group_names(self, parent_id, document_type, parent_field='contract_id'):
        domain = [
            (parent_field, '=', parent_id),
            ('document_type', '=', document_type),
        ]
        docs = self.search(domain, order='sequence, id')
        prefix = self._document_prefix(document_type)
        for idx, rec in enumerate(docs, start=1):
            expected = '%s %s' % (prefix, self._alpha_index(idx))
            if rec.annexure_sequence_name != expected:
                rec.with_context(skip_auto_name_sync=True).write({'annexure_sequence_name': expected})

    def _renumber_impacted_groups(self, before_map=None):
        groups = set(before_map or set())
        for rec in self:
            if rec.contract_id and rec.document_type:
                groups.add((rec.contract_id.id, rec.document_type, 'contract_id'))
            elif rec.monitoring_id and rec.document_type:
                groups.add((rec.monitoring_id.id, rec.document_type, 'monitoring_id'))
        for parent_id, document_type, parent_field in groups:
            self._renumber_group_names(parent_id, document_type, parent_field)

    def _sync_name_from_file_name(self):
        for rec in self:
            if rec.file_name and rec.name != rec.file_name:
                rec.with_context(internal_sync=True).write({
                    'name': rec.file_name,
                })

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        if not vals.get('document_type'):
            vals['document_type'] = self.env.context.get('default_document_type', 'supporting')
        return vals

    @staticmethod
    def _is_pdf_content(datas):
        if not datas:
            return False
        try:
            raw = base64.b64decode(datas)
        except Exception:
            return False
        # Some producers prepend BOM/whitespace before the PDF header.
        head = raw[:1024].lstrip(b'\xef\xbb\xbf\x00\t\r\n\x0c\x0b ')
        return head.startswith(b'%PDF-')

    def _ensure_pdf_only(self):
        for rec in self:
            name_is_pdf = bool(rec.file_name and rec.file_name.lower().endswith('.pdf'))
            mimetype_is_pdf = bool(
                rec.attachment_id and rec.attachment_id.mimetype in ('application/pdf', 'application/x-pdf')
            )
            content_is_pdf = bool(rec.datas and rec._is_pdf_content(rec.datas))
            if rec.datas and not (name_is_pdf or mimetype_is_pdf or content_is_pdf):
                raise ValidationError(_('Only PDF files are allowed.'))

    def _upsert_attachment(self):
        for rec in self:
            parent_id = rec.contract_id.id if rec.contract_id else rec.monitoring_id.id
            parent_field = 'contract_id' if rec.contract_id else 'monitoring_id'
            attachment_name = rec.file_name or rec.name or ('%s.pdf' % rec._next_document_name(parent_id, rec.document_type, parent_field))
            res_model = 'ecdhs.contract' if rec.contract_id else 'ecdhs.contract.monitoring'
            res_id = parent_id
            vals = {
                'name': attachment_name,
                'datas': rec.datas,
                'mimetype': 'application/pdf',
                'res_model': res_model,
                'res_id': res_id,
            }
            if not rec.attachment_id:
                rec.attachment_id = self.env['ir.attachment'].sudo().create(vals).id
            else:
                rec.attachment_id.sudo().write(vals)

    def _sync_to_documents_file_plan(self):
        """Create/update documents.document entries so files appear in File Plan."""
        for rec in self:
            if not rec.attachment_id or not rec.folder_id:
                continue
            owner = (rec.contract_id.end_user_id.id if rec.contract_id else False) or self.env.user.id
            vals = {
                'attachment_id': rec.attachment_id.id,
                'folder_id': rec.folder_id.id,
                'owner_id': owner,
                'res_model': rec._name,
                'res_id': rec.id,
                'name': rec.name or rec.attachment_id.name,
            }
            document = self.env['documents.document'].sudo().search([
                ('attachment_id', '=', rec.attachment_id.id),
            ], limit=1)
            if document:
                document.sudo().write(vals)
            else:
                self.env['documents.document'].sudo().create(vals)

    @staticmethod
    def _get_changed_fields(vals):
        return {'name', 'file_name', 'datas', 'attachment_id', 'contract_id', 'sequence', 'document_type'} & set(vals.keys())

    @api.model_create_multi
    def create(self, vals_list):
        # Guard against callers that pass a single dict instead of a list.
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        prepared_vals_list = []
        for vals in vals_list:
            vals = dict(vals or {})
            # If document_type not explicitly set, check context for default
            if 'document_type' not in vals:
                vals['document_type'] = self.env.context.get('default_document_type', 'supporting')
            if not vals.get('contract_id'):
                vals['contract_id'] = self.env.context.get('default_contract_id')
            if not vals.get('monitoring_id'):
                vals['monitoring_id'] = self.env.context.get('default_monitoring_id')
            if vals.get('file_name'):
                vals['name'] = vals['file_name']
            prepared_vals_list.append(vals)

        records = super().create(prepared_vals_list)
        records._sync_name_from_file_name()
        records._renumber_impacted_groups()
        records._ensure_pdf_only()
        records._upsert_attachment()

        # Assign documents to appropriate subfolders in contract's folder structure
        for doc in records:
            if doc.contract_id and doc.contract_id.folder_id:
                subfolder_name = doc._get_subfolder_name_for_document_type(doc.document_type)
                subfolder = doc.contract_id._get_contract_subfolder(subfolder_name)
                if subfolder:
                    doc.sudo().write({'folder_id': subfolder.id})
        records._sync_to_documents_file_plan()

        return records

    def write(self, vals):
        if self.env.context.get('internal_sync'):
            return super().write(vals)

        if self.env.context.get('skip_auto_name_sync'):
            return super().write(vals)

        vals = dict(vals)

        before_groups = set()
        for rec in self:
            if rec.contract_id and rec.document_type:
                before_groups.add((rec.contract_id.id, rec.document_type, 'contract_id'))
            elif rec.monitoring_id and rec.document_type:
                before_groups.add((rec.monitoring_id.id, rec.document_type, 'monitoring_id'))
        res = super().write(vals)
        if {'file_name', 'attachment_id'} & set(vals.keys()):
            self._sync_name_from_file_name()
        if {'sequence', 'document_type', 'contract_id'} & set(vals.keys()):
            self._renumber_impacted_groups(before_groups)
        if self._get_changed_fields(vals):
            self._ensure_pdf_only()
        if self._get_changed_fields(vals):
            self._upsert_attachment()

        # Re-assign folder if contract_id or document_type changes
        if 'contract_id' in vals or 'document_type' in vals:
            for doc in self:
                if doc.contract_id and doc.contract_id.folder_id:
                    subfolder_name = doc._get_subfolder_name_for_document_type(doc.document_type)
                    subfolder = doc.contract_id._get_contract_subfolder(subfolder_name)
                    if subfolder:
                        doc.sudo().write({'folder_id': subfolder.id})

        if self._get_changed_fields(vals) or 'folder_id' in vals:
            self._sync_to_documents_file_plan()

        return res

    @api.constrains('datas', 'name')
    def _check_pdf_only(self):
        self._ensure_pdf_only()

    def action_preview_document(self):
        self.ensure_one()
        if not self.attachment_id:
            raise ValidationError(_('Please upload a PDF document first.'))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=false' % self.attachment_id.id,
            'target': 'new',
        }


    def unlink(self):
        attachments = self.mapped('attachment_id')
        res = super().unlink()
        if attachments:
            attachments.sudo().unlink()
        return res
