from odoo import models, fields


class InternalAuditPlanTracking(models.Model):
    _name = 'internal.audit.plan.tracking'
    _description = 'Internal Audit Plan Tracking'

    internal_audit_plan_tracking_id = fields.Many2one('internal.audit.plan', string='Internal Audit Plan')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([
        ('new', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'), ],
        default="preparer", string="Previous Stage")
    new_stage_id = fields.Selection([
        ('new', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'), ],
        default="preparer", string="New Stage")
    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
