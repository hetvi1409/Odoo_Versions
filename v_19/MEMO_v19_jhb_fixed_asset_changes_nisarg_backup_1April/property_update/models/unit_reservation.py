from odoo import fields, models, _
from odoo.exceptions import UserError


class UnitReservation(models.Model):
    """Class for change the field's parameter."""
    _inherit = 'unit.reservation'

    building_unit = fields.Many2one('product.template', 'Building Unit',
                                    domain=[('is_property', '=', True),
                                            ('state', '=', 'free')],
                                    required=False)
    building= fields.Many2one('building','Building',
                              domain=[('state', '=', 'free')], required=True)

    def action_confirm(self):
        """Overwrite this function to change the property state."""
        res = super().action_confirm()
        self.building.write({'state': 'reserved'})
        return res

    def unlink(self):
        """Overwrite this method to solve the error when deleting the record."""
        for rec in self:
            if rec.state !='draft':
                raise UserError(_('You can not delete a reservation not in '
                                  'draft state'))
        super().unlink()

    def action_cancel(self):
        res = super().action_cancel()
        self.building.write({'state':  'free'})
        return res