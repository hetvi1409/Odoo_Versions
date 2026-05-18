from odoo import fields, models, _


class Region(models.Model):
    _inherit = 'regions'

    user_ids = fields.Many2many('res.users', string='Mangers',)

    def action_open_property(self):
        """Open a property"""
        property = self.env['building'].search([('region_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property',
            'view_mode': 'list,form',
            'res_model': 'building',
            'domain': [('id', 'in', property.ids)],
        }
