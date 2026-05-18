from odoo import models, fields

class ResProvince(models.Model):
    _name = 'res.province'
    _description = 'Province details'
    _rec_name = 'province'

    country_id = fields.Many2one('res.country', string='Country')
    province = fields.Char(string='Province')