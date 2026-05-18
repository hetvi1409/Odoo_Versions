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

from odoo import models, fields, api, _
from math import radians, sin, cos, sqrt, atan2, asin
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class DeliveryAssign(models.Model):
    _name = 'assign.delivery'
    _description = 'Assigned Deliveries to Driver'

    driver_id = fields.Many2one('res.users', 'Driver')
    delivery_date = fields.Date('Delivery Date')
    delivery_order_ids = fields.One2many('assign.delivery.line', 'assign_delivery_record_id', 'Deliveries')
    sequence_number = fields.Char('Priority')

    def create_assign_delivery(self, sloc, vals,sequence):
        driver_id = vals[0]
        delivery_date = vals[1]
        assign_line_dicts = vals[2]
        data_list = []
        for line in assign_line_dicts:
            sequence = line.get("sequence")
            line.update({
                'driver_id': driver_id,
                'delivery_date': delivery_date,
                'sequence_number': str(sequence)
            })
            picking_id = self.env['stock.picking'].browse(line.get('order_id'))
            picking = self.env['assign.delivery.line'].search([('order_id','=',picking_id.id)])
            if not picking:
                data_list.append((0, 0, line))
                picking_id.sudo().write({
                    'responsible_driver': driver_id,
                    'is_assigned': True,
                    'sequence_number': str(sequence)
                })
        create_vals = {
            'driver_id': driver_id,
            'delivery_date': delivery_date,
            'delivery_order_ids': data_list,
            'sequence_number': str(sequence)
        }
        record = self.create(create_vals)
        locations = {}
        for order_line in record.delivery_order_ids:
            partner_orders = []
            partner = order_line.customer_id
            address = partner.street if partner.street else ''  + ' ' \
                    + partner.street2 if partner.street2 else ''+ ' ' \
                    + partner.city if partner.city else ''

            partner.geo_localize()
            if partner.id not in locations.keys():
                locations[partner.id] = []
            partner_orders = locations[partner.id]
            partner_orders.append({
                'partner_name': partner.name,
                'order': order_line.order_id.name,
                'cordinates': [partner.partner_latitude, partner.partner_longitude],
                'address': address,
                })
            locations[partner.id] = partner_orders
        sorted_locations = self.sort_locations(sloc, locations)
        self._send_driver_email(driver_id, delivery_date, assign_line_dicts)
        return sorted_locations

    def unlock_delivery(self,order):
        picking = self.env['stock.picking'].browse(int(order))
        picking.sudo().write({'responsible_driver':False})
        delivery_line = self.env['assign.delivery.line'].search([('order_id','=',picking.id)])
        delivery_line.sudo().unlink()
        return True

    def _send_driver_email(self, driver_id, delivery_date, delivery_lines):
        user = self.env['res.users'].browse(driver_id)
        if not user.partner_id.email:
            raise UserError(_("Selected driver does not have an email address."))

        mail_template = self.env.ref('aspl_delivery_plan_ee.email_template_driver_notification',
                                     raise_if_not_found=False)
        if mail_template:
            mail_template.send_mail(user.id, force_send=True, email_values={
                'email_to': user.partner_id.email,
            })
        else:
            body = "<p>Hello %s,</p>" \
                   "<p>You have been assigned to deliver %d orders on %s.</p>" % (
                       user.name, len(delivery_lines), delivery_date)

            self.env['mail.mail'].create({
                'subject': 'New Delivery Assignment',
                'body_html': body,
                'email_to': user.partner_id.email,
            }).send()

    def process_delivery(self, sloc, data):
        location_data = {}
        for order in data:
            partner_orders = []
            partner = self.env['res.partner'].browse(order.get('partner_id')[0])
            address = partner.street if partner.street else ''  + ' ' \
                    + partner.street2 if partner.street2 else ''+ ' ' \
                    + partner.city if partner.city else ''

            partner.geo_localize()
            if partner.id not in location_data.keys():
                location_data[partner.id] = []
            partner_orders = location_data[partner.id]
            partner_orders.append({
                'partner_name': partner.name,
                'order': order.get('name'),
                'cordinates': [partner.partner_latitude, partner.partner_longitude],
                'address': address,
                'partner_id': partner.id,
                'order_id': order.get('id'),
                })
            location_data[partner.id] = partner_orders
        sorted_locations = self.sort_locations(sloc, location_data)
        return sorted_locations

    def sort_locations(self, sloc, locations):
        sorted_locations = []
        visited_locations = set()

        while locations:
            distance_list = []

            # Find the nearest location from the current sloc
            for partner_id, orders in locations.items():
                first_order = orders[0]  # Take the first order’s coordinates
                dest_coords = first_order['cordinates']
                distance = self.calculateDistance(sloc, dest_coords)
                distance_list.append((partner_id, orders, dest_coords, distance))

            # Sort locations based on distance
            sorted_distance_list = sorted(distance_list, key=lambda x: x[3])

            # Pick the nearest location
            if sorted_distance_list:
                nearest_location = sorted_distance_list.pop(0)  # Get the closest location
                partner_id, orders, new_sloc, _ = nearest_location

                # Update the current location sloc
                sloc = new_sloc  # Now, the current location is this stop
                sorted_locations.append({
                    'partner_id': partner_id,
                    'orders': orders,
                    'priority': len(sorted_locations) + 1
                })

                # Remove the visited location
                visited_locations.add(partner_id)
                locations.pop(partner_id)
        return sorted_locations

    def get_delivery_product_lines(self, order_id):
        _logger.info("Order ID >> %s", order_id)

        order = self.env['stock.picking'].sudo().browse(order_id).exists()
        if not order:
            _logger.warning("Stock Picking %s does not exist", order_id)
            return {}

        # Warehouse name (safe)
        warehouse = order.location_id.warehouse_id
        warehouse_name = warehouse.name if warehouse else ""

        order_lines = {
            "warehouse_name": warehouse_name,
        }

        data = []

        # Use move_ids_without_package (correct field)
        for line in order.move_ids:
            data.append({
                "line_id": line.id,
                "product_name": line.product_id.display_name,
                "quantity": line.product_uom_qty,
            })

        order_lines["data_lines"] = data
        return order_lines


    # def get_delivery_product_lines(self, order_id):
    #     print("Order ID>>", order_id)
    #     # Order ID>> 5
    #     order = self.env['stock.picking'].sudo().browse(order_id)
    #     print("Order>>", order)
    #     # Order>> stock.picking('5',)
    #     print("Order ID>>", order.location_id.warehouse_id.name)
    #     order_lines = {
    #         'warehouse_name': order.location_id.warehouse_id.name
    #     }
    #     print("Order Lines>>", order_lines)
    #     # Order Lines>> {'warehouse_name': 'WH/Stock'}
    #     data = []
    #     # for line in order.move_ids_without_package:
    #     for line in order.move_ids:
    #         data.append({
    #             'line_id': line.id,
    #             'product_name': line.product_id.name,
    #             'quantity': line.quantity,
    #         })
    #     print("Data>>", data)
    #     order_lines['data_lines'] = data
    #     return order_lines

    def fetch_loggedin_source_location(self, user_id):
        user_company_partner = self.env['res.users'].browse(user_id).company_id.partner_id
        user_company_partner.geo_localize()

        return [user_company_partner.partner_latitude, user_company_partner.partner_longitude]

    def calculateDistance(self, sourceLoc, destLoc):
        # To calculate distance between two coordinates
        lat1, lon1 = map(radians, sourceLoc)
        lat2, lon2 = map(radians, destLoc)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))
        R = 6371
        return R * c


