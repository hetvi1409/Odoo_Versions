from odoo import models, fields

class ApproverRole(models.Model):
    _name = "approver.role"
    _description = "Approver Role"

    name = fields.Char("Role Name", required=True)
