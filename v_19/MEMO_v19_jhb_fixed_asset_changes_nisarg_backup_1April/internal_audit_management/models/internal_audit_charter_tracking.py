from odoo import models, fields


class InternalAuditCharterTracking(models.Model):
    _name = 'internal.audit.charter.tracking'
    _description = 'Internal Audit Charter Tracking'

    internal_audit_charter_tracking_id = fields.Many2one('internal.audit.charter', string='Internal Audit Charter')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                              ('approve', 'Approve')],
                             default="new", string="Previous Stage")
    new_stage_id = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                                  ('approve', 'Approve')],
                                 default="new", string="New Stage")
    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