class DeliveryAssignLines(models.Model):
    _name = 'assign.delivery.line'
    _description = 'Assigned Delivery Lines'

    assign_delivery_record_id = fields.Many2one('assign.delivery', 'Assigned Delivery Order', ondelete='cascade')
    sequence = fields.Integer('Sequence')
    customer_id = fields.Many2one('res.partner', 'Customer')
    driver_id = fields.Many2one('res.users', 'Driver')
    order_id = fields.Many2one('stock.picking', 'Order Name')
    delivery_date = fields.Date('Delivery Date')
    state = fields.Selection(selection=[
        ('draft', 'Shipment Planned'),
        ('out_for_delivery', 'Out For Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], default='draft', string='Status')
    sequence_number = fields.Char('Priority')

    street = fields.Char(related="customer_id.street")
    street2 = fields.Char(related="customer_id.street2")
    zip = fields.Char(related="customer_id.zip")
    city = fields.Char(related="customer_id.city")
    state_id = fields.Many2one(related="customer_id.state_id")
    country_id = fields.Many2one(related="customer_id.country_id")

    def action_set_out_for_delivery(self):
        self.state = 'out_for_delivery'

    def action_set_delivered(self):
        self.state = 'delivered'

    def action_set_failed(self):
        self.state = 'failed'

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals and vals['state'] in ['delivered','failed'] :
            for record in self:
                picking = record.order_id
                if picking and picking.state not in ['done', 'cancel']:
                    try:
                        picking.sudo().with_context({'from_picking':True}).button_validate()
                    except Exception as e:
                        raise UserError(f"Cannot validate picking {picking.name}: {str(e)}")

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
