from odoo import api, fields, models


class Category(models.Model):
    """City"""
    _name = 'helpdesk.category'
    _description = "Category"

    name = fields.Char(string="Category", required=True)
    team_id = fields.Many2one('helpdesk.team')
    sub_category_ids = fields.One2many('helpdesk.sub.category', 'category_id', string="Sub-Category")


class SubCategory(models.Model):
    """City"""
    _name = 'helpdesk.sub.category'
    _description = "Sub Category"

    name = fields.Char(string="Sub Category", required=True)
    category_id = fields.Many2one('helpdesk.category', domain="[('team_id', '=?', team_id)]", required=True)
    team_id = fields.Many2one('helpdesk.team')

    @api.onchange('category_id')
    def _onchange_category_id(self):
        """Update team id based on category"""
        if self.category_id:
            self.team_id = self.category_id.team_id if self.category_id else ""

    def action_get_sub_category(self, id):
        """Sub-Category"""
        return self.search_read([('category_id', '=', int(id))], ['id', 'name'])