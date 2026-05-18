from odoo import models, fields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def action_view_tank_details(self):
        self.ensure_one()

        form_view_ref = self.env.ref('fuel_card_register.fuel_tank_form', False)
        result = self.env['ir.actions.act_window']._for_xml_id(
            'fuel_card_register.fuel_tank_action')
        result.update({
            'views': [(form_view_ref.id, 'form')],
            'context': {
                'default_vehicle_id': self.id,
            },
        })
        return result

    def action_view_card_details(self):
        self.ensure_one()

        form_view_ref = self.env.ref('fuel_card_register.fuel_card_form',
                                     False)
        result = self.env['ir.actions.act_window']._for_xml_id(
            'fuel_card_register.fuel_card_action')
        result.update({
            'views': [(form_view_ref.id, 'form')],
            'context': {
                'default_assigned_vehicle_id': self.id,
            },
        })
        return result
