from odoo import models, fields


class AuditCharterTracking(models.Model):
    _name = 'audit.charter.tracking'
    _description = 'Audit Charter Tracking'

    audit_charter_tracking_id = fields.Many2one('internal.audit.charter', string='Audit Charter Tracking')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
    ], 'State', default='preparer', tracking=True)

    new_stage_id = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
    ], 'State', default='preparer', tracking=True)

    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
