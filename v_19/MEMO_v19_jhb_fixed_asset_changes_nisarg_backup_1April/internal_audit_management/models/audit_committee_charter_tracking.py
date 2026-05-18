from odoo import models, fields


class AuditCommitteeCharterTracking(models.Model):
    _name = 'audit.committee.charter.tracking'
    _description = 'Audit Committee Charter Tracking'

    audit_committee_charter_tracking_id = fields.Many2one('audit.committee.charter', string='Audit Committee Charter')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
    ], 'Previous State', default='preparer', tracking=True)
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
