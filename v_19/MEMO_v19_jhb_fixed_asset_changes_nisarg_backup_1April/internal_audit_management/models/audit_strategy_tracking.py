from odoo import models, fields


class AuditStrategyTracking(models.Model):
    _name = 'audit.strategy.tracking'
    _description = 'Audit Strategy Tracking'

    audit_strategy_tracking_id = fields.Many2one('audit.strategy', string='Audit Strategy')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),],
                             default="preparer", string="Previous Stage")
    new_stage_id = fields.Selection([('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),],
                                 default="preparer", string="New Stage")
    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
