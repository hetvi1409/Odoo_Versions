from odoo import http
from odoo.http import request

class AssetImpairmentReportController(http.Controller):
    @http.route('/asset_impairment/report', type='http', auth='user')
    def download_report(self, asset_id, **kwargs):
        asset = request.env['account.asset'].browse(int(asset_id))  # Adjust this to the model you're using
        if not asset.exists():
            return request.not_found()

        file_content = asset.export_asset_impairment_xlsx()  # Ensure this method exists for generating the report
        filename = 'Asset_Impairment_Report.xlsx'

        return request.make_response(file_content, [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', f'attachment; filename="{filename}"')
        ])
