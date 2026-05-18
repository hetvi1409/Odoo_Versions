from odoo import api, models


class AssetMovableReport(models.AbstractModel):
    _name = 'report.asset_verification_report.asset_verification_report'
    _description = 'Asset Movable Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        history_model = self.env['asset.verification.history']

        def _latest_only(recordset):
            """Return only the latest history per asset (assumes recordset ordered desc)."""
            seen = set()
            latest_ids = []
            for rec in recordset:
                asset_id = rec.history_id.id
                if asset_id in seen:
                    continue
                seen.add(asset_id)
                latest_ids.append(rec.id)
            return history_model.browse(latest_ids)

        if data.get('verification_job_location_id'):
            job = data.get('verification_job_location_id')
            domain = [('account_verification_job_id', '=', job)]

            status = data.get('verification_status')
            if status == 'verified':
                print('\n\n Verified job lines domain:', domain)
                domain.append(('verified', '=', True))
                only_latest = True
                only_asset = False
            elif status == 'not_verified':
                print('\n\n Not verified job lines domain:', domain)
                domain.append(('verified', '=', False))
                only_latest = False
                only_asset = True
            elif status == 'all':
                print('\n\n All job lines domain:', domain)
                only_latest = True
                only_asset = True

            # search job lines
            job_lines = self.env['asset.verification.job.line'].search(domain)
            asset_ids = job_lines.mapped('asset_id').ids

        # domain (with optional period filters)
        domain = [('history_id', 'in', asset_ids)]
        if data.get('period_start_date'):
            domain.append(('create_date', '>=', data['period_start_date']))
        if data.get('period_end_date'):
            domain.append(('create_date', '<=', data['period_end_date']))


        # Order by verification date desc so _latest_only picks the newest first
        histories = history_model.search(domain, order='create_date desc, id desc')
        asset  = self.env['account.asset']

        if only_latest:
            histories = _latest_only(histories)
        if only_asset:
            histories = asset.browse(asset_ids)


        return {
            'doc_ids': histories.ids,
            'doc_model': 'asset.verification.job.line',
            'docs': histories,
            'data': data,
            'job_lines': job_lines
        }
