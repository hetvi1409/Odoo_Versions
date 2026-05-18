from odoo.tools.json import json_default
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _, api


class AssetRegisterReport(models.TransientModel):
    _name = 'assets.register.reports'
    _description = "Assets Register Reports"

    type = fields.Selection([
        ('minor', 'Minor Assets'),
        ('major', 'Major Assets'),
        ('all', 'All Assets')], string="Asset Type", required=True,default='all')

    def action_generate_report(self):
        """Generate asset report in PDF or Excel"""
        data = {
            'type': self.type,
            'custodian_id': False,
            'department_id': False
        }
        return self.env.ref('asset_verification_report.action_report_asset_register_report').report_action(self, data=data)

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
        # domain = [('state', '!=', 'draft')]
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
        elif data['type'] == 'All':
            print("ALL ASSETS")
            heading_name = "All Asset Movable Report"
        assets = self.env['account.asset'].search(domain)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Assets Register Report')
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})

        worksheet.set_row(0, 30)
        worksheet.set_row(2, 25)

        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 18)
        worksheet.set_column(3, 3, 22)
        worksheet.set_column(4, 4, 22)
        worksheet.set_column(5, 5, 22)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 18)
        worksheet.set_column(8, 8, 18)
        worksheet.set_column(9, 9, 12)

        worksheet.merge_range('B1:E1', _('Asset Register Report'), head)
        # Header
        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#DCE6F1'})
        headers = ['Asset', "Description", 'Barcode', 'Department',
                   'Location', 'Custodian', 'Condition', 'Acquisition Value', 'Book Value', 'Status']
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)

        # Data
        row = 3
        for asset in assets:
            worksheet.write(row, 0, asset.name or '')
            worksheet.write(row, 1, asset.description or '')
            worksheet.write(row, 2, asset.alternative_ref or '')
            worksheet.write(row, 3, asset.custodian_department_id.name or '')
            worksheet.write(row, 4, asset.job_location_id.name or '')
            worksheet.write(row, 5, asset.custodian_id.name or '')
            worksheet.write(row, 6, asset.condition or '')
            worksheet.write(row, 7, asset.original_value or 0)
            worksheet.write(row, 8, asset.book_value or 0)
            worksheet.write(row, 9, asset.state or '')
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

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