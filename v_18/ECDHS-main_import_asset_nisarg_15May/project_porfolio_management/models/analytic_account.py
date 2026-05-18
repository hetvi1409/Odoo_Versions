from odoo import fields, models


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"


    parent_id = fields.Many2one("account.analytic.account")