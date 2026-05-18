from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    sur_name = fields.Char(string="Surname", help="Surname for the employee")
    initials = fields.Char(string="Initial", help="Initial for the employee")


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    sur_name = fields.Char(
        related="employee_id.sur_name",
        string="Surname",
        readonly=True,
        compute_sudo=True,
    )
    initials = fields.Char(
        related="employee_id.initials",
        string="Initial",
        readonly=True,
        compute_sudo=True,
    )


