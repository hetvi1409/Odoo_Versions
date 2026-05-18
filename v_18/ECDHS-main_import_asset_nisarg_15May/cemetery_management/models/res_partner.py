from odoo import fields, models


class ResPartner(models.Model):
    """Adding fields to partner form"""
    _inherit = 'res.partner'

    undertaker = fields.Boolean(string="Undertaker", related="user_id.undertaker")
    surname = fields.Char(string="Surname")
    forenames = fields.Char(string="Forenames")
