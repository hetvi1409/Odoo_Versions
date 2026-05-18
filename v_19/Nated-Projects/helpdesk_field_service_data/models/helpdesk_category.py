from odoo import fields, models


class HelpdeskCategory(models.Model):
    """Helpdesk Category"""
    _name = 'helpdesk.category'
    _description = 'Helpdesk category'

    name = fields.Char(string="Name", help="Name of the category",
                       required=True)
    department_id = fields.Many2one('helpdesk.department', string="Department",
                                    required=True)
