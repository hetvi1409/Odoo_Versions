from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    home_icon_count = fields.Integer(string="Column count", default=6)
    home_icon_size = fields.Integer(string="Icon size", default=70)
    home_font_size_multiplier = fields.Integer(string="Text size", default=100)
    home_icon_spacing = fields.Integer(string="Icon inner spacing", default=10)
    home_icon_margin = fields.Integer(string="Icon margin", default=16)
    home_icon_radius = fields.Float(string="Corner radius", default=17.1428571)
    home_top_margin = fields.Integer(string="Top margin", default=48)
    home_fit_to_screen_width = fields.Boolean(string="Fit to screen width", default=False)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            'home_icon_count',
            'home_icon_size',
            'home_font_size_multiplier',
            'home_icon_spacing',
            'home_icon_margin',
            'home_icon_radius',
            'home_top_margin',
            'home_fit_to_screen_width',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            'home_icon_count',
            'home_icon_size',
            'home_font_size_multiplier',
            'home_icon_spacing',
            'home_icon_margin',
            'home_icon_radius',
            'home_top_margin',
            'home_fit_to_screen_width',
        ]

    def action_update_home_customizer_settings(self, vals):
        self.ensure_one()
        if self.id != self.env.user.id:
            return False
        
        allowed_fields = [
            'home_icon_count', 'home_icon_size', 'home_font_size_multiplier',
            'home_icon_spacing', 'home_icon_margin', 'home_icon_radius',
            'home_top_margin', 'home_fit_to_screen_width'
        ]
        filtered_vals = {k: v for k, v in vals.items() if k in allowed_fields}
        
        return self.sudo().write(filtered_vals)

    @api.model
    def get_home_customizer_settings(self):
        user = self.env.user
        return {
            'home_icon_count': user.home_icon_count,
            'home_icon_size': user.home_icon_size,
            'home_font_size_multiplier': user.home_font_size_multiplier,
            'home_icon_spacing': user.home_icon_spacing,
            'home_icon_margin': user.home_icon_margin,
            'home_icon_radius': user.home_icon_radius,
            'home_top_margin': user.home_top_margin,
            'home_fit_to_screen_width': user.home_fit_to_screen_width,
        }

    @api.model
    def update_home_customizer_settings(self, vals):
        user = self.env.user
        allowed_fields = [
            'home_icon_count', 'home_icon_size', 'home_font_size_multiplier',
            'home_icon_spacing', 'home_icon_margin', 'home_icon_radius',
            'home_top_margin', 'home_fit_to_screen_width'
        ]
        filtered_vals = {k: v for k, v in vals.items() if k in allowed_fields}
        return user.sudo().write(filtered_vals)