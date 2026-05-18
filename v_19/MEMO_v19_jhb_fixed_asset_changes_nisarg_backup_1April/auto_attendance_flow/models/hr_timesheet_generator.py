# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import calendar
import pytz


class HrTimesheetGenerator(models.Model):
    _name = 'hr.timesheet.generator'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Timesheet Generator'
    _rec_name = 'employee_id'

    @staticmethod
    def year_range_selection(start_offset, end_offset, steps=1):
        current_year = fields.Datetime.now().year
        return [(str(year), str(year)) for year in range(current_year - start_offset, current_year + end_offset, steps)]

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
        ('1', 'January'), ('2', 'February'), ('3', 'March'),
        ('4', 'April'), ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'), ('9', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December'),
    ], string='Month', required=True, default=str(datetime.now().month))

    year = fields.Selection(string='Year', selection=lambda self: self.year_range_selection(50, 20),
                            default=lambda self: str(fields.Datetime.now().year),
                            help='Select the year for which you want to add timesheet for which year.')

    # One2many field for attendance lines
    attendance_ids = fields.One2many('hr.attendance', 'timesheet_generator_id', string='Attendance Lines',
                                     order='check_in asc')

    # State field to track generation
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft',tracking=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', readonly=True)
    manager_surname = fields.Char(string='Surname', readonly=True)
    manager_initials = fields.Char(string='Initials', readonly=True)
    manager_sap_employee_number = fields.Char(string='SAP/Employee Number', readonly=True)
    manager_contact_phone = fields.Char(string='Contact Telephone or Cell Phone Number', readonly=True)
    show_manager_tree = fields.Boolean(
        string="Show Manager Tree",
        compute="_compute_show_manager_tree",
        store=False
    )
    show_user_tree = fields.Boolean(
        string="Show User Tree",
        compute="_compute_show_manager_tree",
        store=False
    )
    rejection_reason = fields.Text("Rejection Reason")

    def _compute_show_manager_tree(self):
        """Decide which tree to show based on user groups"""
        for rec in self:
            user = self.env.user
            rec.show_manager_tree = user.has_group("hr.group_hr_user") or user.has_group("hr.group_hr_manager")
            rec.show_user_tree = user.has_group("base.group_user") and not rec.show_manager_tree

    def write(self, vals):
        result = super(HrTimesheetGenerator, self).write(vals)
        for record in self:
            if record.state in ('approved') and record.signature:
                template = self.env.ref('auto_attendance_flow.mail_template_timesheet_approved')
                base_url = self.get_base_url()
                url = f"{base_url}/web#id={record.id}&model=hr.timesheet.generator&view_type=form"
                user = record.employee_id.name
                template.with_context(approve_user=user, request=record.state, url=url).sudo().send_mail(
                    record.id, force_send=True,
                    email_values={
                        'email_to': record.employee_id.user_partner_id.email or record.employee_id.work_email})


    @api.model
    def default_get(self, fields_list):
        res = super(HrTimesheetGenerator, self).default_get(fields_list)
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        if not employee:
            return res

        res.update({
            'employee_id': employee.id,
            'name': employee.name.split(' ')[0] if employee.name else '',
            'surname': ' '.join(employee.name.split(' ')[1:]) if employee.name and len(
                employee.name.split(' ')) > 1 else '',
            'initials': employee.name[0] if employee.name else '',
            'department_id': employee.department_id.id if employee.department_id else False,
            'branch_directorate_id': employee.parent_id.department_id.id if employee.parent_id and employee.parent_id.department_id else False,
            'sap_employee_number': employee.identification_id or '',
            'contact_phone': employee.mobile_phone or employee.work_phone or '',
            'manager_id': employee.parent_id.id if employee.parent_id else False,
            'manager_surname': ' '.join(employee.parent_id.name.split(' ')[1:]) if employee.parent_id.name and len(
                employee.parent_id.name.split(' ')) > 1 else '',
            'manager_initials': employee.parent_id.name[0] if employee.parent_id.name else '',
            'manager_sap_employee_number': employee.parent_id.identification_id or '',
            'manager_contact_phone': employee.parent_id.mobile_phone or employee.parent_id.work_phone or '',
        })

        return res

    @api.constrains('month', 'year', 'employee_id')
    def _check_unique_month_year(self):
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
        """Generate attendance lines for the selected month/year including weekends and holidays"""
        self.ensure_one()

        if not self.employee_id:
            raise UserError(_('No employee record found.'))

        # Clear existing attendance lines
        self.attendance_ids.unlink()

        # Get the first and last day of the selected month
        year = int(self.year)
        month = int(self.month)
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1])

        # timezone: prefer employee.user_id.tz, else current user tz, else UTC
        tz_name = (self.employee_id.user_id.tz or self.env.user.tz) or 'UTC'
        try:
            tz = pytz.timezone(tz_name)
        except Exception:
            tz = pytz.utc

        # Get employee's working calendar
        calendar_id = self.employee_id.resource_calendar_id or self.env.company.resource_calendar_id

        # Get holidays in the month
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

        # Generate attendance lines for all days in the month
        current_date = first_day
        attendance_lines = []
        while current_date <= last_day:
            is_weekend = current_date.weekday() >= 5
            is_holiday = current_date.date() in holiday_dates
            is_special = is_weekend or is_holiday

            if not is_special:
                # Weekday: default 08:00 - 16:00 (LOCAL times)
                local_check_in = datetime(current_date.year, current_date.month, current_date.day, 8, 0, 0)
                local_check_out = datetime(current_date.year, current_date.month, current_date.day, 16, 0, 0)
            else:
                # Weekend / holiday: 00:00 local (placeholder)
                local_check_in = datetime(current_date.year, current_date.month, current_date.day, 0, 0, 0)
                local_check_out = datetime(current_date.year, current_date.month, current_date.day, 0, 0, 0)

            # localize -> convert to UTC -> string for Odoo
            try:
                local_ci = tz.localize(local_check_in)
                utc_ci = local_ci.astimezone(pytz.utc)
                check_in_val = fields.Datetime.to_string(utc_ci)
                local_co = tz.localize(local_check_out)
                utc_co = local_co.astimezone(pytz.utc)
                check_out_val = fields.Datetime.to_string(utc_co)
            except Exception:
                # fallback: store naive string (still better than nothing)
                check_in_val = fields.Datetime.to_string(local_check_in)
                check_out_val = fields.Datetime.to_string(local_check_out)

            attendance_lines.append((0, 0, {
                'employee_id': self.employee_id.id,
                'check_in': check_in_val,
                'check_out': check_out_val,
                'is_placeholder': True,
                'timesheet_generator_id': self.id,
                'is_weekend_or_holiday': is_special,
            }))
            current_date += timedelta(days=1)

        # sort ascending by check_in (strings in iso format sort correctly)
        attendance_lines = sorted(attendance_lines, key=lambda l: l[2]['check_in'])

        # Bypass constraints during batch creation
        self.with_context(bypass_attendance_constraints=True).write({
            'attendance_ids': attendance_lines,
            'state': 'generated'
        })

        # Reload the current record so front-end shows the new lines immediately
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Success'),
        #         'message': _('Timesheet lines generated successfully for %s %s') %
        #                    (dict(self._fields['month'].selection)[self.month], self.year),
        #         'type': 'success',
        #     }
        # }

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_approve_timesheet(self):
        if not self.manager_id:
            raise ValidationError("Please add Manager before sign the timesheet.")
        if self.manager_id.user_id.id != self.env.user.id:
            raise ValidationError("Only manager can sign and approve timesheet.")
        return {
            'name': 'Sign and Approve',
            'type': 'ir.actions.act_window',
            'res_model': 'timesheet.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_timesheet_generator_id': self.id,
                'default_field': 'signature',
                'default_user_id': self.manager_id.user_id.id,
                'default_mode': 'approver',
            }
        }

    def action_open_reject_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'timesheet.action.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_timesheet_generator_id': self.id,
                'default_action_type': 'reject'
            }
        }


