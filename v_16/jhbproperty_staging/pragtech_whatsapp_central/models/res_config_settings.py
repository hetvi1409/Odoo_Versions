import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json
import requests


class base(models.TransientModel):
    _inherit = "res.config.settings"

    whatsapp_greeting = fields.Text('Greeting Message')
    whatsapp_ending = fields.Text('Ending Message')

    whatsapp_integrators = fields.Selection([
        ('apichat', 'API Chat'),
        ('chatapi', 'Chat API'),
        ('gupshup', 'GupShup API'),
        ('meta', 'Meta'),
    ], string="Whatsapp Integrators", default='apichat')

    # whatsapp_client = fields.Char('Client', required=True)
    # whatsapp_secret = fields.Char('Secret', required=True)
    whatsapp_authenticate = fields.Boolean('Authenticate', default=False)

    whatsapp_endpoint = fields.Char('Whatsapp Endpoint', help="Whatsapp api endpoint url with instance id")
    whatsapp_token = fields.Char('Whatsapp Token')

    meta_phone_number_id = fields.Char(
        string='Meta Phone Number ID',
    )

    meta_api_token = fields.Char(
        string='Meta API Token',
    )

    meta_webhook = fields.Char(
        string='Meta Webhook Verify Token',
    )

    whatsapp_client = fields.Char('Client')
    whatsapp_secret = fields.Char('Secret')
    starting_message = fields.Char('Initial Message', required=True, default='hello,hi,hey')
    main_menu_prefix = fields.Char('Main Menu Prefix', required=True)
    previous_menu_prefix = fields.Char('Previous Menu Prefix', required=True)
    
    whatsapp_gupshup_api = fields.Char('GupShup Endpoint', help="Whatsapp api endpoint url with instance id")

    @api.onchange('whatsapp_integrators')
    def _onchange_whatsapp_integrators(self):
        if self.whatsapp_integrators:
            whatsapp_helpdesk_messages_records = self.env['whatsapp.helpdesk.messages'].search([])
            for line in whatsapp_helpdesk_messages_records:
                line.integrators = self.whatsapp_integrators

    @api.model
    def get_values(self):
        res = super(base, self).get_values()
        Param = self.env['ir.config_parameter'].sudo()
        res['whatsapp_greeting'] = Param.sudo().get_param('pragtech_whatsapp_central.whatsapp_greeting')
        res['whatsapp_ending'] = Param.sudo().get_param('pragtech_whatsapp_central.whatsapp_ending')
        res['whatsapp_integrators'] = Param.sudo().get_param('pragtech_whatsapp_central.whatsapp_integrators')
        res['whatsapp_client'] = Param.sudo().get_param('pragtech_whatsapp_central.whatsapp_client')
        res['whatsapp_secret'] = Param.sudo().get_param('pragtech_whatsapp_central.whatsapp_secret')

        res['meta_phone_number_id'] = Param.sudo().get_param('pragtech_whatsapp_central.meta_phone_number_id')
        res['meta_api_token'] = Param.sudo().get_param('pragtech_whatsapp_central.meta_api_token')
        res['meta_webhook'] = Param.sudo().get_param('pragtech_whatsapp_central.meta_webhook')

        res['whatsapp_authenticate'] = Param.sudo().get_param('pragtech_whatsapp_central.whatsapp_authenticate')
        res['whatsapp_endpoint'] = Param.sudo().get_param('pragtech_whatsapp_central.whatsapp_endpoint')
        res['whatsapp_token'] = Param.sudo().get_param('pragtech_whatsapp_central.whatsapp_token')

        res['whatsapp_gupshup_api'] = Param.sudo().get_param('pragtech_whatsapp_central.whatsapp_gupshup_api')

        res['starting_message'] = Param.sudo().get_param('pragtech_whatsapp_central.starting_message',
                                                         default='hello,hi,hey')
        res['main_menu_prefix'] = Param.sudo().get_param('pragtech_whatsapp_central.main_menu_prefix', default='*')
        res['previous_menu_prefix'] = Param.sudo().get_param('pragtech_whatsapp_central.previous_menu_prefix',
                                                             default='#')
        return res

    def set_values(self):
        super(base, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.whatsapp_greeting',
                                                         self.whatsapp_greeting)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.whatsapp_ending',
                                                         self.whatsapp_ending)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.whatsapp_integrators',
                                                         self.whatsapp_integrators)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.whatsapp_client',
                                                         self.whatsapp_client)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.whatsapp_secret',
                                                         self.whatsapp_secret)

        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.whatsapp_endpoint',
                                                         self.whatsapp_endpoint)
                                                         
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.whatsapp_gupshup_api',
                                                         self.whatsapp_gupshup_api)

        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.meta_phone_number_id',
                                                         self.meta_phone_number_id)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.meta_api_token',
                                                         self.meta_api_token)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.meta_webhook',
                                                         self.meta_webhook)
                                                         
                                                         
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.whatsapp_token',
                                                         self.whatsapp_token)

        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.starting_message',
                                                         self.starting_message)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.main_menu_prefix',
                                                         self.main_menu_prefix)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_central.previous_menu_prefix',
                                                         self.previous_menu_prefix)


    '''def action_get_qr_code_w_survey(self):
        return {
            'name': _("Scan WhatsApp QR Code"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'whatsapp.survey.scan.qr',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_get_chat_api_qr_code(self):
        return {
            'name': _("Scan WhatsApp Chat API QR Code"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'chat.api.whatsapp.scan.qr',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_chat_api_logout_from_whatsapp(self):
        Param = self.sudo().get_values()
        try:
            url = Param.get('whatsapp_endpoint') + '/logout?token=' + Param.get('whatsapp_token')
            headers = {
                "Content-Type": "application/json",
            }
            tmp_dict = {
                "accountStatus": "Logout request sent to WhatsApp"
            }
            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
            if response.status_code == 201 or response.status_code == 200:
                _logger.info("\nWhatsapp logout successfully")
                self.env['ir.config_parameter'].sudo().set_param(
                    'pragtech_whatsapp_central.whatsapp_authenticate', False)
        except Exception as e_log:
            _logger.exception(e_log)
            raise UserError(_('Please add proper whatsapp endpoint or whatsapp token'))'''
