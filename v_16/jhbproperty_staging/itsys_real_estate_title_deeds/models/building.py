from datetime import timedelta
from odoo import api, fields, models, _
import requests
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class Building(models.Model):
    _inherit = 'building'

    def _auto_init(self):
        """Ensure legacy databases always have sync timestamp columns."""
        res = super()._auto_init()
        self._cr.execute(
            """
            ALTER TABLE building
            ADD COLUMN IF NOT EXISTS last_title_deed_sync timestamp,
            ADD COLUMN IF NOT EXISTS last_trim_sync timestamp
            """
        )
        return res

    title_deeds_ids = fields.One2many('title.deeds', 'building_id',
                                      string="Title Deeds")
    type_of_take = fields.Selection([('acquisition', 'Normal acquisition'), ('devaluation', 'devaluation'),
                                     ('discondition', ' discondition of township establishment'),
                                     ('rectification', 'rectification'), ('others', 'others')],
                                    string="Type of take-on",
                                    help="Select the type of take-on")
    trim_document_ids = fields.One2many('title.deeds', 'trim_building_id',

                                      string="Trim Documents")
    last_title_deed_sync = fields.Datetime(string="Last Title Deed Sync", readonly=True)
    last_trim_sync = fields.Datetime(string="Last Trim Document Sync", readonly=True)

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


    @api.model
    def _cron_update_title_deeds(self):
        """Nightly sync: process up to 1000 buildings whose title deeds haven't been synced in the last 7 days."""
        cutoff = fields.Datetime.now() - timedelta(days=7)
        domain = [
            ('jmc_number', '!=', False),
            '|',
            ('last_title_deed_sync', '=', False),
            ('last_title_deed_sync', '<', cutoff),
        ]
        buildings = self.env['building'].search(
            domain, limit=1000, order='last_title_deed_sync asc'
        )
        _logger.info('Cron: syncing title deeds for %d buildings', len(buildings))
        for building in buildings:
            try:
                building.action_update_title_deeds()
            except Exception as exc:
                _logger.exception(
                    'Cron: failed to sync title deeds for building %s (JMC: %s)',
                    building.id, building.jmc_number,
                )
                building.message_post(
                    body=_('Nightly title deed sync failed: %s') % exc,
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )

    @api.model
    def _cron_update_trim_documents(self):
        """Nightly sync: process up to 1000 buildings whose trim documents haven't been synced in the last 7 days."""
        cutoff = fields.Datetime.now() - timedelta(days=7)
        domain = [
            ('jmc_number', '!=', False),
            '|',
            ('last_trim_sync', '=', False),
            ('last_trim_sync', '<', cutoff),
        ]
        buildings = self.env['building'].search(
            domain, limit=1000, order='last_trim_sync asc'
        )
        _logger.info('Cron: syncing trim documents for %d buildings', len(buildings))
        for building in buildings:
            try:
                building.action_update_trim_documents()
            except Exception as exc:
                _logger.exception(
                    'Cron: failed to sync trim documents for building %s (JMC: %s)',
                    building.id, building.jmc_number,
                )
                building.message_post(
                    body=_('Nightly trim document sync failed: %s') % exc,
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )

    def action_update_title_deeds(self):
        """Update Title Deeds"""
        _logger.info('called action_update_title_deeds function')
        for rec in self:
            if not rec.jmc_number:
                raise UserError(
                    _('Please set a JMC Number before updating title deeds.')
                )

            url = "http://localhost:5000/api/TrimFiles/GetTitleDeedByJMC"
            try:
                _logger.info('URL %s', url)
                response = requests.get(
                    url,
                    params={'jmcNumber': rec.jmc_number},
                    timeout=30,
                )
                response.raise_for_status()
                res = response.json()
            except requests.exceptions.RequestException as exc:
                _logger.exception(
                    'Failed to fetch title deeds for building %s', rec.id)
                raise UserError(
                    _('Could not retrieve title deeds for JMC Number %s.') %
                    rec.jmc_number
                ) from exc
            except ValueError as exc:
                _logger.exception(
                    'Invalid JSON while fetching title deeds for building %s',
                    rec.id)
                raise UserError(
                    _('The title deeds service returned an invalid response for JMC Number %s.') %
                    rec.jmc_number
                ) from exc

            data_list = res.get('data') or []
            _logger.info('title deeds payload: %s', data_list)
            for data in data_list:
                file_path = data.get('filePath')
                _logger.info('filePath: %s', file_path)
                if not file_path or file_path == 'There is no file path for JMC Number provided':
                    _logger.info('Response: %s', file_path)
                    continue

                record = self.env['title.deeds'].search([
                    ('type', '=', 'title'),
                    ('file_path', '=', file_path),
                    ('building_id', '=', rec.id)
                ], limit=1)
                if record:
                    continue

                vals = {
                    'building_id': rec.id,
                    'type': 'title',
                    'jmc_number': data.get('jmC_Number') or rec.jmc_number,
                    'full_jmc_number': data.get('full_JMC_Number'),
                    'name': data.get('title_Deed'),
                    'number': data.get('title_Deed_Number'),
                    'year': data.get('title_Deed_Year'),
                    'file_path': file_path,
                    'message': res.get('message'),
                }
                deeds = self.env['title.deeds'].create(vals)
                _logger.info('title deeds: %s', deeds)
            rec.last_title_deed_sync = fields.Datetime.now()

    def action_update_trim_documents(self):
        """Update Title Deeds"""
        _logger.info('called action_update_trim_documents function')
        for rec in self:
            if not rec.jmc_number:
                raise UserError(
                    _('Please set a JMC Number before updating trim documents.')
                )

            url = "http://localhost:5000/api/TrimFiles/GetFilesByJMC"
            try:
                _logger.info('Trim URL %s', url)
                response = requests.get(
                    url,
                    params={'jmcNumber': rec.jmc_number},
                    timeout=30,
                )
                response.raise_for_status()
                res = response.json()
            except requests.exceptions.RequestException as exc:
                _logger.exception(
                    'Failed to fetch trim documents for building %s', rec.id)
                raise UserError(
                    _('Could not retrieve trim documents for JMC Number %s.') %
                    rec.jmc_number
                ) from exc
            except ValueError as exc:
                _logger.exception(
                    'Invalid JSON while fetching trim documents for building %s',
                    rec.id)
                raise UserError(
                    _('The trim documents service returned an invalid response for JMC Number %s.') %
                    rec.jmc_number
                ) from exc

            data_list = res.get('data') or []
            _logger.info('response: %s', res)
            _logger.info('data: %s', data_list)
            for data in data_list:
                _logger.info('data: %s', data)
                _logger.info('Message: %s', data.get('message'))
                full_record_id = data.get('fullRecordId')
                if not full_record_id:
                    continue

                record = self.env['title.deeds'].search([
                    ('type', '=', 'trim'),
                    ('full_record_id', '=', full_record_id),
                    ('trim_building_id', '=', rec.id)
                ], limit=1)
                if record:
                    continue

                vals = {
                    'trim_building_id': rec.id,
                    'type': 'trim',
                    'jmc_number': rec.jmc_number,
                    'name': data.get('title'),
                    'filename': data.get('FrontEndFileName'),
                    'full_record_id': full_record_id,
                    'file_path': data.get('FilePath'),
                    'uri': data.get('uri'),
                    'message': data.get('rcStructuredTitle') or data.get('message'),
                }
                deeds = self.env['title.deeds'].create(vals)
                _logger.info('title deeds: %s', deeds)
            rec.last_trim_sync = fields.Datetime.now()
