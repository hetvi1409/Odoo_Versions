from odoo import models, fields


class QualityControlPeerTracking(models.Model):
    _name = 'quality.control.peer.tracking'
    _description = 'Quality Control Peer Tracking'

    quality_control_peer_tracking_id = fields.Many2one('quality.control.peer', string='Quality Control Peer Tracking')
    user_id = fields.Many2one('res.users', string='User')
    previous_stage_id = fields.Selection([('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected')],
                             default="preparer", string="Previous Stage")
    new_stage_id = fields.Selection([('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected')],
                                 default="preparer", string="New Stage")
    comment = fields.Text(string='Comment')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
