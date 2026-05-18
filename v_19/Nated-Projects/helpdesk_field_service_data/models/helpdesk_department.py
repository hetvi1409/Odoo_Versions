from odoo import fields, models


class HelpdeskDepartment(models.Model):
    """Helpdesk Department"""
    _name = 'helpdesk.department'
    _description = "Helpdesk Department"

    name = fields.Char(string="Name", help="Name of the department", required=True)
