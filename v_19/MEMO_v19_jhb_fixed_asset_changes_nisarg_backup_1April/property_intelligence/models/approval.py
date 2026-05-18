# -*- coding: utf-8 -*-
from odoo import api, fields, models, api

class Approval(models.Model):
    _inherit = 'approval.request'

    property_intelligence_id = fields.Many2one('property.intelligence',
                                               string='Property Intelligence')
    investigation_report_ids = fields.Many2many('ir.attachment',
                                                'investigation_report_rel',
                                                string='Investigation Report')
    image_ids = fields.Many2many('ir.attachment', 'investigation_image_rel',
                                 string='Investigation Images')

    def action_approve(self, approver=None):
        res = super(Approval, self).action_approve(approver=approver)
        for request in self:
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'approval.request'),
                ('res_id', '=', request.id)
            ])
            property_intelligence_record = request.property_intelligence_id
            if property_intelligence_record:
                property_intelligence_record.write({
                    'feedback_document_ids': [(6, 0, attachments.ids)],
                    'state': 'feedback'
                })
        return res

    def action_refuse(self, approver=None):
        res = super(Approval, self).action_refuse(approver=approver)
        for request in self:
            property_intelligence_record = request.property_intelligence_id
            if property_intelligence_record:
                property_intelligence_record.write({
                    'state': 'refuse'
                })
        return res
