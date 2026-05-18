from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ConversationConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def set_values(self):
        res = super(ConversationConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('pragmatic_odoo_whatsapp_integration.activate_facebook', self.activate_facebook)
        self.env['ir.config_parameter'].set_param('pragmatic_odoo_whatsapp_integration.activate_whatsapp',
                                                  self.activate_whatsapp)
        self.env['ir.config_parameter'].set_param('pragmatic_odoo_whatsapp_integration.whatsapp_client_id',
                                                  self.whatsapp_client_id)
        self.env['ir.config_parameter'].set_param('pragmatic_odoo_whatsapp_integration.whatsapp_client_secret',
                                                  self.whatsapp_client_secret)
        self.env['ir.config_parameter'].set_param('pragmatic_odoo_whatsapp_integration.activate_instagram',
                                                  self.activate_instagram)
        return res

    @api.model
    def get_values(self):
        res = super(ConversationConfigSettings, self).get_values()
        activate_facebook = self.env['ir.config_parameter'].sudo().get_param('pragmatic_odoo_whatsapp_integration.activate_facebook')
        activate_whatsapp = self.env['ir.config_parameter'].sudo().get_param(
            'pragmatic_odoo_whatsapp_integration.activate_whatsapp')
        whatsapp_client_id = self.env['ir.config_parameter'].sudo().get_param(
            'pragmatic_odoo_whatsapp_integration.whatsapp_client_id')
        whatsapp_client_secret = self.env['ir.config_parameter'].sudo().get_param(
            'pragmatic_odoo_whatsapp_integration.whatsapp_client_secret')
        activate_instagram = self.env['ir.config_parameter'].sudo().get_param(
            'pragmatic_odoo_whatsapp_integration.activate_instagram')
        res.update(
            activate_facebook=activate_facebook,
            activate_whatsapp=activate_whatsapp,
            whatsapp_client_id=whatsapp_client_id,
            whatsapp_client_secret=whatsapp_client_secret,
            activate_instagram=activate_instagram,
        )
        return res

    @api.model
    def default_get(self, fields):
        # installed_modules = self.env['ir.module.module'].search([('state', '=', 'installed')])
        result = super(ConversationConfigSettings, self).default_get(fields)
        facebook = self.env['ir.module.module'].search([('name', '=', 'pragtech_facebook_messenger')])
        whatsapp = self.env['ir.module.module'].search([('name', '=', 'pragtech_whatsapp_messenger')])

        if not facebook or facebook.state != 'installed':
            result['facebook_installed'] = False
        else:
            result['facebook_installed'] = True

        if not whatsapp or whatsapp.state != 'installed':
            result['whatsapp_installed'] = False
        else:
            result['whatsapp_installed'] = True
        return result

    """@api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        installed_modules = self.env['ir.module.module'].search([('state', '=', 'installed')])
        ret_val = super(ConversationConfigSettings, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            installed_modules = self.env['ir.module.module'].search([('state', '=', 'installed')])
            facebook = self.env['ir.module.module'].search([('name', '=', 'pragtech_facebook_messenger')])
            for record in self:
                if not facebook or facebook.state != 'installed':
                    record.facebook_installed = False
                else:
                    record.facebook_installed = True
        return ret_val"""
    facebook_installed = fields.Boolean(string="Facebook Install state")
    activate_facebook = fields.Boolean(string="Facebook")
    # facebook_app_id = fields.Char(string='App ID')
    # facebook_app_secret = fields.Char(string='App Secret')
    whatsapp_installed = fields.Boolean(string="Whatsapp Install state")
    activate_whatsapp = fields.Boolean(string="Whatsapp")
    whatsapp_client_id = fields.Char(string="client id")
    whatsapp_client_secret = fields.Char(string="client secret")
    instagram_installed = fields.Boolean(string="Instagram Install state")
    activate_instagram = fields.Boolean(string="Instagram")
    instagram_id = fields.Char(string="Instagram id")
    instagram_key = fields.Char(string="Instagram key")
    whatsapp_endpoint = fields.Char('Whatsapp Endpoint', help="Whatsapp api endpoint url with instance id")
    whatsapp_token = fields.Char('Whatsapp Token')
    whatsapp_authenticate = fields.Boolean('Authenticate', default=False)
    