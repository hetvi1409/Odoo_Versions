from odoo.exceptions import ValidationError
from odoo import api, fields, models, tools, _


class Channel(models.Model):
    _inherit = 'building.attachment.line'

    def open_document_wizard(self):
        # Get the value of the field you want to pass to the wizard
        jmc_number = self.building_attach_id.jmc_number
        region = self.building_attach_id.region_id

        # Create a new record in the document.classification model
        document_classification = self.env['document.classification'].create({
            'jmc_no': jmc_number,
            'regions_id': region.name,
            # Set the value for the field in the wizard
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'document.classification',
            'res_id': document_classification.id, # Pass the ID of the created record
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
        }