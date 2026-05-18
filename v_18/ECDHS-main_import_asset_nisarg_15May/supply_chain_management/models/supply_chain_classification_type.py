from odoo import api, models, fields


from odoo import models, fields

class SupplyChainClassificationType(models.Model):
    _name = 'supply.chain.classification.type'
    _description = 'Supply Chain Classification Type'

    name = fields.Char(string='Name')
    child_ids = fields.Many2many('supply.chain.sub.classification.type', 'parent_id', string='Child Classifications')

    @api.model
    def create(self, values):
        # Create the document.folder record when a classification type is created
        new_classification_type = super(SupplyChainClassificationType, self).create(
            values)
        parent_folder = self.env['documents.document'].search([('name', '=', 'Supply Chain Management')])
        if not parent_folder:
            parent_folder = self.env['documents.document'].create({
                'name': 'Supply Chain Management'
            })
        # Create a documents.folder record with the same name as the classification type
        folder_values = {
            'name': new_classification_type.name,
            'parent_folder_id': parent_folder.id
        }
        self.env['documents.document'].create(folder_values)

        return new_classification_type

