# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import fields, models, _,api



class TimeBudget(models.Model):

    _name = "time.budget"
    _description = "Calculate Time Buget"

    project_id = fields.Many2one(comodel_name="project.project",
                                          help="Calculate and estimate the total time budget")
    rank_id = fields.Many2one('hr.job', string="Rank",help="Enter the rank")
    auditor_id = fields.Many2one('hr.employee', string="Auditor",help="Enter the auditor")
    hours = fields.Float(string="Hours",help="Hours Spend")
    comments = fields.Char(string="Comments",help="Add Comments")
    planned_hours = fields.Float(string="PLANNING",help="Hours Spend for planning")
    field_hours = fields.Float(string="FIELDWORK",help="Hours Spend for field work")
    reporting_hours = fields.Float(string="REPORTING",help="Hours Spend for reporting")
    task_time_id = fields.Many2one('project.task')

    @api.onchange('planned_hours','field_hours','reporting_hours')
    def _onchange_planned_hours(self):
        for record in self:
            total_hours = record.planned_hours + record.field_hours + record.reporting_hours
            if total_hours > record.hours and total_hours !=0 and record.hours!=0:
                raise ValidationError(
                    f"Must be less than the  Hours ({record.hours})."
                )



