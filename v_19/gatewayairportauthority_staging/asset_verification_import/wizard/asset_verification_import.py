from odoo import models, fields, _, api
import base64
from openpyxl import load_workbook
from odoo.exceptions import UserError
import io
from datetime import date


class AssetImportWizard(models.TransientModel):
    _inherit = 'asset.import.wizard'

    def action_download_template(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/asset_verification_import/static/xls/asset_verification_data.xlsx',
            'target': 'self',
        }

    def action_import(self):
        """Override to skip import for specific file names"""

        # if self.filename and self.filename.startswith('asset_verification_data'):
        if self.filename == 'asset_verification_data.xlsx' or self.filename.startswith('asset_verification_data ('):
            file_data = base64.b64decode(self.file)
            workbook = load_workbook(filename=io.BytesIO(file_data), data_only=True)
            sheet = workbook.active

            headers = {}
            for col in range(1, sheet.max_column + 1):
                header_value = sheet.cell(row=1, column=col).value
                if header_value:
                    headers[header_value.strip()] = col


            required_headers = ['Assets', 'Barcode', 'Condition', 'Verified', 'Serial Number', 'Location', 'Custodian']
            for header in required_headers:
                if header not in headers:
                    print("=====missing header=====",header)
                    raise UserError(_("Missing required header: %s") % header)

            Asset = self.env['account.asset']
            AssetVerification = self.env['asset.verification.history']

            for row in range(2, sheet.max_row + 1):
                asset_name = sheet.cell(row=row, column=headers['Assets']).value
                barcode = sheet.cell(row=row, column=headers['Barcode']).value
                condition = sheet.cell(row=row, column=headers['Condition']).value
                verified = sheet.cell(row=row, column=headers['Verified']).value
                serial_number = sheet.cell(row=row, column=headers['Serial Number']).value
                location = sheet.cell(row=row, column=headers['Location']).value
                custodian = sheet.cell(row=row, column=headers['Custodian']).value

                asset = False
                if serial_number:
                    serial_number = str(serial_number).strip()
                    print("=====searching by serial number=====", serial_number)
                    asset = Asset.search([('serial_number', '=', serial_number)], limit=1)
                    if asset:
                        print("=====asset found by serial number=====", asset.name)

                # If not found by serial number, try barcode
                if not asset and barcode:
                    barcode = str(barcode).strip()
                    print("=====searching by barcode=====", barcode)
                    asset = Asset.search([('alternative_ref', '=', barcode)], limit=1)
                    if asset:
                        print("=====asset found by barcode=====", asset.name)

                # If still not found, try asset name
                if not asset and asset_name:
                    asset_name = str(asset_name).strip()
                    print("=====searching by asset name=====", asset_name)
                    asset = Asset.search([('name', '=', asset_name)], limit=1)
                    if asset:
                        print("=====asset found by name=====", asset.name)

                # Skip if asset not found
                if not asset:
                    continue

                # IMPORT LOCATION
                location_rec = False
                if location:
                    location_name = str(location).strip()
                    print("=====location name=====", location_name)
                    AssetLocation = self.env["asset.verification.job.location"]
                    location_rec = AssetLocation.search([('name', '=', location_name)], limit=1)
                    if not location_rec:
                        location_rec = AssetLocation.create({'name': location_name})
                    asset.job_location_id = location_rec.id

                # Import Custodian
                custodian_rec = False
                if custodian:
                    custodian_name = str(custodian).strip()
                    custodian_rec = self.env['res.users'].search([('name', '=', custodian_name)], limit=1)
                    if custodian_rec:
                        asset.custodian_id = custodian_rec.id


                AssetVerification.create({
                    'history_id': asset.id,
                    'parent_barcode': barcode if barcode else asset.alternative_ref,
                    'condition': self.env['asset.condition'].search([('name', '=', condition)], limit=1) if condition else False,
                    'past_year': date.today().year - 1,
                    'this_year': date.today().year,
                    'is_verified': verified,
                    'create_date': date.today(),
                    'location_id': location_rec.id if location_rec else False,
                    'asset_verification_user_id': self.env.user.id,
                    'date_verification': date.today(),
                })
                print("=====asset verification history created for asset=====", asset.name)

        return super(AssetImportWizard, self).action_import()



