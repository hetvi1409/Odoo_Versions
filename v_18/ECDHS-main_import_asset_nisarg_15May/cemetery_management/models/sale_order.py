from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    burial_booking_id = fields.Many2one('cemetery.application', string='Burial Booking')
    type_of_death = fields.Selection([('natural', 'Natural'),
                                      ('unnatural', 'Unnatural')]
                                     , string="Type of Death")
    cause_death_id = fields.Many2one('cause.death', string="Cause Death")
