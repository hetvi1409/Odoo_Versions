# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AttendanceRecapReportWizard(models.TransientModel):
    _name = 'attendance.recap.report.wizard'
    _description = 'Employee Attendance Report Wizard'

    employee_ids = fields.Many2many('hr.employee', string='Employees', required=True)
    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    select_all = fields.Boolean('Select All')

    _check_date = models.Constraint(
        "CHECK(date_end >= date_start)",
        "The Start Date Should be Less Than End Date and End Date Should be Greater Than Start Date."
    )

    @api.onchange('select_all')
    def _onchange_employee(self):
        if self.select_all:
            for rec in self.env['hr.employee'].search([]):
                for line in rec.attendance_ids:
                    self.employee_ids = [(4,line.employee_id.id)]
        else:
            self.employee_ids = False

    def get_report(self):
        data = {}
        data['form'] = self.read(['date_start', 'date_end', 'select_all', 'employee_ids'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_start', 'date_end', 'select_all', 'employee_ids'])[0])
        return self.env.ref('auto_attendance_flow.attendance_recap_report').report_action(self, data=data, config=False)