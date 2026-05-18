# -*- coding: utf-8 -*-

import base64
from odoo import api, fields, models,_
from datetime import date, datetime, timedelta
from collections import defaultdict
from odoo.exceptions import UserError,ValidationError
import pytz
import logging

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    time_off_type_id = fields.Many2one('hr.leave.type', string="Time Off Type")
    overtime_approved = fields.Boolean(
        string="Overtime Approved", readonly=False, default=False)
    approved_document_id = fields.Many2one('documents.document', string='Overtime Approved Document')
    hr_overtime_id = fields.Many2one('hr.overtime', string="Related Overtime", readonly=True)

    @api.model
    def emp_auto_checkout(self):
        try:
            attendances = self.sudo().search([('check_out', '=', None)])
            attendances.write({
                'check_out': fields.Datetime.now(),
            })
        except:
            pass

    @api.constrains('check_out')
    def _check_overtime_approval(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                hours_worked = (rec.check_out - rec.check_in).total_seconds() / 3600
                if hours_worked > 8 and not rec.overtime_approved:
                    raise ValidationError(
                        _("Overtime must be approved with a letter before logging more than 8 hours."))

    @api.model
    def send_emp_attendance_report(self):
        today = datetime.today()
        first_day_this_month = today.replace(day=1)
        last_day_previous_month = first_day_this_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        try:
            data = {}
            # Step 1: Group employees by manager
            manager_employees_map = defaultdict(list)
            for employee in self.env['hr.employee'].search([]):
                for line in employee.attendance_ids:
                    if line.employee_id.parent_id:
                        manager_employees_map[line.employee_id.parent_id].append(line.employee_id.id)

            # Step 2: Iterate each manager and generate one report for their employees
            for manager, employee_ids in manager_employees_map.items():
                if not manager.user_id or not manager.user_id.partner_id.email:
                    continue  # Skip if no email

                email_to = manager.user_id.partner_id.email
                if email_to:
                    vals = {
                        'date_start': first_day_previous_month,
                        'date_end': last_day_previous_month,
                        'employee_ids': [(6, 0, employee_ids)],
                        'select_all': False
                    }
                    wizard_id = self.env['attendance.recap.report.wizard'].sudo().create(vals)
                    # Prepare data
                    data = {'form': wizard_id.read(['date_start', 'date_end', 'select_all', 'employee_ids'])[0]}
                    report = self.env.ref('auto_attendance_flow.attendance_recap_report')

                    # Generate PDF
                    pdf_content, _ = self.env["ir.actions.report"].sudo()._render_qweb_pdf(
                        'auto_attendance_flow.attendance_recap_report', wizard_id.id, data=data)
                    attachment = self.env['ir.attachment'].sudo().create({
                        'name': f"Attendance Report .pdf",
                        'type': 'binary',
                        'datas': base64.b64encode(pdf_content),
                        'res_model': 'hr.employee',
                        'res_id': manager.id,
                        'mimetype': 'application/pdf',
                    })

                    try:
                        template_id = self.env.ref('auto_attendance_flow.send_mail_employee_attendance_report')
                    except Exception:
                        raise UserError(_("Template Not Found!!! Error"))
                    template_id.email_to = email_to
                    template_id.attachment_ids = attachment
                    send_mail_id = template_id.send_mail(self.id, force_send=True)

        except Exception as e:
            _logger.error("Error in send_emp_attendance_report: %s", str(e))

    def get_date(self, date_time):
        if self._context.get('tz', False):
            tz = pytz.timezone(self._context.get('tz'))
        elif self.env.user.tz:
            tz = pytz.timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if sign == '-':
            date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=hour_tz, minutes=min_tz)
        if sign == '+':
            date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=hour_tz, minutes=min_tz)
        return date

    @api.model
    def generate_employee_overtime(self):
        config_id = self.env['ir.config_parameter'].sudo().get_param
        weekday_ot_rate = float(config_id('auto_attendance_flow.weekday_ot_rate'))
        holiday_ot_rate = float(config_id('auto_attendance_flow.weekend_ot_rate'))
        weekend_ot_rate = float(config_id('auto_attendance_flow.holiday_ot_rate'))
        ot_time_limit = int(config_id('auto_attendance_flow.ot_time_limit'))
        if self.employee_id:
            employee = self.employee_id
            is_weekday = False
            is_holiday = False
            res_calendar_attendance_id = False
            res_holidays_attendance_id = False
            ot_rate = 0.0
            resource_calendar_id = employee.resource_calendar_id if employee.resource_calendar_id \
                else config_id
            if resource_calendar_id:
                for each_res_calendar_attendance in resource_calendar_id.attendance_ids:
                    if int(each_res_calendar_attendance.dayofweek) == self.check_in.weekday():
                        if not res_calendar_attendance_id or \
                                (
                                        res_calendar_attendance_id and res_calendar_attendance_id.hour_to <= each_res_calendar_attendance.hour_to):
                            res_calendar_attendance_id = each_res_calendar_attendance
                        is_weekday = True
                for each_res_holiday_attendance in resource_calendar_id.global_leave_ids:
                    date_from = each_res_holiday_attendance.date_from.strftime('%d/%m/%Y')
                    date_from = datetime.strptime(date_from, '%d/%m/%Y').date()
                    date_to = each_res_holiday_attendance.date_to.strftime('%d/%m/%Y')
                    date_to = datetime.strptime(date_to, '%d/%m/%Y').date()
                    delta = date_to - date_from
                    for i in range(delta.days + 1):
                        date_holiday = date_from + timedelta(days=i)
                        if date_holiday == self.check_in.date():
                            if not res_holidays_attendance_id or \
                                    (
                                            res_holidays_attendance_id and res_holidays_attendance_id.hour_to <= each_res_calendar_attendance.hour_to):
                                res_holidays_attendance_id = each_res_calendar_attendance
                            is_holiday = True
                if res_calendar_attendance_id:
                    ot_rate = employee.weekday_ot_rate if employee.weekday_ot_rate \
                        else weekday_ot_rate if (weekday_ot_rate) \
                        else 0.0
                elif res_holidays_attendance_id:
                    ot_rate = employee.holiday_ot_rate if employee.holiday_ot_rate \
                        else holiday_ot_rate if (holiday_ot_rate) \
                        else 0.0
                else:
                    ot_rate = employee.weekend_ot_rate if employee.weekend_ot_rate \
                        else weekend_ot_rate if (weekend_ot_rate) \
                        else 0.0
            if res_holidays_attendance_id:
                hour_to_hr = (str(res_holidays_attendance_id.hour_to).split(".")[0] if '.' in str(
                    res_holidays_attendance_id.hour_to) \
                                  else str(res_holidays_attendance_id.hour_to)) if res_holidays_attendance_id else '00'
                hour_to_minute = (
                    str(int(float(str(res_holidays_attendance_id.hour_to).split(".")[1]) * 0.6)) if '.' in str(
                        res_holidays_attendance_id.hour_to) \
                        else '00') if res_holidays_attendance_id else '00'
            else:
                hour_to_hr = (
                    str(res_calendar_attendance_id.hour_to).split(".")[0] if '.' in str(
                        res_calendar_attendance_id.hour_to) \
                        else str(res_calendar_attendance_id.hour_to)) if res_calendar_attendance_id else '00'
                hour_to_minute = (
                    str(int(float(str(res_calendar_attendance_id.hour_to).split(".")[1]) * 0.6)) if '.' in str(
                        res_calendar_attendance_id.hour_to) \
                        else '00') if res_calendar_attendance_id else '00'

            date_to_add = datetime.now().replace(hour=int(hour_to_hr), minute=int(hour_to_minute), second=0)
            ot_time_limit = ot_time_limit if ot_time_limit else 0.0
            if ot_time_limit:
                date_to_add = date_to_add + timedelta(minutes=ot_time_limit)

            date_to_compare = self.get_date(str(date_to_add.strftime(
                "%Y-%m-%d %H:%M:%S")))

            overtime_min = 0.0
            overtime_hour = 0.0
            for each_attendance_id in self:
                if each_attendance_id.check_out:
                    if is_holiday:
                        check_in_date = date_to_compare if date_to_compare > fields.Datetime.from_string(
                            each_attendance_id.check_in) \
                            else fields.Datetime.from_string(each_attendance_id.check_in)
                        based_on = 'holiday'
                    elif is_weekday:
                        check_in_date = date_to_compare if date_to_compare > fields.Datetime.from_string(
                            each_attendance_id.check_in) \
                            else fields.Datetime.from_string(each_attendance_id.check_in)
                        based_on = 'weekday'
                    else:
                        check_in_date = fields.Datetime.from_string(each_attendance_id.check_in)
                        based_on = 'weekend'
                    check_out_date = fields.Datetime.from_string(each_attendance_id.check_out)
                    duration = (check_out_date - check_in_date).total_seconds()
                    overtime_min += divmod(duration, 60)[0]
                    overtime_hour += (overtime_min / 60)
                    overtime_hour = (each_attendance_id.check_out - each_attendance_id.check_in).total_seconds() / 3600
            if overtime_hour and ot_rate:
                if self.hr_overtime_id:
                    self.hr_overtime_id.sudo().write({'employee_id': employee.id,
                                                                 'date': self.check_in.date(),
                                                                 'based_on': based_on,
                                                                 'ot_rate': ot_rate,
                                                                 'overtime': overtime_hour,
                                                                 })
                else:
                    hr_overtime_id = self.env['hr.overtime'].sudo().create({'employee_id': employee.id,
                                                                     'date': self.check_in.date(),
                                                                     'based_on': based_on,
                                                                     'ot_rate': ot_rate,
                                                                     'overtime': overtime_hour,
                                                                     })
                    self.update({'hr_overtime_id': hr_overtime_id.id})

    def write(self, vals):
        res = super(HrAttendance, self).write(vals)
        # if vals.get('overtime_approved') and vals.get('approved_document_id'):
        #     self.generate_employee_overtime()
        for att in self:
            if vals.get('overtime_approved') or att.overtime_approved:
                if not att.approved_document_id:
                    raise ValidationError("Please attach an overtime approval document.")

                if att.check_in and att.check_out:
                    att.generate_employee_overtime()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            # Get start of the current week (Monday)
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())  # Monday
            context = {}
            limit = float(
                self.env['ir.config_parameter'].sudo().get_param('auto_attendance_flow.ot_time_limit', default='600'))
            emp_attendances = self.sudo().search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', start_of_week),('overtime_approved','=',True)
            ])
            if emp_attendances:
                total_hours = sum(
                    (att.check_out - att.check_in).total_seconds() / 3600
                    for att in emp_attendances if att.check_out
                )
                context.update({
                    'total_hours': total_hours or 0.0,
                })
                total_hours_min = total_hours * 60
                if total_hours_min > limit:
                    raise ValidationError(
                        _(f"Overtime limit exceeded, you have total overtime ({(limit/60):.2f} hours this week)."))
                if total_hours_min == limit:
                    template = self.env.ref('auto_attendance_flow.overtime_alert_email_template')
                    if template:
                        template.with_context(**context).send_mail(rec.id, force_send=True)


                if rec.overtime_approved and not rec.hr_overtime_id:
                    if not rec.approved_document_id:
                        raise ValidationError("Please attach an overtime approval document.")

                    if rec.check_in and rec.check_out:
                        rec.generate_employee_overtime()
        return records