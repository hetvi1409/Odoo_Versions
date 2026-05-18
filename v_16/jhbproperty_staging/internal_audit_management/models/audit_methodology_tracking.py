from odoo import models, fields


class AuditMethodologyTracking(models.Model):
    _name = 'audit.methodology.tracking'
    _description = 'Audit Methodology Tracking'

    audit_methodology_tracking_id = fields.Many2one('audit.methodology', string='Audit Methodology')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                              ('approve', 'Approve')],
                             default="new", string="Previous Stage")
    new_stage_id = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                                  ('approve', 'Approve')],
                                 default="new", string="New Stage")
    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
