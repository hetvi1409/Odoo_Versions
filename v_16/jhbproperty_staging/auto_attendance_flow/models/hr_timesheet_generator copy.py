# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import calendar


class HrTimesheetGenerator(models.Model):
    _name = 'hr.timesheet.generator'
    _description = 'Timesheet Generator'
    _rec_name = 'employee_id'

    # Employee Information Fields
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    name = fields.Char(string='Name/s', readonly=True)
    surname = fields.Char(string='Surname', readonly=True)
    initials = fields.Char(string='Initials', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    branch_directorate_id = fields.Many2one('hr.department', string='Branch/Directorate', readonly=True)
    sap_employee_number = fields.Char(string='SAP/Employee Number', readonly=True)
    contact_phone = fields.Char(string='Contact Telephone or Cell Phone Number', readonly=True)

    # Signature and Date
    signature = fields.Binary(string='Signature')
    signature_date = fields.Datetime(string='Signature Date', default=fields.Datetime.now)

    # Month and Year Selection
    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string='Month', required=True, default=str(datetime.now().month))

    year = fields.Integer(string='Year', required=True, default=datetime.now().year)

    # One2many field for attendance lines
    attendance_ids = fields.One2many('hr.attendance', 'timesheet_generator_id', string='Attendance Lines')

    # State field to track generation
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated'),
    ], string='State', default='draft')

    @api.model
    def default_get(self, fields_list):
        """Auto-populate fields based on current user's employee record"""
        res = super(HrTimesheetGenerator, self).default_get(fields_list)

        # Get current user's employee record
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        if not employee:
            # If no employee record found, we'll handle this in the view
            return res

        # Auto-populate fields from employee record
        res.update({
            'employee_id': employee.id,
            'name': employee.name.split(' ')[0] if employee.name else '',
            'surname': ' '.join(employee.name.split(' ')[1:]) if employee.name and len(employee.name.split(' ')) > 1 else '',
            'initials': employee.name[0] if employee.name else '',
            'department_id': employee.department_id.id if employee.department_id else False,
            'branch_directorate_id': employee.parent_id.department_id.id if employee.parent_id and employee.parent_id.department_id else False,
            'sap_employee_number': employee.identification_id or '',
            'contact_phone': employee.mobile_phone or employee.work_phone or '',
        })

        return res

    @api.constrains('month', 'year', 'employee_id')
    def _check_unique_month_year(self):
        """Ensure only one record per employee per month/year"""
        for record in self:
            if record.employee_id:
                existing = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('month', '=', record.month),
                    ('year', '=', record.year),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_('A timesheet for %s %s already exists for this employee.') %
                                        (dict(self._fields['month'].selection)[record.month], record.year))

    def action_generate_timesheets(self):
        """Generate attendance lines for the selected month/year excluding weekends and holidays"""
        self.ensure_one()

        if not self.employee_id:
            raise UserError(_('No employee record found. Please contact your administrator to create your employee record.'))

        # Clear existing attendance lines
        self.attendance_ids.unlink()

        # Get the first and last day of the selected month
        year = self.year
        month = int(self.month)
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1])

        # Get employee's working calendar
        calendar_id = self.employee_id.resource_calendar_id
        if not calendar_id:
            calendar_id = self.env.company.resource_calendar_id

        # Get holidays for the period
        holidays = self.env['resource.calendar.leaves'].search([
            ('calendar_id', '=', calendar_id.id),
            ('date_from', '<=', last_day),
            ('date_to', '>=', first_day),
        ])

        holiday_dates = set()
        for holiday in holidays:
            current_date = holiday.date_from.date()
            end_date = holiday.date_to.date()
            while current_date <= end_date:
                holiday_dates.add(current_date)
                current_date += timedelta(days=1)

        # Generate attendance lines for each working day
        current_date = first_day
        attendance_lines = []

        while current_date <= last_day:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:  # Monday=0 to Friday=4
                # Skip holidays
                if current_date.date() not in holiday_dates:
                    attendance_lines.append((0, 0, {
                        'employee_id': self.employee_id.id,
                        'check_in': current_date.replace(hour=8, minute=0, second=0),  # Default 8 AM
                        'check_out': False,  # To be filled by employee
                        'timesheet_generator_id': self.id,
                    }))

            current_date += timedelta(days=1)

        # Create attendance lines
        self.write({
            'attendance_ids': attendance_lines,
            'state': 'generated'
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Timesheet lines generated successfully for %s %s') %
                          (dict(self._fields['month'].selection)[self.month], self.year),
                'type': 'success',
            }
        }

    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.write({'state': 'draft'})
        return True


class HrAttendanceInherit(models.Model):
    _inherit = 'hr.attendance'

    timesheet_generator_id = fields.Many2one('hr.timesheet.generator', string='Timesheet Generator')