class HrAttendanceInherit(models.Model):
    _inherit = 'hr.attendance'
    _order = "check_in asc"

    timesheet_generator_id = fields.Many2one('hr.timesheet.generator', string='Timesheet Generator')
    is_placeholder = fields.Boolean("Placeholder", default=False)
    overtime_approved = fields.Boolean("Overtime Approved", default=False)
    is_weekend_or_holiday = fields.Boolean(
        "Is Weekend or Holiday", compute="_compute_is_weekend_or_holiday", store=True
    )
    validated_overtime_hours = fields.Float(string="Extra Hours", compute='_compute_worked_hours', store=True,
                                            readonly=False, tracking=True)
    overtime_status = fields.Selection(selection=[('to_approve', "To Approve"),
                                                  ('approved', "Approved"),
                                                  ('refused', "Refused")], default='to_approve',
                                       compute="_compute_overtime_status",
                                       store=True, tracking=True, options="{'clickable': '1'}", readonly=False)
    timesheet_status = fields.Selection([
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Timesheet Status', default='to_approve', tracking=True)
    is_overtime = fields.Boolean(string="Is Overtime?",default=False)

    @api.constrains('check_in', 'check_out')
    def _check_times_consistency(self):
        for att in self:
            if att.check_in and att.check_out:
                if att.check_out < att.check_in:
                    raise ValidationError(_("Check-out cannot be earlier than check-in."))

    @api.depends('check_in', 'employee_id')
    def _compute_is_weekend_or_holiday(self):
        for rec in self:
            is_special = False
            if rec.check_in:
                dt = rec.check_in
                # Check weekend
                if dt.weekday() >= 5:
                    is_special = True
                else:
                    # Check holiday
                    calendar_id = rec.employee_id.resource_calendar_id or rec.env.company.resource_calendar_id
                    holidays = rec.env['resource.calendar.leaves'].search([
                        ('calendar_id', '=', calendar_id.id),
                        ('date_from', '<=', dt),
                        ('date_to', '>=', dt),
                    ])
                    if holidays:
                        is_special = True
            rec.is_weekend_or_holiday = is_special

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Block manual addition of time on weekends/holidays (unless the record was created by the generator)
        for rec in records:
            # If record not created by generator AND there's real check_in/check_out on a weekend => block
            if not rec.timesheet_generator_id and rec.is_weekend_or_holiday and rec.check_in and rec.check_out and (
                    rec.check_out - rec.check_in).total_seconds() > 0:
                raise ValidationError(_("You cannot add time on weekends or public holidays."))
        # run the same validations as in write
        records._validate_overtime_and_leave_rules()
        return records

    def write(self, vals):
        res = super().write(vals)
        # validate for all affected records
        self._validate_overtime_and_leave_rules()
        # enforce readonly of overtime_approved for non-admins/managers
        if 'overtime_approved' in vals:
            # only HR managers or Settings can toggle
            if not (self.env.user.has_group('hr.group_hr_manager') or self.env.user.has_group('base.group_system')):
                raise ValidationError(_("You are not allowed to change Overtime Approved."))
        return res

    def _validate_overtime_and_leave_rules(self):
        """
        Validate rules:
        - No manual time additions on weekends/holidays (unless created via generator)
        - Weekday >8h requires is_overtime True and approved_document_id
        - Weekend/holiday time must be marked is_overtime True and have proof
        - Leave days (time_off_type_id) must have proof and is_overtime False
        """
        for att in self:
            # skip placeholder generator rows that are 00:00 (these are allowed)
            if att.timesheet_generator_id:
                # allow the generator-created placeholders but *do not* allow users to convert them on weekends
                # (we will block writes that set real check_in/check_out on a weekend if not allowed)
                pass

            # compute total hours (use validated_overtime_hours + worked_hours)
            total_hours = float((att.worked_hours or 0.0) + (att.validated_overtime_hours or 0.0))

            # find weekend/holiday flag (already computed save in is_weekend_or_holiday)
            if att.is_weekend_or_holiday:
                # If there is non-zero time and it's not a generator placeholder -> require is_overtime + proof
                if att.check_in and att.check_out and (att.check_out - att.check_in).total_seconds() > 0:
                    if not att.is_overtime:
                        raise ValidationError(_("Time on weekends/holidays must be marked as 'Is Overtime?'."))
                    if not att.approved_document_id:
                        raise ValidationError(_("Please attach proof of overtime for weekend/holiday work."))

            elif att.time_off_type_id:
                # leave on a weekday
                if att.is_overtime:
                    raise ValidationError(_("A leave day cannot be marked as overtime."))
                if not att.approved_document_id:
                    raise ValidationError(_("Please attach proof document for leave."))
            else:
                # normal weekday working time
                if total_hours > 8.0:
                    # requires is_overtime and proof
                    if not att.is_overtime:
                        raise ValidationError(_("For more than 8 hours, mark 'Is Overtime?' for the line."))
                    if not att.approved_document_id:
                        raise ValidationError(_("Please attach proof of overtime."))

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for rec in self:
            rec.worked_hours = 0.0
            rec.validated_overtime_hours = 0.0

            if rec.check_in and rec.check_out:
                check_in = rec.check_in
                check_out = rec.check_out

                # Define cutoff as 16:00 on check-in date
                cutoff_dt = datetime.combine(check_in.date(), time(hour=16, minute=0))
                weekday = check_in.weekday()  # 0=Mon ... 6=Sun
                is_weekend = weekday >= 5

                # TODO: Adjust holiday lookup if using resource.calendar.leaves
                is_holiday = self.env['resource.calendar.leaves'].search_count([
                    ('date_from', '<=', check_in),
                    ('date_to', '>=', check_out),
                    ('calendar_id', '=', rec.employee_id.resource_calendar_id.id)
                ]) > 0

                if is_weekend or is_holiday:
                    # ✅ Case 2: Weekends & Holidays → all time = overtime
                    overtime = check_out - check_in
                    rec.validated_overtime_hours = round(overtime.total_seconds() / 3600.0, 2)
                    rec.overtime_bool = True
                    if not rec.overtime_proof:
                        raise ValidationError(_("Proof of Overtime is required on weekends/holidays."))
                else:
                    # ✅ Case 3: Normal weekdays → split at 16:00
                    if check_out <= cutoff_dt:
                        worked = check_out - check_in
                        rec.worked_hours = round(worked.total_seconds() / 3600.0, 2)
                    else:
                        worked = cutoff_dt - check_in
                        if worked.total_seconds() > 0:
                            rec.worked_hours = round(worked.total_seconds() / 3600.0, 2)

                        overtime_start = max(check_in, cutoff_dt)
                        overtime = check_out - overtime_start
                        if overtime.total_seconds() > 0:
                            rec.validated_overtime_hours = round(overtime.total_seconds() / 3600.0, 2)

                    # ✅ Rule: More than 8 hours requires overtime proof
                    total_hours = rec.worked_hours + rec.validated_overtime_hours
                    if total_hours > 8.0:
                        rec.overtime_bool = True
                        if not rec.overtime_proof:
                            raise ValidationError(_("Proof of Overtime is required for more than 8 hours."))

    def _compute_overtime_status(self):
        """
        Compute overtime status based on company validation settings.
        Handles cases where:
        - Employee has no company
        - Attendance has no employee
        - Company validation setting is missing
        """
        for attendance in self:
            # Default status if any validation fails
            status = "to_approve"

            if not attendance.overtime_status:
                # Check if attendance has employee
                if not attendance.employee_id:
                    attendance.overtime_status = status
                    continue

                # Check if employee has company
                if not attendance.employee_id.company_id:
                    attendance.overtime_status = status
                    continue

                # Get company validation setting with fallback
                validation_type = attendance.employee_id.company_id.attendance_overtime_validation
                if not validation_type:
                    attendance.overtime_status = status
                    continue

                # Set status based on validation type
                attendance.overtime_status = "to_approve" if validation_type == 'by_manager' else "approved"
            else:
                # Keep existing status if already set
                attendance.overtime_status = attendance.overtime_status
