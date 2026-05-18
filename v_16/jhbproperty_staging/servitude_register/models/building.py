from odoo import fields, models, _


class Building(models.Model):
    _inherit = 'building'

    servitude_ids = fields.Many2many('servitude.register', string="Servitude Register")

    def action_view_servitude(self):
        """View servitude"""
        servitude = self.servitude_ids
        action = {
            'name': _('Servitude Register'),
            'type': 'ir.actions.act_window',
            'res_model': servitude._name,
            'context': {'create': False},
        }
        if len(servitude) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': servitude.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', servitude.ids)],
            })
        return action
