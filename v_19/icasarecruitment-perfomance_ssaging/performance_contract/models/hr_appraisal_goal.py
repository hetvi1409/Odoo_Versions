# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrAppraisalGoal(models.Model):
    _inherit = "hr.appraisal.goal"

    weightage = fields.Float(string="Weightage")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    is_assigned = fields.Boolean(string="Is Assigned", default=False, readonly=True)

    status = fields.Selection([('good','Good'),('average','Average'),('below_average','Below Average'),('poor','Poor')],
                              string="Evaluation Status ",
                              tracking=True,
                              compute='_compute_status',
                              store=True,
                              )
    result = fields.Float(string="Result", groups="performance_contract.group_performance_evaluator")
    color = fields.Char(string="Color")

    # def default_get(self, fields):
    #     res = super(HrAppraisalGoal, self).default_get(fields)
    #     if context := self._context:
    #         if employee_id := context.get('default_employee_id'):
    #             res['employee_id'] = employee_id
    #             res['employee_ids'] = [(6, 0, [employee_id])]
    #             res['is_assigned'] = True
    #     return res


    @api.onchange('employee_id')
    def _onchange_employee_ids(self):
        if self.employee_id:
            if self.employee_id not in self.employee_ids:
                self.employee_ids = [(6, 0, [self.employee_id.id])]
        else:
            self.employee_ids = [(5, 0, 0)]  # remove all employees if employee_id is cleared

    @api.depends('result')
    def _compute_status(self):
        for record in self:
            if 80 <= record.result <= 100:
                record.status = 'good'
            elif 50 <= record.result <= 79:
                record.status = 'average'
            elif 25 <= record.result <= 49:
                record.status = 'below_average'
            else:
                record.status = 'poor'