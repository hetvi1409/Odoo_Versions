# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import pytz

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # hr_attendance_start_time = fields.Char(string="Start Time", readonly=False)
    hr_attendance_end_time = fields.Char(string="End Time", readonly=False)
    weekday_ot_rate = fields.Float(string="Weekday Overtime Rate")
    weekend_ot_rate = fields.Float(string="Weekend Overtime Rate")
    holiday_ot_rate = fields.Float(string="Holiday Overtime Rate")
    ot_time_limit = fields.Integer(string="Week Overtime Time Limit")
    auto_checkin_enabled = fields.Boolean(string="Allow users to auto Check-in", config_parameter='auto_attendance_flow.auto_checkin_enabled')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_id = self.env['ir.config_parameter'].sudo().get_param
        # hr_attendance_start_time = self.env['ir.config_parameter'].sudo().get_param('hr_attendance_start_time') or False
        hr_attendance_end_time = self.env.ref('auto_attendance_flow.ir_cron_data_checkout_attendance').nextcall.astimezone(
            pytz.timezone(self.env.user.employee_id.tz or 'UTC')).replace(tzinfo=None).time()
        weekday_ot_rate = float(config_id('auto_attendance_flow.weekday_ot_rate'))
        holiday_ot_rate = float(config_id('auto_attendance_flow.weekend_ot_rate'))
        weekend_ot_rate = float(config_id('auto_attendance_flow.holiday_ot_rate'))
        ot_time_limit = int(config_id('auto_attendance_flow.ot_time_limit'))
        res.update({
            # 'hr_attendance_start_time': hr_attendance_start_time,
            'hr_attendance_end_time': hr_attendance_end_time,
            'weekday_ot_rate': weekday_ot_rate,
            'weekend_ot_rate': weekend_ot_rate,
            'holiday_ot_rate': holiday_ot_rate,
            'ot_time_limit': ot_time_limit,
        })

        return res

    def set_values(self):
        def utc_dt(dt):
            local = pytz.timezone(self.env.user.tz or 'UTC')
            return local.localize(dt, is_dst=None).astimezone(pytz.utc).replace(tzinfo=None)

        res = super(ResConfigSettings, self).set_values()
        time_check_out = datetime.strptime(self.hr_attendance_end_time or '', "%H:%M:%S").replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day)
        if datetime.strptime(self.hr_attendance_end_time, "%H:%M:%S").time() < datetime.now(pytz.timezone(self.env.user.tz or 'UTC')).time():
            time_check_out = time_check_out + timedelta(days=1)
        else:
            time_check_out = time_check_out
        self.env.ref('auto_attendance_flow.ir_cron_data_checkout_attendance').write({
            'nextcall': utc_dt(time_check_out),
        })
        # self.env['ir.config_parameter'].sudo().set_param("hr_attendance_start_time", self.hr_attendance_start_time)
        config_param_obj = self.env['ir.config_parameter'].sudo().set_param
        config_param_obj("auto_attendance_flow.weekday_ot_rate", self.weekday_ot_rate)
        config_param_obj("auto_attendance_flow.weekend_ot_rate", self.weekend_ot_rate)
        config_param_obj("auto_attendance_flow.holiday_ot_rate", self.holiday_ot_rate)
        config_param_obj("auto_attendance_flow.ot_time_limit", self.ot_time_limit)
        return res

    @api.constrains('weekday_ot_rate', 'weekend_ot_rate', 'ot_time_limit', 'holiday_ot_rate')
    def _check_overtime_configuration(self):
        if self.weekday_ot_rate < 0 or self.weekend_ot_rate < 0 or self.ot_time_limit < 0 or self.holiday_ot_rate < 0:
            raise ValidationError(_('Please enter valid value.'))
