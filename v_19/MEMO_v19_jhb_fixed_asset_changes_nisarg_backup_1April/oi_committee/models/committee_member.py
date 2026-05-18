
from odoo import models, fields, api

class CommitteeMember(models.Model):
    _name = 'committee.member'
    _description = 'Committee Member'   
    _order = 'sequence,id'
    _rec_name = 'employee_id'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    
    committee_id = fields.Many2one('committee', required = True)
    employee_id = fields.Many2one('hr.employee', required = True)
    user_id = fields.Many2one(related='employee_id.user_id', store = True, readonly = True)
    member_type = fields.Selection([('president','President'), ('secretary', 'Secretary'), ('member', 'Member'), ('reserve', 'Reserve Member')], required = True, default = 'member')
    sequence = fields.Integer()
        
    department_id = fields.Many2one('hr.department', string='Department', compute = '_calc_employee_related', store = True)
    job_id = fields.Many2one('hr.job', string='Job Position', compute = '_calc_employee_related', store = True)
    
    @api.depends('employee_id')
    def _calc_employee_related(self):
        for record in self:
            record.department_id = record.employee_id.department_id
            record.job_id = record.employee_id.job_id    