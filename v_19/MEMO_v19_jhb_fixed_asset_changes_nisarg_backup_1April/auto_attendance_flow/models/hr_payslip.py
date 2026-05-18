# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import fields, models, api, exceptions, _


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        self.compute_sheet()
        overtime_id = self.env['hr.overtime']
        for overtime_id in self.overtime_ids:
            overtime_id.update({'payslip_id': self.id})
        self.update({'state': 'done', 'paid': True})
        return res

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_overtime_ids(self):
        overtime_ids = self.env['hr.overtime'].sudo().search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ])
        self.overtime_ids = overtime_ids

    overtime_ids = fields.One2many('hr.overtime', 'payslip_id', compute='compute_overtime_ids',
                                   string='Overtime')
