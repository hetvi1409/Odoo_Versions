# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResDistrict(models.Model):
    """District"""
    _name = "res.district"
    _description = "District"

    name = fields.Char(string='District', required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)
    province_id = fields.Many2one('res.province', string="Province", required=True)


class ResDistrictCity(models.Model):
    """City"""
    _name = "res.district.city"
    _description = "City / Town"

    name = fields.Char(string='City/Town', required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)
    province_id = fields.Many2one('res.province', string="Province", required=True)
    district_id = fields.Many2one('res.district',
                                  domain="[('country_id', '=?', country_id)]", string="District", required=True)


