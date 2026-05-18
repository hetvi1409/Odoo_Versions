# -*- coding: utf-8 -*-
from odoo import fields, models
class RiskAnalysis(models.Model):
    _name = "risk.analysis"

    task_id = fields.Many2one('project.task')
    flow_chart = fields.Html(string='Flow Chart')
    activity_description = fields.Html(string='Activity Description')
    risk_description = fields.Html(string='Risk Description')
    rating = fields.Char(string='Rating')
    control_description = fields.Html(string='Control Description')
    control_rating = fields.Char(string='Control Rating')
    residual_risk = fields.Char(string='Residual Risk')
    reporting_point = fields.Char(string='Reporting Point')
    audit_procedures = fields.Html(string='Audit Procedures')
    is_same_prior_year = fields.Boolean(string='Is Same as Prior Year (Y/N)')
