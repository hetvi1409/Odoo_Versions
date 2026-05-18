from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    property_id = fields.Many2one('building', string="Property", required=True)
    jmc_number = fields.Char(string="JMC Number", help="JMC number")
    maintenance_request_documents_ids = fields.One2many(
        'documents.document',
        'maintenance_request_id',
        string='Documents',
        copy=False
    )

    @api.onchange('property_id')
    def onchange_property(self):
        """Onchange property Details and update jmc_property_id on related documents"""
        self.jmc_number = self.property_id.jmc_number
        # Update jmc_property_id for all related documents
        for doc in self.maintenance_request_documents_ids:
            doc.jmc_property_id = self.property_id.id

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    maintenance_request_id = fields.Many2one('maintenance.request',
                                      string="JMC Number", tracking=True,
                                      context={'list_view_ref':'maintenance.hr_equipment_request_view_tree'})

    def action_preview_document(self):
        self.ensure_one()
        if not self.attachment_id:
            raise ValidationError("Please first upload document")

        preview_url = f'/web/content/{self.attachment_id.id}?download=false'
        if not preview_url:
            raise ValidationError("Preview not supported for this file type.")
        return {
            'type': 'ir.actions.act_url',
            'url': preview_url,
            'target': 'new',
        }