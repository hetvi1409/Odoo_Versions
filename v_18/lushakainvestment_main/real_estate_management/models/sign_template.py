from odoo import fields, models


class SignTemplate(models.Model):
    _inherit = 'sign.template'

    contract_id = fields.Many2one('rental.contract')