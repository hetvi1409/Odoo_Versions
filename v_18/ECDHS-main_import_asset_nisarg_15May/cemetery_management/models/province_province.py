from odoo import models, fields


class ProvinceProvince(models.Model):
    _name = 'province.province'
    _description = 'Province Details'

    name = fields.Char(string='Province', required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)

class WardWard(models.Model):
    _name = 'ward.ward'
    _description = "Ward"

    name = fields.Char(string='Ward', required=True)
    district = fields.Char(string='District', required=False)
    city = fields.Char(string='City', required=False)
    country_id = fields.Many2one('res.country', string="Country", required=True)
    province_id = fields.Many2one('province.province', string="Province")
    municipality_id = fields.Many2one('municipality.municipality',
                                      string="Municipality",
                                      domain="[('province_id', '=?', province_id)]")
