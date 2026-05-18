from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    sur_name = fields.Char(string="Surname", help="Surname for the employee")
    initials = fields.Char(string="Initial", help="Initial for the employee")


