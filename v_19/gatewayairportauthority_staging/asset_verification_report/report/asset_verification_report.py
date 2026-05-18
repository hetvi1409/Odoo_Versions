from odoo import api, models
from .asset_report_mixin import AssetVerificationReportMixin


class AssetMovableReport(AssetVerificationReportMixin, models.AbstractModel):
    _name = 'report.asset_verification_report.asset_verification_report'
    _description = 'Asset Movable Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        resolved = self._resolve_report_data(data)

        job_lines = resolved['job_lines']
        final_assets = resolved['final_assets']
        status = data.get('verification_status') or 'all'

        if status == 'not_verified':
            docs = final_assets
            doc_model = 'account.asset'
        elif status == 'verified':
            docs = job_lines
            doc_model = 'asset.verification.history'
        else:
            docs = job_lines
            doc_model = 'asset.verification.history'

        return {
            'doc_ids': docs.ids,
            'doc_model': doc_model,
            'docs': docs,
            'data': data,
            'job_lines': job_lines,
            'final_assets': final_assets,
        }