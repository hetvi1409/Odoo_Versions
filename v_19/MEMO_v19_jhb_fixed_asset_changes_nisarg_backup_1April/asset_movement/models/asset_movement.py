from odoo import models, fields, api
from datetime import datetime
from odoo.tools.json import json_default
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _


class AssetLocationHistory(models.Model):
    _name = "asset.location.history"
    _description = "Asset Location History"
    _order = "date desc, id desc"

    asset_id = fields.Many2one("account.asset", string="Asset", required=True)
    old_location_id = fields.Many2one("asset.verification.job.location", string="Old Location")
    new_location_id = fields.Many2one("asset.verification.job.location", string="New Location")
    changed_by = fields.Many2one("res.users", string="Changed By", default=lambda self: self.env.user)
    date = fields.Datetime(string="Changed On", default=lambda self: fields.Datetime.now())

    def action_get_xlsx_report_value(self, data):
        """"""
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Movement Register',
                     },
            'report_type': 'xlsx_reports',
        }

    def get_xlsx_report(self, data, response):
        domain = []
        heading_name = ""
        if data['asset_id']:
            domain.append(('asset_id', '<', data['asset_id']))

        assets = self.env['asset.location.history'].search(domain)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Assets Disposal Report')
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})

        worksheet.merge_range('B1:E1', _('Asset Disposal Report'), head)
        # Header
        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#DCE6F1'})
        headers = ['Asset', 'Old Location', 'New Location',
                   'Changed By', 'Changed On', ]
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
            worksheet.write(row, 0, asset.asset_id.name or '')
            worksheet.write(row, 1, asset.old_location_id.name or '')
            worksheet.write(row, 2, asset.new_location_id.name or '')
            worksheet.write(row, 3, asset.changed_by.name or '')
            worksheet.write(row, 4, asset.date or '')
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
