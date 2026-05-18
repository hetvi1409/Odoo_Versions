
from odoo import models, fields

class ScsCluster(models.Model):
    _name = 'scs.cluster'
    _description = 'SCM Competency Cluster'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    code = fields.Char(help='Cluster code, e.g., 1..13')
    sequence = fields.Integer(default=10)
    competency_ids = fields.One2many('scs.competency', 'cluster_id', string='Competencies')
