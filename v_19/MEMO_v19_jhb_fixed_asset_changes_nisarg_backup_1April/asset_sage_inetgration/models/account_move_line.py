from odoo import fields, models


class AccountMoveLine(models.Model):
    """Account move line"""
    _inherit = 'account.move.line'

    sage_unique_identifier = fields.Char(string="Sage ID")
    audit_number = fields.Char(string="Audit Number")

