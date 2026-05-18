from odoo import models, fields


class FuelCard(models.Model):
    _name = 'fuel.card'
    _description = 'Fuel Card'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Card number/identifier')
    active = fields.Boolean(string='Is the card active?')
    assigned_vehicle_id = fields.Many2one('fleet.vehicle',string='Default vehicle')
    status = fields.Selection([('available','Available'),('issued','Issued'),('inactive','Inactive')])
