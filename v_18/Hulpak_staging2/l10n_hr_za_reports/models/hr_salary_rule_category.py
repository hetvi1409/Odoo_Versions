from odoo import fields, models


class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'

    sdl = fields.Boolean(string="SDL")
    uif = fields.Boolean(string="UIF")
