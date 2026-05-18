from odoo import api, fields, models
from odoo.fields import Command, Domain


class Building(models.Model):
    _inherit = "building"

    stand_number = fields.Char(string="Stand Number")
    title_deed_number = fields.Char('Title Deed Number')
    jmc_number = fields.Char(
        string="JMC Number",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: ('New')
    )

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submitted for Approval'),
         ('free', 'Available'),
         ('reserved', 'In-Progress'),
         ('on_lease', 'Leased'),
         ('disposed', 'Disposed'),
         ('sold', 'Sold'),
         ('blocked', 'Blocked'), ('reject', 'Rejected')
         ], 'State', default='draft')
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
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        domain = Domain(domain or Domain.TRUE)
        # first search only by login, then the normal search
        if (
            name and not operator in Domain.NEGATIVE_OPERATORS
            and (records := self.search_fetch((Domain('jmc_number', '=', name) | Domain('stand_number', '=', name) )& domain, ['display_name']))
        ):
            return [(records.id, records.display_name)]
        return super().name_search(name, domain, operator, limit)

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #
    #     if name:
    #         recs = self.search(
    #             [('name', operator, name)] + (args or []), limit=limit)
    #         if not recs:
    #             recs = self.search(
    #                 [('jmc_number', operator, name)] + (args or []),
    #                 limit=limit)
    #         if not recs:
    #             recs = self.search(
    #                 [('stand_number', operator, name)] + (args or []),
    #                 limit=limit)
    #         # return recs.name_get()
    #     return recs




