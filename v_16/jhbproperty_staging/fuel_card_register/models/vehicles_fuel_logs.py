from odoo import models, fields


class VehiclesFuelLogs(models.Model):
    _name = 'vehicles.fuel.logs'
    _description = 'Vehicles Fuel Logs'

    vehicle_id = fields.Many2one('fleet.vehicle',string='Vehicle')
    employee_id = fields.Many2one('hr.employee',string='Employee')
    liter = fields.Float(string='Liter')
    fuel_tank_id = fields.Many2one('fuel.tank',string='Fuel Tank')
    price_per_liter = fields.Float(string='Price Per Liter')
    total_price = fields.Float(string='Total Price')
    new_odometer_reading = fields.Float(string='New Odometer Reading')
    previous_odometer_reading = fields.Float(string='Previous Odometer Reading')
    additional_date = fields.Date(string='Date')
    invoice_ref = fields.Char(string='Invoice Reference')
    vendor_id = fields.Many2one('res.partner',string='Vendor')