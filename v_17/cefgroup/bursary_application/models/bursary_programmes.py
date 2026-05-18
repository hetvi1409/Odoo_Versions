from odoo import fields, models


class BursaryBursary(models.Model):
    _name = "bursary.programme"
    _description = "Bursary Programme"

    name = fields.Char(string="Programme" , required=True)

    _sql_constraints = [
        ('unique_programme_name', 'UNIQUE(name)', 'The Programme name must be unique.')
    ]