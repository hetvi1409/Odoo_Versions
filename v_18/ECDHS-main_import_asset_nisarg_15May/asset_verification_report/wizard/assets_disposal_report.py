from odoo.tools.json import json_default
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetDisposalReport(models.TransientModel):
    _name = 'assets.disposal.reports'
    _description = "Assets Disposal Reports"

    type = fields.Selection([
        ('minor', 'Minor Assets'),
        ('major', 'Major Assets'),
        ('all', 'All')
    ], string="Asset Type", required=True, default='all')

    def action_generate_report(self):
        """Generate asset report in PDF or Excel"""
        data = {
            'type': self.type,
        }
        return self.env.ref('asset_verification_report.action_asset_disposal_report').report_action(self, data=data)

    def action_get_xlsx_report_value(self, data):
        """"""
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
        # domain = [('state', 'not in', ['model', 'draft'])]
        domain = [('state', '==', 'asset_disposed')]
        heading_name = ""
        threshold = self.env['ir.config_parameter'].sudo().get_param('asset_registry.minor_major_threshold', 5000)
        threshold = float(threshold)
        if data['type'] == 'minor':
            domain.append(('original_value', '<=', threshold))
        elif data['type'] == 'major':
            domain.append(('original_value', '>', threshold))
        elif data['type'] == 'all':
            pass
        assets = self.env['account.asset'].search(domain)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Assets Disposal Report')
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})

        worksheet.merge_range('B1:E1', _('Asset Disposal Report'), head)
        # Header
        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#DCE6F1'})
        headers = ['Asset', 'Barcode',
                   'Disposal Date','Disposal Method','Disposal Value',
                   'Department', 'Custodian', ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)
        worksheet.set_row(0, 30)
        worksheet.set_row(2, 25)
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 1, 18)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 18)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 20)
        worksheet.set_column(6, 6, 20)
        # Data
        row = 3
        for asset in assets:
            worksheet.write(row, 0, asset.name or '')
            worksheet.write(row, 1, asset.alternative_ref or '')
            worksheet.write(row, 2, asset.disposal_date or '')
            worksheet.write(row, 3, asset.disposal_method or '')
            worksheet.write(row, 4, asset.original_value or '')
            worksheet.write(row, 5, asset.custodian_department_id.name or '')
            worksheet.write(row, 6, asset.custodian_id.name or '')
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
