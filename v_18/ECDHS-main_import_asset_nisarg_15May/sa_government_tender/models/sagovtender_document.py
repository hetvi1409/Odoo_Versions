# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64


class TenderDocument(models.Model):
    """Tender Documents"""
    _name = 'sagovtender.document'
    _description = 'Tender Document'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Document Name', required=True)
    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        ondelete='cascade'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    document_type = fields.Selection([
        ('sagovtender_document', 'Tender Document'),
        ('compliance', 'Compliance Document'),
        ('technical', 'Technical Document'),
        ('financial', 'Financial Document'),
        ('legal', 'Legal Document'),
        ('specification', 'Specification'),
        ('terms_conditions', 'Terms & Conditions'),
        ('sbd_form', 'SBD Form'),
        ('pricing_schedule', 'Pricing Schedule'),
        ('technical_drawing', 'Technical Drawing'),
        ('other', 'Other'),
    ], string='Document Type', required=True, default='')
    description = fields.Text(string='Description')
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        ondelete='cascade',
        help='Document file attachment'
    )
    attachment_filename = fields.Char(string='Filename', related='attachment_id.name', readonly=False, store=True)
    datas = fields.Binary(related='attachment_id.datas', required=True, readonly=False)
    file_size = fields.Integer(string='File Size', related='attachment_id.file_size', readonly=True)
    mandatory = fields.Boolean(
        string='Mandatory',
        default=True,
        help='Whether this document is mandatory for bidders'
    )
    public = fields.Boolean(
        string='Public',
        default=True,
        help='Whether this document is publicly accessible'
    )
    version = fields.Char(string='Version', default='1.0')
    uploaded_by_id = fields.Many2one(
        'res.users',
        string='Uploaded By',
        default=lambda self: self.env.user
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    upload_date = fields.Datetime(
        string='Upload Date',
        default=fields.Datetime.now
    )
    notes = fields.Text(string='Notes')

    def _sync_attachment(self, vals=None):
        self.ensure_one()
        attachment_vals = {
            'name': self.attachment_filename or self.name or 'Tender Document',
            'datas': self.datas,
            'res_model': self._name,
            'res_id': self.id,
            'res_field': 'attachment_id',
            'public': bool(self.public),
        }
        if self.attachment_id:
            if vals and any(key in vals for key in ('datas', 'attachment_filename', 'name', 'attachment_id', 'public')):
                self.attachment_id.sudo().write(attachment_vals)
            else:
                self.attachment_id.sudo().write({
                    'res_model': self._name,
                    'res_id': self.id,
                    'res_field': 'attachment_id',
                    'public': bool(self.public),
                })
        elif self.datas:
            attachment = self.env['ir.attachment'].sudo().create(attachment_vals)
            self.attachment_id = attachment.id

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to link attachment to this document and create from binary upload."""
        records = super().create(vals_list)
        for record, vals in zip(records, vals_list):
            record._sync_attachment(vals)
            # NEW: Link to checklist item if created from checklist
            if self.env.context.get('checklist_item_id'):
                checklist_item = self.env['sagovtender.document.checklist'].browse(
                    self.env.context['checklist_item_id']
                )
                checklist_item.write({'tender_document_id': record.id})
        return records

    def write(self, vals):
        """Override write to update attachment linkage and binary upload."""
        result = super().write(vals)
        if any(key in vals for key in ('datas', 'attachment_filename', 'name', 'attachment_id', 'public')):
            for record in self:
                record._sync_attachment(vals)
        return result

    @api.onchange('document_type')
    def _onchange_document_type(self):
        """Set document name equal to document type when document type changes"""
        if self.document_type:
            # Get the display name of the selected document type
            document_type_dict = dict(self._fields['document_type'].selection)
            self.name = document_type_dict.get(self.document_type, self.document_type)

    def action_preview_document(self):
        self.ensure_one()
        if not self.attachment_id:
            raise ValidationError("Please first upload document")

        preview_url = f"/web/content/{self.attachment_id.id}?download=false"
        return {
            'type': 'ir.actions.act_url',
            'url': preview_url,
            'target': 'new',
        }