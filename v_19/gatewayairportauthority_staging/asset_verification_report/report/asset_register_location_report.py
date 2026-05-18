from odoo import api, models


class AssetRegisterReport(models.AbstractModel):
    _name = 'report.asset_verification_report.asset_register_location_report'
    _description = 'Asset Register Location Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        # fetch threshold from config parameter
        threshold = float(self.env['ir.config_parameter'].sudo().get_param('asset_registry.minor_major_threshold', 1000))
        if data['type'] == 'minor':
            domain.append(('original_value', '<=', threshold))
        elif data['type'] == 'major':
            domain.append(('original_value', '>', threshold))
        elif data['type'] == 'all':
            pass
        if data['custodian_id']:
        #     docs = data['report_data']
            domain.append(('custodian_id', '=', int(data['custodian_id'])))
        if data['job_location_id']:
            domain.append(('job_location_id', '=', int(data['job_location_id'])))
        docs = self.env['account.asset'].search(domain)
        return {
            'doc_ids': docids,
            'doc_model': 'account.asset',
            'docs': docs,
            'company': self.env.company,
            'data': {
            }
        }

