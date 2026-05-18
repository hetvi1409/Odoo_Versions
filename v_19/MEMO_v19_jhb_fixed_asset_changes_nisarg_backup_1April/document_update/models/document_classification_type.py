from odoo import api, models, fields


class DocumentClassification(models.Model):
    _name = 'document.classification.type'
    _description = 'Document Classification Types'

    name = fields.Char(string='Name')

    @api.model
    def create(self, values):
        # Create the document.folder record when a classification type is created
        new_classification_type = super(DocumentClassification, self).create(
            values)
        parent_folder = self.env['documents.document'].search([('name', '=', 'Property Management')])
        # Create a documents.document record with the same name as the classification type
        folder_values = {
            'name': new_classification_type.name,
            'folder_id': parent_folder.id
        }
        self.env['documents.document'].create(folder_values)
        return new_classification_type

