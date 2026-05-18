from odoo import api, models


class AssetDisposalReport(models.AbstractModel):
    _name = 'report.asset_verification_report.asset_disposal_report'
    _description = 'Asset Register Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = [('state', '==', 'asset_disposed')]
        threshold = self.env['ir.config_parameter'].sudo().get_param('asset_registry.minor_major_threshold', 5000)
        threshold = float(threshold)
        if data['type'] == 'minor':
            domain.append(('original_value', '<=', threshold))
        elif data['type'] == 'major':
            domain.append(('original_value', '>', threshold))
        elif data['type'] == 'all':
            pass
        docs = self.env['account.asset'].search(domain)
        return {
            'doc_ids': docids,
            'doc_model': 'account.asset',
            'docs': docs,
            'data': {
            }
        }

