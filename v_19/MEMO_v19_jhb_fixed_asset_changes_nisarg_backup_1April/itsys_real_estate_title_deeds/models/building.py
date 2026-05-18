from odoo import api, fields, models, _
import requests
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class Building(models.Model):
    _inherit = 'building'

    title_deeds_ids = fields.One2many('title.deeds', 'building_id',
                                      string="Title Deeds")
    type_of_take = fields.Selection([('acquisition', 'Normal acquisition'), ('devaluation', 'devaluation'),
                                     ('discondition', ' discondition of township establishment'),
                                     ('rectification', 'rectification'), ('others', 'others')],
                                    string="Type of take-on",
                                    help="Select the type of take-on")
    trim_document_ids = fields.One2many('title.deeds', 'trim_building_id',

                                      string="Trim Documents")

    @api.model
    def create(self, vals):
        res = super(Building, self).create(vals)
        if 'trim_document_ids' in vals:
            for item in vals.get('trim_document_ids', []):
                if isinstance(item, list) and len(item) > 2 and isinstance(
                        item[2], dict):
                    name = item[2].get('name')
                    if name:
                        res.message_post(
                            body=_("%s trim document line is added.") % (name))
        if 'title_deeds_ids' in vals:
            for item in vals.get('title_deeds_ids', []):
                if isinstance(item, list) and len(item) > 2 and isinstance(
                        item[2], dict):
                    name = item[2].get('name')
                    if name:
                        res.message_post(
                            body=_("%s tittle document line is added.") % (
                                name))

        return res

    def write(self, vals):
        res = super(Building, self).write(vals)
        if 'trim_document_ids' in vals:
            for item in vals.get('trim_document_ids', []):
                if isinstance(item, list) and len(item) > 2 and isinstance(
                        item[2], dict):
                    name = item[2].get('name')
                    if name:
                        self.message_post(
                            body=_("%s trim document line is added.") % (name))
        if 'title_deeds_ids' in vals:
            for item in vals.get('title_deeds_ids', []):
                if isinstance(item, list) and len(item) > 2 and isinstance(
                        item[2], dict):
                    name = item[2].get('name')
                    if name:
                        self.message_post(
                            body=_("%s tittle document line is added.") % (
                                name))

        return res

    def _change_tabs(self):
        buildings = self.env['building'].search([('title_deeds_ids', '!=', False)])
        trim_document_buildings = buildings.title_deeds_ids.filtered(lambda build: build.type == 'trim' and build.building_id != False)
        for trim_document_building in trim_document_buildings:
            trim_document_building.trim_building_id = trim_document_building.building_id.id
            trim_document_building.building_id = False
        # raise UserError(len(trim_document_buildings))


    def action_update_title_deeds(self):
        """Update Title Deeds"""
        _logger.info('called action_update_title_deeds function')
        for rec in self:

            url = "http://localhost:5000/api/TrimFiles/GetTitleDeedByJMC"
            payload = {
                # 'jmcNumber': rec.jmc_number,
            }
            headers = {}
            try:
                url += "?jmcNumber=" + str(rec.jmc_number)
                _logger.info('URL %s', url)
                response = requests.request("GET", url, headers=headers,
                                            data=payload)
                _logger.info('Json Format %s', response.json())
                if response.status_code == 200:
                    res = response.json()
                    _logger.info('data: %s', res['data'])
                    for data in res['data']:
                        _logger.info('filePath: %s', data['filePath'])
                        if data['filePath'] != 'There is no file path for JMC Number provided':
                            record = self.env['title.deeds'].search([
                                ('type', '=', 'title'),
                                ('file_path', '=', data['filePath']),
                                ('building_id', '=', rec.id)
                            ])
                            if not record:
                                vals = {
                                    'building_id': rec.id,
                                    'type': 'title',
                                    'jmc_number': data['jmC_Number'],
                                    'full_jmc_number': data['full_JMC_Number'],
                                    'name': data['title_Deed'],
                                    'number': data['title_Deed_Number'],
                                    'year': data['title_Deed_Year'],
                                    'file_path': data['filePath'],
                                    'message': res['message'],
                                }
                                if vals:
                                    deeds = self.env['title.deeds'].create(vals)
                                    _logger.info('title deeds: %s', deeds)
                        else:
                            _logger.info('Response: %s', data['filePath'])

            except Exception as e:
                raise UserError(e)

    def action_update_trim_documents(self):
        """Update Title Deeds"""
        _logger.info('called action_update_trim_documents function')
        for rec in self:
            url = "http://localhost:5000/api/TrimFiles/GetFilesByJMC"
            payload = {
            }
            headers = {}
            vals = {}
            try:
                url += "?jmcNumber=" + str(rec.jmc_number)
                _logger.info('Trim URL %s', url)
                response = requests.request("GET", url, headers=headers,
                                            data=payload)
                if response.status_code == 200:
                    res = response.json()
                    _logger.info('response: %s', res)
                    _logger.info('data: %s', res['data'])
                    for data in res['data']:
                        _logger.info('data: %s', data)
                        _logger.info('Message: %s', data['message'])
                        record = self.env['title.deeds'].search([
                            ('type', '=', 'trim'),
                            ('full_record_id', '=', data['fullRecordId']),
                            ('trim_building_id', '=', rec.id)
                        ])
                        if not record:
                            vals = {
                                'trim_building_id': rec.id,
                                'type': 'trim',
                                'jmc_number': rec.jmc_number,
                                'name': data['title'],
                                'filename': data['FrontEndFileName'],
                                'full_record_id': data['fullRecordId'],
                                'file_path': data['FilePath'],
                                'uri': data['uri'],
                                'message': data['rcStructuredTitle'],
                            }
                            if vals:
                                deeds = self.env['title.deeds'].create(vals)
                                _logger.info('title deeds: %s', deeds)
                    # _logger.info('data: %s', res['data'])
                    # for res in response.json():
                    #     _logger.info('Trim response details: %s', res)
                    #     _logger.info('Trim response details data: %s', res['data'])
                    #     data = res['data']
                    #     vals = {
                    #         'building_id': rec.id,
                    #         'type': 'trim',
                    #         'jmc_number': data['jmC_Number'],
                    #         'full_jmc_number': data['full_JMC_Number'],
                    #         'name': data['title_Deed'],
                    #         'number': data['title_Deed_Number'],
                    #         'year': data['title_Deed_Year'],
                    #         'file_path': data['filePath'],
                    #     }
                    #     # deeds = self.env['title.deeds'].create(vals)
                    #     _logger.info('Trim response details: %s', deeds)
            except Exception as e:
                raise UserError(e)
