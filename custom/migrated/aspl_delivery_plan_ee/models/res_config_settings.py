# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from email.policy import default
from odoo import fields, models, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    map_type = fields.Selection([
        ('Leaflet', 'Leaflet'),
        ('Google Map', 'Google Map')
    ], default="Leaflet",string="Map Type", config_parameter='aspl_delivery_plan_ee.map_type')
    api_key = fields.Char(string="Google Map Key", config_parameter='aspl_delivery_plan_ee.api_key')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
