from odoo import models, fields, _


class Judge(models.Model):
    _name = 'court.judge'
    _description = 'Judge'
    _order = "id desc"

    name = fields.Char("Judge Name")
    contact = fields.Char("Contact")
    court_id = fields.Many2one("court.court", "Court")

