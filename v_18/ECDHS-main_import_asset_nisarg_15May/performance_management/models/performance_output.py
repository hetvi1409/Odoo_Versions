# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PerformanceOutcome(models.Model):
    """ This model represents performance.outcome."""
    _name = 'performance.output'
    _description = 'Performance Output'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)

    user_id = fields.Many2one('res.users', string='Responsible')
    start_date = fields.Date(string="Dates")
    end_date = fields.Date(string="Dates")
    portfolio_id = fields.Many2one('performance.portfolio', string="Portfolio")
    programme_id = fields.Many2one('performance.programme', string='Programme')
    sub_programme_id = fields.Many2one('sub.programme', string='Sub-Programme')
    outcome_id = fields.Many2one('performance.outcome', string="Outcome")
    description = fields.Html(string="Output Description")
    indicator_ids = fields.One2many('output.indicator', 'output_id', string="Output Indicator")

    @api.onchange('outcome_id', 'sub_programme_id', 'programme_id')
    def _onchange_sub_programme_id(self):
        """Triggered when the sub_programme_id changes to update related values."""
        if self.outcome_id:
            self.sub_programme_id = self.outcome_id.sub_programme_id.id
        if self.sub_programme_id:
            self.programme_id = self.sub_programme_id.programme_id.id
        if self.programme_id:
            self.portfolio_id = self.programme_id.portfolio_id.id
