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

from odoo import fields,models
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import logging

_logger = logging.getLogger(__name__)


def geo_localize_address(address):
    _logger.info(f"Geocoding address: {address}")
    geolocator = Nominatim(user_agent="odoo_stock_geocoder")
    try:
        location = geolocator.geocode(address)
        _logger.info(f"Location result: {location}")
        return location
    except GeocoderTimedOut:
        _logger.warning("Geocoding timed out")
        return None


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state_id = fields.Many2one('res.country.state', string="State")
    zip = fields.Char(string="ZIP")
    country_id = fields.Many2one('res.country', string="Country")
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")

    def action_refresh_coordinates(self):
        for record in self:
            address = ', '.join(filter(None, [
                record.street,
                record.city,
                record.state_id.name if record.state_id else '',
                record.zip,
                record.country_id.name if record.country_id else ''
            ]))
            location = geo_localize_address(address)
            if location:
                record.latitude = str(location.latitude)
                record.longitude = str(location.longitude)
            else:
                record.latitude = ''
                record.longitude = ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
