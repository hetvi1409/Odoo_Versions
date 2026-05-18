from datetime import datetime, time
from odoo import fields


class AssetVerificationReportMixin:


    def _get_date_range(self, data):
        start_raw = data.get('period_start_date')
        end_raw = data.get('period_end_date')
        print("\n\n\n START_RAW:",start_raw)
        print("\n\n\n END_RAW:",end_raw)
        if start_raw and end_raw:
            start = fields.Date.to_date(start_raw)
            end = fields.Date.to_date(end_raw)
            return datetime.combine(start, time.min), datetime.combine(end, time.max)
        return False, False

    def _build_date_domain(self, data, base_domain=None):
        domain = list(base_domain or [])
        start_dt, end_dt = self._get_date_range(data)
        if start_dt:
            domain.append(('create_date', '>=', start_dt))
        if end_dt:
            domain.append(('create_date', '<=', end_dt))
        print("FINAL DOMAIN:", domain)
        return domain

    def _apply_date_filter(self, records, data):
        print('\n\n\n APPLY DATE FILTER--->record:',records)
        # asset.verification.history
        start_dt, end_dt = self._get_date_range(data)
        print('start:', start_dt, 'end:', end_dt)
        if start_dt and end_dt:
            records = records.search([
                ('id', 'in', records.ids),
                ('create_date', '>=', start_dt),
                ('create_date', '<=', end_dt),
            ])
        print("\n\n\n len+++++++++records:",len(records))
        # len+++++++++records: 699
        return records

    def _get_assets_for_job(self, job_id):
        job = self.env['asset.verification.job'].browse(job_id)
        if job.job_location_id:
            return self.env['account.asset'].search([
                ('job_location_id', '=', job.job_location_id.id)
            ])
        return self.env['account.asset'].search([])

    def _get_latest_histories(self, assets):
        histories = self.env['asset.verification.history'].search(
            [('history_id', 'in', assets.ids)],
        )
        # order='create_date desc, id desc'
        seen = set()
        latest_ids = []
        for rec in histories:
            aid = rec.history_id.id
            if aid not in seen:
                seen.add(aid)
                latest_ids.append(rec.id)
        print("\n\n\n latest_ids----------?", latest_ids)
        print("\n\n\n latest_ids----------?", len(latest_ids))
        # latest_ids----------? 2397

        return histories.browse(latest_ids)

    def _split_verified_unverified(self, assets):
        verified_histories = assets.mapped('latest_verification_history_id').filtered(bool)
        unverified_assets = assets.filtered(lambda a: not a.latest_verification_history_id)
        return verified_histories, unverified_assets

    #
    def _resolve_report_data(self, data):
        History = self.env['asset.verification.history']
        Asset = self.env['account.asset']

        empty_history = History.browse([])
        empty_asset = Asset.browse([])

        status = data.get('verification_status') or 'all'

        # LANDSCAPE
        if data.get('context', {}).get('landscape'):
            job_location_id = data.get('job_location_id')
            assets = self._get_assets_for_job(job_location_id) if job_location_id else Asset.search([])
        elif data.get('verification_job_location_id'):
            job_id = data['verification_job_location_id']
            asset_ids = data.get('asset_ids', [])
            assets = Asset.browse(asset_ids) if asset_ids else self._get_assets_for_job(job_id)
        else:
            assets = Asset.search([])

        # ── Find verified histories using same domain as compute ──────────
        # ANY history within the period counts — not just the latest
        history_domain = [('history_id', 'in', assets.ids)]
        start_dt, end_dt = self._get_date_range(data)
        if start_dt:
            history_domain.append(('create_date', '>=', start_dt))
        if end_dt:
            history_domain.append(('create_date', '<=', end_dt))

        matched_histories = History.search(
            history_domain, order='create_date desc, id desc'
        )

        # Deduplicate — one history row per asset (latest within period)
        seen = set()
        latest_ids = []
        for rec in matched_histories:
            aid = rec.history_id.id
            if aid not in seen:
                seen.add(aid)
                latest_ids.append(rec.id)

        verified_histories = History.browse(latest_ids)
        verified_asset_ids = seen  # same set used for splitting

        # Not verified = in scope but no history within the period
        unverified_assets = assets.filtered(lambda a: a.id not in verified_asset_ids)

        # ── Return based on status ────────────────────────────────────────
        if status == 'verified':
            print("\n\n VERIFIED STATUS - VERIFIED--->", len(verified_histories))
            return {'job_lines': verified_histories, 'final_assets': empty_asset}
        if status == 'not_verified':
            print("\n\n NOT VERIFIED STATUS - UNVERIFIED--->", len(unverified_assets))
            return {'job_lines': empty_history, 'final_assets': unverified_assets}
        # 'all'
        print("\n\n ALL STATUS - VERIFIED--->", len(verified_histories))
        print("\n\n ALL STATUS - UNVERIFIED--->", len(unverified_assets))
        return {'job_lines': verified_histories, 'final_assets': unverified_assets}