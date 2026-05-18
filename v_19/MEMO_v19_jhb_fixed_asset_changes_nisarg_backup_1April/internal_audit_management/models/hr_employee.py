# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # role = fields.Selection([('reviewer', 'Reviewer'), ('approver', 'Approver'),
    #                          ('preparer', 'Preparer')], string='Role')
    role_ids = fields.Many2many('audit.role', string='Role')

    department_ids = fields.Many2many('hr.department', string='Allowed Teams')
