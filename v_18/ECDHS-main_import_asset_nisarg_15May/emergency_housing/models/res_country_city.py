from odoo import fields, models


class City(models.Model):
    """City"""
    _name = 'res.country.city'
    _description = "City"

    name = fields.Char(string="City", required=True)
    country_id = fields.Many2one('res.country', string='Country')
    province_id = fields.Many2one('res.province', string='Province',
                                  domain="[('country_id', '=?', country_id)]")
    latitude = fields.Float('Latitude', digits=(10, 7), copy=False)
    longitude = fields.Float('Longitude', digits=(10, 7), copy=False)
