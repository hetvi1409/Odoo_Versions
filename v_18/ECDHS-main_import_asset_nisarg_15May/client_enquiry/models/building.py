from odoo import api, fields, models


class Building(models.Model):
    _inherit = "building"

    stand_number = fields.Char(string="Stand Number")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search(
                [('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search(
                    [('jmc_number', operator, name)] + (args or []),
                    limit=limit)
            if not recs:
                recs = self.search(
                    [('stand_number', operator, name)] + (args or []),
                    limit=limit)
            return recs.name_get()
        return super(Building, self).name_search(
            name, args=args, operator=operator, limit=limit)
