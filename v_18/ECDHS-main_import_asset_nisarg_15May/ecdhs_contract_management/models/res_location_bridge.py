# -*- coding: utf-8 -*-
from odoo import models


class ResProvince(models.Model):
    _inherit = 'res.province'


class ResRegion(models.Model):
    _inherit = 'res.region'


class ResMunicipality(models.Model):
    _inherit = 'res.municipality'
