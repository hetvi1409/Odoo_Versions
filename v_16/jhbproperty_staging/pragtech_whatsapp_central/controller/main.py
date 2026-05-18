from odoo.addons.phone_validation.tools import phone_validation
from odoo import http, _, modules
import logging
import json
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
import phonenumbers
import datetime
from odoo.exceptions import AccessError
import time
from odoo.http import request, Response
from odoo.tools import date_utils
import pytz
from odoo.tools import ustr
import requests
from requests.structures import CaseInsensitiveDict
from odoo.addons.pragtech_whatsapp_base.controller.main import WhatsappBase
import base64
from werkzeug.urls import url_join

_logger = logging.getLogger(__name__)


class AttachmentGlobalUrl(http.Controller):

    @http.route(['/whatsapp_attachment/<string:whatsapp_access_token>/get_attachment'], type='http', auth='public')
    def social_post_instagram_image(self, whatsapp_access_token):
        social_post = request.env['ir.attachment'].sudo().search(
            [('access_token', '=', whatsapp_access_token)])

        if not social_post:
            raise Forbidden()

        # called manually to throw a ValidationError if not valid instagram image

        status, headers, image_base64 = request.env['ir.http'].sudo().binary_content(
            id=social_post.id,
            default_mimetype='image/jpeg'
        )

        return request.env['ir.http']._content_image_get_response(status, headers, image_base64)


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


