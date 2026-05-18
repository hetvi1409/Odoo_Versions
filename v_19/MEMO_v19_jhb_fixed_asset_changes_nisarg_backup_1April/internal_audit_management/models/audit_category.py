from odoo import fields, models


class AuditAssignmentCategory(models.Model):
    """Audit Assignment Category model"""
    _name = "audit.assignment.category"
    _description = "Stores the categories or disciplines for audit assignments"

    name = fields.Char(string="Name", help="Name of the audit assignment")
