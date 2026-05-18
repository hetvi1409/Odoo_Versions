# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from email.policy import default
import base64
from io import BytesIO

from odoo import api, fields, models
import datetime
from odoo.tools.translate import _
import calendar
from odoo.exceptions import UserError, AccessError
from datetime import time, datetime, date, timedelta
from openpyxl import load_workbook


class BuildingApprovalBulkImport(models.Model):
    _name = "building.approval.bulk.import"
    _description = "Building Approval Bulk Import"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default=lambda self: _('New Import'), tracking=True)
    import_type = fields.Selection([
        ('acquisition', 'Building Approval/Acquisition'),
        ('disposal', 'Building Removal/Disposal Approval'),
    ], string='Import Type', required=True, tracking=True)
    upload_file = fields.Binary(string='Upload Your File', attachment=True)
    upload_filename = fields.Char(string='File Name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('imported', 'Imported'),
    ], string='Status', default='draft', readonly=True, tracking=True)
    imported_count = fields.Integer(string='Imported Records', compute='_compute_import_counters', readonly=True)
    failed_count = fields.Integer(string='Failed Records', compute='_compute_import_counters', readonly=True)
    skipped_count = fields.Integer(string='Skipped Records', compute='_compute_import_counters', readonly=True)
    acquisition_line_ids = fields.One2many(
        'building.approval',
        'bulk_import_id',
        string='Building Approval Records'
    )
    disposal_line_ids = fields.One2many(
        'building.removal.approval',
        'bulk_import_id',
        string='Building Removal Approval Records'
    )
    status_line_ids = fields.One2many(
        'building.approval.bulk.import.status',
        'bulk_import_id',
        string='Import Status Lines'
    )
    failed_status_line_ids = fields.One2many(
        'building.approval.bulk.import.status',
        compute='_compute_failed_status_lines',
        string='Import Status Lines (Failed/Skipped)',
        readonly=True,
    )

    @api.onchange('upload_filename')
    def _onchange_upload_filename(self):
        for record in self:
            if record.upload_filename:
                record.name = record.upload_filename

    @api.depends('status_line_ids.status')
    def _compute_import_counters(self):
        for record in self:
            imported = 0
            failed = 0
            skipped = 0
            for line in record.status_line_ids:
                if line.status == 'imported':
                    imported += 1
                elif line.status == 'not_found':
                    failed += 1
                elif line.status == 'skipped':
                    skipped += 1
            record.imported_count = imported
            record.failed_count = failed
            record.skipped_count = skipped

    @api.depends('status_line_ids', 'status_line_ids.status')
    def _compute_failed_status_lines(self):
        for record in self:
            record.failed_status_line_ids = record.status_line_ids.filtered(
                lambda l: l.status in ('not_found', 'skipped')
            )

    @staticmethod
    def _normalize_header(value):
        if value is None:
            return ''
        return ' '.join(str(value).strip().lower().split())

    def _find_header_row(self, worksheet, required_headers):
        max_scan_row = min(worksheet.max_row, 40)
        for row_index in range(1, max_scan_row + 1):
            row_values = {
                self._normalize_header(worksheet.cell(row=row_index, column=column).value)
                for column in range(1, worksheet.max_column + 1)
            }
            row_values.discard('')
            if all(header in row_values for header in required_headers):
                return row_index
        raise UserError(_('Unable to find the expected header row in the first sheet.'))

    def _get_column(self, header_map, possible_names, required=True):
        for candidate in possible_names:
            if candidate in header_map:
                return header_map[candidate]
        if required:
            raise UserError(_('Missing expected column(s): %s') % ', '.join(possible_names))
        return False

    @staticmethod
    def _to_date(value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str) and value.strip():
            return fields.Date.to_date(value)
        return False

    def _cleanup_existing_import_lines(self):
        self.ensure_one()
        if self.import_type == 'acquisition':
            lines = self.acquisition_line_ids
        else:
            lines = self.disposal_line_ids

        non_draft = lines.filtered(lambda l: l.state != 'draft')
        if non_draft:
            raise UserError(_('Only draft imported lines can be replaced.'))
        lines.unlink()
        self.status_line_ids.sudo().unlink()

    def _get_building_jmc_map(self, codes):
        building_model = self.env['building']
        if 'jmc_number' not in building_model._fields:
            raise UserError(_('Building JMC Number is not available. Ensure the Property Update module is installed and upgraded.'))

        return {
            rec.jmc_number: rec
            for rec in building_model.search([('jmc_number', 'in', list(set(codes)))])
            if rec.jmc_number
        }

    def _import_acquisition_rows(self, worksheet):
        required_headers = ['jmc number', 'property description', 'region']
        header_row = self._find_header_row(worksheet, required_headers)
        header_map = {
            self._normalize_header(worksheet.cell(row=header_row, column=column).value): column
            for column in range(1, worksheet.max_column + 1)
            if self._normalize_header(worksheet.cell(row=header_row, column=column).value)
        }

        code_col = self._get_column(header_map, ['jmc number', 'asset number'])
        name_col = self._get_column(header_map, ['property description', 'asset description'])
        region_col = self._get_column(header_map, ['region', 'mun region'])
        registration_date_col = self._get_column(header_map, ['registration date'], required=False)
        # New optional columns from Excel
        location_col = self._get_column(header_map, ['location'], required=False)
        zoning_col = self._get_column(header_map, ['zoning'], required=False)
        ward_col = self._get_column(header_map, ['ward'], required=False)
        title_deed_col = self._get_column(header_map, ['title deed number', 'title deed'], required=False)
        area_col = self._get_column(header_map, ['area'], required=False)
        value_col = self._get_column(header_map, ['value', 'property value'], required=False)
        sg_id_col = self._get_column(header_map, ['sg id', 'sg_id'], required=False)
        comments_col = self._get_column(header_map, ['comments', 'notes'], required=False)

        company_partner = self.env.company.partner_id
        if not company_partner:
            raise UserError(_('Please set a company partner before importing acquisition records.'))

        count = 0
        status_vals = []
        for row_index in range(header_row + 1, worksheet.max_row + 1):
            code = worksheet.cell(row=row_index, column=code_col).value
            description = worksheet.cell(row=row_index, column=name_col).value
            region_name = worksheet.cell(row=row_index, column=region_col).value
            if not code and not description and not region_name:
                continue

            region = False
            if region_name:
                region = self.env['regions'].search([
                    ('name', 'ilike', str(region_name).strip())
                ], limit=1)

            purchase_date = False
            if registration_date_col:
                purchase_date = self._to_date(worksheet.cell(row=row_index, column=registration_date_col).value)

            vals = {
                'name': str(description or code).strip(),
                'code': str(code).strip() if code else False,
                'region_id': region.id if region else False,
                'partner_id': company_partner.id,
                'purchase_date': purchase_date,
                'state': 'draft',
                'latitude': 0.0,
                'longitude': 0.0,
                'document_id': self.upload_file,
                'bulk_import_id': self.id,
            }
            # Add optional columns
            if location_col:
                location_val = worksheet.cell(row=row_index, column=location_col).value
                vals['location'] = str(location_val).strip() if location_val else False
            if zoning_col:
                zoning_val = worksheet.cell(row=row_index, column=zoning_col).value
                vals['zoning'] = str(zoning_val).strip() if zoning_val else False
            if ward_col:
                ward_val = worksheet.cell(row=row_index, column=ward_col).value
                vals['ward'] = str(ward_val).strip() if ward_val else False
            if title_deed_col:
                title_deed_val = worksheet.cell(row=row_index, column=title_deed_col).value
                vals['title_deed_number'] = str(title_deed_val).strip() if title_deed_val else False
            if area_col:
                area_val = worksheet.cell(row=row_index, column=area_col).value
                if area_val:
                    try:
                        vals['area'] = float(area_val)
                    except (ValueError, TypeError):
                        vals['area'] = False
            if value_col:
                value_val = worksheet.cell(row=row_index, column=value_col).value
                if value_val:
                    try:
                        vals['value'] = float(value_val)
                    except (ValueError, TypeError):
                        vals['value'] = False
            if sg_id_col:
                sg_id_val = worksheet.cell(row=row_index, column=sg_id_col).value
                vals['sg_id'] = str(sg_id_val).strip() if sg_id_val else False
            if comments_col:
                comments_val = worksheet.cell(row=row_index, column=comments_col).value
                vals['comments'] = str(comments_val).strip() if comments_val else False

            self.env['building.approval'].create(vals)
            count += 1
            status_vals.append({
                'bulk_import_id': self.id,
                'row_number': row_index,
                'reference': str(code).strip() if code else str(description or ''),
                'display_name': str(description or code or ''),
                'status': 'imported',
                'message': _('Imported successfully.'),
            })

        if status_vals:
            self.env['building.approval.bulk.import.status'].sudo().create(status_vals)
        return {
            'count': count,
            'missing_codes': [],
            'failed_count': 0,
            'skipped_count': 0,
        }

    def _import_disposal_rows(self, worksheet):
        required_headers = ['asset number', 'comments']
        header_row = self._find_header_row(worksheet, required_headers)
        header_map = {
            self._normalize_header(worksheet.cell(row=header_row, column=column).value): column
            for column in range(1, worksheet.max_column + 1)
            if self._normalize_header(worksheet.cell(row=header_row, column=column).value)
        }

        code_col = self._get_column(header_map, ['asset number', 'jmc number'])
        comments_col = self._get_column(header_map, ['comments', 'notes'])
        registration_date_col = self._get_column(header_map, ['registration date'], required=False)
        # New optional columns from Excel
        asset_description_col = self._get_column(header_map, ['asset description', 'description'], required=False)
        location_col = self._get_column(header_map, ['location'], required=False)
        mun_region_col = self._get_column(header_map, ['mun region', 'region'], required=False)
        zoning_col = self._get_column(header_map, ['zoning'], required=False)
        title_deed_col = self._get_column(header_map, ['title deed number', 'title deed'], required=False)
        book_value_col = self._get_column(header_map, ['historical book value', 'historical_amount', 'book value'], required=False)

        codes = []
        rows_data = []
        skipped_vals = []
        for row_index in range(header_row + 1, worksheet.max_row + 1):
            code = worksheet.cell(row=row_index, column=code_col).value
            comments = worksheet.cell(row=row_index, column=comments_col).value
            if not code and not comments:
                continue
            normalized_code = str(code).strip() if code else False
            if not normalized_code:
                skipped_vals.append({
                    'bulk_import_id': self.id,
                    'row_number': row_index,
                    'reference': str(code or ''),
                    'display_name': str(comments or ''),
                    'status': 'skipped',
                    'message': _('Skipped: missing Asset Number / JMC Number.'),
                })
                continue
            rows_data.append((row_index, normalized_code, comments))
            codes.append(normalized_code)

        building_map = self._get_building_jmc_map(codes)
        missing_codes = sorted(set(codes) - set(building_map.keys()))

        count = 0
        failed_count = 0
        skipped_count = len(skipped_vals)
        status_vals = list(skipped_vals)
        for row_index, code, comments in rows_data:
            if code not in building_map:
                failed_count += 1
                status_vals.append({
                    'bulk_import_id': self.id,
                    'row_number': row_index,
                    'reference': code,
                    'display_name': str(comments or ''),
                    'status': 'not_found',
                    'message': _('No matching Building found.'),
                })
                continue

            removal_date = False
            if registration_date_col:
                removal_date = self._to_date(worksheet.cell(row=row_index, column=registration_date_col).value)
            region = False
            if mun_region_col:
                region_name = worksheet.cell(row=row_index, column=mun_region_col).value
                if region_name:
                    region = self.env['regions'].search([
                        ('name', 'ilike', str(region_name).strip())
                    ], limit=1)
            vals = {
                'building_id': building_map[code].id,
                'removal_reason': str(comments or _('Imported from disposal file')),
                'removal_date': removal_date or fields.Date.context_today(self),
                'document_id': self.upload_file,
                'attachment_id': self.upload_file,
                'disposal_method': 'sale',
                'state': 'draft',
                'bulk_import_id': self.id,
            }
            building_vals = {}
            # Add optional columns
            if asset_description_col:
                asset_desc_val = worksheet.cell(row=row_index, column=asset_description_col).value
                vals['asset_description'] = str(asset_desc_val).strip() if asset_desc_val else False
                if asset_desc_val:
                    building_vals['description'] = str(asset_desc_val).strip()
            if location_col:
                location_val = worksheet.cell(row=row_index, column=location_col).value
                vals['location'] = str(location_val).strip() if location_val else False
                if location_val:
                    building_vals['location'] = str(location_val).strip()
            if region:
                building_vals['region_id'] = region.id
            if zoning_col:
                zoning_val = worksheet.cell(row=row_index, column=zoning_col).value
                vals['zoning'] = str(zoning_val).strip() if zoning_val else False
                if zoning_val:
                    building_vals['zoning'] = str(zoning_val).strip()
            if title_deed_col:
                title_deed_val = worksheet.cell(row=row_index, column=title_deed_col).value
                vals['title_deed_number'] = str(title_deed_val).strip() if title_deed_val else False
                if title_deed_val:
                    building_vals['title_deed_number'] = str(title_deed_val).strip()
            if book_value_col:
                book_value_val = worksheet.cell(row=row_index, column=book_value_col).value
                if book_value_val:
                    try:
                        vals['historical_book_value'] = float(book_value_val)
                        building_vals['historical_amount'] = float(book_value_val)
                    except (ValueError, TypeError):
                        vals['historical_book_value'] = False
            if comments:
                vals['notes'] = str(comments)
                building_vals['note'] = str(comments)

            if building_vals:
                building_map[code].write(building_vals)

            self.env['building.removal.approval'].create(vals)
            count += 1
            status_vals.append({
                'bulk_import_id': self.id,
                'row_number': row_index,
                'reference': code,
                'display_name': building_map[code].name,
                'status': 'imported',
                'message': _('Imported successfully.'),
            })

        if status_vals:
            self.env['building.approval.bulk.import.status'].sudo().create(status_vals)
        return {
            'count': count,
            'missing_codes': missing_codes,
            'failed_count': failed_count,
            'skipped_count': skipped_count,
        }

    def action_import_file(self):
        self.ensure_one()
        if self.state == 'imported':
            raise UserError(_('This import record is already imported.'))
        if not self.import_type:
            raise UserError(_('Select the import type first.'))
        if not self.upload_file:
            raise UserError(_('Upload a file before importing.'))

        if self.upload_filename:
            self.name = self.upload_filename

        file_content = base64.b64decode(self.upload_file)
        workbook = load_workbook(filename=BytesIO(file_content), data_only=True)
        if not workbook.sheetnames:
            raise UserError(_('The uploaded workbook has no sheets.'))

        self._cleanup_existing_import_lines()
        worksheet = workbook[workbook.sheetnames[0]]
        if self.import_type == 'acquisition':
            result = self._import_acquisition_rows(worksheet)
        else:
            result = self._import_disposal_rows(worksheet)

        count = result.get('count', 0)
        missing_codes = result.get('missing_codes', [])

        self.write({
            'state': 'imported',
        })

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Building Approval Bulk Import'),
            'res_model': 'building.approval.bulk.import',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': self.id,
            'target': 'current',
        }

        message = _('%s records imported successfully.') % count
        if missing_codes:
            message += _(' No matching Building found for: %s') % ', '.join(missing_codes)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import Completed'),
                'message': message,
                'type': 'warning' if missing_codes else 'success',
                'sticky': bool(missing_codes),
                'next': action,
            },
        }

    def action_view_imported_records(self):
        self.ensure_one()
        if self.import_type == 'acquisition':
            return {
                'type': 'ir.actions.act_window',
                'name': _('Imported Building Approvals'),
                'res_model': 'building.approval',
                'view_mode': 'tree,form',
                'views': [(False, 'tree'), (False, 'form')],
                'domain': [('bulk_import_id', '=', self.id)],
                'context': {'create': False},
                'target': 'current',
            }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Imported Building Removal Approvals'),
            'res_model': 'building.removal.approval',
            'view_mode': 'tree,form',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('bulk_import_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current',
        }

    def action_view_imported_acquisition(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Imported Building Approvals'),
            'res_model': 'building.approval',
            'view_mode': 'tree,form',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('bulk_import_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current',
        }

    def action_view_imported_disposal(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Imported Building Removal Approvals'),
            'res_model': 'building.removal.approval',
            'view_mode': 'tree,form',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('bulk_import_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current',
        }


class BuildingApprovalBulkImportStatus(models.Model):
    _name = 'building.approval.bulk.import.status'
    _description = 'Building Approval Bulk Import Status'
    _order = 'row_number asc, id asc'

    bulk_import_id = fields.Many2one('building.approval.bulk.import', required=True, ondelete='cascade')
    row_number = fields.Integer(string='Row')
    reference = fields.Char(string='Reference')
    display_name = fields.Char(string='Description')
    status = fields.Selection([
        ('imported', 'Imported'),
        ('not_found', 'No Matching Building'),
        ('skipped', 'Skipped'),
    ], string='Import Status', required=True)
    message = fields.Char(string='Message')


class BuildingApproval(models.Model):
    _name = "building.approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', size=16)
    region_id = fields.Many2one('regions', 'Region', )
    partner_id = fields.Many2one('res.partner', 'Owner',required="True")
    purchase_date = fields.Date('Purchase Date')
    launch_date = fields.Date(string="Launch Date")
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    company_id = fields.Many2one('res.company', string="Company", groups="base.group_multi_company")
    active = fields.Boolean('Active',
                            help="If the active field is set to False, it will allow you to hide the top without removing it.",
                            default=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('send', 'Send for Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ], string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    redirect_url = fields.Char(compute="_compute_redirect_url",store="True")
    latitude = fields.Float("Latitude", digits=(9, 6), required=True)
    longitude = fields.Float("Longitude", digits=(9, 6), required=True)
    asset_id = fields.Many2one('building')
    document_id = fields.Binary(string="Approval Document",required="True")
    bulk_import_id = fields.Many2one('building.approval.bulk.import', string='Bulk Import')
    # Unmapped acquisition Excel columns
    location = fields.Char(string='Location')
    zoning = fields.Char(string='Zoning')
    ward = fields.Char(string='Ward')
    title_deed_number = fields.Char(string='Title Deed Number')
    area = fields.Float(string='Area (m²)', digits=(12, 2))
    value = fields.Float(string='Market Value', digits=(12, 2))
    sg_id = fields.Char(string='SG ID')
    comments = fields.Text(string='Notes')


    @api.depends('state')
    def _compute_redirect_url(self):
        for record in self:
            if record.state != 'approved':
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                base_url += '/web#id=%d&view_type=list&model=%s' % (record.id, 'building.approval')
                record.redirect_url = base_url
            else:
                asset_id = self.env['building'].search([('approval_request_id','=',record.id)])
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                base_url += '/web#id=%d&view_type=list&model=%s' % (asset_id.id, 'building')
                record.redirect_url = base_url



    def action_approve(self):
        for record in self:
            record.state = 'approved'
            message_body = (
                f" Asset {record.name} has been approved. "
            )
            mail_values = {}

            if record.partner_id.email:  # Ensure the partner has an email address
                mail_values = {
                    'email_to': record.partner_id.email,
                    # Other values can be set as needed
                }

            # Check if a building with matching jmc_number already exists
            existing_building = None
            if record.code:
                existing_building = self.env['building'].search([
                    ('jmc_number', '=', record.code)
                ], limit=1)

            if existing_building:
                # Link to existing building
                record.asset_id = existing_building.id
                message_body += f"<br/><strong style='color: orange;'>⚠️ WARNING:</strong> Building with JMC Number {record.code} already exists. Approval record has been linked to existing building: <strong>{existing_building.name}</strong>"
            else:
                # Create new building
                vals = {
                    'name': record.name,
                    'code': record.code,
                    'region_id': record.region_id.id if record.region_id else False,
                    'partner_id': record.partner_id.id if record.partner_id else False,
                    'purchase_date': record.purchase_date,
                    'launch_date': record.launch_date,
                    'account_analytic_id': record.account_analytic_id.id if record.account_analytic_id else False,
                    'company_id': record.company_id.id if record.company_id else False,
                    'latitude': record.latitude,
                    'longitude': record.longitude,
                    'jmc_number': record.code,  # Set jmc_number to approval code
                    'approval_request_id': record.id,
                    'location': record.location,
                    'zoning': record.zoning,
                    'ward': record.ward,
                    'title_deed_number': record.title_deed_number,
                    'area': record.area,
                    'sg_id': record.sg_id,
                    'market_value': record.value,
                    'note': record.comments,
                    'description': record.name,
                }

                property_id = self.env['building'].create(vals)
                record.asset_id = property_id.id
                message_body += f" New building created with JMC Number {record.code}."

            template = self.env.ref('itsys_real_estate_approval.email_template_approval_confirmed')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.partner_id.id],
            )

        return self._get_post_action_response()

    def action_reject(self):
        for record in self:
            record.state = 'reject'
            message_body = (
                f" Asset {record.name} has been rejected. "
            )
            mail_values = {}

            if record.partner_id.email:  # Ensure the partner has an email address
                mail_values = {
                    'email_to': record.partner_id.email,
                    # Other values can be set as needed
                }
            # Send to all followers and specifically to the Impairment Manager group
            template = self.env.ref('itsys_real_estate_approval.email_template_rejected')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.partner_id.id],
            )

        return self._get_post_action_response()

    def action_submit_for_approval(self):
        """ Submit the asset for approval """
        self.write({'state': 'send'})
        manager_group = self.env.ref('itsys_real_estate_approval.group_property_approval_manager')

        # Get partner objects
        mail_values = {}

        partners = manager_group.users.mapped('partner_id')

        for partner in partners:
            if partner.email:  # Ensure the partner has an email address
                mail_values = {
                    'email_to': partner.email,
                    # Other values can be set as needed
                }
        template = self.env.ref('itsys_real_estate_approval.email_template_to_confirm')
        template.send_mail(self.id, force_send=True, email_values=mail_values)

        # Send an in-app notification
        for asset in self:
            message_body = (
                f" Asset {asset.name} has been submitted for approval. "
            )
            # Send to all followers and specifically to the Impairment Manager group
            manager_group = self.env.ref('itsys_real_estate_approval.group_property_approval_manager')

            partner_ids = manager_group.users.mapped('partner_id.id')

            asset.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=partner_ids,
            )

        return self._get_post_action_response()

    def _get_post_action_response(self):
        params = self.env.context.get('params') or {}
        if params.get('target') == 'new' or self.env.context.get('dialog_size'):
            return {'type': 'ir.actions.act_window_close'}
        return True

    def action_view_building(self):
        """Opens the related building form view."""
        self.ensure_one()  # Ensure the record exists
        if self.asset_id:  # Check if the building exists
            return {
                'type': 'ir.actions.act_window',
                'name': 'Building',
                'res_model': 'building',
                'view_mode': 'form',
                'res_id': self.asset_id.id,  # Open the specific building
                'target': 'current',  # Open in the current window
            }


