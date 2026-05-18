# -*- coding: utf-8 -*-
from odoo import fields, models


class StockPicking(models.Model):
    """Inherit model 'stock.picking' and add required fields """
    _inherit = 'stock.picking'

    is_enable_order_line = fields.Boolean(string='Include Product Details',
                                          default=True,
                                          help="If you want to print the "
                                               "product details in your report"
                                               " enable this field.")
    vehicle_no = fields.Char(string='Vehicle Number',
                             help="Enter the vehicle number.")
    vehicle_driver_name = fields.Char(string='Driver Name',
                                      help="Enter the driver's name.")
    driver_contact_number = fields.Char(string='Contact No',
                                        help="Enter the driver's contact"
                                             " number.")
    corresponding_company = fields.Char(string='Company',
                                        help="Enter the corresponding company.")
