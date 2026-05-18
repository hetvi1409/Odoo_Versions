# -*- coding: utf-8 -*-
from odoo import api, fields, models, api

class ClientEnquirySlaPolicyStatus(models.Model):
    _inherit = 'client.enquiry.sla.policy.status'


    property_intelligence_id = fields.Many2one('property.intelligence',string ='Property Intelligence')
