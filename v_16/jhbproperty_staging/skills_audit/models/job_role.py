
from odoo import models, fields

class ScsJobRole(models.Model):
    _name = 'scs.job.role'
    _description = 'SCM Job Role'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    requirement_ids = fields.One2many('scs.role.requirement', 'role_id', string='Competency Requirements')

class ScsRoleRequirement(models.Model):
    _name = 'scs.role.requirement'
    _description = 'Role Requirement for Competency'
    _rec_name = 'competency_id'

    role_id = fields.Many2one('scs.job.role', required=True, ondelete='cascade')
    competency_id = fields.Many2one('scs.competency', required=True, ondelete='cascade')
    required_level = fields.Selection([
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='basic', required=True)
    _sql_constraints = [
        ('role_comp_uniq', 'unique(role_id, competency_id)', 'Requirement already defined for this role and competency.'),
    ]
