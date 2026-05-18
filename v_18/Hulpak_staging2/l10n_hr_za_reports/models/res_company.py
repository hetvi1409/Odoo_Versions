from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    paye_number = fields.Char(string="PAYE Number")
    uif_number = fields.Char(string="UIF Number")
    sdl_number = fields.Char(string="SDL Number")