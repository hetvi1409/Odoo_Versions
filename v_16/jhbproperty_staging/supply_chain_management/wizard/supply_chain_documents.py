from odoo import api, models, fields


class SupplyChainDocument(models.TransientModel):
    _name = 'supply.chain.document'
    _description = 'Supply Chain Document'

    # Add fields as needed for your wizard
    attachment = fields.Binary(string='Attachments')
    attachment_filename = fields.Char(string='File')
    folder_id = fields.Many2one('supply.chain.classification.type', string="Classification")
    sub_folder_id = fields.Many2one('supply.chain.sub.classification.type', string="Sub Classification")

    @api.onchange('folder_id')
    def onchange_folder_id(self):
        if self.folder_id:
            # Create a domain to filter sub_folder_id based on the selected folder_id
            domain = [('id', 'in', self.folder_id.child_ids.ids)]
            return {'domain': {'sub_folder_id': domain}}

    def document_upload(self):
        # Access the documents.document model
        document = self.env['documents.document']

        # Find or create the parent folder based on the classification
        parent_folder = self.env['documents.folder'].search([
            ('name', '=', self.folder_id.name)
        ], limit=1)
    #
        if not parent_folder:
            parent_folder = self.env['documents.folder'].create({
                'name': self.folder_id.name,
            })
    #
        # Find or create the sub parent folder
        sub_parent_folder = self.env['documents.folder'].search([
            ('name', '=', self.sub_folder_id.name),
            ('parent_folder_id', '=', parent_folder.id)
        ], limit=1)

        if not sub_parent_folder:
            sub_parent_folder = self.env['documents.folder'].create({
                'name': self.sub_folder_id.name,
                'parent_folder_id': parent_folder.id,
            })

        attachment_report = self.env['ir.attachment'].create({
            'name': self.attachment_filename,
            'datas': self.attachment,
        })

        # Create a new document record
        new_document = document.create({
            'name': self.attachment_filename,
            'res_model': 'document.classification',
            'attachment_id': attachment_report.id,
            'res_id': 1,  # Replace with the related record's ID
            'folder_id': sub_parent_folder.id,
        })
