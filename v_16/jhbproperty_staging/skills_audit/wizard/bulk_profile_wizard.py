
from odoo import models, fields

class BulkProfileWizard(models.TransientModel):
    _name = 'scs.bulk.profile.wizard'
    _description = 'Bulk Employee Profile Generator'

    department_id = fields.Many2one('hr.department')
    role_id = fields.Many2one('scs.job.role', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    def action_generate(self):
        EmployeeProfile = self.env['scs.employee.profile']
        employees = self.employee_ids
        if not employees and self.department_id:
            employees = self.env['hr.employee'].search([('department_id','=',self.department_id.id)])
        for emp in employees:
            if not EmployeeProfile.search([('employee_id','=',emp.id)], limit=1):
                EmployeeProfile.create({'employee_id': emp.id, 'role_id': self.role_id.id})
        return {'type': 'ir.actions.act_window_close'}