class Building(models.Model):
    _inherit = "building"

    approval_request_id = fields.Many2one('building.approval')
    # Defensive fallback so views referencing building.jmc_number can load even
    # before/without property_update metadata being refreshed in the database.
    jmc_number = fields.Char(string='JMC Number')
    # Additional property fields from Excel imports
    location = fields.Char(string='Location')
    zoning = fields.Char(string='Zoning')
    ward = fields.Char(string='Ward')
    title_deed_number = fields.Char(string='Title Deed Number')
    area = fields.Float(string='Area (m²)', digits=(12, 2))
    sg_id = fields.Char(string='SG ID')
    market_value = fields.Float(string='Market Value', digits=(12, 2))
    historical_amount = fields.Float(string='Historical Amount', digits=(12, 2))

    def action_remove_asset(self):
        """Opens the Building Removal Approval form view"""
        self.ensure_one()
        record_id = self.env['building.removal.approval'].search([('building_id','=',self.id)])
        if record_id:
            property_condition_label = dict(self._fields['property_condition'].selection).get(self.property_condition)

            record_id.write({
                'notes': property_condition_label
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Remove Building',
                'res_model': 'building.removal.approval',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id':record_id.id,
                'target': 'current',  # Opens in a new window
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Remove Building',
                'res_model': 'building.removal.approval',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_building_id': self.id,
                    'default_notes': dict(self._fields['property_condition'].selection).get(self.property_condition)# Pre-fill the building in the removal approval form
                },
                'target': 'current',  # Opens in a new window
            }



