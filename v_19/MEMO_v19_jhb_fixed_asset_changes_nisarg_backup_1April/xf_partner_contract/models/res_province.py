from odoo import models, fields

class ResProvince(models.Model):
    _name = 'res.province'
    _description = 'Province details'
    _rec_name = 'province'

    country_id = fields.Many2one('res.country', string='Country')
    province = fields.Char(string='Province')

class ResRegion(models.Model):
    _name = 'res.region'
    _description = 'Region details'
    _rec_name = 'region'

    country_id = fields.Many2one('res.country', string='Country')
    province_id = fields.Many2one('res.province', string='Province',
                                  domain="[('country_id', '=?', country_id)]")
    region = fields.Char(string='Region')

class ResMunicipality(models.Model):
    _name = 'res.municipality'
    _description = 'Municipality details'
    _rec_name = 'municipality'

    country_id = fields.Many2one('res.country', string='Country')
    province_id = fields.Many2one('res.province', string='Province', domain="[('country_id', '=?', country_id)]")
    region_id = fields.Many2one('res.region',string='Region',domain="[('province_id', '=?', province_id)]")
    municipality = fields.Char(string='Municipality')






