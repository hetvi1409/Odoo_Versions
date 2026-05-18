from odoo import models, fields, api

class ProjectDashboardLinkWizard(models.TransientModel):
    _name = "project.dashboard.link.wizard"
    _description = "Dashboard Links Wizard"

    link_ids = fields.One2many("project.dashboard.link.line", "wizard_id", "Links")

    @api.model
    def default_get(self, fields_list):
        """Preload wizard with existing saved links"""
        res = super().default_get(fields_list)

        links = self.env["project.dashboard.link"].search([("user_id", "=", self.env.user.id)])
        link_lines = []
        for link in links:
            link_lines.append((0, 0, {
                "name": link.name,
                "url": link.url,
                "icon": link.icon,
            }))

        res["link_ids"] = link_lines
        return res

    def action_save(self):
        # Replace old links for user
        self.env["project.dashboard.link"].search([("user_id", "=", self.env.user.id),("is_default", "=", False)]).unlink()
        for line in self.link_ids:
            self.env["project.dashboard.link"].create({
                "name": line.name,
                "url": line.url,
                "icon": line.icon,
                "user_id": self.env.user.id,
                "is_default": False,
            })
        return {"type": "ir.actions.act_window_close"}


class ProjectDashboardLinkLine(models.TransientModel):
    _name = "project.dashboard.link.line"
    _description = "Dashboard Link Line"

    wizard_id = fields.Many2one("project.dashboard.link.wizard")
    name = fields.Char("Caption", required=True)
    url = fields.Char("Link", required=True)
    icon = fields.Binary("Icon")
