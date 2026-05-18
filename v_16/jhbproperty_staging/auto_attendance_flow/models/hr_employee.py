# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    weekday_ot_rate = fields.Float(string="Weekday OT Rate")
    weekend_ot_rate = fields.Float(string="Weekend OT Rate")
    holiday_ot_rate = fields.Float(string="Holiday OT Rate")


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    weekday_ot_rate = fields.Float(string="Weekday OT Rate")
    weekend_ot_rate = fields.Float(string="Weekend OT Rate")
    holiday_ot_rate = fields.Float(string="Holiday OT Rate")