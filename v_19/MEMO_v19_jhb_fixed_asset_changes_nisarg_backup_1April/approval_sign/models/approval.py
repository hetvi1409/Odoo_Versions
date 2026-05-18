# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ApprovalCategory(models.Model):
    _inherit = 'approval.request'

    signature = fields.Binary(string="Signature")

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['approval.request'].browse(docids)
        company = self.env.user.company_id  # Get the current company

        return {
            'doc_ids': docs.ids,
            'doc_model': self.env['approval.request'],
            'docs': docs,
            'company': company,
        }