from odoo import api, fields, models


class HrDepartment(models.Model):
    """Department"""
    _inherit = 'hr.department'

    recruit_dept = fields.Boolean(string="Recruit dept")
