from odoo import models, fields


class QualityControlOutsourcedPeerTracking(models.Model):
    _name = 'quality.control.outsourced.peer.tracking'
    _description = 'Quality Control Outsourced Peer Tracking'

    quality_control_outsourced_peer_tracking_id = fields.Many2one('quality.control.outsourced.peer', string='Quality Control Outsourced Peer Tracking')
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
