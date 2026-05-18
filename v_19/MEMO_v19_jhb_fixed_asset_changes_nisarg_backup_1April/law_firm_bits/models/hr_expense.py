from odoo import models, fields, _


class Expense(models.Model):
    _inherit = 'hr.expense'

    is_law_expense = fields.Boolean(default=False)
    partner_id = fields.Many2one("res.partner")

    move_line_ids = fields.One2many("account.move.line", 'expense_id')
