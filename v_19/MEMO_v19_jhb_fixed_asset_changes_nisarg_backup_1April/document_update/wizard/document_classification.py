from odoo import models, fields


class DocumentClassification(models.TransientModel):
    _name = 'document.classification'
    _description = 'Document Classification'

    # Add fields as needed for your wizard
    classification_id = fields.Many2one(
        comodel_name='document.classification.type', string='Classification')
    attachment = fields.Binary(string='Attachments')
    attachment_filename = fields.Char(string='File')
    jmc_no = fields.Char(string='JMC Number')
    regions_id = fields.Char(string='Region')
    doc_s = fields.Many2one(
        comodel_name='documents.document', string="doc")

    def doc_upload(self):
        # Access the documents.document model
        document = self.env['documents.document']

        # Find or create the parent folder based on the classification
        parent_folder = self.env['documents.document'].search([
            ('name', '=', self.classification_id.name)
        ], limit=1)

        if not parent_folder:
            parent_folder = self.env['documents.document'].create({
                'name': self.classification_id.name,
            })

        # Find or create the sub parent folder based on the region
        sub_parent_folder = self.env['documents.document'].search([
            ('name', '=', self.regions_id),
            ('folder_id', '=', parent_folder.id)
        ], limit=1)

        if not sub_parent_folder:
            sub_parent_folder = self.env['documents.document'].create({
                'name': self.regions_id,
                'folder_id': parent_folder.id,
            })

        # Find or create the subfolder based on the unique jmc_number under the region
        jmc_folder = self.env['documents.document'].search([
            ('name', '=', self.jmc_no),
            ('folder_id', '=', sub_parent_folder.id)
        ], limit=1)

        if not jmc_folder:
            folder_values = {
                'name': self.jmc_no,
                'folder_id': sub_parent_folder.id,
            }
            jmc_folder = self.env['documents.document'].create(folder_values)

        attachment_report = self.env['ir.attachment'].create({
            'name': self.attachment_filename,
            'datas': self.attachment,
            # 'res_model': self.assessment_id._name,
            # 'res_id': self.assessment_id.id
        })

        # Create a new document record
        new_document = document.create({
            'name': self.attachment_filename,
            'res_model': 'document.classification',
            'attachment_id': attachment_report.id,
            'res_id': 1,  # Replace with the related record's ID
            'folder_id': jmc_folder.id,
        })
