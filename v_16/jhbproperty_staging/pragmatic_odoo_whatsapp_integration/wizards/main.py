from odoo import api, models, tools, fields, _
import odoo
import json
import requests
import logging
import threading
import base64
import time
import re
import select
from odoo.tools import date_utils
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval, time

_logger = logging.getLogger(__name__)

try:
    import phonenumbers
    from phonenumbers.phonenumberutil import region_code_for_country_code
    _sms_phonenumbers_lib_imported = True

except ImportError:
    _sms_phonenumbers_lib_imported = False
    _logger.info(
        "The `phonenumbers` Python module is not available. "
        "Phone number validation will be skipped. "
        "Try `pip3 install phonenumbers` to install it."
    )


def json_dump(v):
    return json.dumps(v, separators=(',', ':'), default=date_utils.json_default)


def hashable(key):
    if isinstance(key, list):
        key = tuple(key)
    return key


class CreateConversationChannels(models.TransientModel):
    _name = 'conversations.create'
    _description = 'Create conversation channels'

    def _default_unique_user(self):
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        return dbuuid + '_' + str(self.env.uid)

    # partner_ids = fields.Many2many('res.partner', 'whatsapp_msg_send_partner_res_partner_rel', 'wizard_id', 'partner_id', 'Recipients')
    message = fields.Text('Message', required=True)
    # attachment_ids = fields.Many2many('ir.attachment', 'whatsapp_msg_send_partner_ir_attachments_rel', 'wizard_id', 'attachment_id', 'Attachments')
    unique_user = fields.Char(default=_default_unique_user)

    def _phone_get_country(self, partner):
        if 'country_id' in partner:
            return partner.country_id
        return self.env.user.company_id.country_id

    def _msg_sanitization(self, partner, field_name):
        number = partner[field_name]
        if number and _sms_phonenumbers_lib_imported:
            country = self._phone_get_country(partner)
            country_code = country.code if country else None
            try:
                phone_nbr = phonenumbers.parse(number, region=country_code, keep_raw_input=True)
            except phonenumbers.phonenumberutil.NumberParseException:
                return number
            if not phonenumbers.is_possible_number(phone_nbr) or not phonenumbers.is_valid_number(phone_nbr):
                return number
            phone_fmt = phonenumbers.PhoneNumberFormat.E164
            return phonenumbers.format_number(phone_nbr, phone_fmt)
        else:
            return number

    def _get_records(self, model):
        if self.env.context.get('active_domain'):
            records = model.search(self.env.context.get('active_domain'))
        elif self.env.context.get('active_ids'):
            records = model.browse(self.env.context.get('active_ids', []))
        else:
            records = model.browse(self.env.context.get('active_id', []))
        return records

    @api.model
    def default_get(self, fields):
        result = super(CreateConversationChannels, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        if res_id:
            rec = self.env[active_model].browse(res_id)
            Attachment = self.env['ir.attachment']
            res_name = 'Invoice_' + rec.number.replace('/', '_') if active_model == 'account.move' else rec.name.replace('/', '_')
            msg = result.get('message', '')
            result['message'] = msg

            if not self.env.context.get('default_recipients') and active_model and hasattr(self.env[active_model], '_sms_get_default_partners'):
                model = self.env[active_model]
                records = self._get_records(model)
                partners = records._sms_get_default_partners()
                phone_numbers = []
                no_phone_partners = []
                if active_model != 'res.partner':
                    is_attachment_exists = Attachment.search([('res_id', '=', res_id), ('name', 'like', res_name + '%'), ('res_model', '=', active_model)], limit=1)
                    if not is_attachment_exists:
                        attachments = []
                        if active_model == 'sale.order':
                            template = self.env.ref('sale.email_template_edi_sale')
                        elif active_model == 'account.move':
                            template = self.env.ref('account.email_template_edi_invoice')
                        elif active_model == 'purchase.order':
                            if self.env.context.get('send_rfq', False):
                                template = self.env.ref('purchase.email_template_edi_purchase')
                            else:
                                template = self.env.ref('purchase.email_template_edi_purchase_done')
                        elif active_model == 'stock.picking':
                            template = self.env.ref('stock.mail_template_data_delivery_confirmation')
                        elif active_model == 'account.payment':
                            template = self.env.ref('account.mail_template_data_payment_receipt')
                        report = template.report_template
                        report_service = report.report_name
                        if report.report_type not in ['qweb-html', 'qweb-pdf']:
                            raise UserError(_('Unsupported report type %s found.') % report.report_type)
                        res, format = report._render_qweb_pdf([res_id])
                        res = base64.b64encode(res)
                        if not res_name:
                            res_name = 'report.' + report_service
                        ext = "." + format
                        if not res_name.endswith(ext):
                            res_name += ext
                        attachments.append((res_name, res))
                        attachment_ids = []
                        for attachment in attachments:
                            attachment_data = {
                                'name': attachment[0],
                                'datas': attachment[1],
                                'type': 'binary',
                                'res_model': active_model,
                                'res_id': res_id,
                            }
                            attachment_ids.append(Attachment.create(attachment_data).id)
                        if attachment_ids:
                            result['attachment_ids'] = [(6, 0, attachment_ids)]
                    else:
                        result['attachment_ids'] = [(6, 0, [is_attachment_exists.id])]

                for partner in partners:
                    number = self._msg_sanitization(partner, self.env.context.get('field_name') or 'mobile')
                    if number:
                        phone_numbers.append(number)
                    else:
                        no_phone_partners.append(partner.name)
                if len(partners) > 1:
                    if no_phone_partners:
                        raise UserError(_('Missing mobile number for %s.') % ', '.join(no_phone_partners))
                result['partner_ids'] = [(6, 0, partners.ids)]
                result['message'] = msg
        return result

    def action_send_msg_res_partner(self):
        Param = self.env['res.config.settings'].sudo().get_values()
        active_id = self.partner_ids
        active_model = 'res.partner'
        phone_numbers = []
        no_phone_partners = []
        try:
            status_url = Param.get('whatsapp_endpoint')+'/status?token='+Param.get('whatsapp_token')
            status_response = requests.get(status_url)
        except Exception as e_log:
            _logger.exception(e_log)
            raise UserError(_('Please add proper whatsapp endpoint or whatsapp token'))
        json_response_status = json.loads(status_response.text)
        if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status['accountStatus'] == 'authenticated':
            if active_model == 'res.partner':
                for res_partner_id in self.partner_ids:
                    number = str(res_partner_id.country_id.phone_code) + res_partner_id.mobile
                    if res_partner_id.country_id.phone_code and res_partner_id.mobile:
                        whatsapp_number = res_partner_id.mobile
                        whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(res_partner_id.country_id.phone_code), "")
                        phone_exists_url = Param.get('whatsapp_endpoint') + '/checkPhone?token=' + Param.get(
                            'whatsapp_token') + '&phone=' + str(
                            res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        phone_exists_response = requests.get(phone_exists_url)
                        json_response_phone_exists = json.loads(phone_exists_response.text)
                        if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and json_response_phone_exists['result'] == 'exists':
                            url = Param.get('whatsapp_endpoint')+'/sendMessage?token='+Param.get('whatsapp_token')
                            headers = {"Content-Type": "application/json"}
                            tmp_dict  = {
                                "phone": "+"+str(res_partner_id.country_id.phone_code)+""+whatsapp_msg_number_without_code,
                                "body": self.message}
                            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                            if response.status_code == 201 or response.status_code == 200:
                                _logger.info("\nSend Message successfully")
                            if self.attachment_ids:
                                for attachment in self.attachment_ids:
                                    with open("/tmp/" + attachment.name, 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        url_send_file = Param.get('whatsapp_endpoint') + '/sendFile?token=' + Param.get('whatsapp_token')
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": "+"+str(res_partner_id.country_id.phone_code)+""+whatsapp_msg_number_without_code,
                                            "body": "data:"+attachment.mimetype+";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info("\nSend file attachment successfully11")
                        else:
                            no_phone_partners.append(res_partner_id.name)
                    else:
                        raise UserError(_('Please enter %s mobile number or select country', res_partner_id))
                if len(no_phone_partners) >= 1:
                    raise UserError(
                        _('Please add valid whatsapp number for %s customer') % ', '.join(no_phone_partners))
        else:
            raise UserError(_('Please authorize your mobile number with chat api'))

    def _procure_calculation_orderpoint(self):
        with api.Environment.manage():
            # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            # scheduler_cron = self.sudo().env.ref('procurement.ir_cron_scheduler_action')
            # # Avoid to run the scheduler multiple times in the same time
            # try:
            #     with tools.mute_logger('odoo.sql_db'):
            #         self._cr.execute("SELECT id FROM ir_cron WHERE id = %s FOR UPDATE NOWAIT", (scheduler_cron.id,))
            # except Exception:
            #     _logger.info('Attempt to run procurement scheduler aborted, as already running')
            #     self._cr.rollback()
            #     self._cr.close()
            #     return {}

            self.env['facebook.messenger'].search([])
            new_cr.close()
            return {}

    def loop(self):
        """ Dispatch postgres notifications to the relevant polling threads/greenlets """
        _logger.info("Bus.loop listen imbus on db postgres")
        with odoo.sql_db.db_connect('postgres').cursor() as cr:
            conn = cr._cnx
            cr.execute("listen imbus")
            cr.commit();
            while True:
                if select.select([conn], [], [], 50) == ([], [], []):
                    pass
                else:
                    conn.poll()
                    channels = []
                    while conn.notifies:
                        channels.extend(json.loads(conn.notifies.pop().payload))
                    # dispatch to local threads/greenlets
                    events = set()
                    for channel in channels:
                        events.update(self.channels.pop(hashable(channel), set()))
                    for event in events:
                        event.set()

    def run(self):
        while True:
            try:
                self.loop()
            except Exception as e:
                _logger.exception("Bus.loop error, sleep and retry")
                time.sleep(50)

    def procure_calculation(self):
        threaded_calculation = threading.Thread(target=self.run, args=())
        threaded_calculation.start()
        return {'type': 'ir.actions.act_window_close'}
