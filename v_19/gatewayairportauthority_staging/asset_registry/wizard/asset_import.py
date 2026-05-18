from datetime import datetime, timedelta
import xlrd
import re
import tempfile
import binascii
import base64
import openpyxl
from odoo import fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AssetImport(models.TransientModel):
    _name = 'asset.import'
    _description = 'Asset import'

    file = fields.Binary(string='File', required=True)

    def action_import_asset(self):
        """Import asset"""
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(base64.b64decode(self.file))
            fp.close()  # Ensure data is written before reading

            # Load workbook with openpyxl
            book = openpyxl.load_workbook(fp.name, data_only=True)
            sheet = book.active  # Use the first sheet

        except FileNotFoundError:
            raise UserError(
                f'No such file or directory found: {self.file_name}.')
        except binascii.Error:
            raise UserError('Error decoding the uploaded file.')
        except Exception as e:
            raise UserError(
                f"An error occurred while processing the file: {str(e)}")
        for index, row in enumerate(sheet.iter_rows(values_only=True)):
            if index == 0:  # Skip the header row
                continue

            try:
                excel_date = row[0]
                # if type(excel_date) == str:
                #     date_object = datetime.strptime(excel_date, '%d/%m/%Y')
                #     formatted_date = date_object.strftime('%Y-%m-%d')
                # else:
                #     excel_base_date = datetime(1899, 12,30)  # Excel base date (there's a difference due to Excel bug)
                #
                #     python_date = excel_base_date + timedelta(days=int(excel_date))
                #     formatted_date = python_date.strftime('%Y-%m-%d')
                supplier_det = self.env['res.partner'].sudo().search([('name', '=', row[1])], limit=1)
                payment_number = row[2] if len(row) > 2 else ''
                order_number = row[3] if len(row) > 3 else ''
                original_amount = float(str(row[4]).replace(',', '')) if \
                row[4] != '-' and row[4] else ""
                description = row[5] if len(row) > 5 else ''
                afs_classification = self.env['asset.category'].sudo().search([('name', '=', row[6])], limit=1)
                asset_model = self.env['account.asset'].sudo().search(
                        [('state', '=', 'model'), ('name', '=', row[7])], limit=1)
                serial_number = row[8] if len(row) > 8 else ''
                unique_asset_no = row[9] if len(row) > 9 else ''
                location_details = self.env['asset.verification.job.location'].sudo().search([('name', '=', row[10])], limit=1)
                chief_directorate = self.env['hr.department'].sudo().search([('name', '=', row[11])], limit=1)
                custodian_user = self.env['hr.employee'].sudo().search([('name', '=', row[12])], limit=1)
                condition = row[13] if len(row) > 13 else ''
                life_cycle = row[14] if len(row) > 14 else ''
                disposal_date = row[15]
                formatted_disposal_date = False
                if disposal_date:
                    if not isinstance(disposal_date, datetime):
                        date_str = str(disposal_date).lstrip("'")

                        try:
                            # formatted_disposal_date = date_str
                            # Try parsing as DD/MM/YYYY first
                            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                            formatted_disposal_date = date_obj.strftime(
                                "%Y-%m-%d")
                        except ValueError:
                            try:
                                # If it fails, try parsing as YYYY-MM-DD
                                date_obj = datetime.strptime(date_str,
                                                             "%d/%m/%Y")
                                formatted_disposal_date = date_obj.strftime(
                                    "%Y-%m-%d")
                            except ValueError:
                                raise ValueError(
                                    f"Unknown date format: {date_str}")


                    else:
                        # If already a datetime object, use it directly
                        formatted_disposal_date = disposal_date

                        # Convert to desired format (DD/MM/YYYY)

                disposal_price = row[16] if len(row) > 16 else 0.0
                disposal_method = row[17] if len(row) > 17 else ''
                if description:
                    self.env['account.asset'].create({
                        'name': description,
                        'acquisition_date': excel_date,
                        'supplier_id': supplier_det.id if supplier_det else None,
                        'payment_number': payment_number,
                        'order_number': order_number,
                        'original_value': original_amount,
                        'description': description,
                        'afs_classification': afs_classification.id if afs_classification else None,
                        'model_id': asset_model.id if asset_model else None,
                        'serial_number': serial_number,
                        'alternative_ref': unique_asset_no,
                        'job_location_id': location_details.id if location_details else None,
                        'department_id': chief_directorate.id if chief_directorate else None,
                        'custodian_id': custodian_user.id if custodian_user else None,
                        'condition': condition,
                        'original_useful_life': life_cycle,
                        'disposal_date': formatted_disposal_date if formatted_disposal_date else None,
                        'disposal_price': disposal_price,
                        'disposal_method': disposal_method,
                        'state': 'draft',
                    })
            except IndexError:
                pass
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
