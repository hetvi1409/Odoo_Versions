# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import re

class IndicatorTargetQuarter(models.Model):
    """Quarterly splits for an annual indicator target"""
    _name = 'indicator.target.quarter'
    _description = 'Indicator Target Quarter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'annual_target_id, sequence'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    annual_target_id = fields.Many2one('indicator.target', string='Annual Target', required=True, ondelete='cascade')
    indicator_id = fields.Many2one('output.indicator', string='Indicator', related='annual_target_id.indicator_id', store=True)
    quarter = fields.Selection([('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')], required=True, index=True)
    sequence = fields.Integer(default=10)
    due_date = fields.Date(string='Due Date')
    # Values for quarterly target (allow either numeric or textual)
    value_numeric = fields.Integer(string='Quarter Target (Numeric)')
    value_text = fields.Text(string='Quarter Target (Text)')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    # Rolling/aggregate fields for reporting convenience
    achieved_numeric = fields.Integer(string='Achieved (Numeric)', compute='_compute_achieved', store=True)
    variance_numeric = fields.Integer(string='Variance (Numeric)', compute='_compute_achieved', store=True)

    _sql_constraints = [
        ('quarter_unique_per_annual', 'unique(annual_target_id, quarter)',
         'Each quarter (Q1–Q4) must be unique per annual target.')
    ]

    @api.depends('quarter', 'annual_target_id')
    def _compute_name(self):
        for rec in self:
            year_lbl = rec.annual_target_id.target_name_id.name or rec.annual_target_id.name or ''
            rec.name = f'{year_lbl}-{rec.quarter}'.strip()

    @api.depends('annual_target_id', 'annual_target_id.indicator_id')
    def _compute_achieved(self):
        Reporting = self.env['reporting.collection'].sudo()
        for rec in self:
            if not rec.id:
                rec.achieved_numeric = 0.0
                rec.variance_numeric = rec.value_numeric or 0.0
                continue
            lines = Reporting.search([('quarter_target_id', '=', rec.id)])
            total = sum(lines.mapped('achieved_target_numeric') or [0.0])
            rec.achieved_numeric = total
            rec.variance_numeric = (rec.value_numeric or 0.0) - (total or 0.0)