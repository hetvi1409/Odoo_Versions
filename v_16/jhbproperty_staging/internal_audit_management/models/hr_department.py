# -*- coding: utf-8 -*-
from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    lead_id = fields.Many2one('hr.employee', string='Lead')
    employee_ids = fields.Many2many('hr.employee', string='Members')

    def action_view_members(self):
        """View Members"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Members',
            'target': 'current',
            'domain': [('id', 'in', self.employee_ids.ids)],
            'res_model': 'hr.employee',
            'view_mode': 'tree,kanban,form',
        }
