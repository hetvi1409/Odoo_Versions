# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PerformanceOutcome(models.Model):
    """ This model represents performance.outcome."""
    _name = 'performance.outcome'
    _description = 'Performance Outcome'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)

    user_id = fields.Many2one('res.users', string='Responsible')
    portfolio_id = fields.Many2one('performance.portfolio', string="Portfolio")
    programme_id = fields.Many2one('performance.programme', string='Programme')
    sub_programme_id = fields.Many2one('sub.programme', string='Sub-Programme')
    outcome_description = fields.Html(string="Outcome Description")
    output_ids = fields.One2many('performance.output', 'outcome_id', string="Outputs")
    indicator_ids = fields.One2many('output.indicator', 'outcome_id', string="Output Indicator")

    @api.onchange('sub_programme_id', 'programme_id')
    def _onchange_sub_programme_id(self):
        """Triggered when the sub_programme_id changes to update related values."""
        if self.sub_programme_id:
            self.programme_id = self.sub_programme_id.programme_id.id
        if self.programme_id:
            self.portfolio_id = self.programme_id.portfolio_id.id
