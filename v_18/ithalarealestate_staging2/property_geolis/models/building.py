from odoo import fields, models


class Property(models.Model):
    _inherit = "building"

    open_map = fields.Boolean('Open Map')

    def action_open_map(self):
        if self.open_map is True:
            self.open_map = False
        else:
            self.open_map = True
