# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError


class HrOvertime(models.Model):
    _name = "hr.overtime"
    _inherit = 'mail.thread'
    _description = 'HR Overtime'

    def _default_employee(self):
        return self.env.user.employee_id

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        if not self.env.user.has_group('base.group_system'):
            domain += [('employee_id.user_id', '=', self.env.user.id)]
        res = super(HrOvertime, self).search(
            domain=domain, offset=offset, limit=limit, order=order, count=count)
        return res

    employee_id = fields.Many2one(
        'hr.employee', string="Employee", default=_default_employee,
        required=True, ondelete='cascade')
    name = fields.Char(string="Name")
    date = fields.Date(
        string="Date", default=date.today())
    based_on = fields.Selection([
        ('weekday', 'Weekday'), ('weekend', 'Weekend'),
        ('holiday', 'Holiday')], 'Based On')
    ot_rate = fields.Float(string='OT Rate')
    overtime = fields.Float(string="Overtime")
    payslip_id = fields.Many2one('hr.payslip', string="Related Payslip")

    @api.model
    def create(self, vals):
        ot_name = self.env['ir.sequence'].next_by_code('hr.overtime')
        if ot_name:
            vals.update({'name': ot_name})
        res = super(HrOvertime, self).create(vals)
        return res

