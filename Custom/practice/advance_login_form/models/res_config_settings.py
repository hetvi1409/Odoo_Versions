
from odoo import api, fields, models, modules, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    login_background_image = fields.Binary(
        string=_('Login Background Image'),
        help=_('Select a background image to display on the login page.')
    )
    background_color = fields.Char(
        string=_('Background Color'),
        config_parameter='advance_login_form.background_color',
        help=_('Set the background color for the login page. Use a valid hex color code (e.g., #FFFFFF for white).')
    )
    text_color = fields.Char(
        string=_('Text Color'),
        config_parameter='advance_login_form.text_color',
        help=_('Set the text color for the login form. Use a valid hex color code.')
    )
    button_color = fields.Char(
        string=_('Button Color'),
        config_parameter='advance_login_form.button_color',
        help=_('Set the color of the login button. Use a valid hex color code.')
    )
    button_hover_color = fields.Char(
        string=_('Button Hover Color'),
        config_parameter='advance_login_form.button_hover_color',
        help=_('Set the color of the login button when hovered. Use a valid hex color code.')
    )
    alignment = fields.Selection([
        ('left', _('Left')),
        ('right', _('Right')),
        ('center', _('Center')),
    ],
        string=_('Form Alignment'),
        default='center',
        config_parameter='advance_login_form.alignment',
        help=_('Choose the alignment for the login form: left, right, or center.')
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            login_background_image=self.env['ir.config_parameter'].sudo(
            ).get_param('advance_login_form.login_background_image')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        set_login_background_image = self.login_background_image or False
        param.set_param('advance_login_form.login_background_image',
                        set_login_background_image)
