from odoo import api, models, fields
from datetime import datetime


class AccountAsset(models.Model):
    """Inheriting the asset model"""
    _inherit = 'account.asset'

    @api.model
    def get_movable_asset_details(self):
        """Optimized query to get movable asset details grouped by classification"""
        sql_query = """
            SELECT
                categ.name,
                COUNT(asset.id) as asset_count,
                COALESCE(SUM(asset.original_value), 0) as total_value
            FROM account_asset AS asset
            INNER JOIN asset_category AS categ ON asset.asset_category_id = categ.id
            WHERE asset.asset_category_id IS NOT NULL
            GROUP BY categ.id, categ.name
            ORDER BY categ.name
        """

        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        return result

    @api.model
    def get_movable_asset_graph_details(self):
        sql_query = """SELECT categ.name,
                    (SELECT COALESCE(SUM(asset.original_value), 0) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id)
                    FROM asset_category AS categ"""

        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        sum = []
        category = []
        for record in result:
            sum.append(record[1])
            category.append(record[0])
        value = {'category': category, 'sum': sum}
        return value

    @api.model
    def get_overall_movable_asset_details(self):
        categories = self.env['asset.category'].search([])
        result = []

        for categ in categories:
            assets = self.env['account.asset'].search([('asset_category_id', '=', categ.id)])
            verified_assets = assets.history_ids.filtered(lambda a: a.is_verified == True).mapped('history_id')
            not_verified_assets = assets - verified_assets
            result.append((
                categ.name,
                len(not_verified_assets),
                sum(not_verified_assets.mapped('original_value') or [0.0]),
                len(verified_assets),
                sum(verified_assets.mapped('original_value') or [0.0]),
                len(assets),
                sum(assets.mapped('original_value') or [0.0])
            ))

        return result

    @api.model
    def get_asset_verification_number(self):
        sql_query = """
            SELECT
                COUNT(DISTINCT CASE WHEN asset.is_verified = TRUE THEN asset.id END) as verified_count,
                COUNT(DISTINCT CASE WHEN asset.is_verified IS NULL OR asset.is_verified = FALSE THEN asset.id END) as not_verified_count
            FROM account_asset AS asset
        """

        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchone()

        verified_count = result[0] or 0
        not_verified_count = result[1] or 0

        return {
            'key': ['verified', 'not_verified'],
            'value': [verified_count, not_verified_count]
        }

    @api.model
    def get_asset_verification_carrying_value(self):
        sql_query = """
            SELECT
                COALESCE(SUM(CASE WHEN asset.is_verified = TRUE THEN asset.original_value ELSE 0 END), 0) as verified_value,
                COALESCE(SUM(CASE WHEN asset.is_verified IS NULL OR asset.is_verified = FALSE THEN asset.original_value ELSE 0 END), 0) as not_verified_value
            FROM account_asset AS asset
        """

        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchone()

        verified_value = float(result[0] or 0.0)
        not_verified_value = float(result[1] or 0.0)

        return {
            'key': ['verified', 'not_verified'],
            'value': [verified_value, not_verified_value]
        }

    @api.model
    def get_graph_condition_asset(self):
        sql_query = """SELECT asset.current_condition_this_year, count(asset)
                        FROM account_asset AS asset
                        Group By asset.current_condition_this_year """
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        condition = []
        count = []
        for record in result:
            condition.append(record[0])
            count.append(record[1])
        return {
            'condition': condition,
            'count': count
        }

    @api.model
    def get_asset_not_verified(self):
        """Optimized query to get not verified assets grouped by category"""
        sql_query = """
            SELECT
                categ.name,
                COUNT(DISTINCT asset.id) as not_verified_count
            FROM account_asset AS asset
            INNER JOIN asset_category AS categ ON asset.asset_category_id = categ.id
            WHERE asset.is_verified = FALSE OR asset.is_verified IS NULL
            GROUP BY categ.id, categ.name
            ORDER BY categ.name
        """

        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        categ = []
        count = []
        for record in result:
            categ.append(record[0])
            count.append(record[1])
        return {
            'categ': categ,
            'count': count
        }

    @api.model
    def get_asset_verified_condition(self):
        conditions = self.env['asset.condition'].search([])
        condition_count = {cond.name: 0 for cond in conditions}
        assets = self.env['account.asset'].search([])

        for asset in assets:
            all_histories = asset.history_ids
            print(all_histories)

            if not all_histories:
                continue

            # Get the latest history by create_date
            latest_history = all_histories.sorted(key=lambda h: h.create_date or fields.Datetime.now(),reverse=True)[:1]

            if not latest_history:
                continue

            latest_history = latest_history[0]
            condition = latest_history.condition.name

            if condition in condition_count:
                condition_count[condition] += 1
        return {
            'condition': list(condition_count.keys()),
            'count': list(condition_count.values()),
        }

    # @api.model
    # def get_asset_verification_progress(self):
    #     sql_query = """SELECT categ.name,
    #                     (SELECT Count(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified is null OR asset.is_verified = false),
    #                     (SELECT Count(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified = true)
    #                     FROM asset_category AS categ"""
    #     self.env.cr.execute(sql_query)
    #     result = self.env.cr.fetchall()
    #     condition = []
    #     count = []
    #     count_verified = []
    #     for record in result:
    #         condition.append(record[0])
    #         count.append(record[1])
    #         count_verified.append(record[2])
    #     return {
    #         'condition': condition,
    #         'count': count,
    #         'count_verified': count_verified
    #     }

    @api.model
    def get_asset_verification_progress(self):
        print("\n\n\n get_asset_verification_progress====>",self)
        movable_category_ids = self.env['asset.category'].search([('is_movable', '=', True)]).ids

        immovable_category_ids = self.env['asset.category'].search([('is_immovable', '=', True)]).ids

        intangible_category_ids = self.env['asset.category'].search([('is_intangible', '=', True)]).ids
        movable_count = self.env['account.asset'].search_count([('afs_classification', 'in', movable_category_ids)])
        immovable_count = self.env['account.asset'].search_count([('afs_classification', 'in', immovable_category_ids)])
        intangible_count = self.env['account.asset'].search_count([('afs_classification', 'in', intangible_category_ids)])

        return {
            'movable_assets': movable_count,
            'immovable_assets': immovable_count,
            'intangible_assets': intangible_count,
        }

    @api.model
    def get_asset_verification_location(self):
        locations = self.env['asset.verification.job.location'].search([])
        locations_names = []
        count = []
        count_verified = []

        for location in locations:
            assets = self.env['account.asset'].search([('job_location_id', '=', location.id)])
            verified_assets = assets.history_ids.filtered(lambda a: a.is_verified == True).mapped('history_id')
            not_verified_assets = assets - verified_assets

            locations_names.append(location.name)
            count.append(len(not_verified_assets))
            count_verified.append(len(verified_assets))

        return {
            'location': locations_names,
            'count': count,
            'count_verified': count_verified
        }

    # @api.model
    # def get_asset_type(self):
    #     minor_asset = self.env['account.asset'].search([('asset_type', '=', 'minor')])
    #     major_asset = self.env['account.asset'].search([('asset_type', '=', 'major')])
    #
    #     len_minor = len(minor_asset)
    #     len_major = len(major_asset)
    #
    #     return {
    #         'key': ['minor_asset', 'major_asset'],
    #         'value': [len_minor, len_major]
    #     }

    @api.model
    def get_asset_dashboard_data(self):
        return {
            "movable_assets": self.get_movable_asset_details(),
            "movable_graph": self.get_movable_asset_graph_details(),
            "overall_verification": self.get_overall_movable_asset_details(),
            "verification_number": self.get_asset_verification_number(),
            "verification_value": self.get_asset_verification_carrying_value(),
            "condition_asset": self.get_graph_condition_asset(),
            "asset_verified": self.get_asset_verified(),
            "verified_condition": self.get_asset_verified_condition(),
            "verification_progress": self.get_asset_verification_progress(),
            "verification_location": self.get_asset_verification_location(),
            # "asset_type": self.get_asset_type(),
        }
