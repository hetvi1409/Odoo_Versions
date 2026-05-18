from odoo import http
from odoo.http import request
import base64

class AssetVerificationReportController(http.Controller):

    @http.route('/asset_verification/report/<string:job_ids>', type='http', auth='user')
    def download_asset_verification_report(self, job_ids, **kwargs):
        ids = [int(i) for i in job_ids.split(',') if i.isdigit()]
        jobs = request.env['asset.verification.job'].sudo().browse(ids)

        if not jobs.exists():
            return request.not_found()

        # For now, download ONE report (first job)
        excel_data = jobs[0].generate_excel_report()

        filename = f"Asset_Verification_Report_{jobs[0].name}.xlsx"

        return request.make_response(
            excel_data,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )