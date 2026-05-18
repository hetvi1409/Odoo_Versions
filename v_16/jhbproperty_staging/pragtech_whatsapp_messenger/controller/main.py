import base64
import datetime
import json
import logging
import time
import werkzeug.urls
import werkzeug.utils
from werkzeug.exceptions import BadRequest
import phonenumbers
import pytz
import requests
from odoo import http, _, modules
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home # SIGN_UP_REQUEST_PARAMS
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import ustr
from odoo.http import request, JsonRPCDispatcher, Response
from requests.structures import CaseInsensitiveDict
from werkzeug.urls import url_join
from odoo.addons.pragtech_whatsapp_base.controller.main import WhatsappBase

_logger = logging.getLogger(__name__)
from odoo.addons.phone_validation.tools import phone_validation

def _json_response_inherit(self, result=None, error=None):
    response = ''
    if error is not None:
        response = error
    if result is not None:
        response = result
    mime = 'application/json'
    # body = json.dumps(response, default=date_utils.json_default)
    body = ''

    return Response(
        body, status=error and error.pop('http_status', 200) or 200,
        headers=[('Content-Type', mime), ('Content-Length', len(body))]
    )


class SendMessage(http.Controller):
    _name = 'send.message.controller'

    def format_amount(self, amount, currency):
        fmt = "%.{0}f".format(currency.decimal_places)
        lang = http.request.env['res.lang']._lang_get(http.request.env.context.get('lang') or 'en_US')

        formatted_amount = lang.format(fmt, currency.round(amount), grouping=True, monetary=True) \
            .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')
        pre = post = u''
        if currency.position == 'before':
            pre = u'{symbol}\N{NO-BREAK SPACE}'.format(symbol=currency.symbol or '')
        else:
            post = u'\N{NO-BREAK SPACE}{symbol}'.format(symbol=currency.symbol or '')
        return u'{pre}{0}{post}'.format(formatted_amount, pre=pre, post=post)

    @http.route('/whatsapp/send/message', type='http', auth='public', website=True, csrf=False)
    def sale_order_paid_status(self, **post):
        pos_order = http.request.env['pos.order'].sudo().search([('pos_reference', '=', post.get('order'))])
        user_context = pos_order.env.context.copy()
        user_context.update({'lang': pos_order.partner_id.lang})
        pos_order.env.context = user_context

        context = request.env.context.copy()
        context.update({'lang': pos_order.partner_id.lang})
        request.env.context = context

        if pos_order.partner_id:
            if pos_order.partner_id.mobile and pos_order.partner_id.country_id.phone_code:
                doc_name = 'POS'
                msg = _("Hello") + " " + pos_order.partner_id.name
                if pos_order.partner_id.parent_id:
                    msg += "(" + pos_order.partner_id.parent_id.name + ")"
                msg += "\n\n" + _("Your") + " "
                msg += doc_name + " *" + pos_order.name + "* "
                msg += " " + _("with Total Amount") + " " + self.format_amount(pos_order.amount_total, pos_order.pricelist_id.currency_id) + "."
                msg += "\n\n" + _("Following is your order details.")
                for line_id in pos_order.lines:
                    msg += "\n\n*" + _("Product") + ":* " + line_id.product_id.name + "\n*" + _("Qty") + ":* " + str(line_id.qty) + " " + "\n*" + _(
                        "Unit Price") + ":* " + str(line_id.price_unit) + "\n*" + _("Subtotal") + ":* " + str(line_id.price_subtotal)
                    msg += "\n------------------"
                Param = http.request.env['res.config.settings'].sudo().get_values()
                whatsapp_number = pos_order.partner_id.mobile
                whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(pos_order.partner_id.country_id.phone_code),
                                                                                             "")
                phone_exists_url = Param.get('whatsapp_endpoint') + '/checkPhone?token=' + Param.get(
                    'whatsapp_token') + '&phone=' + str(pos_order.partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                phone_exists_response = requests.get(phone_exists_url)
                json_response_phone_exists = json.loads(phone_exists_response.text)
                if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and \
                        json_response_phone_exists['result'] == 'exists':
                    url = Param.get('whatsapp_endpoint') + '/sendMessage?token=' + Param.get('whatsapp_token')
                    headers = {"Content-Type": "application/json"}
                    tmp_dict = {
                        "phone": "+" + str(pos_order.partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                        "body": msg}
                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                    if response.status_code == 201 or response.status_code == 200:
                        _logger.info("\nSend Message successfully")
                        return "Send Message successfully"
                elif json_response_phone_exists.get('result') == 'not exists':
                    return "Phone not exists on whatsapp"
                else:
                    return json_response_phone_exists.get('error')


class AuthSignupHomeDerived(AuthSignupHome):

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""
        get_param = request.env['ir.config_parameter'].sudo().get_param
        countries = request.env['res.country'].sudo().search([])
        return {
            'signup_enabled': request.env['res.users']._get_signup_invitation_scope() == 'b2c',
            'reset_password_enabled': get_param('auth_signup.reset_password') == 'True',
            'countries': countries
        }

    # def get_auth_signup_qcontext(self):
    #     SIGN_UP_REQUEST_PARAMS.add('mobile')
    #     qcontext = super().get_auth_signup_qcontext()
    #     return qcontext

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'mobile', 'country_id')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()


class Whatsapp(WhatsappBase):

    def convert_epoch_to_unix_timestamp(self, msg_time):
        try:
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(msg_time)))
        except:
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(msg_time)/1000))
        date_time_obj = datetime.datetime.strptime(formatted_time, '%Y-%m-%d %H:%M:%S')
        dt = False
        if date_time_obj:
            timezone = pytz.timezone(request.env['res.users'].sudo().browse([int(2)]).tz or 'UTC')
        dt = pytz.UTC.localize(date_time_obj)
        dt = dt.astimezone(timezone)
        dt = ustr(dt).split('+')[0]
        return date_time_obj

    def get_profile_data(self, psid, page_access_token):
        url = 'https://graph.facebook.com/v15.0/{}/whatsapp_business_profile?fields=about,address,description,email,profile_picture_url,websites,vertical'.format(psid)
        headers = {
            "Authorization": "Bearer {}".format(page_access_token)
            }
        try:
            response = requests.get(url, headers=headers)
            return response.json()
        except:
            pass

    @http.route(['/whatsapp_meta/response/message'], type='http', auth='public', methods=['GET', 'POST'], website=True,
                csrf=False)
    def whatsapp_meta_webhook(self):
        _logger.info("In whatsapp integration controller")
        super(Whatsapp, self).whatsapp_meta_webhook()
        if request.httprequest.method == 'GET':
            try:
                if request.httprequest.method == 'GET':
                    facebook_verify_token = request.env['ir.config_parameter'].sudo().get_param(
                        'pragtech_whatsapp_messenger.whatsapp_meta_webhook_token')
                    # facebook_verify_token = "abcdef"
                    VERIFY_TOKEN = facebook_verify_token

                    if 'hub.mode' in request.httprequest.args:
                        mode = request.httprequest.args.get('hub.mode')

                    if 'hub.verify_token' in request.httprequest.args:
                        token = request.httprequest.args.get('hub.verify_token')

                    if 'hub.challenge' in request.httprequest.args:
                        challenge = request.httprequest.args.get('hub.challenge')

                    if 'hub.mode' in request.httprequest.args and 'hub.verify_token' in request.httprequest.args:
                        mode = request.httprequest.args.get('hub.mode')
                        token = request.httprequest.args.get('hub.verify_token')

                        if mode == 'subscribe' and token == VERIFY_TOKEN:

                            challenge = request.httprequest.args.get('hub.challenge')

                            return http.Response(challenge, status=200)
                        else:
                            return http.Response('ERROR', status=403)

                    test_json = {'names': 'Test name', 'email': 'Test email', 'phone': 'Test phone', 'ID': 'test ID'}
                    test_json = json.loads(test_json)

                    return http.Response(test_json, status=200)  # 'SOMETHING', 200
            except TypeError:
                return http.local_redirect('/web', query=request.params, keep_hash=True)
        elif request.httprequest.method == 'POST':
            data = request.httprequest.data
            whatapp_msg = request.env['whatsapp.messages']
            body = json.loads(data.decode('utf-8'))
            _logger.info("Data In whatsapp integration controller %s", str(body))

            if "messages" in body["entry"][0]["changes"][0]["value"]:
                sender = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
                mobile = '+' + sender
                mobile_coutry_code = phonenumbers.parse(mobile, None)
                mobile_number = mobile_coutry_code.national_number
                country_code = mobile_coutry_code.country_code
                res_country_id = request.env['res.country'].sudo().search([('phone_code', '=', country_code)], limit=1)
                reg_sanitized_number = phone_validation.phone_format(str(mobile_number), res_country_id.code, country_code)

                if 'text' in body["entry"][0]["changes"][0]["value"]["messages"][0]:
                    message = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
                timestamp = body["entry"][0]["changes"][0]["value"]["messages"][0]["timestamp"]
                time_var = self.convert_epoch_to_unix_timestamp(int(timestamp))
                facebook_page_access = request.env['ir.config_parameter'].sudo().get_param(
                                'pragtech_whatsapp_messenger.whatsapp_meta_token')
                profile_data = self.get_profile_data(sender, facebook_page_access)
                if profile_data:
                    if 'profile_picture_url' in profile_data:
                        profile_pic = profile_data['profile_picture_url']
                        profile_pic = profile_pic.replace("\\", "")
                        data_base64 = base64.b64encode(requests.get(profile_pic.strip()).content)

                partner_exists = request.env["res.partner"].sudo().search(
                    [('name', '=', body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]),
                     ('chatId', '=', sender)])
                if not partner_exists:
                    partner_exists = request.env["res.partner"].sudo().search([('mobile', '=', mobile)])
                if not partner_exists:
                    partner_exists = request.env["res.partner"].sudo().search([('mobile', '=', reg_sanitized_number)])

                if partner_exists:
                    if 'profile_picture_url' in profile_data:
                        partner_exists.write({'image_1920': data_base64})

                if not partner_exists:
                    if 'profile_picture_url' in profile_data:
                        if res_country_id:
                            partner = request.env["res.partner"].sudo().create(
                                {'name': body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"],
                                 'chatId': sender, 'mobile': mobile, 'country_id': res_country_id.id,
                                 'image_1920': data_base64})
                        else:
                            partner = request.env["res.partner"].sudo().create(
                                {'name': body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"],
                                 'chatId': sender, 'mobile': mobile, 'image_1920': data_base64})
                    else:
                        if res_country_id:
                            partner = request.env["res.partner"].sudo().create(
                                {'name': body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"],
                                 'chatId': sender, 'mobile': mobile, 'country_id': res_country_id.id})
                        else:
                            partner = request.env["res.partner"].sudo().create(
                                {'name': body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"],
                                 'chatId': sender, 'mobile': mobile})
                else:
                    partner = partner_exists

                if 'text' in body["entry"][0]["changes"][0]["value"]["messages"][0] and \
                        body["entry"][0]["changes"][0]["value"]["messages"][0]["type"] == "text":
                    if message != '':
                        msg_dict = {
                            'name': message,
                            'message_id': 'None',
                            'to': 'To Me',
                            'chatId': sender,
                            'type': body["entry"][0]["changes"][0]["value"]["messages"][0]["type"],
                            'senderName': sender,
                            'chatName': partner.name,
                            'author': partner.name,
                            'time': datetime.datetime.now(),
                            'state': 'received',
                        }
                        try:
                            res_whatsapp_msg = whatapp_msg.sudo().create(msg_dict)
                        except:
                            pass
                        self.send_notification_to_admin_meta(partner, message)

                else:
                    attachment_type = body["entry"][0]["changes"][0]["value"]["messages"][0]["type"]
                    attachments_body = body["entry"][0]["changes"][0]["value"]["messages"][0][attachment_type]

                    self.send_attachment_to_admin(partner, attachments_body)
            elif "statuses" in body["entry"][0]["changes"][0]["value"]:
                status = body["entry"][0]["changes"][0]["value"]['statuses'][0]['status']
                sender = body["entry"][0]["changes"][0]["value"]["statuses"][0]["recipient_id"]
                mobile = '+' + sender
                mobile_coutry_code = phonenumbers.parse(mobile, None)
                mobile_number = mobile_coutry_code.national_number
                country_code = mobile_coutry_code.country_code
                res_country_id = request.env['res.country'].sudo().search([('phone_code', '=', country_code)], limit=1)
                reg_sanitized_number = phone_validation.phone_format(str(mobile_number), res_country_id.code, country_code)
                partner_exists = request.env["res.partner"].sudo().search(
                    [('chatId', '=', sender)])
                if not partner_exists:
                    partner_exists = request.env["res.partner"].sudo().search([('mobile', '=', mobile)])
                if not partner_exists:
                    partner_exists = request.env["res.partner"].sudo().search([('mobile', '=', reg_sanitized_number)])

                messages = request.env['whatsapp.messages'].sudo().search([('to', '=', mobile), ('fromMe', '=', True)], order="time desc")
                if messages:
                    for message in messages:
                        # message.sudo().write({'msg_status': status})
                        if message.msg_status != 'read' and status == 'delivered':
                            message.sudo().write({'msg_status': status, 'is_delivered': True, 'time_delivered': datetime.datetime.now()})
                        if message.msg_status != 'read' and status == 'read':
                            message.sudo().write({'msg_status': status, 'is_read': True, 'time_read': datetime.datetime.now()})
                    # if status == "sent":
                    #     message.sudo().write({'is_sent': True, 'time_sent': datetime.datetime.now()})
                    # elif status == "delivered":
                    #     message.sudo().write({'is_delivered': True, 'time_delivered': datetime.datetime.now()})
                    if status == "read":
                        # message.sudo().write({'is_read': True, 'time_read': datetime.datetime.now()})
                        channel = request.env['mail.channel'].sudo().search([('channel_type', '=', 'multi_livechat_NAMEs'), ('name', '=', 'Chat with {}'.format(partner_exists.name))])
                        if channel:
                            for message in channel.message_ids:
                                if message.message_seen == False:
                                    message.sudo().write({'message_seen': True})
                                    request.env['bus.bus'].sudo()._sendone(channel.chat_partner.id, 'mail.message/toggle_star', {
                                        'message_ids': message.ids,
                                        'starred': True,
                                    })
                                # notif_create_values = [{
                                #     'mail_message_id': message.id,
                                #     'res_partner_id': channel.chat_partner.id,
                                #     'is_read': True,  # discard Inbox notification
                                #     'notification_status': 'sent',
                                #     'failure_type': '',
                                # } for message in channel.message_ids]
                                notif_create_values = request.env['mail.notification'].sudo().search([('res_partner_id', '=', channel.chat_partner.id), ('is_read', '=', False), ('mail_message_id', '=', message.id)])
                                if notif_create_values:
                                    notif_create_values.write({'is_read': True})
                                    



    @http.route(['/whatsapp/responce/message'], type='json', auth='public')
    def whatsapp_responce(self):
        _logger.info("In whatsapp integration controller")
        data = json.loads(request.httprequest.data)
        _logger.info("data %s: ", str(data))
        _request = data
        if 'messages' in data and data['messages']:
            msg_list = []
            msg_dict = {}
            res_partner_obj = request.env['res.partner']
            whatapp_msg = request.env['whatsapp.messages']
            mail_channel_obj = request.env['mail.channel']
            mail_message_obj = request.env['mail.message']
            project_task_obj = request.env['project.task']
            for msg in data['messages']:
                if 'quotedMsgId' in msg and msg['quotedMsgId'] and '@g.us' in msg['chatId']:
                    project_task_id = project_task_obj.sudo().search([('whatsapp_msg_id', '=', msg['quotedMsgId'])])
                    if 'chatId' in msg and msg['chatId']:
                        chat_id = msg['chatId']
                        chatid_split = chat_id.split('@')
                        if len(chatid_split[0]) > 14:
                            number_change = chatid_split[0].split('-')
                            mobile = '+'+number_change[0]
                        else:
                            mobile = '+' + chatid_split[0]
                        mobile_coutry_code = phonenumbers.parse(mobile, None)
                        mobile_number = mobile_coutry_code.national_number
                        country_code = mobile_coutry_code.country_code
                        res_country_id = request.env['res.country'].sudo().search([('phone_code', '=', country_code)], limit=1)
                        reg_sanitized_number = phone_validation.phone_format(str(mobile_number), res_country_id.code, country_code)
                        res_partner_obj = res_partner_obj.sudo().search([('mobile', '=', reg_sanitized_number)], limit=1)
                        mail_message_id = mail_message_obj.sudo().search([('whatsapp_message_id', '=', msg['quotedMsgId'])], limit=1)
                        if mail_message_id.model == 'mail.channel' and mail_message_id.res_id:
                            channel_id = mail_channel_obj.sudo().search([('id', '=', mail_message_id.res_id)])
                            channel_id.with_context(from_odoobot=True).message_post(body=msg['body'], message_type="notification",
                                                                                    subtype_xmlid="mail.mt_comment", author_id=res_partner_obj.id)
                            mail_message_id.with_context(from_odoobot=True)
                    if project_task_id:
                        if msg.get('body') == 'done' or msg.get('body') == 'Done':
                            task_type_done_id = request.env['project.task.type'].sudo().search([('name', '=', 'Done')], limit=1)
                            if task_type_done_id:
                                project_task_update_rec = project_task_id.sudo().write({'stage_id': task_type_done_id.id})
                elif 'chatId' in msg and msg['chatId']:
                    if '@c.us' in msg['chatId']:  # @c.us is for contacts & @g.us is for group
                        res_partner_obj = res_partner_obj.sudo().search([('chatId', '=', msg['chatId'])], limit=1)
                        msg_dict = {
                            'name': msg['body'],
                            'message_id': msg['id'],
                            'fromMe': msg['fromMe'],
                            'to': msg['chatName'] if msg['fromMe'] == True else 'To Me',
                            'chatId': msg['chatId'],
                            'type': msg['type'],
                            'senderName': msg['senderName'],
                            'chatName': msg['chatName'],
                            'author': msg['author'],
                            'time': self.convert_epoch_to_unix_timestamp(msg['time']),
                            'state': 'sent' if msg['fromMe'] == True else 'received',
                        }
                        if res_partner_obj:

                            if msg['type'] == 'image' and res_partner_obj:
                                url = msg['body']
                                image_data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                                msg_dict.update({
                                    'message_body': msg['caption'],
                                    'msg_image': image_data,
                                    'partner_id': res_partner_obj.id,

                                })
                            if res_partner_obj and msg['type'] == 'chat' or msg['type'] == 'video' or msg['type'] == 'audio':
                                msg_dict.update({'message_body': msg['body'], 'partner_id': res_partner_obj.id})
                            if msg['type'] == 'document' and res_partner_obj:
                                msg_dict.update({'message_body': msg['caption'], 'partner_id': res_partner_obj.id})

                        else:
                            chat_id = msg['chatId']
                            chatid_split = chat_id.split('@')
                            if len(chatid_split[0]) > 14:
                                change_number = chatid_split[0].split('-')
                                mobile = '+'+change_number[0]
                            else:
                                mobile = '+' + chatid_split[0]
                            mobile_coutry_code = phonenumbers.parse(mobile, None)
                            mobile_number = mobile_coutry_code.national_number
                            res_partner_obj = res_partner_obj.sudo().search([('mobile', '=', mobile_number)], limit=1)
                            if not res_partner_obj:
                                mobile_coutry_code = phonenumbers.parse(mobile, None)
                                mobile_number = mobile_coutry_code.national_number
                                country_code = mobile_coutry_code.country_code
                                mobile = '+' + str(country_code) + ' ' + str(mobile_number)
                                res_partner_obj = res_partner_obj.sudo().search([('mobile', '=', mobile)], limit=1)
                            if not res_partner_obj:
                                mobile_coutry_code = phonenumbers.parse(mobile, None)
                                res_country_id = request.env['res.country'].sudo().search([('phone_code', '=', country_code)], limit=1)
                                reg_sanitized_number = phone_validation.phone_format(str(mobile_number), res_country_id.code, country_code)
                                res_partner_obj = res_partner_obj.sudo().search([('mobile', '=', reg_sanitized_number)], limit=1)
                            if res_partner_obj:
                                res_partner_obj.chatId = chat_id
                                msg_dict.update({
                                    'message_body': msg['body'],
                                    'partner_id': res_partner_obj.id,
                                })
                            else:
                                res_partner_dict = {}
                                if msg.get('senderName'):
                                    res_partner_dict['name'] = msg.get('senderName')
                                elif msg.get('chatName'):
                                    res_partner_dict['name'] = msg.get('chatName')
                                res_country_id = request.env['res.country'].sudo().search([('phone_code', '=', mobile_coutry_code.country_code)],
                                                                                          limit=1)
                                if res_country_id:
                                    res_partner_dict['country_id'] = res_country_id.id
                                res_partner_dict['mobile'] = mobile
                                res_partner_dict['chatId'] = chat_id
                                #res_partner_dict['user_id'] = request.env.user
                                res_partner_id = request.env['res.partner'].sudo().create(res_partner_dict)
                                if res_partner_id:
                                    msg_dict.update({'partner_id': res_partner_id.id})
                                    if msg['type'] == 'chat':
                                        msg_dict.update({'message_body': msg['body']})
                                    if msg['type'] == 'document' or msg['type'] == 'image' or msg['type'] == 'video' or msg['type'] == 'audio':
                                        if msg['type'] == 'video' or msg['type'] == 'audio':
                                            msg_dict.update({'message_body': msg.get('body')})
                                        elif msg['type'] == 'image':
                                            url = msg['body']
                                            image_data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                                            msg_dict.update({'msg_image': image_data})
                                        else:
                                            msg_dict.update({'message_body': msg.get('caption')})

                        if res_partner_obj or res_partner_id:
                            partner = False
                            if res_partner_obj:
                                partner = res_partner_obj
                            elif res_partner_id:
                                partner = res_partner_id

                            self.send_notification_to_admin(partner, msg)

                        _logger.info("msg_dict %s: ", str(msg_dict))
                        if len(msg_dict) > 0:
                            msg_list.append(msg_dict)
            for msg in msg_list:
                whatapp_msg_id = whatapp_msg.sudo().search([('message_id', '=', msg.get('message_id'))])
                if whatapp_msg_id:
                    whatapp_msg_id.sudo().write(msg)
                    _logger.info("whatapp_msg_id %s: ", str(whatapp_msg_id))
                    if 'messages' in data and data['messages']:
                        for msg in data['messages']:
                            if whatapp_msg_id and msg['type'] == 'document':
                                msg_attchment_dict = {}
                                url = msg['body']
                                data_base64 = base64.b64encode(requests.get(url.strip()).content)
                                msg_attchment_dict = {'name': msg['caption'], 'datas': data_base64, 'type': 'binary',
                                                      'res_model': 'whatsapp.messages', 'res_id': whatapp_msg_id.id}
                                attachment_id = request.env['ir.attachment'].sudo().create(msg_attchment_dict)
                                res_update_whatsapp_msg = whatapp_msg_id.sudo().write({'attachment_id': attachment_id.id})
                                _logger.info("res_update_whatsapp_msg %s: ", str(res_update_whatsapp_msg))
                else:
                    res_whatsapp_msg = whatapp_msg.sudo().create(msg)
                    _logger.info("res_whatsapp_msg2111 %s: ", str(res_whatsapp_msg))
                    if 'messages' in data and data['messages']:
                        for msg in data['messages']:
                            if res_whatsapp_msg and msg['type'] == 'document':
                                msg_attchment_dict = {}
                                url = msg['body']
                                data_base64 = base64.b64encode(requests.get(url.strip()).content)
                                msg_attchment_dict = {'name': msg['caption'], 'datas': data_base64, 'type': 'binary',
                                                      'res_model': 'whatsapp.messages', 'res_id': res_whatsapp_msg.id}
                                attachment_id = request.env['ir.attachment'].sudo().create(msg_attchment_dict)
                                res_update_whatsapp_msg = res_whatsapp_msg.sudo().write({'attachment_id': attachment_id.id})
                                _logger.info("res_update_whatsapp_msg %s: ", str(res_update_whatsapp_msg))

        elif 'ack' in data:
            status = data["ack"][0]["status"]
            chat_id = data["ack"][0]["chatId"]
            if '@' in chat_id:
                chatid_split = chat_id.split('@')
                if len(chatid_split[0]) > 14:
                    number_change = chatid_split[0].split('-')
                    mobile = number_change[0]
                else:
                    mobile = chatid_split[0]
            else:
                mobile = chat_id
            message = request.env['whatsapp.messages'].sudo().search([('to', '=', mobile)], order="time desc", limit=1)
            if message:
                message.sudo().write({'msg_status': status})
                if status == "sent":
                    message.sudo().write({'is_sent': True, 'time_sent': datetime.datetime.now()})
                elif status == "delivered":
                    message.sudo().write({'is_delivered': True, 'time_delivered': datetime.datetime.now()})
                elif status == "read":
                    message.sudo().write({'is_read': True, 'time_read': datetime.datetime.now()})
                    channel = request.env['mail.channel'].sudo().search([('channel_type', '=', 'multi_livechat_NAMEs'), ('name', '=', 'Chat with {}'.format(mobile))])
                    if channel:
                        for message in channel.message_ids:
                            message.sudo().write({'message_seen': True})
                            notif_create_values = request.env['mail.notification'].sudo().search([('res_partner_id', '=', channel.chat_partner.id), ('is_read', '=', False), ('mail_message_id', '=', message.id)])
                            if notif_create_values:
                                notif_create_values.write({'is_read': True})

        ir_module_module_id = request.env['ir.module.module'].sudo().search([('name', '=', 'pragmatic_odoo_whatsapp_marketing'),
                                                                             ('state', '=', 'installed')])
        if ir_module_module_id:
            self.whatsapp_marketing_bidirectional_message(data)
        else:
            return 'OK'

    def whatsapp_marketing_bidirectional_message(self, data):
        if 'messages' in data and data['messages']:
            msg_dict = {}
            whatsapp_contact_obj = request.env['whatsapp.contact']
            whatsapp_group_obj = request.env['whatsapp.group']
            whatapp_msg = request.env['whatsapp.messages']
            for msg in data['messages']:
                if 'chatId' in msg and msg['chatId']:
                    whatsapp_contact_obj = whatsapp_contact_obj.sudo().search([('whatsapp_id', '=', msg['chatId'])], limit=1)
                    whatsapp_group_obj = whatsapp_group_obj.sudo().search([('group_id', '=', msg['chatId'])], limit=1)
                    if whatsapp_contact_obj:
                        msg_dict = {'whatsapp_contact_id': whatsapp_contact_obj.id}
                    if whatsapp_group_obj:
                        msg_dict = {'whatsapp_group_id': whatsapp_group_obj.id}
                    if len(msg_dict) > 0:
                        whatapp_msg_id = whatapp_msg.sudo().search([('message_id', '=', msg['id'])])
                        if whatapp_msg_id:
                            whatapp_msg_id.sudo().write(msg_dict)
        return 'OK'

    def send_notification_to_admin(self, partner, msg):
        mail_channel_obj = request.env['mail.channel']
        whatsapp_chat_ids = request.env.ref('pragtech_whatsapp_messenger.group_whatsapp_chat')
        whatsapp_chat_users_ids = whatsapp_chat_ids.sudo().users
        whatsapp_partner_ids = whatsapp_chat_users_ids.mapped('partner_id')
        admin_partner = request.env['res.partner'].sudo().search([('id', '=', 3)])

        if partner:
            incoming_channel_exist = mail_channel_obj.sudo().search([('name', '=', 'Incoming messages'),('channel_type', '=', 'multi_livechat_sent_channel')], limit=1)
            if not incoming_channel_exist:
                image_path = modules.get_module_resource('pragtech_whatsapp_messenger', 'static/img', 'whatsapp_logo.png')
                image = base64.b64encode(open(image_path, 'rb').read())
                partner_list = []
                for whatsapp_chat_partner_id in whatsapp_partner_ids:
                    partner_list.append(whatsapp_chat_partner_id.id)
                partner_list.append(partner.id)
                incoming_channel = mail_channel_obj.sudo().create({
                        'name': 'Incoming messages',
                        'channel_partner_ids': [(6, 0, partner_id) for partner_id in partner_list],
                        'channel_type': 'multi_livechat_sent_channel',
                        'is_chat': True,
                        # 'public': 'public',
                        'image_128': image,
                    })
                if not msg['fromMe']:
                    incoming_channel.with_context(from_odoobot=True).message_post(body=msg['body'],
                                                                            message_type="notification",
                                                                            subtype_xmlid="mail.mt_comment",
                                                                            author_id=partner.id)
            else:
                if not msg['fromMe']:
                    incoming_channel_exist.with_context(from_odoobot=True).message_post(body=msg['body'],
                                                                            message_type="notification",
                                                                            subtype_xmlid="mail.mt_comment",
                                                                            author_id=partner.id)
                                                                            
            channel_exist = mail_channel_obj.sudo().search([('name', '=', 'Chat with {}'.format(partner.name))], limit=1)
            if channel_exist:
                # if msg['fromMe']:
                #     channel_exist.with_context(from_odoobot=True).message_post(body=msg['body'],
                #                                                                message_type="notification",
                #                                                                subtype_xmlid="mail.mt_comment",
                #                                                                author_id=whatsapp_partner_ids.id)
                if not msg['fromMe']:
                    if msg['type'] != 'chat':
                        msg_attchment_dict = {}
                        url = msg['body']
                        data_base64 = base64.b64encode(requests.get(url.strip()).content)
                        msg_attchment_dict = {'name': msg['senderName'], 'datas': data_base64, 'type': 'binary',
                                              'res_model': 'mail.channel', 'res_id': channel_exist.id}
                        attachment_id = request.env['ir.attachment'].sudo().create(msg_attchment_dict)
                        channel_exist.with_context(from_odoobot=True).message_post(body=msg['body'], attachment_ids=[attachment_id.id], message_type="notification",
                                                                                   subtype_xmlid="mail.mt_comment",
                                                                                   author_id=partner.id)
                    else:
                        channel_exist.with_context(from_odoobot=True).message_post(body=msg['body'], message_type="notification",
                                                                                   subtype_xmlid="mail.mt_comment", author_id=partner.id)
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
            else:
                image_path = modules.get_module_resource('pragtech_whatsapp_messenger', 'static/img', 'whatsapp_logo.png')
                image = base64.b64encode(open(image_path, 'rb').read())
                partner_list = []
                for whatsapp_chat_partner_id in whatsapp_partner_ids:
                    partner_list.append(whatsapp_chat_partner_id.id)
                partner_list.append(partner.id)

                if len(partner_list) > 0:
                    channel = mail_channel_obj.sudo().create({
                        'name': 'Chat with {}'.format(partner.name),
                        'channel_partner_ids': [(6, 0, partner_id) for partner_id in partner_list],
                        'channel_type': 'multi_livechat_NAMEs',
                        'chat_partner': partner.id,
                        'is_chat': True,
                        # 'public': 'public',
                        'image_128': image,
                    })
                    if msg['fromMe']:
                        channel.with_context(from_odoobot=True).message_post(body=msg['body'],
                                                                             message_type="notification",
                                                                             subtype_xmlid="mail.mt_comment",
                                                                             author_id=partner.id)
                    else:
                        channel.with_context(from_odoobot=True).message_post(body=msg['body'], message_type="notification",
                                                                         subtype_xmlid="mail.mt_comment", author_id=partner.id)
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }

    def send_notification_to_admin_meta(self, partner, msg):
        mail_channel_obj = request.env['mail.channel']
        whatsapp_chat_ids = request.env.ref('pragtech_whatsapp_messenger.group_whatsapp_chat')
        whatsapp_chat_users_ids = whatsapp_chat_ids.sudo().users
        whatsapp_partner_ids = whatsapp_chat_users_ids.mapped('partner_id')
        admin_partner = request.env['res.partner'].sudo().search([('id', '=', 3)])

        if partner:
            channel_exist = mail_channel_obj.sudo().search([('name', '=', 'Chat with {}'.format(partner.name)),
                                                            ('whatsapp_meta_id', '=', partner.chatId)], limit=1)
            
            if channel_exist:
                channel_exist.with_context(from_odoobot=True).message_post(body=msg, message_type="notification",
                                                                            subtype_xmlid="mail.mt_comment",
                                                                            author_id=partner.id)
            else:
                image_path = modules.get_module_resource('pragtech_whatsapp_messenger', 'static/img', 'whatsapp_logo.png')
                image = base64.b64encode(open(image_path, 'rb').read())
                partner_list = []
                for facebook_chat_partner_id in whatsapp_partner_ids:
                    partner_list.append(facebook_chat_partner_id.id)
                partner_list.append(partner.id)

                if len(partner_list) > 0:
                    channel = mail_channel_obj.sudo().create({
                        'name': 'Chat with {}'.format(partner.name),
                        'channel_partner_ids': [(6, 0, partner_id) for partner_id in partner_list],
                        'channel_type': 'multi_livechat_NAMEs',
                        'chat_partner': partner.id,
                        'is_chat': True,
                        'whatsapp_meta_id': partner.chatId,
                        # 'public': 'public',
                        'image_128': image,
                    })
                    channel.with_context(from_odoobot=True).message_post(body=msg,
                                                                          message_type="notification",
                                                                          subtype_xmlid="mail.mt_comment",
                                                                          author_id=partner.id)
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }

    def send_attachment_to_admin(self, partner, attachment):
        mail_channel_obj = request.env['mail.channel']
        whatsapp_chat_ids = request.env.ref('pragtech_whatsapp_messenger.group_whatsapp_chat')
        whatsapp_chat_users_ids = whatsapp_chat_ids.sudo().users
        whatsapp_partner_ids = whatsapp_chat_users_ids.mapped('partner_id')
        config_obj = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        if partner:
            channel_exist = mail_channel_obj.sudo().search([('name', '=', 'Chat with {}'.format(partner.name)),
                                                            ('whatsapp_meta_id', '=', partner.chatId)], limit=1)
            mime_type = attachment["mime_type"]
            media_id = attachment["id"]
            if 'caption' in attachment:
                caption = attachment["caption"]
            else:
                caption = 'whatsapp attachment'
            url = "https://graph.facebook.com/v15.0/{}".format(media_id)
            page_access_token = request.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_whatsapp_messenger.whatsapp_meta_token')
            headers = {
            "Authorization": "Bearer {}".format(page_access_token)
            }
            image = requests.get(url.strip(), headers=headers).json()
            # image_url = image["url"].replace("\" "")
            image_datas = base64.b64encode(requests.get(image["url"], headers=headers).content)
            if channel_exist:
                attachment = request.env['ir.attachment'].sudo().create(
                    {'name': caption, 'res_id': channel_exist.id, 'res_model': 'mail.channel',
                     'mimetype': mime_type, 'type': 'binary', 'datas': image_datas, 'create_uid': whatsapp_partner_ids.id, 'public': False})
                channel_exist.with_context(from_odoobot=True).message_post(body=url_join(config_obj, f'/web/content/{attachment.id}'), attachment_ids=[attachment.id], message_type="comment",
                                                                           subtype_xmlid="mail.mt_comment", author_id=partner.id)
            else:

                image_path = modules.get_module_resource('pragtech_whatsapp_messenger', 'static/img', 'whatsapp_logo.png')
                channel_image = base64.b64encode(open(image_path, 'rb').read())
                partner_list = []
                for facebook_chat_partner_id in whatsapp_partner_ids:
                    partner_list.append(facebook_chat_partner_id.id)
                partner_list.append(partner.id)

                if len(partner_list) > 0:
                    channel = mail_channel_obj.sudo().create({
                        'name': 'Chat with {}'.format(partner.name),
                        'channel_partner_ids': [(6, 0, partner_id) for partner_id in partner_list],
                        'channel_type': 'multi_livechat_NAMEs',
                        'chat_partner': partner.id,
                        'is_chat': True,
                        'whatsapp_meta_id': partner.chatId,
                        # 'public': 'public',
                        'image_128': channel_image,
                    })
                    attachment = request.env['ir.attachment'].sudo().create(
                        {'name': caption, 'res_id': channel.id, 'res_model': 'mail.channel',
                         'mimetype': mime_type, 'type': 'binary', 'datas': image_datas, 'create_uid': whatsapp_chat_users_ids.id})
                    channel.with_context(from_odoobot=True).message_post(body=url_join(config_obj, f'/web/content/{attachment.id}'), attachment_ids=[attachment.id],
                                                                          message_type="comment",
                                                                          subtype_xmlid="mail.mt_comment",
                                                                          author_id=partner.id)
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }

