from odoo import models, fields, api

class ProjectDashboardLink(models.Model):
    _name = "project.dashboard.link"
    _description = "Dashboard Links"

    name = fields.Char("Caption", required=True)
    url = fields.Char("Link", required=True)
    icon = fields.Binary("Icon")  # store uploaded icon
    user_id = fields.Many2one("res.users", "User", default=lambda self: self.env.user)
    group_id = fields.Many2one("res.groups", "User Group")
    is_default = fields.Boolean("Is Default", default=False)
