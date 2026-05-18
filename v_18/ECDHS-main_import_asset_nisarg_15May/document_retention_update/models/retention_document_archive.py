# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models


class RetentionDocumentArchiver(models.Model):
    _name = 'retention.document.archiver'

    @api.model
    def archive_retention_documents(self):
        documents_to_archive = self.env['documents.document'].search([])
        # Perform the archiving logic
        for document in documents_to_archive:
            current_date = fields.Datetime.now()
            retention_end_date = document.create_date + timedelta(
                days=document.folder_id.retention_periods * 365)
            if document.folder_id.retention_periods:
                if current_date <= retention_end_date:
                    document.write(
                        {'active': False})  # Set the document as inactive
