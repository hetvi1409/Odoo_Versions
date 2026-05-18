from odoo import fields, models, api, _
from pytz import timezone
from odoo.addons.resource.models.resource import Intervals
from collections import defaultdict
from odoo.osv.expression import AND, OR
from datetime import datetime, time, timedelta


class HrAttendance(models.Model):
    _name = 'hr.attendance'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'hr.attendance']

    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True, tracking=True)
    validated_overtime_hours = fields.Float(string="Extra Hours", compute='_compute_worked_hours', store=True, readonly=False, tracking=True)
    overtime_status = fields.Selection(selection=[('to_approve', "To Approve"),
                                                  ('approved', "Approved"),
                                                  ('refused', "Refused")], default='to_approve', compute="_compute_overtime_status",
                                       store=True, tracking=True,options="{'clickable': '1'}",readonly=False)
    overtime_hours = fields.Float(string="Over Time", compute='_compute_overtime_hours', store=True)
    timesheet_status = fields.Selection([
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Timesheet Status', default='to_approve', tracking=True)

    # Add missing fields
    overtime_approved = fields.Boolean(
        string='Overtime Approved',
        tracking=True,
        help='Technical field to track if overtime has been approved'
    )

    def _get_employee_calendar(self):
        self.ensure_one()
        return self.employee_id.resource_calendar_id or self.employee_id.company_id.resource_calendar_id


    def get_list_url(self):
        """Returns the url for the list view"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        from werkzeug import urls
        Urls = urls.url_join(base_url,'web#id=%s&model=hr.attendance&view_type=form' % self.id)
        return Urls


    def action_approve_overtime(self):
        self.overtime_status = 'approved'

    def action_refuse_overtime(self):
        self.overtime_status = 'refused'

    def action_send_attendance(self):
        manager_group = self.env.ref('hr_attendance.group_hr_attendance_manager')
        template = self.env.ref('hr_attendence_updates.email_template_to_attendance')

        for attendance in self:
            # Prepare recipient emails
            mail_values = {}
            partners = manager_group.users.mapped('partner_id')
            for partner in partners:
                if partner.email:
                    mail_values = {
                        'email_to': partner.email,
                    }

            # Send email for this record
            template.send_mail(attendance.id, force_send=True, email_values=mail_values)

            # Post message to chatter
            message_body = f"Asset {attendance.employee_id.name} has sent the mail."
            asset_manager_group = self.env.ref('asset_approval.group_asset_manager')
            partner_ids = asset_manager_group.users.mapped('partner_id.id')
            attendance.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=partner_ids,
            )



    # def _update_overtime(self, employee_attendance_dates=None):
    #     if employee_attendance_dates is None:
    #         employee_attendance_dates = self._get_attendances_dates()
    #
    #     overtime_to_unlink = self.env['hr.attendance.overtime']
    #     overtime_vals_list = []
    #     affected_employees = self.env['hr.employee']
    #     for emp, attendance_dates in employee_attendance_dates.items():
    #         # get_attendances_dates returns the date translated from the local timezone without tzinfo,
    #         # and contains all the date which we need to check for overtime
    #         attendance_domain = []
    #         for attendance_date in attendance_dates:
    #             attendance_domain = OR([attendance_domain, [
    #                 ('check_in', '>=', attendance_date[0]), ('check_in', '<', attendance_date[0] + timedelta(hours=24)),
    #             ]])
    #         attendance_domain = AND([[('employee_id', '=', emp.id)], attendance_domain])
    #
    #         # Attendances per LOCAL day
    #         attendances_per_day = defaultdict(lambda: self.env['hr.attendance'])
    #         all_attendances = self.env['hr.attendance'].search(attendance_domain)
    #         for attendance in all_attendances:
    #             check_in_day_start = attendance._get_day_start_and_day(attendance.employee_id, attendance.check_in)
    #             attendances_per_day[check_in_day_start[1]] += attendance
    #
    #         # As _attendance_intervals_batch and _leave_intervals_batch both take localized dates we need to localize those date
    #         start = pytz.utc.localize(min(attendance_dates, key=itemgetter(0))[0])
    #         stop = pytz.utc.localize(max(attendance_dates, key=itemgetter(0))[0] + timedelta(hours=24))
    #
    #         # Retrieve expected attendance intervals
    #         calendar = emp.resource_calendar_id or emp.company_id.resource_calendar_id
    #         expected_attendances = emp._employee_attendance_intervals(start, stop)
    #
    #         # working_times = {date: [(start, stop)]}
    #         working_times = defaultdict(lambda: [])
    #         for expected_attendance in expected_attendances:
    #             # Exclude resource.calendar.attendance
    #             working_times[expected_attendance[0].date()].append(expected_attendance[:2])
    #
    #         overtimes = self.env['hr.attendance.overtime'].sudo().search([
    #             ('employee_id', '=', emp.id),
    #             ('date', 'in', [day_data[1] for day_data in attendance_dates]),
    #             ('adjustment', '=', False),
    #         ])
    #
    #         company_threshold = emp.company_id.overtime_company_threshold / 60.0
    #         employee_threshold = emp.company_id.overtime_employee_threshold / 60.0
    #
    #         for day_data in attendance_dates:
    #             attendance_date = day_data[1]
    #             attendances = attendances_per_day.get(attendance_date, self.browse())
    #             unfinished_shifts = attendances.filtered(lambda a: not a.check_out)
    #             overtime_duration = 0
    #             overtime_duration_real = 0
    #             # Overtime is not counted if any shift is not closed or if there are no attendances for that day,
    #             # this could happen when deleting attendances.
    #             if not unfinished_shifts and attendances:
    #                 # The employee is working flexible hours
    #                 if emp.is_flexible:
    #                     work_duration = 0
    #                     for attendance in attendances:
    #                         local_check_in = pytz.utc.localize(attendance.check_in)
    #                         local_check_out = pytz.utc.localize(attendance.check_out)
    #                         work_duration += (local_check_out - local_check_in).total_seconds() / 3600.0
    #                     # In case of fully flexible employee, no overtime is computed
    #                     if not emp.is_fully_flexible:
    #                         overtime_duration = work_duration - emp.resource_id.calendar_id.hours_per_day
    #                         overtime_duration_real = overtime_duration
    #
    #                 # The employee usually doesn't work on that day
    #                 elif not working_times[attendance_date]:
    #                     # User does not have any resource_calendar_attendance for that day (week-end for example)
    #                     overtime_duration = sum(attendances.mapped('worked_hours'))
    #                     overtime_duration_real = overtime_duration
    #                 # The employee usually work on that day
    #                 else:
    #                     # Count time before, during and after 'working hours'
    #                     pre_work_time, work_duration, post_work_time, planned_work_duration = attendances._get_pre_post_work_time(emp, working_times, attendance_date)
    #                     # Overtime within the planned work hours + overtime before/after work hours is > company threshold
    #                     overtime_duration = work_duration - planned_work_duration
    #                     if pre_work_time > company_threshold:
    #                         overtime_duration += pre_work_time
    #                     if post_work_time > company_threshold:
    #                         overtime_duration += post_work_time
    #                     # Global overtime including the thresholds
    #                     overtime_duration_real = sum(attendances.mapped('worked_hours')) - planned_work_duration
    #
    #             overtime = overtimes.filtered(lambda o: o.date == attendance_date)
    #             if not float_is_zero(overtime_duration, 2) or unfinished_shifts:
    #                 # Do not create if any attendance doesn't have a check_out, update if exists
    #                 if unfinished_shifts:
    #                     overtime_duration = 0
    #                 if not overtime and overtime_duration:
    #                     overtime_vals_list.append({
    #                         'employee_id': emp.id,
    #                         'date': attendance_date,
    #                         'duration': overtime_duration,
    #                         'duration_real': overtime_duration_real,
    #                     })
    #                 elif overtime:
    #                     overtime.sudo().write({
    #                         'duration': overtime_duration,
    #                         'duration_real': overtime_duration
    #                     })
    #                     affected_employees |= overtime.employee_id
    #             elif overtime:
    #                 overtime_to_unlink |= overtime
    #     created_overtimes = self.env['hr.attendance.overtime'].sudo().create(overtime_vals_list)
    #     employees_worked_hours_to_compute = (affected_employees.ids +
    #                                          created_overtimes.employee_id.ids +
    #                                          overtime_to_unlink.employee_id.ids)
    #     overtime_to_unlink.sudo().unlink()
    #     to_recompute = self.search([('employee_id', 'in', employees_worked_hours_to_compute)])
    #     self.env.add_to_compute(self._fields['overtime_hours'],
    #                             to_recompute)
    #     self.env.add_to_compute(self._fields['validated_overtime_hours'],
    #                             to_recompute)
    #     self.env.add_to_compute(self._fields['expected_hours'],
    #                             to_recompute)





    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        """ Computes the worked hours of the attendance record.
            The worked hours of resource with flexible calendar is computed as the difference
            between check_in and check_out, without taking into account the lunch_interval"""
        # for attendance in self:
        #     if attendance.check_out and attendance.check_in and attendance.employee_id:
        #         calendar = attendance._get_employee_calendar()
        #         resource = attendance.employee_id.resource_id
        #         tz = timezone(resource.tz) if not calendar else timezone(calendar.tz)
        #         check_in_tz = attendance.check_in.astimezone(tz)
        #         check_out_tz = attendance.check_out.astimezone(tz)
        #         lunch_intervals = []
        #         # if not attendance.employee_id.is_flexible:
        #         #     lunch_intervals = attendance.employee_id._employee_attendance_intervals(check_in_tz, check_out_tz, lunch=True)
        #         # attendance_intervals = Intervals([(check_in_tz, check_out_tz, attendance)]) - lunch_intervals
        #         # delta = sum((i[1] - i[0]).total_seconds() for i in attendance_intervals)
        #         # attendance.worked_hours = delta / 3600.0
        #     else:
        #         attendance.worked_hours = False
        for rec in self:
            rec.worked_hours = 0.0
            rec.validated_overtime_hours = 0.0

            if rec.check_in and rec.check_out:
                check_in = rec.check_in
                check_out = rec.check_out

                # Define cutoff as 16:00 on check-in date
                cutoff_dt = datetime.combine(check_in.date(), time(hour=16, minute=0))

                # Worked hours = check_in to cutoff, or to check_out if earlier
                if check_out <= cutoff_dt:
                    worked = check_out - check_in
                    rec.worked_hours = round(worked.total_seconds() / 3600.0, 2)
                else:
                    # Check-out is after 16:00, so split time
                    worked = cutoff_dt - check_in
                    if worked.total_seconds() > 0:
                        rec.worked_hours = round(worked.total_seconds() / 3600.0, 2)

                    overtime_start = max(check_in, cutoff_dt)
                    overtime = check_out - overtime_start
                    if overtime.total_seconds() > 0:
                        rec.validated_overtime_hours = round(overtime.total_seconds() / 3600.0, 2)

    @api.depends('employee_id', 'overtime_status', 'overtime_hours')
    def _compute_validated_overtime_hours(self):
        no_validation = self.filtered(
            lambda a: a.employee_id.company_id.attendance_overtime_validation == 'no_validation')
        with_validation = self - no_validation

        for attendance in with_validation:
            if attendance.overtime_status not in ['approved', 'refused']:
                attendance.validated_overtime_hours = attendance.overtime_hours

        for attendance in no_validation:
            attendance.validated_overtime_hours = attendance.overtime_hours

    @api.depends('employee_id')
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

    @api.depends('worked_hours')
    def _compute_overtime_hours(self):
        att_progress_values = dict()
        negative_overtime_attendances = defaultdict(lambda: False)
        if self.employee_id:
            self.env['hr.attendance'].flush_model(['worked_hours'])
            self.env['hr.attendance.overtime'].flush_model(['duration'])
            self.env.cr.execute('''
                  WITH employee_time_zones AS (
                      SELECT employee.id AS employee_id,
                             calendar.tz AS timezone
                        FROM hr_employee employee
                  INNER JOIN resource_calendar calendar
                          ON calendar.id = employee.resource_calendar_id
                  )
                  SELECT att.id AS att_id,
                         att.worked_hours AS att_wh,
                         ot.id AS ot_id,
                         ot.duration AS ot_d,
                         ot.date AS od,
                         att.check_in AS ad
                    FROM hr_attendance att
              INNER JOIN employee_time_zones etz
                      ON att.employee_id = etz.employee_id
              INNER JOIN hr_attendance_overtime ot
                      ON date_trunc('day',
                                    CAST(att.check_in
                                             AT TIME ZONE 'utc'
                                             AT TIME ZONE etz.timezone
                                    as date)) = date_trunc('day', ot.date)
                     AND att.employee_id = ot.employee_id
                     AND att.employee_id IN %s
                     AND ot.adjustment IS false
                ORDER BY att.check_in DESC
              ''', (tuple(self.employee_id.ids),))
            a = self.env.cr.dictfetchall()
            grouped_dict = dict()
            for row in a:
                if row['ot_id'] and row['att_wh']:
                    if row['ot_id'] not in grouped_dict:
                        grouped_dict[row['ot_id']] = {'attendances': [(row['att_id'], row['att_wh'])],
                                                      'overtime_duration': row['ot_d']}
                    else:
                        grouped_dict[row['ot_id']]['attendances'].append((row['att_id'], row['att_wh']))

            for overtime in grouped_dict:
                overtime_reservoir = grouped_dict[overtime]['overtime_duration']
                if overtime_reservoir > 0:
                    for attendance in grouped_dict[overtime]['attendances']:
                        if overtime_reservoir > 0:
                            sub_time = attendance[1] - overtime_reservoir
                            if sub_time < 0:
                                att_progress_values[attendance[0]] = 0
                                overtime_reservoir -= attendance[1]
                            else:
                                att_progress_values[attendance[0]] = float(
                                    ((attendance[1] - overtime_reservoir) / attendance[1]) * 100)
                                overtime_reservoir = 0
                        else:
                            att_progress_values[attendance[0]] = 100
                elif overtime_reservoir < 0 and grouped_dict[overtime]['attendances']:
                    att_id = grouped_dict[overtime]['attendances'][0][0]
                    att_progress_values[att_id] = overtime_reservoir
                    negative_overtime_attendances[att_id] = True
        for attendance in self:
            if negative_overtime_attendances[attendance.id]:
                attendance.overtime_hours = att_progress_values.get(attendance.id, 0)
            else:
                attendance.overtime_hours = attendance.worked_hours * (
                            (100 - att_progress_values.get(attendance.id, 100)) / 100)

    def action_open_send_mail_wizard(self):
        """Open the mail compose wizard"""
        return {
            'name': _('Send Attendance Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'attendance.mail.compose.wizard',
            'target': 'new',
            'context': {
                'default_template_id': self.env.ref('hr_attendence_updates.email_template_to_attendance').id,
                'default_attendance_ids': [(6, 0, self.ids)],
            }
        }

    def action_approve_timesheet(self):
        """Approve timesheet status"""
        for record in self:
            record.write({
                'timesheet_status': 'approved'
            })
        return True

    def action_decline_timesheet(self):
        """Decline timesheet status"""
        for record in self:
            record.write({
                'timesheet_status': 'refused'
            })
        return True

    def action_open_approval_wizard(self):
        """Open the timesheet approval wizard directly"""
        # if not self:
        #     raise UserError(_("Please select attendance records to review."))

        return {
            'name': _('Review Timesheets'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'timesheet.approval.wizard',
            'target': 'new',
            'context': {
                'default_attendance_ids': self.ids,
                'form_view_ref': 'hr_attendence_updates.view_timesheet_approval_wizard',
            }
        }

