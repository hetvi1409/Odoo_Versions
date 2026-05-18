from odoo import api, fields, models, _, modules
import requests
import json
import logging
import base64
from odoo.osv import expression
import re
from odoo import tools
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
import json
from requests.structures import CaseInsensitiveDict
from odoo.exceptions import ValidationError

class mailChannel(models.Model):
    _inherit = 'mail.channel'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *, message_type='notification', **kwargs):
        if self.channel_type == 'multi_livechat_NAMEs':
            if kwargs.get('attachment_ids'):
                message_type = "comment"
        message = super(mailChannel, self).message_post(**kwargs)
        param = self.env['res.config.settings'].sudo().get_values()
        if not self._context.get('from_odoobot'):
            if self.channel_type == 'multi_livechat_NAMEs':
                if kwargs.get('attachment_ids'):
                    message.write({"message_type": "comment"})
                    # self.upload_image(message.attachment_ids, message.body)
                if param.get('use_chat_api'):
                    self.send_whatsapp_message(self.chat_partner, kwargs, message)
                else:
                    if kwargs.get('attachment_ids'):
                        message.write({"message_type": "comment"})
                        self.upload_image(self.chat_partner, message.attachment_ids, message.body)
                    else:
                        self.send_whatsapp_meta_message(kwargs, message.body)
                sent_channel_exist = self.env['mail.channel'].sudo().search([('name', '=', 'Sent messages'),('channel_type', '=', 'multi_livechat_sent_channel')], limit=1)
                if not sent_channel_exist:
                    image_path = modules.get_module_resource('pragtech_whatsapp_messenger', 'static/img', 'whatsapp_logo.png')
                    image = base64.b64encode(open(image_path, 'rb').read())
                    whatsapp_chat_ids = self.env.ref('pragtech_whatsapp_messenger.group_whatsapp_chat')
                    whatsapp_chat_users_ids = whatsapp_chat_ids.sudo().users
                    whatsapp_partner_ids = whatsapp_chat_users_ids.mapped('partner_id')
                    partner_list = []
                    for whatsapp_chat_partner_id in whatsapp_partner_ids:
                        partner_list.append(whatsapp_chat_partner_id.id)
                    # partner_list.append(partner.id)
                    sent_channel = self.env['mail.channel'].sudo().create({
                            'name': 'Sent messages',
                            'channel_partner_ids': [(6, 0, partner_id) for partner_id in partner_list],
                            'channel_type': 'multi_livechat_sent_channel',
                            'is_chat': True,
                            # 'public': 'public',
                            'image_128': image,
                        })
                    sent_channel.message_post(body=kwargs.get('body'), message_type="notification", subtype_xmlid="mail.mt_comment", author_id=self.env.user.partner_id.id)
                else:
                    sent_channel_exist.message_post(body=kwargs.get('body'), message_type="notification", subtype_xmlid="mail.mt_comment", author_id=self.env.user.partner_id.id)
        # if self.channel_type == 'multi_livechat_NAME':
        #     self.send_whatsapp_message(self.channel_partner_ids, kwargs, message)
        return message

    def convert_email_from_to_name(self, str1):
        result = re.search('"(.*)"', str1)
        return result.group(1)

    def custom_html2plaintext(self, html):
        html = re.sub('<br\s*/?>', '\n', html)
        html = re.sub('<.*?>', '', html)
        return html
    
    def send_default_amswer(self, channel_id, message):
        if isinstance(message, str):
            self.browse(channel_id).with_context(from_odoobot=False).message_post(body=message, message_type="notification",
                                                subtype_xmlid="mail.mt_comment")
        else:
            self.browse(channel_id).with_context(from_odoobot=False).message_post(body='', attachment_ids=message, message_type="notification",
                                                subtype_xmlid="mail.mt_comment")
    
    def get_pdf_data(self, report_name, doc_ids):
        report = self.env['ir.actions.report']#._get_report_from_name(report_name)
        context = dict(self.env.context)

        pdf = report.with_context(context)._render_qweb_pdf(report_name, doc_ids)[0]
        pdf = base64.b64encode(pdf).decode()

        return pdf
    
    def upload_pdf(self, caption, report_name, doc_ids, channel_id):
        data = self.get_pdf_data(report_name, doc_ids)
        # data_base64 = base64.b64encode(data)
        msg_attchment_dict = {
            'name': caption,
            'datas': data,
            'type': 'binary',
            'mimetype': 'application/pdf',
            'res_model': 'mail.channel',
            'res_id': 4
        }
        attachment = self.env['ir.attachment'].sudo().create(msg_attchment_dict)

        download_url = "/report/download"
        self.browse(channel_id).with_context(from_odoobot=False).message_post(attachment_ids=[attachment.id], body='', message_type="comment",
                                                subtype_xmlid="mail.mt_comment")

    def upload_image(self, partner_id, file_data, file_name):
        terminal_log_obj = self.env['terminal.log']
        param = self.env['res.config.settings'].sudo().get_values()
        whatsapp_msg_number = partner_id.mobile
        if whatsapp_msg_number:
            whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "")
            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                '+' + str(partner_id.country_id.phone_code), "")
            recipient_phone_number = "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
        for attachment in file_data:
            if param.get('whatsapp_phone_number') and param.get('whatsapp_meta_token'):       
                phone_id = param.get('whatsapp_phone_number')
                access_token = param.get('whatsapp_meta_token')
                url = "https://graph.facebook.com/v15.0/{}/media".format(phone_id)
                attachment_data = base64.b64decode(attachment.datas)
                
                files2 = {
                    # 'messaging_product': "whatsapp",
                    'file': ( attachment.name, attachment_data, attachment.mimetype, {'Expires': '0'}),
                }
                param = {
                    'messaging_product': "whatsapp"
                }

                headers = {
                # "Content-type": "application/json",
                "Authorization": "Bearer {}".format(access_token)                                                                                                                 
                }
                result = requests.post(url, headers=headers, files=files2, data=param)
                _logger.info("\nJson Response: {}".format(result.json()))
                log_message = "Json Response:{}".format(result.json())
                terminal_log_obj.log_info(log_message)
                if result.status_code == 200 or result.status_code == 201:
                    result_json = result.json()
                    obj_id = result_json["id"]
                    file_type = attachment.mimetype
                    file_type = file_type.split("/")
                    file_type = file_type[0]
                    if file_type == "application":
                        json_data = {
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": partner_id.chatId if not whatsapp_msg_number else recipient_phone_number,
                            "type": "document",
                            "document": {
                                "id": obj_id,
                                "caption": file_name,
                                "filename": attachment.name
                            }
                        }
                    else:
                        json_data = {
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": partner_id.chatId if not whatsapp_msg_number else recipient_phone_number,
                            "type": file_type,
                            file_type: {
                                "id": obj_id,
                            }
                        }
                    
                    new_url = "https://graph.facebook.com/v15.0/{}/messages".format(phone_id)
                    new_result = requests.post(new_url, headers=headers, json=json_data)
                    _logger.info("\nJson Response: {}".format(new_result.json()))
                    log_message = "Json Response:{}".format(new_result.json())
                    terminal_log_obj.log_info(log_message)
                    if new_result.status_code == 200 or new_result.status_code == 201:
                        _logger.info("\nSend attachment successful")
                    else:
                        raise ValidationError(str(new_result.status_code)+" Error occured during upload")
                else:
                    raise ValidationError(str(result.status_code)+" Error in file upload")
                # return result.json
                whatsapp_msg = self.env['whatsapp.messages']
                vals = {
                    'message_body': "attachment",
                    'senderName': self.env.user.partner_id.name,
                    'state': 'sent',
                    'to': self.chat_partner.chatId if not whatsapp_msg_number else recipient_phone_number,
                    'partner_id': self.env.user.partner_id.id,
                    'time': fields.Datetime.now(),
                    'fromMe': True
                }
                whatsapp_msg_id = whatsapp_msg.sudo().create(vals)

    def send_whatsapp_meta_message(self, kwargs, message):
        terminal_log_obj = self.env['terminal.log']
        if self.chat_partner:
            partner_id = self.env['res.partner'].search([('id', '=', self.chat_partner.id)])
            whatsapp_msg_number = partner_id.mobile
            if whatsapp_msg_number:
                whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "")
                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                    '+' + str(partner_id.country_id.phone_code), "")
                recipient_phone_number = "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
            param = self.env['res.config.settings'].sudo().get_values()
            if param.get('whatsapp_phone_number') and param.get('whatsapp_meta_token'):       
                phone_id = param.get('whatsapp_phone_number')
                access_token = param.get('whatsapp_meta_token')
                url = "https://graph.facebook.com/v15.0/{}/messages".format(phone_id)
                req_headers = CaseInsensitiveDict()
                req_headers["Authorization"] = "Bearer "+access_token
                req_headers["Content-Type"] = "application/json"
                data_json = {
                    "messaging_product": "whatsapp",
                    "to": self.chat_partner.chatId if not whatsapp_msg_number else recipient_phone_number,
                    "type": "template",
                    "template": {
                        "name": self.custom_html2plaintext(message),
                        "language": {
                            "code": "en_US"
                        }
                    }
                }
                
                data_json_open = {
                    "messaging_product": "whatsapp",
                    "to": self.chat_partner.chatId if not whatsapp_msg_number else recipient_phone_number,
                    "text": {"body": self.custom_html2plaintext(message)},
                }

                result_window_open = requests.post(url, headers=req_headers, json=data_json)
                _logger.info("\nJson Response: {}".format(result_window_open.json()))
                log_message = "Json Response:{}".format(result_window_open.json())
                terminal_log_obj.log_info(log_message)
                if result_window_open.status_code == 200 or result_window_open.status_code == 201:
                    _logger.info("\nSend template message successful")
                else:
                    result = requests.post(url, headers=req_headers, json=data_json_open)
                    _logger.info("\nJson Response: {}".format(result.json()))
                    log_message = "Json Response:{}".format(result.json())
                    terminal_log_obj.log_info(log_message)
                    if result.status_code == 200 or result.status_code == 201:
                        _logger.info("\nSend message successful")
                    else:
                        raise ValidationError(str(result.status_code)+" Error occured, pls try again")
                whatsapp_msg = self.env['whatsapp.messages']
                vals = {
                    'message_body': self.custom_html2plaintext(message),
                    'senderName': self.env['res.partner'].search([('id', '=', kwargs.get('author_id'))]).name if 'author_id' in kwargs else '',
                    'state': 'sent',
                    'to': self.chat_partner.chatId if not whatsapp_msg_number else recipient_phone_number,
                    'partner_id': self.env.user.partner_id.id,
                    'time': fields.Datetime.now(),
                    'fromMe': True
                }
                whatsapp_msg_id = whatsapp_msg.sudo().create(vals)
        else:
            raise ValidationError("No message author")

    def send_whatsapp_message(self, partner_ids, kwargs, message_id):
        terminal_log_obj = self.env['terminal.log']
        if 'author_id' in kwargs and kwargs.get('author_id'):
            partner_id = self.env['res.partner'].search([('id', '=', kwargs.get('author_id'))])
            param = self.env['res.config.settings'].sudo().get_values()
            no_phone_partners = []
            invalid_whatsapp_number_partner = []
            if param.get('whatsapp_endpoint') and param.get('whatsapp_token'):
                status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
                status_response = requests.get(status_url)
                json_response_status = json.loads(status_response.text)
                if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status['accountStatus'] == 'authenticated':
                    if partner_id.country_id.phone_code and partner_id.mobile:
                        whatsapp_msg_number = partner_id.mobile
                        whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "")
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                            '+' + str(partner_id.country_id.phone_code), "")
                        phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get('whatsapp_token') + '&phone=' + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        phone_exists_response = requests.get(phone_exists_url)
                        json_response_phone_exists = json.loads(phone_exists_response.text)
                        if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and json_response_phone_exists['result'] == 'exists':
                            _logger.info("\nPartner phone exists")
                            url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                            headers = {"Content-Type": "application/json"}
                            html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))

                            if kwargs.get('email_from'):
                                if '<' in kwargs.get('email_from') and '>' in kwargs.get('email_from'):
                                    tmp_dict = {
                                        "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": self.convert_email_from_to_name(kwargs.get('email_from'))+''+ str(self.id) + ': '+ html_to_plain_text
                                    }
                                else:
                                    tmp_dict = {
                                        "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": kwargs.get('email_from')+ '' + str(self.id) + ': ' + html_to_plain_text
                                    }
                            else:
                                tmp_dict = {
                                    "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                    "body": html_to_plain_text
                                }
                            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                            _logger.info("\nJson Response: {}".format(response.json()))
                            log_message = "Json Response:{}".format(response.json())
                            terminal_log_obj.log_info(log_message)
                            if response.status_code == 201 or response.status_code == 200:
                                _logger.info("\nSend Message successfully")
                                response_dict = response.json()
                                message_id.with_context({'from_odoobot': True}).write({'whatsapp_message_id': response_dict.get('id')})
                            if message_id.attachment_ids:
                                for attachment in message_id.attachment_ids:
                                    with open(attachment._full_path(attachment.store_fname), 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        url_send_file = param.get(
                                            'whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": "+" + str(
                                                partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file,
                                                                           json.dumps(dict_send_file),
                                                                           headers=headers_send_file)
                                        _logger.info("\nJson Response: {}".format(response_send_file.json()))
                                        log_message = "Json Response:{}".format(response_send_file.json())
                                        terminal_log_obj.log_info(log_message)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info("\nSend file attachment successfully11")
                        else:
                            invalid_whatsapp_number_partner.append(partner_id.name)
                    else:
                        no_phone_partners.append(partner_id.name)
                else:
                    raise UserError(_('Please authorize your mobile number with chat api'))
            if len(invalid_whatsapp_number_partner) >= 1:
                raise UserError(_('Please add valid whatsapp number for %s customer')% ', '.join(invalid_whatsapp_number_partner))
        else:
            param = self.env['res.config.settings'].sudo().get_values()
            no_phone_partners = []
            invalid_whatsapp_number_partner = []
            for partner_id in partner_ids:
                if param.get('whatsapp_endpoint') and param.get('whatsapp_token'):
                    status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
                    status_response = requests.get(status_url)
                    json_response_status = json.loads(status_response.text)
                    if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
                        'accountStatus'] == 'authenticated':
                        if partner_id.country_id.phone_code and partner_id.mobile:
                            whatsapp_msg_number = partner_id.mobile
                            whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "")
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(partner_id.country_id.phone_code), "")
                            phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get(
                                'whatsapp_token') + '&phone=' + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                            phone_exists_response = requests.get(phone_exists_url)
                            json_response_phone_exists = json.loads(phone_exists_response.text)
                            if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and \
                                    json_response_phone_exists['result'] == 'exists':
                                _logger.info("\nPartner phone exists")
                                url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                                headers = {"Content-Type": "application/json"}
                                html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))
                                if kwargs.get('email_from'):
                                    if '<' in kwargs.get('email_from') and '>' in kwargs.get('email_from'):
                                        tmp_dict = {
                                            "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": self.convert_email_from_to_name(kwargs.get('email_from')) + '' + str(
                                                self.id) + ': ' + html_to_plain_text
                                        }
                                    else:
                                        tmp_dict = {
                                            "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": kwargs.get('email_from') + '' + str(self.id) + ': ' + html_to_plain_text
                                        }
                                else:
                                    tmp_dict = {
                                        "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": html_to_plain_text
                                    }
                                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                                _logger.info("Json Response: {}".format(response.json()))
                                log_message = "Json Response:{}".format(response.json())
                                terminal_log_obj.log_info(log_message)
                                if response.status_code == 201 or response.status_code == 200:
                                    _logger.info("\nSend Message successfully")
                                    response_dict = response.json()
                                    message_id.with_context({'from_odoobot': True}).write({'whatsapp_message_id': response_dict.get('id')})
                                if message_id.attachment_ids:
                                    Param = self.env['res.config.settings'].sudo().get_values()
                                    for attachment in message_id.attachment_ids:
                                        # with open(attachment._full_path(attachment.store_fname), 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        url_send_file = param.get(
                                            'whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": "+" + str(
                                                partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file,
                                                                           json.dumps(dict_send_file),
                                                                           headers=headers_send_file)
                                        _logger.info("\nJson Response: {}".format(response_send_file.json()))
                                        log_message = "Json Response:{}".format(response_send_file.json())
                                        terminal_log_obj.log_info(log_message)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info("\nSend file attachment successfully11")
                            else:
                                invalid_whatsapp_number_partner.append(partner_id.name)
                        else:
                            no_phone_partners.append(partner_id.name)
                    else:
                        raise UserError(_('Please authorize your mobile number with chat api'))

        if len(invalid_whatsapp_number_partner) >= 1:
            raise UserError(
                _('Please add valid whatsapp number for %s customer') % ', '.join(invalid_whatsapp_number_partner))

    def add_members(self, partner_ids=None, guest_ids=None, invite_to_rtc_call=False, open_chat_window=False, post_joined_message=True):
        """ Adds the given partner_ids and guest_ids as member of self channels. """
        self.check_access_rights('write')
        self.check_access_rule('write')
        current_partner = self.env['res.partner']
        current_guest = self.env['mail.guest']
        guest = self.env['mail.guest']._get_guest_from_context()
        if self.env.user._is_public() and guest:
            current_guest = guest
        else:
            current_partner = self.env.user.partner_id
        partners = self.env['res.partner'].browse(partner_ids or []).exists()
        guests = self.env['mail.guest'].browse(guest_ids or []).exists()
        notifications = []
        for channel in self:
            members_to_create = []
            if channel.group_public_id:
                invalid_partners = partners.filtered(lambda partner: channel.group_public_id not in partner.user_ids.groups_id)
                if invalid_partners:
                    raise UserError(_(
                        'Channel "%(channel_name)s" only accepts members of group "%(group_name)s". Forbidden for: %(partner_names)s',
                        channel_name=channel.name,
                        group_name=channel.group_public_id.name,
                        partner_names=', '.join(partner.name for partner in invalid_partners)
                    ))
                if guests:
                    raise UserError(_(
                        'Channel "%(channel_name)s" only accepts members of group "%(group_name)s". Forbidden for: %(guest_names)s',
                        channel_name=channel.name,
                        group_name=channel.group_public_id.name,
                        guest_names=', '.join(guest.name for guest in guests)
                    ))
            existing_members = self.env['mail.channel.member'].search(expression.AND([
                [('channel_id', '=', channel.id)],
                expression.OR([
                    [('partner_id', 'in', partners.ids)],
                    [('guest_id', 'in', guests.ids)]
                ])
            ]))
            members_to_create += [{
                'partner_id': partner.id,
                'channel_id': channel.id,
            } for partner in partners - existing_members.partner_id]
            members_to_create += [{
                'guest_id': guest.id,
                'channel_id': channel.id,
            } for guest in guests - existing_members.guest_id]
            new_members = self.env['mail.channel.member'].sudo().create(members_to_create)
            for member in new_members.filtered(lambda member: member.partner_id):
                # notify invited members through the bus
                user = member.partner_id.user_ids[0] if member.partner_id.user_ids else self.env['res.users']
                if user:
                    notifications.append((member.partner_id, 'mail.channel/joined', {
                        'channel': member.channel_id.with_user(user).with_context(allowed_company_ids=user.company_ids.ids).sudo().channel_info()[0],
                        'invited_by_user_id': self.env.user.id,
                        'open_chat_window': open_chat_window,
                    }))

                if post_joined_message:
                    # notify existing members with a new message in the channel
                    if member.partner_id == self.env.user.partner_id:
                        notification = _('<div class="o_mail_notification">joined the channel</div>')
                    else:
                        notification = _(
                            '<div class="o_mail_notification">invited %s to the channel</div>',
                            member.partner_id._get_html_link(),
                        )
                    # member.channel_id.message_post(body=notification, message_type="notification", subtype_xmlid="mail.mt_comment")
            for member in new_members.filtered(lambda member: member.guest_id):
                # member.channel_id.message_post(body=_('<div class="o_mail_notification">joined the channel</div>'), message_type="notification", subtype_xmlid="mail.mt_comment")
                guest = member.guest_id
                if guest:
                    notifications.append((guest, 'mail.channel/joined', {
                        'channel': member.channel_id.sudo().channel_info()[0],
                    }))
            notifications.append((channel, 'mail.channel/insert', {
                'channelMembers': [('insert', list(new_members._mail_channel_member_format().values()))],
                'id': channel.id,
                'memberCount': channel.member_count,
            }))
            if existing_members:
                # If the current user invited these members but they are already present, notify the current user about their existence as well.
                # In particular this fixes issues where the current user is not aware of its own member in the following case:
                # create channel from form view, and then join from discuss without refreshing the page.
                notifications.append((current_partner or current_guest, 'mail.channel/insert', {
                    'channelMembers': [('insert', list(existing_members._mail_channel_member_format().values()))],
                    'id': channel.id,
                    'memberCount': channel.member_count,
                }))
        if invite_to_rtc_call:
            for channel in self:
                current_channel_member = self.env['mail.channel.member'].sudo().search([('channel_id', '=', channel.id), ('partner_id', '=', current_partner.id), ('guest_id', '=', current_guest.id)])
                if current_channel_member and current_channel_member.rtc_session_ids:
                    current_channel_member._rtc_invite_members(member_ids=new_members.ids)
        self.env['bus.bus']._sendmany(notifications)

    def _action_unfollow(self, partner):
        self.message_unsubscribe(partner.ids)
        if partner not in self.with_context(active_test=False).channel_partner_ids:
            return True
        channel_info = self.channel_info()[0]  # must be computed before leaving the channel (access rights)
        member = self.env['mail.channel.member'].search([('channel_id', '=', self.id), ('partner_id', '=', partner.id)])
        member_id = member.id
        member.unlink()
        # side effect of unsubscribe that wasn't taken into account because
        # channel_info is called before actually unpinning the channel
        channel_info['is_pinned'] = False
        self.env['bus.bus']._sendone(partner, 'mail.channel/leave', channel_info)
        notification = _('<div class="o_mail_notification">left the channel</div>')
        # post 'channel left' message as root since the partner just unsubscribed from the channel
        # self.sudo().message_post(body=notification, subtype_xmlid="mail.mt_comment", author_id=partner.id)
        self.env['bus.bus']._sendone(self, 'mail.channel/insert', {
            'channelMembers': [('insert-and-unlink', {'id': member_id})],
            'id': self.id,
            'memberCount': self.member_count,
        })

    chat_partner = fields.Many2one('res.partner')

    channel_type = fields.Selection(selection_add=[("multi_livechat_NAMEs", "Whatsapp Chats")], ondelete={"multi_livechat_NAMEs": "cascade"})
    whatsapp_meta_id = fields.Char('Whatsapp phone id')
