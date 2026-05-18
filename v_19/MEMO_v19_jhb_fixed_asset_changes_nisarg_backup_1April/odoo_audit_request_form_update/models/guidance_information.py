from odoo import fields, models


class GuidanceInformation(models.Model):
    _name = 'guidance.information'
    _description = "Guidance and Other Information"

    name = fields.Char(string='Name')
    audit_category_id = fields.Many2one('custom.audit.category',
                                        string='Audit Category')
    guidance = fields.Char(string='Guidance')
    information = fields.Char(string='Information')
