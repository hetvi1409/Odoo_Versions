from odoo import models, fields


class MunicipalityMunicipality(models.Model):
    _name = 'municipality.municipality'
    _description = 'Municipality Details'

    name = fields.Char(string='Name', required=True)
    province_id = fields.Many2one('province.province', 
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string="Country")
    company_id = fields.Many2one('res.company', string="Company")
