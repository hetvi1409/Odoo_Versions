from odoo import fields, models


class EnquiryAssessment(models.Model):
    _inherit = 'enquiry.assessment'

    reg_date = fields.Date(string='Registration Date')
    title_deed_number = fields.Char(string='Title Deed Number',
                                    related='property_id.title_deed_number')
    location = fields.Char(string='Location', related='property_id.township')
    property_description = fields.Text(string='Property Description')
    region_id = fields.Many2one('regions', string='Region',
                                related='property_id.region_id')
    ward = fields.Char(string='Ward', related='property_id.ward')
    market_value = fields.Float(string='Market Value',
                                related='property_id.market_value')
    zoning_id = fields.Many2one(string='Zoning ID',
                                related='property_id.zoning_id')
    sg_id = fields.Char(string='SG ID', related='property_id.sg_id')
