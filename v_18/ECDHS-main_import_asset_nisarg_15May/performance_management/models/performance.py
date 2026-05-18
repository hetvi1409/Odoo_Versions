# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PerformancePortfolio(models.Model):
    """ This model represents performance.portfolio."""
    _name = 'performance.portfolio'
    _description = 'Portfolio'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    description = fields.Html(string="Details")
    start_date = fields.Date(string="Dates")
    end_date = fields.Date(string="Dates")
    value = fields.Integer(string='Value')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    user_id = fields.Many2one('res.users', string='Responsible')
    line_ids = fields.One2many('performance.line', 'portfolio_id', string="Description")
    programme_ids = fields.One2many('performance.programme', 'portfolio_id', string="Programme")
    sub_programme_ids = fields.One2many(
        'sub.programme',
        'portfolio_id',
        string='Sub-Programme',
        domain=[('parent_id', '=', False)]
    )
    sub_programme_child_ids = fields.One2many(
        'sub.programme',
        'programme_id',
        string='Child Sub-Programme',
        domain=[('parent_id', '!=', False)]
    )
    outcome_ids = fields.One2many('performance.outcome', 'portfolio_id', string="Outcome")
    output_ids = fields.One2many('performance.output', 'portfolio_id', string="Outputs")
    indicator_ids = fields.One2many('output.indicator', 'portfolio_id', string="Output Indicator")

    @api.model_create_multi
    def create(self, vals):
        """Override the default create method to customize record creation logic."""
        return super().create(vals)


class PerformanceLine(models.Model):
    """ This model represents performance.portfolio."""
    _name = 'performance.line'
    _description = 'Performance Line'

    name = fields.Char(string='Description', required=True)
    portfolio_id = fields.Many2one('performance.portfolio', string='Portfolio', ondelete='restrict')

