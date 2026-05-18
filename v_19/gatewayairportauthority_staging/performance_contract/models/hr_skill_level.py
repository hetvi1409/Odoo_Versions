# -*- coding: utf-8 -*-
from odoo import models, fields


class HrEmployeeSkill(models.Model):
    _inherit = "hr.employee.skill"

    skill_level_progress = fields.Integer(related="skill_level_id.level_progress",string="Skill progress",store=True)

    def default_get(self, fields):
        res = super(HrEmployeeSkill, self).default_get(fields)
        if 'employee_id' in fields and self.env.context.get('default_employee_id'):
            res['employee_id'] = self.env.context.get('default_employee_id')
        return res