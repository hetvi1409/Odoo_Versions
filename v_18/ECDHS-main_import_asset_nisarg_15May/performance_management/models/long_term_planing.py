# -*- coding: utf-8 -*-
from odoo import api, fields, models


class LongTermPlaning(models.Model):
    """ This model represents long.term.planing."""
    _name = 'long.term.planing'
    _description = 'Long Term Planing'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    portfolio_id = fields.Many2one('performance.portfolio', string='Portfolio')
    start_date = fields.Date(string="Dates")
    end_date = fields.Date(string="Dates")
    value = fields.Integer(string='Value')
    user_id = fields.Many2one('res.users', string="Responsible")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    programme_id = fields.Many2one('performance.programme', string='Programme')
    sub_programme_id = fields.Many2one('sub.programme', string='Sub-Programme')
    outcome_id = fields.Many2one('performance.outcome', string="Outcome")
    output_id = fields.Many2one('performance.output', string="Output")
    indicator_id = fields.Many2one('output.indicator', string="Output Indicator")
    medium_planing_ids = fields.One2many('medium.term.planing', 'long_term_id',
                                         string="Medium Term Planning")
    short_planing_ids = fields.One2many('short.term.planing', 'long_term_id',
                                        string="Short Term Planning")

    @api.onchange('indicator_id', 'output_id', 'outcome_id', 'sub_programme_id', 'programme_id')
    def _onchange_sub_programme_id(self):
        """Triggered when the sub_programme_id changes to update related values."""
        if self.indicator_id:
            self.output_id = self.indicator_id.output_id.id
        if self.output_id:
            self.outcome_id = self.output_id.outcome_id.id
        if self.outcome_id:
            self.sub_programme_id = self.outcome_id.sub_programme_id.id
        if self.sub_programme_id:
            self.programme_id = self.sub_programme_id.programme_id.id
        if self.programme_id:
            self.portfolio_id = self.programme_id.portfolio_id.id

