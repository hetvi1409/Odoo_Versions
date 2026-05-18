# -*- coding: utf-8 -*-

from datetime import datetime, date, time
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class EmployeeReportAttendance(models.AbstractModel):
    _name = 'report.auto_attendance_flow.employee_attendance_report_view'
    _description = 'Employee Attendance Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        # Convert to datetime if it's a date or string
        if isinstance(date_start, str):
            date_start = datetime.strptime(date_start, DATE_FORMAT)
        if isinstance(date_end, str):
            date_end = datetime.strptime(date_end, DATE_FORMAT)

        # Convert to full-day datetime ranges
        date_start_obj = datetime.combine(date_start, time.min)
        date_end_obj = datetime.combine(date_end, time.max)
        docs = []
        attendance_info = {}
        record_id = data['form']['id'] if data and data.get('form', False) and data.get('form').get('id', False) else \
            docids[0]
        records = self.env['attendance.recap.report.wizard'].browse(record_id)
        docids = records.ids
        for employee in data['form']['employee_ids']:
            total_hours = []

        for attendance in self.env['hr.attendance'].sudo().search([]).filtered(
                    lambda l: l.employee_id.id == employee
                              and l.check_in and l.check_out
                              and date_start_obj <= l.check_in <= l.check_out <= date_end_obj
            ):

                delta = attendance.check_out - attendance.check_in
                result = 0
                (h, m, s) = str(delta).split(':')
                result = int(h) * 3600 + int(m) * 60 + int(s)
                total_hours.append(result)
                docs.append({
                    'employee': attendance.employee_id.name,
                    'check_in': attendance.check_in,
                    'check_out': attendance.check_out,
                    'delta': delta,
                    })
                total = sum(total_hours)
                hours, remainder = divmod(total, 3600)
                minutes, seconds = divmod(remainder, 60)
                total_time_hours = ''
                total_time_hours = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
                attendance_info[employee] = {
                    'emp_name': attendance.employee_id.name,
                    'department': attendance.department_id.name,
                    'docs': docs,
                    'time1': total_time_hours,
                    }
        if not attendance_info:
            raise UserError(_('No records Found!'))
        return {
            'attendance_info': attendance_info,
            'company_id': self.env.user.company_id,
            'doc_ids': docids,
            'docs': records,
            'o': records,
            'c_id': self
            }