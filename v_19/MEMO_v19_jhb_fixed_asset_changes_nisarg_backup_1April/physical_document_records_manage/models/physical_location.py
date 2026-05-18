# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class CustomPhysicalLocation(models.Model):
    _name = 'custom.physical.location'
    _description = 'Physical Location'

    name = fields.Char(
        string='Name',
        required=True,
    )
    parent_location_id = fields.Many2one(
        'custom.physical.location',
        string="Parent Location",
    )
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: