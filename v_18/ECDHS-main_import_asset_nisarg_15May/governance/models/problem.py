# -*- coding: utf-8 -*-
from odoo import api, fields, models

class DefectAnalysis(models.Model):
    _name = "problem.analysis"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "problem.analysis"

    ref = fields.Char(string='Report Number', default='New', tracking=True)
    name = fields.Char(string='Title')
    event_date = fields.Date(string='Event Date')
    report_date = fields.Date(string='Date Reported')
    description = fields.Html(string='Description')
    employee = fields.Many2one('hr.employee', string='Employee Reporting Event', tracking=True)
    event_type = fields.Selection([('complaint', 'Complaint'), ('defect', 'Defect'), ('safety', 'Safety'),
                                    ('efficiency', 'Efficiency'), ('adr', 'ADR')], string="Event Type",
                                    tracking=True, required=True)
    consequence = fields.Selection([('insignificant', 'Insignificant'), ('minor', 'Minor'), ('moderate', 'Moderate'),
                                   ('major', 'Major'), ('fatal', 'Fatal')], string="Consequence",
                                  tracking=True, required=True)
    suggestions = fields.Html(string='Suggestions', tracking=True)
    action_log = fields.Many2many('action.log', string="Action Log")
    actions = fields.Text(string="Actions")

    issue = fields.Boolean(string='Safety issue?')
    affect = fields.Boolean(string='Multiple products?')
    risk = fields.Boolean(string='Public risk?')
    root_cause = fields.Many2many('root.cause', string="Root Cause")
    lot = fields.Many2many('stock.lot', string="Lot Serial Num")

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('problem.sequence')
        return super(DefectAnalysis, self).create(vals)
