from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    workshop_position = fields.Selection([('leader', 'Leader'), ('worker', 'Worker')])