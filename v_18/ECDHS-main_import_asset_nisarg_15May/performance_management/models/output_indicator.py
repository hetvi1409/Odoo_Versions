# -*- coding: utf-8 -*-
from odoo import models, fields, api

class OutcomeIndicator(models.Model):
    """ This model represents performance.outcome."""
    _name = 'output.indicator'
    _description = 'Output Indicator'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)

    user_id = fields.Many2one('res.users', string='Responsible')
    portfolio_id = fields.Many2one('performance.portfolio', string="Portfolio")
    programme_id = fields.Many2one('performance.programme', string='Programme')
    sub_programme_id = fields.Many2one('sub.programme', string='Sub-Programme')
    outcome_id = fields.Many2one('performance.outcome', string="Outcome")
    output_id = fields.Many2one('performance.output', string="Output")
    long_planing_ids = fields.One2many('long.term.planing', 'indicator_id', string="Long Term Planning")
    medium_planing_ids = fields.One2many('medium.term.planing', 'indicator_id', string="Medium Term Planning")
    short_planing_ids = fields.One2many('short.term.planing', 'indicator_id', string="Short Term Planning")
    start_date = fields.Date(string="Start End Dates")
    end_date = fields.Date(string="Start End Dates")
    dimension_ids = fields.One2many('indicator.dimension', 'indicator_id', string='Indicator Dimension', ondelete='restrict')

    period = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('monthly', 'Monthly'),
        ('bi_monthly', 'Bi-Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('3_per_annum', '3 Per Annum'),
        ('annual', 'Annual'),
        ('biennial', 'Biennial'),
        ('triennial', 'Triennial'),
        ('4_years', '4-Years'),
        ('5_years', '5-Years'),
        ('10_years', '10-Years'),
    ], string="Period (Reporting Cycle)")
    source_of_data = fields.Char(string="Source Of Data")
    method_of_calculation = fields.Char(string="Method Of Calculation")
    spatial_transformation = fields.Char(string="Spatial Transformation (where applicable)")
    calculation_type = fields.Char(string="Calculation Type")
    desired_performance = fields.Char(string="Desired Performance")
    means_of_verification = fields.Char(string="Means of verification")
    assumptions = fields.Char(string="Assumptions")
    department_id = fields.Many2one('hr.department', string="Department")
    section = fields.Char(string="Section")
    target_ids = fields.One2many('indicator.target', 'indicator_id', string='Indicator Annual Target', ondelete='restrict')
    target_quarter_ids = fields.One2many('indicator.target.quarter', 'indicator_id', string='Indicator Target (Quarterly)', ondelete='restrict')
    reporting_collection_ids = fields.One2many('reporting.collection', 'indicator_id', string='Indicator Reporting Collection', ondelete='restrict')

    def _default_res_model(self):
        return self.env.ref('performance_management.model_output_indicator').sudo().id
    res_model_id = fields.Many2one(
        'ir.model', 'Document Model', default = _default_res_model,
        index=True, ondelete='cascade', required=True)

    @api.onchange('output_id', 'outcome_id', 'sub_programme_id', 'programme_id')
    def _onchange_sub_programme_id(self):
        """Triggered when the sub_programme_id changes to update related values."""
        if self.output_id:
            self.outcome_id = self.output_id.outcome_id.id
        if self.outcome_id:
            self.sub_programme_id = self.outcome_id.sub_programme_id.id
        if self.sub_programme_id:
            self.programme_id = self.sub_programme_id.programme_id.id
        if self.programme_id:
            self.portfolio_id = self.programme_id.portfolio_id.id

    def action_compute_quarterly_targets(self):
        """Compute and update/create quarterly target lines for this indicator."""
        quarter_obj = self.env['indicator.target.quarter']

        for indicator in self:
            for annual in indicator.target_ids:
                # Get existing quarterly records for this annual target
                existing_quarters = quarter_obj.search([('annual_target_id', '=', annual.id)])

                # Prepare a list of quarter data (Q1 to Q4)
                quarters_data = []
                for seq in range(1, 5):
                    quarters_data.append({
                        'name': f"{(annual.name or indicator.name or 'Target')} - Q{seq}",
                        'annual_target_id': annual.id,
                        'indicator_id': indicator.id,
                        'quarter': f"Q{seq}",
                        'sequence': seq,
                        'value_numeric': annual.target_numeric,
                    })

                # If there are existing records, update them; otherwise create new ones
                if existing_quarters:
                    for idx, q_data in enumerate(quarters_data):
                        if idx < len(existing_quarters):
                            existing_quarters[idx].write(q_data)
                        else:
                            quarter_obj.create(q_data)
                    # If more existing records than needed, delete extras
                    if len(existing_quarters) > len(quarters_data):
                        extra_records = existing_quarters[len(quarters_data):]
                        extra_records.unlink()
                else:
                    # Create all four quarters if none exist
                    quarter_obj.create(quarters_data)

        return True