# -*- coding: utf-8 -*-

import json
import requests
from odoo import fields, models, _
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)


class ScanWAQRCode(models.TransientModel):
    _name = 'whatsapp.survey.scan.qr'
    _description = 'Scan WhatsApp QR Code'

    def _get_default_image(self):
        Param = self.env['res.config.settings'].sudo().get_values()
        headers = {
            "client-id": Param.get('whatsapp_client'),
            "token": Param.get('whatsapp_secret')}
        url = 'https://api.apichat.io/v1/status'
        response = requests.get(url, headers=headers)
        json_response = json.loads(response.text)
        if not json_response.get('is_connected'):
            a = json_response.get('qr').split('data:image/png;base64,')
            img = a[1]
            return img

    def _check_status(self):
        Param = self.env['res.config.settings'].sudo().get_values()
        headers = {
            "client-id": Param.get('whatsapp_client'),
            "token": Param.get('whatsapp_secret')}
        url = 'https://api.apichat.io/v1/status'
        response = requests.get(url, headers=headers)
        json_response = json.loads(response.text)
        if json_response.get('is_connected'):
            return True
        else:
            return False

    qr_code_img_data = fields.Binary(default=_get_default_image)
    check_status = fields.Boolean(default=_check_status)

    def action_disconnect(self):
        Param = self.env['res.config.settings'].sudo().get_values()
        headers = {
            "client-id": Param.get('whatsapp_client'),
            "token": Param.get('whatsapp_secret')}
        url = 'https://api.apichat.io/v1/logout'
        requests.post(url, headers=headers)
        self.check_status = False
        return {'type': 'ir.actions.client', 'tag': 'reload'}


class ScanChatApiWAQRCode(models.TransientModel):
    _name = 'chat.api.whatsapp.scan.qr'
    _description = 'Scan WhatsApp QR Code'

    def _get_default_image(self):

        Param = self.env['res.config.settings'].sudo().get_values()
        Param_set = self.env['ir.config_parameter'].sudo()
        try:
            url = Param.get('whatsapp_endpoint') + '/status?token=' + Param.get('whatsapp_token')
            response = requests.get(url)
        except Exception as e_log:
            _logger.exception(e_log)
            raise UserError(_('Please add proper whatsapp endpoint or whatsapp token'))
        json_response = json.loads(response.text)
        if response.status_code == 201 or response.status_code == 200:
            # qr_code_image
            if json_response.get('accountStatus') == 'got qr code':
                qr_code_url = Param.get('whatsapp_endpoint') + '/qr_code?token=' + Param.get('whatsapp_token')
                response_qr_code = requests.get(qr_code_url)
                img = base64.b64encode(response_qr_code.content)
                Param_set.set_param("pragmatic_odoo_whatsapp_integration.whatsapp_authenticate", True)
                return img
            elif json_response.get('accountStatus') == 'authenticated':
                raise UserError(_('QR code is already scanned from chat api'))
        elif response.status_code > 200:
            raise UserError(_('There is issue in chat api'))

    qr_code_img_data = fields.Binary(default=_get_default_image)
