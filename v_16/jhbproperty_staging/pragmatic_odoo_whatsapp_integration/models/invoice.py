from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    show_discount_details = fields.Boolean(default=False)