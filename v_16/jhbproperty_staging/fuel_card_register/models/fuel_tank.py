from email.policy import default

from odoo import models, fields


class FuelTank(models.Model):
    _name = 'fuel.tank'
    _description = 'Fuel Tank'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Name',required=True)
    location = fields.Char(string='Location')
    last_clean_date = fields.Date(string='Last Clean Date')
    type_of_fuel = fields.Many2one('fuel.type',string='Type of Fuel')
    vehicle_id = fields.Many2one('fleet.vehicle',string='Vehicle')
    capacity = fields.Float(string='Capacity')
    liters = fields.Float(string='Liters')
    average_price = fields.Float(string='Average Price')
    last_filling_date = fields.Date(string='Last Filling Date')
    last_filling_amount = fields.Float(string='Last Filling Amount')
    last_filling_price = fields.Float(string='Last Filling Price')
    total_filling_fuel = fields.Float(string='Total Filling Fuel')
    last_added_fuel_date = fields.Date(string='Last Added Fuel Date')
    fuel_filling_history = fields.One2many('fuel.filling.history','fuel_tank_id',string='Fuel Filling History')

    def action_add_fuel(self):
        return {
            'name': 'Add Liters',
            'type': 'ir.actions.act_window',
            'res_model': 'fuel.filling.history',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_fuel_tank_id': self.id,
            },
        }

    def action_print_fleet_tank(self):
        return self.env.ref('fuel_card_register.action_report_fuel_tank').report_action(self)

class FuelFillingHistory(models.Model):
    _name = 'fuel.filling.history'
    _description = 'Fuel Filling History'

    fuel_tank_id = fields.Many2one('fuel.tank',string='Fuel Tank')
    fuel_filling_date = fields.Date(string='Date',default=fields.Date.today)
    price = fields.Float(string='Price')
    liters = fields.Float(string='Liters')