class Whatsapp(WhatsappBase):
    _whm_parent_level = 5

    def _check_employee(self, employee_id, **kw):
        if not employee_id:  # to check
            return None
        employee_id = int(employee_id)

        if 'allowed_company_ids' in request.env.context:
            cids = request.env.context['allowed_company_ids']
        else:
            cids = [request.env.company.id]

        Employee = request.env['whatsapp.helpdesk.messages'].with_context(
            allowed_company_ids=cids)
        # check and raise
        if not Employee.check_access_rights('read', raise_exception=False):
            return None
        try:
            Employee.browse(employee_id).check_access_rule('read')
        except AccessError:
            return None
        else:
            return Employee.browse(employee_id)

    def prepare_whmessage_data(self, employee):
        # job = employee.sudo().job_id
        return dict(
            id=employee.id,
            name=employee.name,
            link='/mail/view?model=%s&res_id=%s' % (
                'whatsapp.helpdesk.messages', employee.id,),
            # job_id=employee.id,
            # job_name=job.name or '',
            job_title=employee.code or '',
            direct_sub_count=len(employee.child_ids),
            indirect_sub_count=employee.child_all_count,
        )

    @http.route('/wh/get_org_chart', type='json', auth='user')
    def wh_get_org_chart(self, employee_id, **kw):
        employee = self._check_employee(employee_id, **kw)
        if not employee:  # to check
            return {
                'managers': [],
                'children': [],
            }

        # compute employee data for org chart
        ancestors, current = request.env['whatsapp.helpdesk.messages'].sudo(
        ), employee.sudo()
        while current.parent_id and len(ancestors) < self._whm_parent_level + 1:
            ancestors += current.parent_id
            current = current.parent_id

        values = dict(
            self=self.prepare_whmessage_data(employee),
            managers=[
                self.prepare_whmessage_data(ancestor)
                for idx, ancestor in enumerate(ancestors)
                if idx < self._whm_parent_level
            ],
            managers_more=len(ancestors) > self._whm_parent_level,
            children=[self.prepare_whmessage_data(
                child) for child in employee.child_ids],
        )
        values['managers'].reverse()
        return values

    @http.route('/whatsapp_meta/response/message', type='http', auth='public', methods=['GET', 'POST'], website=True, csrf=False)
    def whatsapp_meta_webhook(self):
        whatsapp_instance_id = request.env['whatsapp.instance'].sudo().search([('status', '!=', 'disable')], limit=1)
        Param = http.request.env['res.config.settings'].sudo().get_values()
        # meta_api_token = whatsapp_instance_id.whatsapp_meta_api_token
        # meta_phone_number_id = whatsapp_instance_id.whatsapp_meta_phone_number_id
        # meta_webhook = whatsapp_instance_id.whatsapp_meta_webhook_token
        meta_api_token = Param.get('meta_api_token')
        meta_phone_number_id = Param.get('meta_phone_number_id')
        meta_webhook = Param.get('meta_webhook')
        if request.httprequest.method == 'GET':
            _logger.info("In whatsapp integration controller verification")
            verify_token = meta_webhook
            VERIFY_TOKEN = verify_token
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

                    # return challenge, 200
                else:
                    return http.Response('ERROR', status=403)
        super(Whatsapp, self).whatsapp_meta_webhook()
        data = json.loads(request.httprequest.data)
        _logger.info("Webhook meta api response dict %s: ", str(data))
        _request = data
        starting_message = Param.get('starting_message')
        main_menu_prefix = Param.get('main_menu_prefix')
        previous_menu_prefix = Param.get('previous_menu_prefix')
        whm_obj = request.env['whatsapp.helpdesk.messages']
        wmh_obj = request.env['whatsapp.messages.history'].sudo()
        if data.get('entry')[0].get('changes')[0].get('value').get('messages'):
            msg = data.get('entry')[0].get('changes')[
                0].get('value').get('messages')
            try:
                headers = CaseInsensitiveDict()
                headers["Authorization"] = "Bearer " + meta_api_token
                headers["Content-Type"] = "application/json"
                meta_test = 'https://graph.facebook.com/v15.0/'
                url = url_join(meta_test, meta_phone_number_id)
                response = requests.get(url, headers=headers)
            except Exception as e_log:
                _logger.exception(e_log)
            # json_response_status = json.loads(response.text)
            if response.status_code == 200:
                url = "https://graph.facebook.com/v16.0/{}/messages".format(
                    meta_phone_number_id)
                req_headers = CaseInsensitiveDict()
                req_headers["Authorization"] = "Bearer " + meta_api_token
                req_headers["Content-Type"] = "application/json"
                enter_message = msg[0].get('text').get('body').lower()
                mobile = msg[0].get('from')
                msg_whatsapp = ''
                starting_message = starting_message.split(',')
                main_menu_prefix = main_menu_prefix.split(',')
                previous_menu_prefix = previous_menu_prefix.split(',')
                if enter_message in starting_message + main_menu_prefix:
                    whm_ids = whm_obj.sudo().search(
                        [('parent_id', '=', False)])
                    msg_whatsapp = Param.get('whatsapp_greeting')
                    parent_whm_ids = False

                else:
                    if enter_message in previous_menu_prefix:
                        previous_record = wmh_obj.search(
                            [('name', '=', mobile)], limit=2, order='id desc')
                        if len(previous_record) == 2:
                            enter_message = previous_record[-1].code.lower()
                            previous_record.unlink()
                            parent_whm_ids = whm_obj.sudo().search(
                                [('code', 'ilike', enter_message)])
                            whm_ids = whm_obj.sudo().search(
                                [('parent_id', 'in', parent_whm_ids.ids)])
                        elif len(previous_record) == 1:
                            enter_message = starting_message and starting_message[0]
                            previous_record.unlink()
                            whm_ids = whm_obj.sudo().search(
                                [('parent_id', '=', False)])
                            msg_whatsapp = "\n" + \
                                Param.get('whatsapp_greeting')
                        else:
                            whm_ids = whm_obj.sudo().search(
                                [('parent_id', '=', False)])
                            msg_whatsapp = "Previous is not suitable!"
                            msg_whatsapp += "\n" + \
                                Param.get('whatsapp_greeting')
                            for whm_id in whm_ids:
                                msg_whatsapp += "\n" + \
                                    _(whm_id.code) + '=> ' + _(whm_id.name)
                            data_json = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": mobile,
                                "type": "text",
                                "text": {
                                    "body": msg_whatsapp,
                                }
                            }
                            response = requests.post(
                                url, headers=req_headers, json=data_json)
                            return
                    if enter_message not in starting_message + main_menu_prefix + previous_menu_prefix:
                        wmh_obj.create(
                            {'name': mobile, 'code': enter_message})
                        parent_whm_ids = whm_obj.sudo().search(
                            [('code', 'in', [enter_message, enter_message.upper()])])
                        whm_ids = whm_obj.sudo().search(
                            [('parent_id', '=', parent_whm_ids.id)], order='id desc')
                        if not whm_ids and parent_whm_ids:
                            whm_ids = parent_whm_ids

                if not whm_ids:
                    data_json = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": mobile,
                        "type": "text",
                        "text": {
                            "body": 'Please Enter the proper code from above code or enter Hello, Hi or Hey!',
                        }
                    }
                    response = requests.post(
                        url, headers=req_headers, json=data_json)
                    return

                if whm_ids != parent_whm_ids:
                    for whm_id in whm_ids:
                        msg_whatsapp = str(
                            "\n") + str(msg_whatsapp) + "\n" + str(whm_id.code) + str(' -> ') + str(whm_id.name)
                        if whm_id.attachment_ids:
                            for attachment in whm_id.attachment_ids:
                                data_json = {
                                    "messaging_product": "whatsapp",
                                    "recipient_type": "individual",
                                    "to": mobile,
                                    "type": "document",
                                    "document": {
                                        "link": attachment.new_url,
                                        "filename": attachment.name
                                    }
                                }
                                response = requests.post(url, headers=req_headers, data=json.dumps(data_json))

                if enter_message not in starting_message + main_menu_prefix:
                    # if enter_message not in ['hello', 'hi', 'hey', '*']:
                    msg_whatsapp += "\n" + \
                        _(main_menu_prefix and main_menu_prefix[0]) + ' -> ' + _(
                            'Main Menu')
                    msg_whatsapp += "\n" + _(previous_menu_prefix and previous_menu_prefix[0]) + ' -> ' + _(
                        'Previous Menu')
                for whm_id in whm_ids:
                    # if whm_id.code.lower() != enter_message:
                    #     continue
                    att_id = request.env['whatsapp.helpdesk.messages'].sudo().search([('code', '=', enter_message.upper())])
                    if enter_message not in Param.get('starting_message') and enter_message != '*' and enter_message != '#':
                        if not att_id:
                            data_json = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": mobile,
                                "type": "text",
                                "text": {
                                    "body": 'Please Enter the proper code from above code or enter Hello, Hi or Hey!',
                                }
                            }
                            response = requests.post(
                                url, headers=req_headers, json=data_json)
                            return
                for action_id in att_id.action_type_ids:
                        if action_id.action_type == 'url':
                            data_json = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": mobile,
                                "type": "text",
                                "text": {
                                        "body": action_id.url,
                                }
                            }
                            response = requests.post(
                                url, headers=req_headers, data=json.dumps(data_json))
                        elif action_id.action_type in 'send_image':
                            data_json = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": mobile,
                                "type": "image",
                                "image": {
                                        "link": action_id.url,
                                        "caption": action_id.name
                                },
                            }
                            response = requests.post(
                                url, headers=req_headers, data=json.dumps(data_json))
                        elif action_id.action_type == 'send_video':
                            data_json = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": mobile,
                                "type": "video",
                                "video": {
                                    "link": action_id.url,
                                    "caption": action_id.name
                                }
                            }
                            response = requests.post(
                                url, headers=req_headers, data=json.dumps(data_json))
                        elif action_id.action_type == 'send_audio':
                            # access_token = Param.get('whatsapp_token')
                            # phone_id = Param.get('meta_phone_number_id')
                            # url_new = "https://graph.facebook.com/v15.0/{}/media".format(phone_id)
                            # attachment_data = base64.b64decode(attachment.datas)
                            # files2 = {
                            #     'file': (attachment.name, attachment_data, attachment.mimetype, {'Expires': '0'}),
                            # }
                            # param = {
                            #     'messaging_product': "whatsapp"
                            # }
                            #
                            # headers = {
                            #     "Authorization": "Bearer {}".format(access_token)
                            # }
                            # result = requests.post(url, headers=headers, files=files2, data=param)
                            # if result.status_code == 200 or result.status_code == 201:
                            #     url = "https://graph.facebook.com/v15.0/{}/messages".format(phone_id)
                            #     result_json = result.json()
                            #     obj_id = result_json["id"]
                            #     data_json = {
                            #         "messaging_product": "whatsapp",
                            #         "recipient_type": "individual",
                            #         "to": mobile,
                            #         "type": "image",
                            #         "image": {
                            #             "id": obj_id,
                            #             "caption": self.message
                            #         },
                            #     }
                            #     if action_id.action_type == 'send_audio':
                            #         data_json = {
                            #             "messaging_product": "whatsapp",
                            #             "recipient_type": "individual",
                            #             "to": mobile,
                            #             "type": "audio",
                            #             "audio": {
                            #                 "id": obj_id,
                            #             }
                            #         }
                            #     response = requests.post(url, headers=req_headers, data=json.dumps(data_json))

                            data_json = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": mobile,
                                "type": "document",
                                "document": {
                                    "link": action_id.url,
                                    "caption": action_id.name
                                }
                            }
                            response = requests.post(
                                url, headers=req_headers, data=json.dumps(data_json))
                        elif action_id.action_type == 'send_file':
                            data_json = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": mobile,
                                "type": "document",
                                "document": {
                                    "link": action_id.url,
                                    "filename": action_id.name
                                }
                            }
                            response = requests.post(
                                url, headers=req_headers, data=json.dumps(data_json))
                        _logger.info("\nresponse==%s, %s>",
                                     response, response.text)
                        if response.status_code == 201 or response.status_code == 200:
                            _logger.info("\nSend Message successfully")

                msg_whatsapp = msg_whatsapp.replace('False', '')
                if whm_id.code.lower() == enter_message:
                    msg_whatsapp += "\n" + Param.get('whatsapp_ending')
                data_json = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": mobile,
                    "type": "text",
                    "text": {
                        "body": msg_whatsapp,
                    }
                }
                response = requests.post(
                    url, headers=req_headers, data=json.dumps(data_json))
                _logger.info("\nresponse==%s, %s>",
                                 response, response.text)
                _logger.info("\nSend Message successfully")
                return "Send Message successfully"

    @http.route(['/whatsapp_message_endpoint'], type='json', auth='public')
    def whatsapp_chat_api_response(self):
        _logger.info("In whatsapp integration controller")
        data = json.loads(request.httprequest.data)
        _logger.info("data %s: ", str(data))
        _request = data
        if 'messages' in data and data['messages']:
            Param = http.request.env['res.config.settings'].sudo().get_values()
            starting_message = Param.get('starting_message')
            main_menu_prefix = Param.get('main_menu_prefix')
            previous_menu_prefix = Param.get('previous_menu_prefix')
            whm_obj = request.env['whatsapp.helpdesk.messages']
            wmh_obj = request.env['whatsapp.messages.history'].sudo()
            if data['messages']:
                msg = data['messages'][0]
                url = 'https://api.apichat.io/v1/sendText'
                headers = {
                    "client-id": Param.get('whatsapp_client'),
                    "token": Param.get('whatsapp_secret'),
                    "Content-Type": "application/json"}
                enter_message = msg.get('body').lower()
                mobile = msg.get('author').split('@')[0]
                msg_whatsapp = ''
                starting_message = starting_message.split(',')
                main_menu_prefix = main_menu_prefix.split(',')
                previous_menu_prefix = previous_menu_prefix.split(',')
                check_personal = msg.get('author').split('@')[1]
                is_personal = str(check_personal)[0]
                if is_personal == 'c':
                    if enter_message in starting_message + main_menu_prefix:
                        whm_ids = whm_obj.sudo().search(
                            [('parent_id', '=', False)])
                        msg_whatsapp = Param.get('whatsapp_greeting')
                        parent_whm_ids = False
                    else:
                        if enter_message in previous_menu_prefix:
                            previous_record = wmh_obj.search(
                                [('name', '=', mobile)], limit=2, order='id desc')
                            if len(previous_record) == 2:
                                enter_message = previous_record[-1].code.lower()
                                previous_record.unlink()
                                parent_whm_ids = whm_obj.sudo().search(
                                    [('code', 'ilike', enter_message)])
                                whm_ids = whm_obj.sudo().search(
                                    [('parent_id', 'in', parent_whm_ids.ids)])
                            elif len(previous_record) == 1:
                                enter_message = starting_message and starting_message[0]
                                previous_record.unlink()
                                whm_ids = whm_obj.sudo().search(
                                    [('parent_id', '=', False)])
                                msg_whatsapp = "\n" + \
                                    Param.get('whatsapp_greeting')
                            else:
                                whm_ids = whm_obj.sudo().search(
                                    [('parent_id', '=', False)])
                                msg_whatsapp = "Previous is not suitable!"
                                msg_whatsapp += "\n" + \
                                    Param.get('whatsapp_greeting')
                                for whm_id in whm_ids:
                                    msg_whatsapp += "\n" + \
                                        _(whm_id.code) + '=> ' + _(whm_id.name)
                                tmp_dict = {
                                    "number": mobile,
                                    "text": msg_whatsapp}
                                requests.post(url, json.dumps(
                                    tmp_dict), headers=headers)
                                return
                        if enter_message not in starting_message + main_menu_prefix + previous_menu_prefix:
                            wmh_obj.create(
                                {'name': mobile, 'code': enter_message})
                            parent_whm_ids = whm_obj.sudo().search(
                                [('code', 'in', [enter_message, enter_message.upper()])])
                            whm_ids = whm_obj.sudo().search(
                                [('parent_id', '=', parent_whm_ids.id)], order='id desc')
                            if not whm_ids and parent_whm_ids:
                                whm_ids = parent_whm_ids
                    if not whm_ids:
                        tmp_dict = {
                            "number": mobile,
                            "text": 'Please Enter the proper code from above code or enter Hello, Hi or Hey!'}
                        requests.post(url, json.dumps(
                            tmp_dict), headers=headers)
                        return
                    #     whm_ids = request.env['whatsapp.helpdesk.messages'].sudo().search([('parent', '=', False)])
                    #     msg_whatsapp = Param.get('whatsapp_greeting')
                    # else:
                    #     whm_ids = request.env['whatsapp.helpdesk.messages'].sudo().search([('parent', 'in', whm_ids.ids)])
                    if whm_ids != parent_whm_ids:
                        for whm_id in whm_ids:
                            # msg_whatsapp = "none value replaced for test"
                            if not msg_whatsapp:
                                msg_whatsapp = enter_message
                            msg_whatsapp += "\n" + \
                                _(whm_id.code) + '=> ' + _(whm_id.name)
                    if enter_message not in starting_message + main_menu_prefix:
                        # if enter_message not in ['hello', 'hi', 'hey', '*']:
                        msg_whatsapp += "\n" + \
                            _(main_menu_prefix and main_menu_prefix[0]) + ' -> ' + _(
                                'Main Menu')
                        msg_whatsapp += "\n" + _(previous_menu_prefix and previous_menu_prefix[0]) + ' -> ' + _(
                            'Previous Menu')

                    for whm_id in whm_ids:
                        if whm_id.code.lower() != enter_message:
                            continue
                        for action_id in whm_id.action_type_ids:
                            if action_id.action_type == 'url':
                                tmp_dict = {
                                    "number": mobile,
                                    "text": action_id.url}
                                response = requests.post('https://api.apichat.io/v1/sendText', json.dumps(tmp_dict),
                                                         headers=headers)
                            elif action_id.action_type in 'send_image':
                                tmp_dict = {
                                    "number": mobile,
                                    "url": action_id.url,
                                    "caption": action_id.name
                                }
                                response = requests.post('https://api.apichat.io/v1/sendImage', json.dumps(tmp_dict),
                                                         headers=headers)
                            elif action_id.action_type == 'send_video':
                                tmp_dict = {
                                    "number": mobile,
                                    "url": action_id.url,
                                    "caption": action_id.name
                                }
                                response = requests.post('https://api.apichat.io/v1/sendVideo', json.dumps(tmp_dict),
                                                         headers=headers)
                            elif action_id.action_type == 'send_audio':
                                tmp_dict = {
                                    "number": mobile,
                                    "url": action_id.url,
                                }
                                response = requests.post('https://api.apichat.io/v1/sendAudio', json.dumps(tmp_dict),
                                                         headers=headers)
                            elif action_id.action_type == 'send_file':
                                tmp_dict = {
                                    "number": mobile,
                                    "url": action_id.url,
                                    "filename": action_id.name
                                }
                                response = requests.post('https://api.apichat.io/v1/sendFile', json.dumps(tmp_dict),
                                                         headers=headers)
                            _logger.info("\nresponse==%s, %s>",
                                         response, response.text)
                            if response.status_code == 201 or response.status_code == 200:
                                _logger.info("\nSend Message successfully")

                    tmp_dict = {
                        "number": mobile,
                        "text": msg_whatsapp}
                    response = requests.post(
                        url, json.dumps(tmp_dict), headers=headers)
                    _logger.info("\nresponse==%s, %s>",
                                 response, response.text)
                    _logger.info("\nSend Message successfully")
                    return "Send Message successfully"

    @http.route(['/whatsapp/response/message'], type='json', auth='public')
    def whatsapp_response(self):
        _logger.info("In whatsapp integration controller")
        data = json.loads(request.httprequest.data)
        _logger.info("data %s: ", str(data))
        _request = data

        if 'messages' in data and data['messages'] and not data['messages'][0]['self']:
            Param = http.request.env['res.config.settings'].sudo().get_values()
            starting_message = Param.get('starting_message')
            main_menu_prefix = Param.get('main_menu_prefix')
            previous_menu_prefix = Param.get('previous_menu_prefix')
            whm_obj = request.env['whatsapp.helpdesk.messages']
            wmh_obj = request.env['whatsapp.messages.history'].sudo()
            if data['messages']:
                msg = data['messages'][0]
                try:
                    status_url = Param.get(
                        'whatsapp_endpoint') + '/status?token=' + Param.get('whatsapp_token')
                    status_response = requests.get(status_url)
                except Exception as e_log:
                    _logger.exception(e_log)
                json_response_status = json.loads(status_response.text)
                if (status_response.status_code == 200 or status_response.status_code == 201):
                    base_url = Param.get(
                        'whatsapp_endpoint') + '/sendMessage?token=' + Param.get('whatsapp_token')
                    headers = {"Content-Type": "application/json"}

                    enter_message = msg.get('body').lower()
                    mobile = msg['author'].split('@')[0]
                    msg_whatsapp = ''
                    starting_message = starting_message.split(',')
                    main_menu_prefix = main_menu_prefix.split(',')
                    previous_menu_prefix = previous_menu_prefix.split(',')
                    if enter_message in starting_message + main_menu_prefix:
                        whm_ids = whm_obj.sudo().search(
                            [('parent_id', '=', False)])
                        msg_whatsapp = Param.get('whatsapp_greeting')
                        parent_whm_ids = False
                    else:
                        if enter_message in previous_menu_prefix:
                            previous_record = wmh_obj.search(
                                [('name', '=', mobile)], limit=2, order='id asc')
                            if len(previous_record) == 2:
                                enter_message = previous_record[-1].code.lower()
                                previous_record.unlink()
                                parent_whm_ids = whm_obj.sudo().search(
                                    [('code', 'ilike', enter_message)])
                                whm_ids = whm_obj.sudo().search(
                                    [('parent_id', 'in', parent_whm_ids.ids)])
                            elif len(previous_record) == 1:
                                enter_message = starting_message and starting_message[0]
                                previous_record.unlink()
                                whm_ids = whm_obj.sudo().search(
                                    [('parent_id', '=', False)])
                                msg_whatsapp = "\n" + \
                                    Param.get('whatsapp_greeting')
                            else:
                                whm_ids = whm_obj.sudo().search(
                                    [('parent_id', '=', False)])
                                msg_whatsapp = "Previous is not suitable!"
                                msg_whatsapp += "\n" + \
                                    Param.get('whatsapp_greeting')
                                for whm_id in whm_ids:
                                    msg_whatsapp += "\n" + \
                                        _(whm_id.code) + '=> ' + _(whm_id.name)

                                tmp_dict = {
                                    "phone": mobile,
                                    "body": msg_whatsapp
                                }
                                requests.post(base_url, json.dumps(
                                    tmp_dict), headers=headers)
                                return
                        if enter_message not in starting_message + main_menu_prefix + previous_menu_prefix:
                            wmh_obj.create(
                                {'name': mobile, 'code': enter_message})
                            parent_whm_ids = whm_obj.sudo().search(
                                [('code', 'in', [enter_message, enter_message.upper()])])
                            whm_ids = whm_obj.sudo().search(
                                [('parent_id', '=', parent_whm_ids.id)], order='id desc')
                            if not whm_ids and parent_whm_ids:
                                whm_ids = parent_whm_ids

                    if not whm_ids:
                        tmp_dict = {
                            "phone": mobile,
                            "body": 'Please Enter the proper code from above code or enter Hello, Hi or Hey!'
                        }
                        requests.post(base_url, json.dumps(
                            tmp_dict), headers=headers)
                        return
                    #     whm_ids = request.env['whatsapp.helpdesk.messages'].sudo().search([('parent', '=', False)])
                    #     msg_whatsapp = Param.get('whatsapp_greeting')
                    # else:
                    #     whm_ids = request.env['whatsapp.helpdesk.messages'].sudo().search([('parent', 'in', whm_ids.ids)])
                    if whm_ids != parent_whm_ids:
                        for whm_id in whm_ids:
                            msg_whatsapp = str(
                                "\n") + str(whm_id.code) + str(' -> ') + str(whm_id.name) + str(msg_whatsapp)
                            if whm_id.attachment_ids:
                                for attachment in whm_id.attachment_ids:
                                    with open("/tmp/" + attachment.name, 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        url_send_file = Param.get(
                                            'whatsapp_endpoint') + '/sendFile?token=' + Param.get(
                                            'whatsapp_token')
                                        headers_send_file = {
                                            "Content-Type": "application/json"}
                                        dict_send_file = {
                                            "chatId": mobile + '@c.us',
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file,
                                                                           json.dumps(
                                                                               dict_send_file),
                                                                           headers=headers_send_file)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info(
                                                "\nSend file attachment successfully11")

                    if enter_message not in starting_message + main_menu_prefix:
                        # if enter_message not in ['hello', 'hi', 'hey', '*']:
                        msg_whatsapp += "\n" + \
                            _(main_menu_prefix and main_menu_prefix[0]) + ' -> ' + _(
                                'Main Menu')
                        msg_whatsapp += "\n" + _(previous_menu_prefix and previous_menu_prefix[0]) + ' -> ' + _(
                            'Previous Menu')

                    for whm_id in whm_ids:
                        if whm_id.code.lower() != enter_message:
                            continue

                        for action_id in whm_id.action_type_ids:
                            if action_id.action_type == 'url':
                                tmp_dict = {
                                    "phone": mobile,
                                    "body": action_id.url
                                }
                                response = requests.post(
                                    base_url, json.dumps(tmp_dict), headers=headers)
                            elif action_id.action_type in 'send_image':
                                tmp_dict = {
                                    "chatId": mobile + '@c.us',
                                    "body": action_id.url,
                                    "filename": action_id.name
                                }
                                response = requests.post(
                                    Param.get(
                                        'whatsapp_endpoint') + '/sendFile?token=' + Param.get('whatsapp_token'),
                                    json.dumps(tmp_dict), headers=headers)
                            elif action_id.action_type == 'send_video':
                                tmp_dict = {
                                    "chatId": mobile + '@c.us',
                                    "body": action_id.url,
                                    "filename": action_id.name
                                }
                                response = requests.post(
                                    Param.get(
                                        'whatsapp_endpoint') + '/sendFile?token=' + Param.get('whatsapp_token'),
                                    json.dumps(tmp_dict), headers=headers)
                            elif action_id.action_type == 'send_audio':
                                tmp_dict = {
                                    "chatId": mobile + '@c.us',
                                    "body": action_id.url,
                                    "isVoiceNote": True,
                                    "filename": action_id.name
                                }
                                response = requests.post(
                                    Param.get(
                                        'whatsapp_endpoint') + '/sendFile?token=' + Param.get('whatsapp_token'),
                                    json.dumps(tmp_dict), headers=headers)
                            elif action_id.action_type == 'send_file':
                                tmp_dict = {
                                    "chatId": mobile + '@c.us',
                                    "body": action_id.url,
                                    "filename": action_id.name
                                }
                                response = requests.post(
                                    Param.get(
                                        'whatsapp_endpoint') + '/sendFile?token=' + Param.get('whatsapp_token'),
                                    json.dumps(tmp_dict), headers=headers)
                            _logger.info("\nresponse==%s, %s>",
                                         response, response.text)
                            if response.status_code == 201 or response.status_code == 200:
                                _logger.info("\nSend Message successfully")
                    msg_whatsapp = msg_whatsapp.replace('False', '')
                    tmp_dict = {
                        "phone": mobile,
                        "body": msg_whatsapp
                    }
                    response = requests.post(
                        base_url, json.dumps(tmp_dict), headers=headers)
                    _logger.info("\nresponse==%s, %s>",
                                 response, response.text)
                    _logger.info("\nSend Message successfully")
        super(Whatsapp, self).whatsapp_response()
                    # return "Send Message successfully"

    @http.route(['/gupshup/response/message'], jsonrpc=None, methods=['POST'], type='json', auth='public')
    def gupshup_whatsapp_response(self):
        data = json.loads(request.httprequest.data)
        #_logger.info("malumhenaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa %s: ", str(data))
        #_logger.info("22222222222222222222222222222222222222222222222 %s: ", str(data['type']))
        _request = data
        if str(data['type']) == "message":
            data_payload = data['payload']
            text_payload = data['payload'].get('payload')
            message = text_payload.get('text')
            message_id = text_payload.get('id')
            Param = http.request.env['res.config.settings'].sudo().get_values()
            Param = http.request.env['res.config.settings'].sudo().get_values()
            starting_message = Param.get('starting_message')
            main_menu_prefix = Param.get('main_menu_prefix')
            previous_menu_prefix = Param.get('previous_menu_prefix')
            whm_obj = request.env['whatsapp.helpdesk.messages']
            wmh_obj = request.env['whatsapp.messages.history'].sudo()
            msg = message
            enter_message = message
            mobile = data_payload.get('destination')
            msg_whatsapp = ''
            status_url = Param.get('whatsapp_gupshup_api')
            base_url = 'https://api.gupshup.io/sm/api/v1/msg'
            headers = {"Content-Type": "application/x-www-form-urlencoded", "apikey":  Param.get(
                'whatsapp_gupshup_api'), 'Cache-Control': 'no-cache', 'cache-control': 'no-cache'}
            app_name = data.get('app')
            starting_message = starting_message.split(',')
            main_menu_prefix = main_menu_prefix.split(',')
            previous_menu_prefix = previous_menu_prefix.split(',')
            if enter_message in starting_message + main_menu_prefix:
                whm_ids = whm_obj.sudo().search([('parent_id', '=', False)])
                msg_whatsapp = Param.get('whatsapp_greeting')
                parent_whm_ids = False
            else:
                if enter_message in previous_menu_prefix:
                    previous_record = wmh_obj.search(
                        [('name', '=', mobile)], limit=2, order='id desc')
                    if len(previous_record) == 2:
                        enter_message = previous_record[-1].code.lower()
                        previous_record.unlink()
                        parent_whm_ids = whm_obj.sudo().search(
                            [('code', 'ilike', enter_message)])
                        whm_ids = whm_obj.sudo().search(
                            [('parent_id', 'in', parent_whm_ids.ids)])
                    elif len(previous_record) == 1:
                        enter_message = starting_message and starting_message[0]
                        previous_record.unlink()
                        whm_ids = whm_obj.sudo().search(
                            [('parent_id', '=', False)])
                        msg_whatsapp = "\n" + Param.get('whatsapp_greeting')
                    else:
                        whm_ids = whm_obj.sudo().search(
                            [('parent_id', '=', False)])
                        msg_whatsapp = "Previous is not suitable!"
                        msg_whatsapp = str(
                            "\n") + str(Param.get('whatsapp_greeting')) + str(msg_whatsapp)
                        for whm_id in whm_ids:
                            msg_whatsapp += "\n" + \
                                _(whm_id.code) + '=> ' + _(whm_id.name)
                            msg_whatsapp = msg_whatsapp.replace('False', '')
                        payload_sender = data['payload'].get('sender')
                        sender_phone = payload_sender.get('phone')
                        source_phone = data['payload'].get('source')
                        temp_data = {
                            'channel': 'whatsapp',
                            'source': source_phone,
                            'destination': sender_phone,
                            'src.name': app_name,
                            'message': json.dumps({
                                'type': 'text',
                                'text': msg_whatsapp
                            })

                        }
                        response = requests.post(
                            base_url, headers=headers, data=temp_data)
                        request._json_response = _json_response_inherit.__get__(
                            request, JsonRequest)
                        return
                if enter_message not in starting_message + main_menu_prefix + previous_menu_prefix:
                    wmh_obj.create(
                        {'name': mobile, 'code': enter_message})
                    parent_whm_ids = whm_obj.sudo().search(
                        [('code', 'in', [enter_message, enter_message.upper()])])
                    whm_ids = whm_obj.sudo().search(
                        [('parent_id', '=', parent_whm_ids.id)], order='id desc')
                    if not whm_ids and parent_whm_ids:
                        whm_ids = parent_whm_ids
            if not whm_ids:
                msg_whatsapp = 'Please Enter the proper code from above code or enter Hello, Hi or Hey!'
                payload_sender = data['payload'].get('sender')
                sender_phone = payload_sender.get('phone')
                source_phone = data['payload'].get('source')
                temp_data = {
                    'channel': 'whatsapp',
                    'source': source_phone,
                    'destination': sender_phone,
                    'src.name': app_name,
                    'message': json.dumps({
                        'type': 'text',
                        'text': msg_whatsapp
                    })

                }
                response = requests.post(
                    base_url, headers=headers, data=temp_data)
                request._json_response = _json_response_inherit.__get__(
                    request, JsonRequest)
                return
            if whm_ids != parent_whm_ids:
                for whm_id in whm_ids:
                    msg_whatsapp = str(
                        "\n") + str(whm_id.code) + str(' -> ') + str(whm_id.name) + str(msg_whatsapp)
                    payload_sender = data['payload'].get('sender')
                    sender_phone = payload_sender.get('phone')
                    source_phone = data['payload'].get('source')
                    for attachment in whm_id.attachment_ids:

                        temp_data = {
                            'channel': 'whatsapp',
                            'source': source_phone,
                            'destination': sender_phone,
                            'src.name': app_name,
                            'message': json.dumps({"type": "file", "url": attachment.new_url, "caption": "", "filename": attachment.name})

                        }
                        response = requests.post(
                            base_url, headers=headers, data=temp_data)

            if enter_message not in starting_message + main_menu_prefix:
                # if enter_message not in ['hello', 'hi', 'hey', '*']:
                msg_whatsapp += "\n" + \
                    _(main_menu_prefix and main_menu_prefix[0]
                      ) + ' -> ' + _('Main Menu')
                msg_whatsapp += "\n" + _(previous_menu_prefix and previous_menu_prefix[0]) + ' -> ' + _(
                    'Previous Menu')
            for whm_id in whm_ids:
                if whm_id.code.lower() != enter_message:
                    continue
                for action_id in whm_id.action_type_ids:
                    if action_id.action_type == 'url':

                        payload_sender = data['payload'].get('sender')
                        sender_phone = payload_sender.get('phone')
                        source_phone = data['payload'].get('source')
                        temp_data = {
                            'channel': 'whatsapp',
                            'source': source_phone,
                            'destination': sender_phone,
                            'src.name': app_name,
                            'message': json.dumps({"type": "text", 'text': action_id.url})

                        }
                        response = requests.post(
                            base_url, headers=headers, data=temp_data)
                        request._json_response = _json_response_inherit.__get__(
                            request, JsonRequest)
                        return

                    elif action_id.action_type in 'send_image':

                        payload_sender = data['payload'].get('sender')
                        sender_phone = payload_sender.get('phone')
                        source_phone = data['payload'].get('source')
                        temp_data = {
                            'channel': 'whatsapp',
                            'source': source_phone,
                            'destination': sender_phone,
                            'src.name': app_name,
                            'message': json.dumps({"type": "image", "previewUrl": action_id.url, "originalUrl": action_id.url, "caption": "", "filename": action_id.name})

                        }
                        response = requests.post(
                            base_url, headers=headers, data=temp_data)
                        request._json_response = _json_response_inherit.__get__(
                            request, JsonRequest)
                        return

                    elif action_id.action_type == 'send_video':

                        payload_sender = data['payload'].get('sender')
                        sender_phone = payload_sender.get('phone')
                        source_phone = data['payload'].get('source')
                        temp_data = {
                            'channel': 'whatsapp',
                            'source': source_phone,
                            'destination': sender_phone,
                            'src.name': app_name,
                            'message': json.dumps({"type": "video", "url": action_id.url, "caption": "", "filename": action_id.name})

                        }
                        response = requests.post(
                            base_url, headers=headers, data=temp_data)
                        request._json_response = _json_response_inherit.__get__(
                            request, JsonRequest)
                        return

                    elif action_id.action_type == 'send_audio':

                        payload_sender = data['payload'].get('sender')
                        sender_phone = payload_sender.get('phone')
                        source_phone = data['payload'].get('source')
                        temp_data = {
                            'channel': 'whatsapp',
                            'source': source_phone,
                            'destination': sender_phone,
                            'src.name': app_name,
                            'message': json.dumps({"type": "audio", "url": action_id.url, "caption": "", "filename": action_id.name})

                        }
                        response = requests.post(
                            base_url, headers=headers, data=temp_data)
                        request._json_response = _json_response_inherit.__get__(
                            request, JsonRequest)
                        return

                    elif action_id.action_type == 'send_file':
                        payload_sender = data['payload'].get('sender')
                        sender_phone = payload_sender.get('phone')
                        source_phone = data['payload'].get('source')
                        temp_data = {
                            'channel': 'whatsapp',
                            'source': source_phone,
                            'destination': sender_phone,
                            'src.name': app_name,
                            'message': json.dumps({"type": "file", "url": action_id.url, "caption": "", "filename": action_id.name})

                        }
                        response = requests.post(
                            base_url, headers=headers, data=temp_data)
                        request._json_response = _json_response_inherit.__get__(
                            request, JsonRequest)
                        return
            msg_whatsapp = msg_whatsapp.replace('False', '')
            payload_sender = data['payload'].get('sender')
            sender_phone = payload_sender.get('phone')
            source_phone = data['payload'].get('source')
            temp_data = {
                'channel': 'whatsapp',
                'source': source_phone,
                'destination': sender_phone,
                'src.name': app_name,
                'message': json.dumps({
                    'type': 'text',
                            'text': msg_whatsapp
                })

            }
            response = requests.post(base_url, headers=headers, data=temp_data)
            request._json_response = _json_response_inherit.__get__(
                request, JsonRequest)
