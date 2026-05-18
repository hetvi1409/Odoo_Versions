from odoo import api, fields, models


class Building(models.Model):
    _inherit = "building"

    stand_number = fields.Char(string="Stand Number")
    zoning_id = fields.Many2one('property.zoning', string="Zoning")
    #
    # def name_get(self):
    #     name_list = []
    #
    #     for rec in self:
    #         name = rec.name
    #         if rec._context.get('jmc_field_value') == True:
    #             name = rec.jmc_number
    #
    #         name_list += [(rec.id, name)]
    #     return name_list


        # result = []
        # # for node in self:
        # #     name = "{}{}".format(node.parent_id and node.parent_id.name_get()[0][1] + "/" or "", node.name)
        # #     result.append((node.id, name))
        # return result



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




