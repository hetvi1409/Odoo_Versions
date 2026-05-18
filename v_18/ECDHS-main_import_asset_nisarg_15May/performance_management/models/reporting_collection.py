# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from markupsafe import Markup
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta
from odoo.tools import pdf
import base64

class ReportingCollection(models.Model):
    """ Reporting collection (submission) """
    _name = 'reporting.collection'
    _description = 'Reporting Collection'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Submission Name', required=False, tracking=False, compute="_onchange_compute_name", store=True)
    user_id = fields.Many2one('res.users', string='Responsible')
    start_date = fields.Date(string="Start End Dates")
    end_date = fields.Date(string="Start End Dates")
    target_id = fields.Many2one('indicator.target', string="Target")
    dimension_id = fields.Many2one('indicator.dimension', string="Dimension")
    indicator_id = fields.Many2one('output.indicator', string="Indicator")
    achieved_target_numeric = fields.Integer(string="(Achieved) Value Numeric")
    achieved_value = fields.Integer(string="(Achieved) Numeric")
    target_numeric = fields.Integer(string="Target Numeric", related='target_id.target_numeric', store=True)
    variance_numeric = fields.Integer(string="Variance Numeric", compute='_compute_variance_numeric', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    residual_performance = fields.Integer(string="Residual Performance")
    blockages = fields.Char(string="Blockages")
    remedial_measures = fields.Char(string="Remedial Measures")
    achievement = fields.Selection([
        ('achieved', 'Achieved'),
        ('partially_achieved', 'Partially Achieved'),
        ('not_achieved', 'Not Achieved'),
        ('not_applicable', 'Not Applicable'),
    ], string="Achievement")
    evidence = fields.Binary(string="Evidence")
    timeframe = fields.Date(string="Time Frames")
    comments = fields.Text(string="Comments")
    line_ids = fields.One2many('reporting.collection.line', 'reporting_id')
    quarter_target_id = fields.Many2one('indicator.target.quarter', string='Quarter Target', ondelete='set null', domain="[('annual_target_id','=', target_id)]")

    # Auto-update name to match the selected quarter
    @api.onchange('quarter_target_id','name')
    def _onchange_compute_name(self):
        for record in self:
            if record.quarter_target_id:
                record.name = f"{record.quarter_target_id.name}"
            else:
                # fallback keep existing name if present
                record.name = record.name or ''

    # When a quarter target is selected, make sure indicator and annual target are set
    @api.onchange('quarter_target_id')
    def _onchange_quarter_target_id(self):
        if self.quarter_target_id:
            self.indicator_id = self.quarter_target_id.indicator_id.id
            self.target_id = self.quarter_target_id.annual_target_id.id

    @api.onchange('target_id')
    def _onchange_target_id(self):
        # When reporting target changes, ensure selected quarter belongs to the chosen annual target
        if self.target_id:
            # enforce domain in UI and clear quarter selection if it doesn't belong
            if self.quarter_target_id and self.quarter_target_id.annual_target_id.id != self.target_id.id:
                self.quarter_target_id = False
            return {'domain': {'quarter_target_id': [('annual_target_id', '=', self.target_id.id)]}}
        else:
            # if no target selected, clear quarter and show all quarters
            if self.quarter_target_id:
                self.quarter_target_id = False
            return {'domain': {'quarter_target_id': []}}

    # When a quarter target is selected, make sure indicator and annual target are set
    @api.onchange('quarter_target_id')
    def _onchange_quarter_target_id(self):
        if self.quarter_target_id:
            self.indicator_id = self.quarter_target_id.indicator_id.id
            self.target_id = self.quarter_target_id.annual_target_id.id

    @api.constrains('achieved_target_numeric', 'achieved_value')
    def _check_achieved_values(self):
        for record in self:
            if record.achieved_target_numeric is not None and record.achieved_target_numeric < 1.00:
                raise ValidationError(_('Please fill value greater than 0 on "(Achieved) Target Numeric". It must be greater than 0'))

    @api.depends('achieved_target_numeric')
    def _compute_variance_numeric(self):
        for record in self:
            record.variance_numeric = (record.target_numeric or 0.0) - (record.achieved_target_numeric or 0.0)

    # # Indicators: Targets Values Updated When Reporting is Updated
    # # Available variables: records = x_reporting_data_colle records being updated
    # # Get all parent targets linked to these child records
    # # 1. Fetch all targets (or filter them appropriately)
    # @api.onchange('achieved_target_numeric', 'target_numeric')
    # def _compute_variance_numeric(self):
    #     """Compute the value of the field variance_numeric."""
    #     for target in self:
    #         total = sum(target.line_ids.mapped('achieved_target_numeric'))
    #         variance = target.target_numeric - total
    #         target.write({'achieved_target_numeric': total, 'variance_numeric': variance})

    # @api.depends('achieved_target_numeric')
    # def _compute_variance_numeric(self):
    #     for record in self:
    #         record.variance_numeric = record.target_numeric - (record.achieved_target_numeric or 0.0)

    def action_preview_document(self):
        self.ensure_one()
        if not self.evidence:
            raise ValidationError("Please first upload evidence document")
        preview_url = f'/web/content/{self._name}/{self.id}/evidence/{self.name}/?download=false'
        if not preview_url:
            raise ValidationError("Preview not supported for this file type.")
        return {
            'type': 'ir.actions.act_url',
            'url': preview_url,
            'target': 'new',
        }

class ReportingCollectionLine(models.Model):
    """ Line items for a reporting collection """
    _name = 'reporting.collection.line'
    _description = 'Reporting Collection Line'

    name = fields.Char(string='Description', required=True)
    reporting_id = fields.Many2one('reporting.collection', string='Reporting')
    currency_id = fields.Many2one(related='reporting_id.currency_id')