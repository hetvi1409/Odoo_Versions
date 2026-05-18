
from odoo import models, fields

class ApprovalConfig(models.Model):
    _inherit = 'approval.config'
    
    committee = fields.Boolean('Committee Approval')