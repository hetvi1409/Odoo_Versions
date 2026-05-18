# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PhysicalRecordKeeperCustom(models.Model):
    _inherit = 'physical.record.keeper.custom'

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
    ], string='Month',required=True,)
    reference_year = fields.Selection(
        string='Year',
        required=True,
        selection=lambda self: self.year_range_selection(50, 20),
        default=lambda self: str(fields.Datetime.now().year),
        help='Select the year for which you want to see file for which year.')
    attachment_id = fields.Many2one('ir.attachment', string="Document File",required=True)
    folder_id = fields.Many2one('documents.folder', string="Document Folder", required=True)

    def _sync_document_record(self):
        """Sync documents.document based on the current attachment/folder/month/year."""
        for record in self:
            if not record.attachment_id or not record.folder_id:
                continue  # Skip incomplete rows

            doc = self.env['documents.document'].sudo().search([
                ('attachment_id', '=', record.attachment_id.id)
            ], limit=1)

            doc_vals = {
                'folder_id': record.folder_id.id,
                'reference_month': record.reference_month,
                'reference_year': record.reference_year,
            }

            if doc:
                doc.write(doc_vals)
            else:
                self.env['documents.document'].sudo().create({
                    'name': record.attachment_id.name,
                    'attachment_id': record.attachment_id.id,
                    'folder_id': record.folder_id.id,
                    'reference_month': record.reference_month,
                    'reference_year': record.reference_year,
                })

    @api.model_create_multi
    def create(self, vals):
        record = super().create(vals)
        record._sync_document_record()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._sync_document_record()
        return res