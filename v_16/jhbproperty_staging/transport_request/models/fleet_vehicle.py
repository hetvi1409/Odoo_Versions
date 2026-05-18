from odoo import models, fields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def action_view_request_details(self):
        self.ensure_one()

        tree_view_ref = self.env.ref('transport_request.transport_request_tree',
                                     False)
        form_view_ref = self.env.ref(
            'transport_request.transport_request_form',
            False)
        result = self.env['ir.actions.act_window']._for_xml_id(
            'transport_request.transport_request_action')
        result.update({
            'views': [[tree_view_ref.id, 'list'],[form_view_ref.id, 'form']],
            'context': {
                'default_assigned_vehicle_id': self.id,
            },
            'view_mode': 'list,form',
            'domain': [('assigned_vehicle_id', '=', self.id)],
        })
        return result
