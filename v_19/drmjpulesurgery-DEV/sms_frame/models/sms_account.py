# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
import base64
from odoo.exceptions import UserError
import requests
class SmsAccount(models.Model):
    _name = "sms.account"
    _description = "SMS Account"

    name = fields.Char(string='Account Name', required=True)
    account_gateway_id = fields.Many2one('sms.gateway', string="Account Gateway", required=True)
    gateway_model = fields.Char(string="Gateway Model", related="account_gateway_id.gateway_model_name")
    company_id = fields.Many2one('res.company', string="Company")

    def send_message(self, from_number, to_number, sms_content, my_model_name='', my_record_id=0, media=None, queued_sms_message=None):
        """Send a message from this account"""
        return self.env[self.gateway_model].send_message(self.id, from_number, to_number, sms_content, my_model_name, my_record_id, media, queued_sms_message)

    @api.model
    def check_all_messages(self):
        """Check for any messages that might have been missed during server downtime"""
        my_accounts = self.env['sms.account'].search([])

        for sms_account in my_accounts:
            self.env[sms_account.account_gateway_id.gateway_model_name].check_messages(sms_account.id)

    def test_sms_connection(self):
        try:
            authorization_key = self.client_id + ':' + self.secret_key
            encoded_key = authorization_key.encode("utf-8")
            autho_header = 'Basic ' + str(base64.b64encode(encoded_key))[2:-1]
            headers = {'Authorization': str(autho_header), 'Content-Type': 'application/json'}
            
            response = requests.request("GET", self.authentication_url, headers=headers)
            message = _("Connection Test Successful!")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as error:
            message = _("Connection Failed!")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'danger',
                    'sticky': False,
                }
            }
            