from odoo import fields, models

class ResRace(models.Model):
    _name = "res.race"
    _description = "Race"
    _rec_name = 'race'

    race = fields.Char(string='Race')