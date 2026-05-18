from odoo import models


class Building(models.Model):
    """Method for building"""
    _inherit = "building"

    # def name_get(self):
    #     res = []
    #     for record in self:
    #         res.append(
    #             (record.id, '%s' % (record.jmc_number)))
    #     return res
    #     if not self.env.context.get('property_jmc_number', True):
    #         return super(Building, self).name_get()
    #     else:
    #         return [(record.id, record.jmc_number) for record in self]
