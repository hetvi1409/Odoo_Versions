from datetime import datetime, timedelta, date
import xlrd
import re
import tempfile
import binascii
import base64
from io import BytesIO
import openpyxl
from odoo import fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AssetImport(models.TransientModel):
    _name = 'asset.import'
    _description = 'Asset import'

    file = fields.Binary(string='File', required=True)

    def _normalize_header(self, value):
        header = str(value or '').strip().lower()
        header = re.sub(r'\s+', ' ', header)
        return re.sub(r'[^a-z0-9 ]', '', header)

    def _find_column_index(self, header_map, aliases, fallback_index=None):
        for alias in aliases:
            idx = header_map.get(self._normalize_header(alias))
            if idx is not None:
                return idx
        return fallback_index

    def _clean_text(self, value):
        if value in (None, False):
            return ''
        return str(value).strip()

    def _get_or_create_by_name(self, model_name, value, extra_vals=None):
        name = self._clean_text(value)
        if not name:
            return self.env[model_name]
        record = self.env[model_name].sudo().search([('name', '=', name)], limit=1)
        if record:
            return record
        create_vals = {'name': name}
        if extra_vals:
            create_vals.update(extra_vals)
        return self.env[model_name].sudo().create(create_vals)

    def _row_value(self, row, index, default=''):
        if index is None or index >= len(row):
            return default
        value = row[index]
        return default if value is None else value

    def _parse_date_value(self, value, row_number, field_label):
        if not value:
            return False

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if isinstance(value, (int, float)):
            try:
                excel_base_date = datetime(1899, 12, 30)
                return (excel_base_date + timedelta(days=float(value))).date()
            except Exception:
                _logger.warning(
                    "Unable to parse numeric %s '%s' at row %s",
                    field_label,
                    value,
                    row_number,
                )
                return False

        text_value = str(value).strip().lstrip("'")
        for date_format in (
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%d %b %Y",
            "%d %b %y",
            "%d %B %Y",
            "%d %B %y",
            "%d %m %Y",
        ):
            try:
                return datetime.strptime(text_value, date_format).date()
            except ValueError:
                continue

        _logger.warning(
            "Unknown %s format '%s' at row %s",
            field_label,
            text_value,
            row_number,
        )
        return False

    def _parse_integer_value(self, value, row_number, field_label):
        if value in (None, '', '-'):
            return False

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        text_value = str(value).strip()
        if text_value.isdigit():
            return int(text_value)

        match = re.search(r'\d+', text_value)
        if match:
            return int(match.group(0))

        _logger.warning(
            "Unknown %s numeric format '%s' at row %s",
            field_label,
            text_value,
            row_number,
        )
        return False

    def _parse_float_value(self, value):
        if value in (None, '', '-', False):
            return False
        if isinstance(value, (int, float)):
            return float(value)
        cleaned = str(value).replace(',', '').strip()
        if not cleaned:
            return False
        try:
            return float(cleaned)
        except ValueError:
            return False

    def _find_header_row_index(self, rows):
        max_scan = min(len(rows), 30)
        for idx in range(max_scan):
            row = rows[idx]
            normalized = {
                self._normalize_header(cell)
                for cell in row if cell not in (None, '')
            }
            if {'date', 'supplier'}.issubset(normalized) and (
                'unique asset no barcodetag' in normalized
                or 'unique asset no barcodetag' in ''.join(normalized)
            ):
                return idx
        return 0

    def _load_excel_rows(self):
        try:
            file_content = base64.b64decode(self.file)
        except binascii.Error:
            raise UserError('Error decoding the uploaded file.')

        if not file_content:
            raise UserError('The uploaded file is empty.')

        xlsx_error = None
        try:
            workbook = openpyxl.load_workbook(
                BytesIO(file_content),
                data_only=True,
                read_only=True,
            )
            sheet = workbook.active
            return list(sheet.iter_rows(values_only=True))
        except Exception as exc:
            xlsx_error = exc

        try:
            workbook = xlrd.open_workbook(file_contents=file_content)
            sheet = workbook.sheet_by_index(0)
            return [tuple(sheet.row_values(i)) for i in range(sheet.nrows)]
        except Exception as xls_exc:
            xlsx_msg = str(xlsx_error).strip() or repr(xlsx_error)
            xls_msg = str(xls_exc).strip() or repr(xls_exc)
            raise UserError(
                f"Unable to read Excel file. XLSX error: {xlsx_msg}. XLS error: {xls_msg}"
            )

    def action_import_asset(self):
        """Import asset"""
        rows = self._load_excel_rows()
        if not rows:
            raise UserError('The uploaded sheet is empty.')

        header_row_idx = self._find_header_row_index(rows)
        header_row = rows[header_row_idx]
        header_map = {}
        for idx, header in enumerate(header_row):
            if header in (None, ''):
                continue
            header_map.setdefault(self._normalize_header(header), idx)

        column_map = {
            'acquisition_date': self._find_column_index(
                header_map, ['Date', 'Acquisition Date'], fallback_index=0
            ),
            'supplier': self._find_column_index(
                header_map, ['Supplier'], fallback_index=1
            ),
            'payment_number': self._find_column_index(
                header_map, ['Payment Number'], fallback_index=2
            ),
            'order_number': self._find_column_index(
                header_map, ['Order Number'], fallback_index=3
            ),
            'amount': self._find_column_index(
                header_map, ['Amount', 'Original Amount'], fallback_index=4
            ),
            'description': self._find_column_index(
                header_map, ['Description'], fallback_index=6
            ),
            'afs_classification': self._find_column_index(
                header_map,
                ['AFS Classification', 'Classification AFS Classification'],
                fallback_index=9,
            ),
            'asset_model': self._find_column_index(
                header_map, ['Model'], fallback_index=10
            ),
            'serial_number': self._find_column_index(
                header_map, ['Serial Number'], fallback_index=11
            ),
            'unique_asset_no': self._find_column_index(
                header_map,
                ['Unique asset no. (barcode/tag)', 'Unique asset no. (barcode/ tag)'],
                fallback_index=12,
            ),
            'location': self._find_column_index(
                header_map, ['Location & Office number', 'Location'], fallback_index=13
            ),
            'chief_directorate': self._find_column_index(
                header_map, ['Chief Directorate & Directorate', 'Chief Directorate'], fallback_index=14
            ),
            'custodian': self._find_column_index(
                header_map, ['Custodian / User', 'Custodian/User', 'Custodian'], fallback_index=15
            ),
            'condition': self._find_column_index(
                header_map, ['Condition'], fallback_index=19
            ),
            'life_cycle': self._find_column_index(
                header_map, ['Life Cycle'], fallback_index=20
            ),
            'disposal_date': self._find_column_index(
                header_map, ['Disposal Date'], fallback_index=27
            ),
            'disposal_price': self._find_column_index(
                header_map, ['Disposal Price'], fallback_index=28
            ),
            'disposal_method': self._find_column_index(
                header_map, ['Disposal Method'], fallback_index=29
            ),
        }

        partner_cache = {}
        category_cache = {}
        model_cache = {}
        location_cache = {}
        department_cache = {}
        employee_cache = {}
        condition_cache = {}

        batch_size = 500
        asset_batch_vals = []
        history_meta_batch = []

        def get_cached_record(cache, key, resolver):
            if key in cache:
                return cache[key]
            cache[key] = resolver()
            return cache[key]

        def flush_batch():
            if not asset_batch_vals:
                return
            created_assets = self.env['account.asset'].create(asset_batch_vals)
            history_vals = []
            for created_asset, meta in zip(created_assets, history_meta_batch):
                condition_id = meta.get('condition_id')
                if not condition_id:
                    continue
                history_vals.append({
                    'history_id': created_asset.id,
                    'parent_barcode': meta.get('barcode') or created_asset.alternative_ref,
                    'date_verification': meta.get('date_verification') or fields.Date.today(),
                    'comments': meta.get('condition_name'),
                    'condition': [(6, 0, [condition_id])],
                    'location_id': meta.get('location_id') or False,
                    'major_group_description': meta.get('description'),
                    'is_verified': True,
                    'past_year': str(fields.Date.today().year - 1),
                    'this_year': str(fields.Date.today().year),
                    'asset_verification_user_id': self.env.user.id,
                    'inspector': self.env.user.name,
                })
            if history_vals:
                self.env['asset.verification.history'].sudo().create(history_vals)
            asset_batch_vals.clear()
            history_meta_batch.clear()

        for index, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 2):
            if not any(cell not in (None, '') for cell in row):
                continue

            unique_asset_no = self._clean_text(self._row_value(row, column_map['unique_asset_no']))
            if not unique_asset_no:
                continue

            excel_date = self._parse_date_value(
                self._row_value(row, column_map['acquisition_date']),
                index,
                'acquisition date',
            )
            if not excel_date:
                continue

            description = self._clean_text(self._row_value(row, column_map['description']))
            if not description:
                continue

            supplier_name = self._clean_text(self._row_value(row, column_map['supplier']))
            supplier_det = get_cached_record(
                partner_cache,
                supplier_name,
                lambda: self.env['res.partner'].sudo().search([('name', '=', supplier_name)], limit=1),
            ) if supplier_name else self.env['res.partner']

            afs_name = self._clean_text(self._row_value(row, column_map['afs_classification']))
            afs_classification = get_cached_record(
                category_cache,
                afs_name,
                lambda: self.env['asset.category'].sudo().search([('name', '=', afs_name)], limit=1),
            ) if afs_name else self.env['asset.category']

            model_name = self._clean_text(self._row_value(row, column_map['asset_model']))
            asset_model = get_cached_record(
                model_cache,
                model_name,
                lambda: self.env['account.asset'].sudo().search(
                    [('state', '=', 'model'), ('name', '=', model_name)], limit=1
                ),
            ) if model_name else self.env['account.asset']

            location_name = self._clean_text(self._row_value(row, column_map['location']))
            location_details = get_cached_record(
                location_cache,
                location_name,
                lambda: self._get_or_create_by_name('asset.verification.job.location', location_name),
            ) if location_name else self.env['asset.verification.job.location']

            chief_name = self._clean_text(self._row_value(row, column_map['chief_directorate']))
            chief_directorate = get_cached_record(
                department_cache,
                chief_name,
                lambda: self._get_or_create_by_name('hr.department', chief_name),
            ) if chief_name else self.env['hr.department']

            custodian_name = self._clean_text(self._row_value(row, column_map['custodian']))
            if custodian_name:
                def resolve_employee():
                    employee = self.env['hr.employee'].sudo().search([('name', '=', custodian_name)], limit=1)
                    if not employee:
                        employee = self.env['hr.employee'].sudo().create({
                            'name': custodian_name,
                            'department_id': chief_directorate.id if chief_directorate else False,
                        })
                    return employee

                custodian_user = get_cached_record(employee_cache, custodian_name, resolve_employee)
            else:
                custodian_user = self.env['hr.employee']

            condition_name = self._clean_text(self._row_value(row, column_map['condition']))
            condition = get_cached_record(
                condition_cache,
                condition_name,
                lambda: self._get_or_create_by_name('asset.condition', condition_name),
            ) if condition_name else self.env['asset.condition']

            payment_number = self._parse_integer_value(
                self._row_value(row, column_map['payment_number']),
                index,
                'payment number',
            )
            order_number = self._clean_text(self._row_value(row, column_map['order_number']))
            original_amount = self._parse_float_value(self._row_value(row, column_map['amount']))
            serial_number = self._clean_text(self._row_value(row, column_map['serial_number']))
            life_cycle = self._parse_integer_value(
                self._row_value(row, column_map['life_cycle']),
                index,
                'life cycle',
            )
            formatted_disposal_date = self._parse_date_value(
                self._row_value(row, column_map['disposal_date']),
                index,
                'disposal date',
            )
            disposal_price = self._parse_float_value(self._row_value(row, column_map['disposal_price']))
            disposal_method = self._clean_text(self._row_value(row, column_map['disposal_method']))

            asset_batch_vals.append({
                'name': description,
                'acquisition_date': excel_date,
                'supplier_id': supplier_det.id if supplier_det else False,
                'payment_number': payment_number or False,
                'order_number': order_number,
                'original_value': original_amount or 0.0,
                'description': description,
                'afs_classification': afs_classification.id if afs_classification else False,
                'model_id': asset_model.id if asset_model else False,
                'serial_number': serial_number,
                'alternative_ref': unique_asset_no,
                'job_location_id': location_details.id if location_details else False,
                'department_id': chief_directorate.id if chief_directorate else False,
                'custodian_id': custodian_user.id if custodian_user else False,
                'original_useful_life': life_cycle or False,
                'disposal_date': formatted_disposal_date or False,
                'disposal_price': disposal_price or 0.0,
                'disposal_method': disposal_method,
                'state': 'draft',
            })
            history_meta_batch.append({
                'barcode': unique_asset_no,
                'date_verification': excel_date,
                'condition_id': condition.id if condition else False,
                'condition_name': condition.name if condition else '',
                'location_id': location_details.id if location_details else False,
                'description': description,
            })

            if len(asset_batch_vals) >= batch_size:
                flush_batch()

        flush_batch()
        return True
    def action_import_supplier(self):
        """Importing supplier data from an Excel file into Odoo"""
        try:
            # Decode the base64 file and write it to a temporary file
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(base64.b64decode(self.file))
            fp.close()  # Ensure data is written

            # Load workbook using openpyxl
            book = openpyxl.load_workbook(fp.name, data_only=True)
            sheet = book.active  # Get the active sheet

        except FileNotFoundError:
            raise UserError(
                f'No such file or directory found: {self.file_name}.')
        except binascii.Error:
            raise UserError('Error decoding the uploaded file.')
        except Exception as e:
            raise UserError(
                f"An error occurred while processing the file: {str(e)}")

        # Process each row in the sheet
        for index, row in enumerate(sheet.iter_rows(values_only=True)):
            if index == 0:  # Skip header row
                continue

            try:
                supplier_name = row[1]  # Assuming second column contains supplier name

                if supplier_name:
                    # Check if supplier already exists
                    supplier_det = self.env['res.partner'].sudo().search(
                        [('name', '=', supplier_name)], limit=1)

                    if not supplier_det:
                        self.env['res.partner'].sudo().create({
                            'name': supplier_name
                        })

            except IndexError:
                pass  # Handle cases where row is incomplete

        return True
    def action_import_afs_classification(self):
        """Importing AFS Classification into odoo"""
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(base64.b64decode(self.file))
            fp.close()  # Ensure data is written

            # Load workbook using openpyxl
            book = openpyxl.load_workbook(fp.name, data_only=True)
            sheet = book.active  # Get the active sheet
        except FileNotFoundError:
            raise UserError(
                f'No such file or directory found: {self.file_name}.')
        except binascii.Error:
            raise UserError('Error decoding the uploaded file.')
        except Exception as e:
            raise UserError(
                f"An error occurred while processing the file: {str(e)}")

        # Process each row in the sheet
        for index, row in enumerate(sheet.iter_rows(values_only=True)):
            if index == 0:  # Skip header row
                continue

            try:
                asset_category = row[6]  # Assuming second column contains supplier name

                if asset_category:
                    asset_category_id = self.env['asset.category'].sudo().search([('name', '=', asset_category)], limit=1)

                    if not asset_category_id:
                        self.env['asset.category'].sudo().create({
                            'name': asset_category
                        })

            except IndexError:
                pass  # Handle cases where row is incomplete

        return True

    def action_import_asset_model(self):
        """Importing Asset Model into Odoo from an Excel file"""
        try:
            # Decode and write to a temporary file
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(base64.b64decode(self.file))
            fp.close()  # Ensure data is written

            # Load workbook with openpyxl
            book = openpyxl.load_workbook(fp.name, data_only=True)
            sheet = book.active  # Use the first sheet

        except FileNotFoundError:
            raise UserError(f'No such file or directory found: {self.file_name}.')
        except binascii.Error:
            raise UserError('Error decoding the uploaded file.')
        except Exception as e:
            raise UserError(f"An error occurred while processing the file: {str(e)}")

        # Process each row in the sheet
        for index, row in enumerate(sheet.iter_rows(values_only=True)):
            if index == 0:  # Skip header row
                continue

            try:
                asset_name = row[7]  # Assuming column 8 contains the asset name

                if asset_name:
                    # Check if the asset model already exists
                    asset_model = self.env['account.asset'].sudo().search(
                        [('state', '=', 'model'), ('name', '=', asset_name)], limit=1
                    )

                    if not asset_model:
                        self.env['account.asset'].sudo().create({
                            'name': asset_name,
                            'state': 'model',
                        })

            except IndexError:
                pass  # Handle cases where row is incomplete

        return True

    def action_import_asset_location(self):
        """Import Asset Locations into Odoo from an Excel file"""
        try:
            # Decode base64 file and write it to a temporary file
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(base64.b64decode(self.file))
            fp.close()  # Ensure file is written before reading

            # Load workbook with openpyxl
            book = openpyxl.load_workbook(fp.name, data_only=True)
            sheet = book.active  # Get the first sheet

        except FileNotFoundError:
            raise UserError(f'No such file or directory found: {self.file_name}.')
        except binascii.Error:
            raise UserError('Error decoding the uploaded file.')
        except Exception as e:
            raise UserError(f"An error occurred while processing the file: {str(e)}")

        # Process each row in the sheet
        for index, row in enumerate(sheet.iter_rows(values_only=True)):
            if index == 0:  # Skip the header row
                continue

            try:
                asset_location_name = row[10]  # Assuming column 11 contains the location name

                if asset_location_name:
                    # Check if the location already exists
                    asset_location = self.env['asset.verification.job.location'].sudo().search(
                        [('name', '=', asset_location_name)], limit=1
                    )

                    if not asset_location:
                        self.env['asset.verification.job.location'].sudo().create({
                            'name': asset_location_name,
                        })

            except IndexError:
                pass  # Skip if the row is incomplete

        return True

    def action_import_chief_directorate(self):
        """Import Chief Directorate into Odoo from an Excel file"""
        try:
            # Decode the base64 file and write it to a temporary file
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(base64.b64decode(self.file))
            fp.close()  # Ensure data is written before reading

            # Load workbook with openpyxl
            book = openpyxl.load_workbook(fp.name, data_only=True)
            sheet = book.active  # Use the first sheet

        except FileNotFoundError:
            raise UserError(f'No such file or directory found: {self.file_name}.')
        except binascii.Error:
            raise UserError('Error decoding the uploaded file.')
        except Exception as e:
            raise UserError(f"An error occurred while processing the file: {str(e)}")

        # Process each row in the sheet
        for index, row in enumerate(sheet.iter_rows(values_only=True)):
            if index == 0:  # Skip the header row
                continue

            try:
                chief_directorate_name = row[11]  # Assuming column 12 contains the chief directorate name

                if chief_directorate_name:
                    # Check if the chief directorate already exists
                    chief_directorate = self.env['hr.department'].sudo().search(
                        [('name', '=', chief_directorate_name)], limit=1
                    )

                    if not chief_directorate:
                        self.env['hr.department'].sudo().create({
                            'name': chief_directorate_name,
                        })

            except IndexError:
                pass  # Handle cases where row is incomplete

        return True


    def action_import_custodian(self):
        """Import Custodian Users into Odoo from an Excel file"""
        try:
            # Decode the base64 file and write it to a temporary file
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(base64.b64decode(self.file))
            fp.close()  # Ensure data is written before reading

            # Load workbook with openpyxl
            book = openpyxl.load_workbook(fp.name, data_only=True)
            sheet = book.active  # Use the first sheet

        except FileNotFoundError:
            raise UserError(f'No such file or directory found: {self.file_name}.')
        except binascii.Error:
            raise UserError('Error decoding the uploaded file.')
        except Exception as e:
            raise UserError(f"An error occurred while processing the file: {str(e)}")

        # Process each row in the sheet
        for index, row in enumerate(sheet.iter_rows(values_only=True)):
            if index == 0:  # Skip the header row
                continue

            try:
                custodian_name = row[12]  # Assuming column 13 contains the custodian name

                # Replace multiple spaces between words with a single space
                if custodian_name is not None:
                    custodian_name.strip()
                    custodian_name_update = re.sub(r'\s+', ' ', custodian_name.strip())

                    if custodian_name_update:
                        # Check if the custodian already exists
                        custodian_user = self.env['hr.employee'].sudo().search(
                            [('name', '=', custodian_name_update)], limit=1
                        )

                        if not custodian_user:
                            self.env['hr.employee'].sudo().create({
                                'name': custodian_name_update,
                            })

            except IndexError:
                pass  # Handle cases where row is incomplete

        return True

    def action_import_classification_custodian(self):
        try:
            # Decode the base64 file and write it to a temporary file
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(base64.b64decode(self.file))
            fp.close()  # Ensure data is written before reading

            # Load workbook with openpyxl
            book = openpyxl.load_workbook(fp.name, data_only=True)
            sheet = book.active  # Use the first sheet

        except FileNotFoundError:
            raise UserError(f'No such file or directory found: {self.file_name}.')
        except binascii.Error:
            raise UserError('Error decoding the uploaded file.')
        except Exception as e:
            raise UserError(f"An error occurred while processing the file: {str(e)}")

        # Process each row in the sheet
        for index, row in enumerate(sheet.iter_rows(values_only=True)):
            if index == 0:  # Skip the header row
                continue

            try:
                barcode = row[9]

                # Search for AFS Classification
                afs_classification = self.env['asset.category'].sudo().search(
                    [('name', '=', row[6])], limit=1)

                # Handle custodian user field properly
                custodian_user = row[12]
                if custodian_user:
                    custodian_name_update = re.sub(r'\s+', ' ',
                                                   custodian_user.strip())

                    # Search for asset using barcode
                    asset_registers = self.env['account.asset'].search(
                        [('alternative_ref', '=', barcode)], limit=1)

                    # Search for custodian user in HR
                    custodian_user_record = self.env[
                        'hr.employee'].sudo().search(
                        [('name', '=', custodian_name_update)], limit=1)

                    # Update only if asset_registers exist
                    if asset_registers and afs_classification and custodian_user_record:
                        asset_registers.write({
                            'afs_classification': afs_classification.id,
                            'custodian_id': custodian_user_record.id
                        })
            except Exception as e:
                print(f"Error processing row {index}: {e}")
        return True