class BuildingRemovalApproval(models.Model):
    _name = "building.removal.approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'building_id'

    removal_date = fields.Date('Removal Request Date', required=True,default=lambda self: fields.Date.context_today(self))
    removal_reason = fields.Text('Reason for Removal', required=True)
    building_id = fields.Many2one('building', 'Building', required=True)
    jmc_number = fields.Char(string='JMC Number', related='building_id.jmc_number', store=True, readonly=True)
    region_id = fields.Many2one('regions', string='Region', related='building_id.region_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string="Company", groups="base.group_multi_company")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('send', 'Sent for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', required=True, readonly=True, tracking=True, default='draft')

    redirect_url = fields.Char(compute="_compute_redirect_url", store=True)
    notes = fields.Html()
    user_id = fields.Many2one('res.users',default=lambda self: self.env.user)
    document_id = fields.Binary(string="Council Approval",required="True")
    selling_input = fields.Float(string='Sell Value')

    attachment_id = fields.Binary(string="Sale Agreement",required="True")
    disposal_method = fields.Selection([
        ('sale', 'Sale'),
        ('donation', 'Donation'),
        ('transfer', 'Transfer'),
        ('scrapping', 'Scrapping'),
        ('other', 'Other')
    ], string='Disposal Method', required=True)
    bulk_import_id = fields.Many2one('building.approval.bulk.import', string='Bulk Import')
    # Unmapped disposal Excel columns
    asset_description = fields.Char(string='Description')
    location = fields.Char(string='Location')
    zoning = fields.Char(string='Zoning')
    title_deed_number = fields.Char(string='Title Deed Number')
    historical_book_value = fields.Float(string='Historical Amount', digits=(12, 2))


    @api.depends('state')
    def _compute_redirect_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            if record.state != 'approved':
                base_url += '/web#id=%d&view_type=list&model=%s' % (record.id, 'building.removal.approval')
            else:
                base_url += '/web#id=%d&view_type=list&model=%s' % (record.building_id.id, 'building')
            record.redirect_url = base_url

    def action_submit_for_approval(self):
        """ Submit the removal request for approval """
        self.write({'state': 'send'})
        manager_group = self.env.ref('itsys_real_estate_approval.group_property_approval_manager')

        mail_values = {}
        partners = manager_group.users.mapped('partner_id')

        for partner in partners:
            if partner.email:
                mail_values = {'email_to': partner.email}

        template = self.env.ref('itsys_real_estate_approval.email_template_removal_to_confirm')
        template.send_mail(self.id, force_send=True, email_values=mail_values)

        for removal in self:
            message_body = f"Removal request for building {removal.building_id.name} has been submitted for approval."
            partner_ids = manager_group.users.mapped('partner_id.id')
            removal.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                 partner_ids=partner_ids)

        return self._get_post_action_response()

    def action_approve(self):
        """ Approve the removal request """
        for record in self:
            record.state = 'approved'
            record.building_id.active = False  # Mark the building as inactive (removed)

            record.building_id.state = 'disposed'
            message_body = f"Building {record.building_id.name} has been approved for removal."
            mail_values = {}
            if record.user_id.partner_id.email:
                mail_values = {'email_to': record.user_id.partner_id.email}

            template = self.env.ref('itsys_real_estate_approval.email_template_removal_approved')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                partner_ids=[record.user_id.partner_id.id])

        return self._get_post_action_response()

    def action_reject(self):
        """ Reject the removal request """
        for record in self:
            record.state = 'rejected'

            message_body = f"Removal request for building {record.building_id.name} has been rejected."
            mail_values = {}
            if record.user_id.partner_id.email:
                mail_values = {'email_to': record.user_id.partner_id.email}

            template = self.env.ref('itsys_real_estate_approval.email_template_removal_rejected')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                partner_ids=[record.user_id.partner_id.id])

        return self._get_post_action_response()

    def _get_post_action_response(self):
        params = self.env.context.get('params') or {}
        if params.get('target') == 'new' or self.env.context.get('dialog_size'):
            return {'type': 'ir.actions.act_window_close'}
        return True
