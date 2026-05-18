from odoo import api, fields, models
from datetime import date, datetime

class ProjectTask(models.Model):
    _inherit = 'project.task'

    code = fields.Char(string="Sequence", copy=False, readonly=True)
    is_ppe = fields.Boolean(string="Project Portfolio")
    baseline_start_date = fields.Date(string="Baseline Start Date")
    baseline_end_date = fields.Date(string="Baseline End Date")
    planned_progress = fields.Float(string="Planned Progress %", compute="_compute_planned_progress", store=True)
    allocation = fields.Float(string="Actual Progress %")
    variance = fields.Float(string="Variance %", compute="_compute_variance", store=True)
    generate_planing = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                        string="Generate Planing")
    critical_path = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                        string="Critical Path")
    type = fields.Selection([('project_task', 'Project Task'), ('task', 'Task'),
                             ('milestone', 'Milestone'), ('summery_task', 'Summery Task')])
    sort_order = fields.Integer(string="Sort Order")
    actual_end_date = fields.Date(string="Actual End Date")
    variance_planned_start_date = fields.Integer(string="Variance Planned Start Date", compute="_compute_start_end_date")
    variance_planned_end_date = fields.Integer(string="Variance Planned End Date", compute="_compute_start_end_date")
    days_overdue = fields.Integer(string="Days Overdue", compute="_compute_days_overdue")

    @api.depends('date_deadline')
    def _compute_days_overdue(self):
        """Days Overdue"""
        for rec in self:
            today = fields.Datetime.now()
            date_deadline = 0
            if rec.date_deadline:
                date_deadline = (today - rec.date_deadline).days if today > rec.date_deadline else 0
            rec.days_overdue = date_deadline

    @api.depends('planned_progress', 'allocation')
    def _compute_variance(self):
        """Compute Variance"""
        for rec in self:
            rec.variance = abs(
                (rec.planned_progress or 0) - (rec.allocation or 0))

    @api.depends('date_deadline', 'planned_date_begin')
    def _compute_planned_progress(self):
        """Compute Planned Progress"""
        for rec in self:
            total_days, days_today, progress = 0, 0, 0
            if rec.planned_date_begin:
                days_today = (fields.Datetime.now() - rec.planned_date_begin).days
                if rec.date_deadline:
                    total_days = (rec.date_deadline - rec.planned_date_begin).days
            if total_days > 0:
                progress = (days_today / total_days) * 100

            progress = max(0, min(progress, 100))
            rec.planned_progress = progress

    @api.depends('date_deadline', 'planned_date_begin', 'baseline_start_date', 'baseline_end_date')
    def _compute_start_end_date(self):
        for rec in self:
            # Normalize planned start (datetime) to date if needed
            planned_start = rec.planned_date_begin.date() if isinstance(rec.planned_date_begin, datetime) else rec.planned_date_begin
            baseline_start = rec.baseline_start_date

            if planned_start and baseline_start:
                rec.variance_planned_start_date = (baseline_start - planned_start).days
            else:
                rec.variance_planned_start_date = 0

            # Normalize deadline (date or datetime) to date if needed
            planned_end = rec.date_deadline.date() if isinstance(rec.date_deadline, datetime) else rec.date_deadline
            baseline_end = rec.baseline_end_date

            if planned_end and baseline_end:
                rec.variance_planned_end_date = (baseline_end - planned_end).days
            else:
                rec.variance_planned_end_date = 0

    @api.model
    def create(self, vals_list):
        """Method to super create function"""
        seq = self.env['ir.sequence'].next_by_code(
            'project.task')
        vals_list['code'] = seq
        res = super().create(vals_list)
        return res