from odoo import api, fields, models, _

from odoo.exceptions import UserError


class RentalContract(models.Model):
    _inherit = "rental.contract"

    active = fields.Boolean(default=True, string="Active")

    def action_archive(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise UserError(_("The records cannot be archived. "
                                  "Archiving is only allowed when the record "
                                  "is in the Draft or Cancelled state."))
        return super().action_archive()