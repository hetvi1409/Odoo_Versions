from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    standard_hours = fields.Float(string="Standard Hours")
    standard_charge_out_rate = fields.Float(string="Standard Charge Out Rate")
    charge_out_rate_1 = fields.Float(string="Charge-Out Rate 1")
    charge_out_rate_2 = fields.Float(string="Charge-Out Rate 2")
