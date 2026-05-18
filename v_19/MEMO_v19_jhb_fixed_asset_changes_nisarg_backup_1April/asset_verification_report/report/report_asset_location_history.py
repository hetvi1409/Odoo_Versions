from odoo import api, models

class AssetLocationHistoryReport(models.AbstractModel):
    _name = "report.asset_verification_report.asset_movement_report"
    _description = "Asset Location History PDF Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        if data['asset_id']:
            domain = [('asset_id', '=', data['asset_id'])]
        docs = self.env['asset.location.history'].search(domain)
        return {
            'doc_ids': docids,
            'doc_model': 'asset.location.history',
            'docs': docs,
            'data': data,
        }
