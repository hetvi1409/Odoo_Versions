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

from odoo import http
from odoo.http import request

class DeliveryMapController(http.Controller):

    @http.route('/delivery/map/config', type='json', auth='user')
    def get_map_config(self):
        map_type = request.env['ir.config_parameter'].sudo().get_param('aspl_delivery_plan_ee.map_type')
        api_key = request.env['ir.config_parameter'].sudo().get_param('aspl_delivery_plan_ee.api_key')
        return {
            'map_type': map_type,
            'api_key': api_key
        }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: