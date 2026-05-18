from odoo.tools.json import json_default
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _, api
import base64
import tempfile
import os

class AssetRegisterJobLocation(models.TransientModel):
    _name = 'assets.register.location'
    _description = "Assets Register by Job Location Reports"


    job_location_id = fields.Many2one('asset.verification.job.location', string="Location", required=True)
    type = fields.Selection([
        ('minor', 'Minor Assets'),
        ('major', 'Major Assets'),
        ('all', 'All Assets')], string="Asset Type", required=True, default='all')

    def action_generate_report(self):
        """Generate asset report in PDF or Excel"""
        data = {
            'type': self.type,
            'job_location_id': self.job_location_id.id,
            'custodian_id': False,
            'department_id': False
        }
        return self.env.ref('asset_verification_report.action_report_asset_register_location_report').report_action(self, data=data)

    def action_get_xlsx_report_value(self, data):
        """"""
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data, default=json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Register',
                     },
            'report_type': 'xlsx_reports',
        }

    def action_export_excel(self):
        data = {
            'type': self.type,
            'job_location_id': self.job_location_id.id,
            'company' : self.env.company,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Register',
                     },
            'report_type': 'xlsx_reports',
        }

    def get_xlsx_report(self, data, response):
        domain = []
        heading_name = ""
        threshold = self.env['ir.config_parameter'].sudo().get_param('asset_registry.minor_major_threshold', 5000)
        threshold = float(threshold)
        if data['type'] == 'minor':
            domain.append(('original_value', '<=', threshold))
            heading_name = "Minor Asset Movable Report"
        elif data['type'] == 'major':
            domain.append(('original_value', '>', threshold))
            heading_name = "Major Asset Movable Report"
        elif data['type'] == 'all':
            heading_name = "All Asset Movable Report"
            pass
        if data['job_location_id']:
            domain.append(('job_location_id', '=', int(data['job_location_id'])))
        assets = self.env['account.asset'].search(domain)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Assets Register Report')

        # ===== CUSTOM HEADER SECTION =====
        company = self.env.company

        title_format = workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'left',
            'valign': 'top'
        })

        list_format = workbook.add_format({
            'font_size': 10,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })

        year_box_format = workbook.add_format({
            'font_size': 14,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4F7BD9',
            'font_color': 'white',
            'border': 1
        })

        green_border = workbook.add_format({
            'bottom': 2,
        })

        worksheet.set_row(0, 60)
        worksheet.set_row(1, 5)
        worksheet.set_row(2, 5)

        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 18)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 18)
        worksheet.set_column(8, 8, 18)
        worksheet.set_column(9, 9, 18)

        # ===== INSERT COMPANY LOGO (A1:B1 only) =====
        temp_logo_path = None
        if company.logo:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_logo_path = temp_file.name
                    temp_file.write(base64.b64decode(company.logo))

                worksheet.insert_image('A1:C1', temp_logo_path, {
                    'x_scale': 0.15,
                    'y_scale': 0.15,
                    'x_offset': 10,
                    'y_offset': 10,
                    'positioning': 1,
                    'object_position': 1
                })
            except Exception as e:
                print(f"Error inserting logo: {e}")
                worksheet.merge_range('A1:B1', company.name or 'GAAL', title_format)
        else:
            worksheet.merge_range('A1:B1', company.name or 'GAAL', title_format)

        inventory_text = """GAAL Inventory Sheet
            1. Please verify physical existence of all assets.
            2. No movement without Asset Management approval.
            3. You are accountable for signed assets.
            4. Disciplinary action applies for negligence."""

        worksheet.merge_range('D1:H1', inventory_text, list_format)
        worksheet.merge_range('I1:K1', '2026\nFinancial Year', year_box_format)
        worksheet.merge_range('A2:J2', '', green_border)

        # ===== REPORT TITLE =====
        head = workbook.add_format({
            'font_size': 16,
            'align': 'center',
            'color': '#008F30',
            'bold': True
        })

        location_style = workbook.add_format({
            'font_size': 14,
            'bold': True,
            'align': 'right',
            'color': "#171817"
        })

        location_value_style = workbook.add_format({
            'font_size': 14,
            'bold': True,
            'align': 'left',
            'color': "#171817"
        })

        worksheet.set_row(3, 25)
        worksheet.merge_range('A4:J4', _('Asset Register By Location Report'), head)
        worksheet.merge_range('A5:E5', _('Location:'), location_style)

        if data['job_location_id']:
            # worksheet.merge_range('A5:E5', _('Location:'), location_style)
            job_location = self.env['asset.verification.job.location'].browse(int(data['job_location_id']))
            print('job_location:', job_location)
            worksheet.merge_range('F5:J5', job_location.name, location_value_style)

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#008F30',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        headers = ['Name', 'Category', 'Item Description', 'Barcode', 'Condition',
                'Office', 'Building', 'Serial Number', 'Location', 'Custodian']

        # Write header row
        header_row = 7
        worksheet.set_row(header_row, 20)
        for col, header in enumerate(headers):
            worksheet.write(header_row, col, header, header_format)

        # Write asset data rows
        data_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        row = header_row + 1
        for asset in assets:
            worksheet.write(row, 0, asset.name or '', data_format)
            worksheet.write(row, 1, asset.afs_classification.name if asset.afs_classification else '', data_format)
            worksheet.write(row, 2, asset.description or '', data_format)
            worksheet.write(row, 3, asset.alternative_ref or '', data_format)
            worksheet.write(row, 4, asset.condition or '', data_format)
            worksheet.write(row, 5, '', data_format)
            worksheet.write(row, 6, asset.job_location_id.building_id.name if asset.job_location_id.building_id else '', data_format)
            worksheet.write(row, 7, asset.serial_number or '', data_format)
            worksheet.write(row, 8, asset.job_location_id.name if asset.job_location_id else '', data_format)
            worksheet.write(row, 9, asset.custodian_id.name if asset.custodian_id else '', data_format)
            row += 1

        # ===== SIGNATURE SECTION =====
        row += 2

        signature_label_format = workbook.add_format({
            'bold': True,
            'align': 'left',
            'valign': 'bottom',
            'font_size': 11
        })

        signature_line_format = workbook.add_format({
            'top': 1,
            'align': 'center',
            'valign': 'top',
            'font_size': 10
        })

        worksheet.set_row(row, 40)
        worksheet.set_row(row + 1, 20)

        worksheet.write(row, 0, 'Custodian Name:', signature_label_format)
        worksheet.merge_range(row + 1, 0, row + 1, 3, '', signature_line_format)
        worksheet.write(row, 4, 'Signature:', signature_label_format)
        worksheet.merge_range(row + 1, 4, row + 1, 7, '', signature_line_format)
        worksheet.write(row, 8, 'Date:', signature_label_format)
        worksheet.merge_range(row + 1, 8, row + 1, 9, '', signature_line_format)


        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        # ===== CLEANUP TEMP FILE =====
        if temp_logo_path and os.path.exists(temp_logo_path):
            try:
                os.unlink(temp_logo_path)
            except:
                pass


    @api.model
    def get_asset_register(self):

        assets = self.env['account.asset'].search([('state', '=', 'open')])
        data = {
            'total_asset': len(self.env['account.asset'].search([('state', '!=', 'model')])),
            'cancelled_asset': len(self.env['account.asset'].search([('state', '=', 'cancelled')])),
            # 'good_asset': len([a for a in assets if (a.condition or '').lower() == 'good']),
            # 'disposed_asset': len([a for a in assets if (a.condition or '').lower() == 'disposed']),
            # 'damaged_asset': len([a for a in assets if (a.condition or '').lower() == 'damaged']),
            'lost_asset': self.env['account.asset'].search_count([('condition', 'ilike', 'Lost')]),
            'damaged_asset': self.env['account.asset'].search_count([('condition', 'ilike', 'damaged')]),
            'disposed_asset': self.env['account.asset'].search_count([('condition', 'ilike', 'asset_disposed')]),
            'good_asset': self.env['account.asset'].search_count([('condition', 'ilike', 'good')]),
            'written_off_asset': self.env['account.asset'].search_count([('condition', 'ilike', 'Written Off')]),
        }
        return data