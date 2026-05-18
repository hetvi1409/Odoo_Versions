
from odoo import models, fields

class ScsTrainingAction(models.Model):
    _name = 'scs.training.action'
    _description = 'Training/Development Action'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    employee_id = fields.Many2one('hr.employee', required=True)
    competency_id = fields.Many2one('scs.competency', required=True)
    training_actions_employee_profile_id = fields.Many2one('scs.employee.profile', string='Employee Profile', ondelete='cascade')
    state = fields.Selection([
        ('draft','Draft'),
        ('in_progress','In Progress'),
        ('done','Done')
    ], default='draft', tracking=True)
    suggested = fields.Boolean(default=False)
    notes = fields.Text()
