import base64
import json
import logging
from datetime import datetime, timedelta

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ApiLog(models.Model):
    _name = 'kw.api.log'
    _inherit = ['generic.mixin.transaction.utils', ]
    _description = 'API log'
    _order = 'create_date DESC'

    name = fields.Char(
        string='URL', )
    json = fields.Text()

    json_file = fields.Binary()

    post = fields.Text()

    post_file = fields.Binary()

    headers = fields.Text()

    error = fields.Text()

    response = fields.Text()

    response_file = fields.Binary()

    ip = fields.Char()

    method = fields.Char()

    code = fields.Char()

    login = fields.Char()

    log_process_time = fields.Integer(
        compute='_compute_log_process_time',
        store=True, readonly=True,
        help='Displays processing time in seconds', )
    process_time = fields.Datetime(
        readonly=True, )

    @api.depends('process_time', 'create_date')
    def _compute_log_process_time(self):
        for obj in self:
            if obj.process_time and obj.create_date:
                delta = obj.process_time - obj.create_date
                obj.log_process_time = int(delta.total_seconds())
            else:
                obj.log_process_time = 0

    @staticmethod
    def try_convert2formatted_json(val):
        try:
            val = json.dumps(json.loads(val), indent=2, ensure_ascii=False)
        except Exception as e:
            _logger.debug(e)
        return val

    @api.model_create_multi
    def create(self, vals_list):
        logging_enabled = self.env['ir.config_parameter'].sudo(
        ).get_param(key='kw_api.kw_api_is_log_enabled')

        if logging_enabled:
            lim = int(self.env['ir.config_parameter'].sudo(
            ).get_param(key='kw_api.kw_api_text_log_limit') or 100)
            for vals in vals_list:
                for x in ['json', 'post', 'response']:
                    if not vals.get(x):
                        continue
                    if len(vals.get(x)) <= lim * 1024:
                        vals[x] = self.try_convert2formatted_json(vals.get(x))
                    else:
                        vals[f'{x}_file'] = base64.b64encode(
                            self.try_convert2formatted_json(vals.get(x)))
                        vals[x] = ''
            return super().create(vals_list)
        return None

    def write(self, vals):
        logging_enabled = self.env['ir.config_parameter'].sudo(
        ).get_param(key='kw_api.kw_api_is_log_enabled')

        if logging_enabled:
            lim = int(self.env['ir.config_parameter'].sudo(
            ).get_param(key='kw_api.kw_api_text_log_limit') or 100)
            for x in ['json', 'post', 'response']:
                if not vals.get(x):
                    continue
                if len(vals.get(x)) <= lim * 1024:
                    vals[x] = self.try_convert2formatted_json(vals.get(x))
                else:
                    data = self.try_convert2formatted_json(vals.get(x))
                    data = str.encode(data)
                    vals[f'{x}_file'] = base64.b64encode(data)
                    vals[x] = ''
            return super().write(vals)
        return None

    @api.model
    def call_clear_logs(self):
        endpoints = self.env["kw.api.custom.endpoint"].sudo(
        ).search([('url', '=', self.name)])

        delete_days_global_config = int(self.env['ir.config_parameter'].sudo(
        ).get_param(key='kw_api.kw_api_log_storage_days'))

        for endpoint in endpoints:
            delete_days_endpoint = int(endpoint.log_expire_days)
            del_date = datetime.now() - timedelta(
                days=(delete_days_endpoint or 1)
            )
            items = self.sudo().search([('create_date', '<', del_date),
                                        ('name', '=', endpoint.url)])
            if items:
                items.unlink()

        del_date_global = datetime.now() - timedelta(
            days=(delete_days_global_config or 1)
        )
        self.sudo().search([('create_date', '<', del_date_global)]).unlink()

    def mark_processed(self):
        self.write({'process_time': fields.Datetime.now()})
