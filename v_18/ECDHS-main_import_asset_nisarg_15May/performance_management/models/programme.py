# -*- coding: utf-8 -*-
from email.policy import default

from odoo import api, fields, models


class PerformanceProgramme(models.Model):
    """ This model represents programme."""
    _name = 'performance.programme'
    _description = 'Programme'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    user_id = fields.Many2one('res.users', string='Responsible')
    start_date = fields.Date(string="Dates")
    end_date = fields.Date(string="Dates")
    value = fields.Integer(string='Value')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    portfolio_id = fields.Many2one('performance.portfolio', string='Portfolio', required=True)
    sub_programme_ids = fields.One2many(
        'sub.programme',
        'programme_id',
        string='Sub-Programme',
        domain=[('parent_id', '=', False)]
    )
    sub_programme_child_ids = fields.One2many(
        'sub.programme',
        'programme_id',
        string='Child Sub-Programme',
        domain=[('parent_id', '!=', False)]
    )
    outcome_ids = fields.One2many('performance.outcome', 'programme_id', string="Outcome")
    description = fields.Html(string="Details")
    output_ids = fields.One2many('performance.output', 'programme_id', string="Outcome")
    indicator_ids = fields.One2many('output.indicator', 'programme_id', string="Output Indicator")
    def _default_res_model(self):
        return self.env.ref('performance_management.model_performance_programme').sudo().id
    res_model_id = fields.Many2one(
        'ir.model', 'Document Model', default = _default_res_model,
        index=True, ondelete='cascade', required=True)

class PerformanceSubProgramme(models.Model):
    """ This model represents programme."""
    _name = 'sub.programme'
    _description = 'Sub-Programme'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    user_id = fields.Many2one('res.users', string='Responsible')
    start_date = fields.Date(string="Dates")
    end_date = fields.Date(string="Dates")
    value = fields.Integer(string='Value')
    currency_id = fields.Many2one('res.currency', default=lambda
        self: self.env.company.currency_id)
    portfolio_id = fields.Many2one('performance.portfolio', string="Portfolio")
    programme_id = fields.Many2one('performance.programme', string='Programme')
    parent_id = fields.Many2one('sub.programme', string="Parent Sub-Programme")
    sub_programme_child_ids = fields.One2many(
        'sub.programme',
        'programme_id',
        string='Child Sub-Programme',
        domain=[('parent_id', '!=', False)]
    )
    description = fields.Html(string="Details")
    output_ids = fields.One2many('performance.output', 'sub_programme_id',
                                 string="Outcome")
    indicator_ids = fields.One2many('output.indicator', 'sub_programme_id',
                                    string="Output Indicator")
    outcome_ids = fields.One2many('performance.outcome', 'sub_programme_id',
                                  string="Outcome")
    def _default_res_model(self):
        return self.env.ref('performance_management.model_sub_programme').sudo().id
    res_model_id = fields.Many2one(
        'ir.model', 'Document Model', default = _default_res_model,
        index=True, ondelete='cascade', required=True)

    @api.onchange('programme_id')
    def _onchange_programme_id(self):
        """Triggered when the programme_id changes to update related values."""
        if not self.portfolio_id:
            self.portfolio_id = self.programme_id.portfolio_id.id


