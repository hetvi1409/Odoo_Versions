from odoo import models, fields, api, _


class DocumentAttachments(models.Model):
    _name = 'document.attachments'
    _description = 'Document Attachments'

    assessment_attachment_id = fields.Many2many('ir.attachment', string="Assessment Documents")
    description = fields.Char(string='Description')
    document_attachment_id = fields.Many2one('oi_risk_management.risk')

    def write(self, vals):
        existing_assessment_attachments = self.assessment_attachment_id
        res = super(DocumentAttachments, self).write(vals)
        if 'assessment_attachment_id' in vals:
            new_assessment_attachments = self.assessment_attachment_id
            removed_attachments = existing_assessment_attachments - new_assessment_attachments
            self._sync_documents(vals['assessment_attachment_id'])
            self._remove_documents(removed_attachments.ids)
        return res

    def _sync_documents(self, assessment_attachment_id):
        """Synchronize attachments with documents.document."""
        document = self.env['documents.document']
        folder_id = self.env.ref('oi_risk_management.document_risk')
        if assessment_attachment_id:
            for attachment_id in assessment_attachment_id:
                attachment = self.env['ir.attachment'].browse(
                    attachment_id[1])
                if not document.search([('attachment_id', '=', attachment.id)]):
                    document.create({
                        'name': attachment.name,
                        'attachment_id': attachment.id,
                        'folder_id': folder_id.id if folder_id else ""
                        # self.env['documents.folder'].search([], limit=1).id,
                    })

    def _remove_documents(self, assessment_attachment_id):
        """Remove documents linked to detached attachments."""
        Document = self.env['documents.document']
        documents_to_remove = Document.search(
            [('attachment_id', 'in', assessment_attachment_id)])
        documents_to_remove.unlink()

    def action_view_documents(self):
        self.ensure_one()
        return {
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'name': _("%(name)s's Documents", name=self.document_attachment_id.name),
            'domain': [
                ('res_model', '=', self._name), ('res_id', '=', self.id),
                ('attachment_id', 'in', self.assessment_attachment_id.ids),
                ('folder_id', '=', self.env.ref('oi_risk_management.document_risk').id)
            ],
            'target': 'new',
            'view_mode': 'kanban,tree,form',
            'context': {'default_res_model': self._name,
                        'default_res_id': self.id},
        }
