from odoo import fields, models


class AccountAnalyticLine(models.Model):
    """Account Analytic Line"""
    _inherit = 'account.analytic.line'

    operational_plan_timesheet_id = fields.Many2one('operational.plan', string="Operational Plan")
    description = fields.Text(string='Motivation/Link to Description')

