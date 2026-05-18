from odoo import models, fields, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    is_lawyers = fields.Boolean(default=False)


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    is_lawyers = fields.Boolean(default=False)
    timesheet_manager_id = fields.Many2one('res.users', string="Timesheet Manager")
