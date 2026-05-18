import json
import io
from odoo.tools.json import json_default
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import api, fields, models, _


class AssetMovableReport(models.TransientModel):
    """Major/Minor Assets Report"""
    _name = 'asset.movable.report'
    _description = 'Major/Minor Assets Report'

    type = fields.Selection([
        ('minor', 'Minor Assets (< 5000)'),
        ('major', 'Major Assets (> 5000)')
    ], string="Asset Type", required=True)

    file_data = fields.Binary('File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)

    @api.model
    def _get_domain(self):
        if self.type == 'minor':
            return [('original_value', '<', 5000)]
        elif self.type == 'major':
            return [('original_value', '>=', 5000)]
        return []

    def action_generate_report(self):
        """Generate asset report in PDF or Excel"""
        assets = self.env['account.asset'].search(self._get_domain())
        data = {
            'type': self.type,
            'assets': assets.ids,
        }
        return self.env.ref('asset_movable_report.action_report_asset_minor_movable_report').report_action(self, data=data)

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
                     'report_name': 'Assets Movable',
                     },
            'report_type': 'xlsx_reports',
        }

    def get_xlsx_report(self, data, response):
        domain = [('state', '!=', 'draft')]
        heading_name = ""
        if data['type'] == 'minor':
            domain.append(('original_value', '<', 5000))
            heading_name = "Minor Asset Movable Report"
        elif data['type'] == 'major':
            domain.append(('original_value', '>=', 5000))
            heading_name = "Major Asset Movable Report"
        assets = self.env['account.asset'].search(domain)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Assets Report')
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})

        worksheet.merge_range('B1:E1', _(heading_name), head)
        # Header
        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#DCE6F1'})
        headers = ['Name of Asset', "Description", 'Category', 'Department',
                   'Custodian', 'Asset Value']
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)

        # Data
        row = 3
        for asset in assets:
            worksheet.write(row, 0, asset.name or '')
            worksheet.write(row, 1, asset.description or '')
            worksheet.write(row, 2, asset.afs_classification.name or '')
            worksheet.write(row, 3, asset.custodian_department_id.name or '')
            worksheet.write(row, 4, asset.custodian_id.name or '')
            worksheet.write(row, 5, asset.original_value or 0)
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


    # def action_export_excel(self):
    #     """Export report as Excel"""
    #     import xlsxwriter
    #
    #     assets = self.env['account.asset'].search(self._get_domain())
    #
    #     output = io.BytesIO()
    #     workbook = xlsxwriter.Workbook(output)
    #     worksheet = workbook.add_worksheet('Assets Report')
    #
    #     # Header
    #     header_format = workbook.add_format({'bold': True, 'bg_color': '#DCE6F1'})
    #     headers = ['Name of Asset', "Description", 'Category', 'Department', 'Custodian', 'Asset Value']
    #     for col, header in enumerate(headers):
    #         worksheet.write(0, col, header, header_format)
    #
    #     # Data
    #     row = 1
    #     for asset in assets:
    #         worksheet.write(row, 0, asset.name or '')
    #         worksheet.write(row, 1, asset.description or '')
    #         worksheet.write(row, 2, asset.afs_classification.name or '')
    #         worksheet.write(row, 3, asset.department_id.name or '')
    #         worksheet.write(row, 4, asset.custodian_id.name or '')
    #         worksheet.write(row, 5, asset.original_value or 0)
    #         row += 1
    #
    #     workbook.close()
    #     output.seek(0)
    #     workbook.close()
    #     output.seek(0)
    #     response.stream.write(output.read())
    #     output.close()
    #     # file_data = base64.b64encode(output.read())
    #     # output.close()
    #     #
    #     # self.write({
    #     #     'file_data': file_data,
    #     #     'file_name': f'{self.type.capitalize()}_Assets_Report_{date.today()}.xlsx'
    #     # })
    #     #
    #     # return {
    #     #     'type': 'ir.actions.act_url',
    #     #     'url': f'/web/content/{self.id}/file_data/{self.file_name}?download=true',
    #     #     'target': 'new',
    #     # }
