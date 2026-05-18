# -*- coding: utf-8 -*-
try:
    from odoo import api, fields, models
except ImportError:
    raise ImportError(
        "This module requires Odoo to be installed. Please install Odoo or "
        "add the module directory to the Odoo addons path."
    )

import re

class IndicatorTarget(models.Model):
    """ This model represents performance.outcome."""
    _name = 'indicator.target'
    _description = 'Indicator Annual Target'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Target Name', required=True, tracking=True, compute="_compute_name", store=True)
    target_name_id = fields.Many2one('target.targets', string='Target Period')
    user_id = fields.Many2one('res.users', string='Responsible')
    indicator_id = fields.Many2one('output.indicator', string="Indicator")
    start_date = fields.Date(string="Start End Dates")
    end_date = fields.Date(string="Start End Dates")
    target_numeric = fields.Integer(string="Target Numeric")
    achieved_target_numeric = fields.Integer(string="Achieved Target Numeric", compute="_compute_variance_numeric")
    variance_numeric = fields.Integer(string="Variance Numeric", compute="_compute_variance_numeric")
    total_achieved_target_numeric = fields.Integer(string="Achieved", compute="_compute_total_achieved_target_numeric")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    target = fields.Integer(string="Target")
    line_ids = fields.One2many('reporting.collection', 'target_id')
    quarter_ids = fields.One2many('indicator.target.quarter', 'annual_target_id', string='Quarterly Targets')

    @api.depends('target_name_id')
    def _compute_name(self):
        for record in self:
            if record.target_name_id:
                record.name = f"{record.target_name_id.name}"
            else:
                # fallback keep existing name if present
                record.name = record.name or ''

    @api.depends('line_ids.achieved_target_numeric', 'line_ids')
    def _compute_variance_numeric(self):
        """Compute the value of the field variance_numeric and achieved numeric."""
        for target in self:
            total_of_achieved_target_numeric_target_lines = sum(target.line_ids.mapped('achieved_target_numeric') or [0.0])
            target.achieved_target_numeric = total_of_achieved_target_numeric_target_lines
            variance = (target.target_numeric or 0.0) - total_of_achieved_target_numeric_target_lines
            target.variance_numeric = variance

    @api.depends('line_ids.achieved_target_numeric')
    def _compute_total_achieved_target_numeric(self):
        """Compute the total achieved target numeric."""
        for target in self:
            total = sum(target.line_ids.mapped('achieved_target_numeric') or [0.0])
            target.total_achieved_target_numeric = total

    def _is_annual_label(self, label):
        # Heuristic for annual year labels like 2024/25 or 2020/21
        if not label:
            return False
        return bool(re.match(r'^\d{4}\/\d{2}$', label.strip()))

    def _split_quarter_values(self, total):
        """Split an annual numeric target into four integer quarters."""
        if total is None:
            return [0, 0, 0, 0]
        total_int = int(total)
        base = total_int // 4
        remainder = total_int % 4
        return [base + (1 if idx < remainder else 0) for idx in range(4)]

    @api.model_create_multi
    def create(self, vals_list):
        # Ensure name is populated before insert to satisfy NOT NULL constraint.
        targets = self.env['target.targets']
        for vals in vals_list:
            if not vals.get('name') and vals.get('target_name_id'):
                target_name = targets.browse(vals['target_name_id']).name
                if target_name:
                    vals['name'] = target_name
        recs = super().create(vals_list)
        for rec in recs:
            lbl = rec.target_name_id.name if rec.target_name_id else rec.name
            if (self._is_annual_label(lbl)
                    and not rec.quarter_ids
                    and not self.env.context.get('install_mode')
                    and not self.env.context.get('import_file')):
                # Auto create Q1–Q4 with sequences
                quarter_values = self._split_quarter_values(rec.target_numeric)
                quarters = [('Q1', 1), ('Q2', 2), ('Q3', 3), ('Q4', 4)]
                for idx, (q, seq) in enumerate(quarters):
                    self.env['indicator.target.quarter'].create({
                        'annual_target_id': rec.id,
                        'quarter': q,
                        'sequence': seq * 10,
                        'value_numeric': quarter_values[idx],
                    })
        return recs

    def action_generate_quarters(self):
        """Manual action to generate missing quarter records for an annual target"""
        for rec in self:
            lbl = rec.target_name_id.name if rec.target_name_id else rec.name
            if self._is_annual_label(lbl):
                have = set(rec.quarter_ids.mapped('quarter'))
                quarter_values = self._split_quarter_values(rec.target_numeric)
                for q in ['Q1', 'Q2', 'Q3', 'Q4']:
                    if q not in have:
                        self.env['indicator.target.quarter'].create({
                            'annual_target_id': rec.id,
                            'quarter': q,
                            'value_numeric': quarter_values[['Q1', 'Q2', 'Q3', 'Q4'].index(q)],
                        })
    # #0. ORIGINAL CODE
    # @api.depends('achieved_target_numeric')
    # @api.onchange('achieved_target_numeric')
    # def _compute_variance_numeric(self):
    #     """Compute the value of the field variance_numeric."""
    #     for target in self:
    #         total = sum(target.line_ids.mapped('achieved_target_numeric'))
    #         target.achieved_target_numeric = total
    #         variance = target.target_numeric - total
    #         target.variance_numeric = variance

    # # 1. Fetch all targets (or filter them appropriately)
    # targets = env['x_targets'].search([])  # Add domain if needed
    # # Recompute sums for these targets
    # for target in targets:
    #     total = sum(target.x_studio_one2many_field_j9_1iqephnqu.mapped('x_studio_numeric_achieved_value'))
    #     variance = target.x_studio_numeric_target - total
    #     target.write({'x_studio_numeric_achieved_target': total, 'x_studio_numeric_variance': variance})

    # #2. Fetch all targets (or filter them appropriately)
    # targets = env['x_targets'].search([])  # Add domain if needed
    # # # Recompute sums for these targets
    # @api.onchange('target_name_id')
    # def _onchange_target_name_id(self):
    #     for target in self:
    #         total = sum(target.x_studio_one2many_field_j9_1iqephnqu.mapped('x_studio_numeric_achieved_value'))
    #         variance = target.x_studio_numeric_target - total
    #         target.write({'x_studio_numeric_achieved_target': total, 'x_studio_numeric_variance': variance})

class TargetTargets(models.Model):
    """ Target period model (simple container)."""
    _name = 'target.targets'
    _description = 'Target Targets'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Submission Name")


class IndicatorTargetReporting(models.Model):
    """ Reporting helper model for Indicator Annual Targets """
    _name = 'target.reporting'
    _description = 'Indicator Annual Target Reporting'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    target_id = fields.Many2one('indicator.target', string="Target")
    user_id = fields.Many2one('res.users', string='Responsible')
    name = fields.Char(string="Submission Name")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    achieved_target_numeric = fields.Integer(string="(Achieved) Target Numeric")