from odoo import http
from odoo.http import request

class AssetVerificationReportController(http.Controller):
    @http.route('/asset_verification/report', type='http', auth='user')
    def download_report(self, job_id, **kwargs):
        job = request.env['asset.verification.job'].browse(int(job_id))
        if not job.exists():
            return request.not_found()

        file_content = job.generate_excel_report()
        filename = 'Asset_Verification_Report.xlsx'

        return request.make_response(file_content, [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', f'attachment; filename="{filename}"')
        ])
