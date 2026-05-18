from odoo import fields, models


class HelpdeskCategory(models.Model):
    """Helpdesk Category"""
    _name = 'helpdesk.sub.category'
    _description = 'Helpdesk category'

    name = fields.Char(string="Name", help="Name of the category",
                       required=True)
    category_id = fields.Many2one('helpdesk.category', string="Category", required=True)
    department_id = fields.Many2one('helpdesk.department', string="Department",
                                    required=True, related="category_id.department_id")
