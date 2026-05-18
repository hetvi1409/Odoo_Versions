import logging
import requests
import base64
import json
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class base(models.TransientModel):
    _inherit = "res.config.settings"

    whatsapp_phone_number = fields.Char('Whatsapp Phone number', help="Whatsapp api endpoint url with instance id")
    whatsapp_endpoint = fields.Char('Whatsapp Endpoint Chat-api', help="Whatsapp api endpoint url with instance id")
    whatsapp_token = fields.Char('Whatsapp Token')
    use_chat_api = fields.Boolean(string="Use chat api")
    whatsapp_meta_token = fields.Char('Whatsapp meta Token')
    whatsapp_meta_webhook_token = fields.Char('Webhook verify token')
    module_whatsapp_webhook_verify = fields.Boolean(string="verify webhook", invisible=True)
    use_meta_api = fields.Boolean(string="Use meta api")
    qr_code_image = fields.Binary("QR code")
    whatsapp_authenticate = fields.Boolean('Authenticate', default=False)
    group_enable_signature = fields.Boolean("Add Signature in so?", implied_group='pragtech_whatsapp_messenger.group_enable_signature')
    group_display_chatter_message = fields.Boolean("Add in chatter message so?",implied_group='pragtech_whatsapp_messenger.group_display_chatter_message')
    group_order_product_details_msg = fields.Boolean("Add Order product details in message so?",implied_group='pragtech_whatsapp_messenger.group_order_product_details_msg')
    group_order_info_msg = fields.Boolean("Add Order information in message so?",implied_group='pragtech_whatsapp_messenger.group_order_info_msg')

    group_purchase_enable_signature = fields.Boolean("Add Signature in po?", implied_group='pragtech_whatsapp_messenger.group_purchase_enable_signature')
    group_purchase_display_chatter_message = fields.Boolean("Add in chatter message po?", implied_group='pragtech_whatsapp_messenger.group_purchase_display_chatter_message')
    group_purchase_order_product_details_msg = fields.Boolean("Add Order product details in message po?",
                                                            implied_group='pragtech_whatsapp_messenger.group_purchase_order_product_details_msg')
    group_purchase_order_info_msg = fields.Boolean("Add Order information in message po?", implied_group='pragtech_whatsapp_messenger.group_purchase_order_info_msg')
    group_stock_enable_signature = fields.Boolean("Add Signature in do?", implied_group='pragtech_whatsapp_messenger.group_stock_enable_signature')
    group_stock_display_chatter_message = fields.Boolean("Add in chatter message do?",
                                                            implied_group='pragtech_whatsapp_messenger.group_stock_display_chatter_message')
    group_stock_product_details_msg = fields.Boolean("Add order product details in message do?",
                                                              implied_group='pragtech_whatsapp_messenger.group_stock_product_details_msg')
    group_stock_info_msg = fields.Boolean("Add order information in message do?", implied_group='pragtech_whatsapp_messenger.group_stock_info_msg')
    group_invoice_enable_signature = fields.Boolean("Add Signature in invoice?", implied_group='pragtech_whatsapp_messenger.group_invoice_enable_signature')
    group_invoice_display_chatter_message = fields.Boolean("Add in chatter message invoice?",
                                                         implied_group='pragtech_whatsapp_messenger.group_invoice_display_chatter_message')
    group_invoice_product_details_msg = fields.Boolean("Add order product details in message invoice?",
                                                     implied_group='pragtech_whatsapp_messenger.group_invoice_product_details_msg')
    group_invoice_info_msg = fields.Boolean("Add order information in message invoice?", implied_group='pragtech_whatsapp_messenger.group_invoice_info_msg')

    group_crm_display_chatter_message = fields.Boolean("Add in chatter message crm?",
                                                           implied_group='pragtech_whatsapp_messenger.group_crm_display_chatter_message')
    group_crm_enable_signature = fields.Boolean("Add Signature in crm?", implied_group='pragtech_whatsapp_messenger.group_crm_enable_signature')

    group_project_display_chatter_message = fields.Boolean("Add in chatter message in project?",
                                                       implied_group='pragtech_whatsapp_messenger.group_project_display_chatter_message')
    group_project_enable_signature = fields.Boolean("Add Signature in project?", implied_group='pragtech_whatsapp_messenger.group_project_enable_signature')

    @api.model
    def get_values(self):
        res = super(base, self).get_values()
        Param = self.env['ir.config_parameter'].sudo()
        res['use_chat_api'] = Param.sudo().get_param('pragtech_whatsapp_messenger.use_chat_api')
        res['whatsapp_phone_number'] = Param.sudo().get_param('pragtech_whatsapp_messenger.whatsapp_phone_number')
        res['whatsapp_endpoint'] = Param.sudo().get_param('pragtech_whatsapp_messenger.whatsapp_endpoint')
        res['whatsapp_token'] = Param.sudo().get_param('pragtech_whatsapp_messenger.whatsapp_token')
        res['use_meta_api'] = Param.sudo().get_param('pragtech_whatsapp_messenger.use_meta_api')
        res['whatsapp_meta_token'] = Param.sudo().get_param('pragtech_whatsapp_messenger.whatsapp_meta_token')
        res['whatsapp_meta_webhook_token'] = Param.sudo().get_param('pragtech_whatsapp_messenger.whatsapp_meta_webhook_token')
        res['module_whatsapp_webhook_verify'] = Param.sudo().get_param('pragtech_whatsapp_messenger.module_whatsapp_webhook_verify')
        res['whatsapp_authenticate'] = Param.sudo().get_param('pragtech_whatsapp_messenger.whatsapp_authenticate')
        res['group_enable_signature'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_enable_signature')
        res['group_display_chatter_message'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_display_chatter_message')
        res['group_order_product_details_msg'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_order_product_details_msg')
        res['group_order_info_msg'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_order_info_msg')
        res['group_purchase_enable_signature'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_purchase_enable_signature')
        res['group_purchase_display_chatter_message'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_purchase_display_chatter_message')
        res['group_purchase_order_product_details_msg'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_purchase_order_product_details_msg')
        res['group_purchase_order_info_msg'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_purchase_order_info_msg')
        res['group_stock_enable_signature'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_stock_enable_signature')
        res['group_stock_display_chatter_message'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_stock_display_chatter_message')
        res['group_stock_product_details_msg'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_stock_product_details_msg')
        res['group_stock_info_msg'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_stock_info_msg')
        res['group_invoice_enable_signature'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_invoice_enable_signature')
        res['group_invoice_display_chatter_message'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_invoice_display_chatter_message')
        res['group_invoice_product_details_msg'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_invoice_product_details_msg')
        res['group_invoice_info_msg'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_invoice_info_msg')
        res['group_crm_enable_signature'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_crm_enable_signature')
        res['group_crm_display_chatter_message'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_crm_display_chatter_message')
        res['group_project_enable_signature'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_project_enable_signature')
        res['group_project_display_chatter_message'] = Param.sudo().get_param('pragtech_whatsapp_messenger.group_project_display_chatter_message')
        res.update(qr_code_image=Param.sudo().get_param('pragtech_whatsapp_messenger.qr_code_image'))
        return res

    def set_values(self):
        super(base, self).set_values()
        if self.whatsapp_endpoint:
            if (self.whatsapp_endpoint)[-1] == '/':
                self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.whatsapp_endpoint', (self.whatsapp_endpoint)[:-1])
            else:
                self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.whatsapp_endpoint', self.whatsapp_endpoint)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.use_chat_api', self.use_chat_api)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.whatsapp_phone_number', self.whatsapp_phone_number)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.whatsapp_token', self.whatsapp_token)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.use_meta_api', self.use_meta_api)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.whatsapp_meta_token', self.whatsapp_meta_token)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.whatsapp_meta_webhook_token', self.whatsapp_meta_webhook_token)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.module_whatsapp_webhook_verify', self.module_whatsapp_webhook_verify)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_enable_signature', self.group_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_display_chatter_message', self.group_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_order_product_details_msg', self.group_order_product_details_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_order_info_msg', self.group_order_info_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_purchase_enable_signature', self.group_purchase_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_purchase_display_chatter_message', self.group_purchase_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_purchase_order_product_details_msg', self.group_purchase_order_product_details_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_purchase_order_info_msg', self.group_purchase_order_info_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_stock_enable_signature', self.group_stock_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_stock_display_chatter_message', self.group_stock_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_stock_product_details_msg',
                                                         self.group_stock_product_details_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_stock_info_msg', self.group_stock_info_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_invoice_enable_signature', self.group_invoice_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_invoice_display_chatter_message', self.group_invoice_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_invoice_product_details_msg',
                                                         self.group_invoice_product_details_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_invoice_info_msg', self.group_invoice_info_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_crm_enable_signature', self.group_crm_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_crm_display_chatter_message', self.group_crm_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_project_enable_signature', self.group_project_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.group_project_display_chatter_message', self.group_project_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.qr_code_image', self.qr_code_image)

    def action_get_qr_code(self):
        return {
            'name': _("Scan WhatsApp QR Code"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'whatsapp.scan.qr',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_logout_from_whatsapp(self):
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
                self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_messenger.whatsapp_authenticate', False)
        except Exception as e_log:
            _logger.exception(e_log)
            raise UserError(_('Please add proper whatsapp endpoint or whatsapp token'))
