from odoo import api, models


class AccountAsset(models.Model):
    """Inheriting the asset model"""
    _inherit = 'account.asset'

    @api.model
    def get_movable_asset_details(self):
        sql_query = """SELECT categ.name, 
                    (SELECT COUNT(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id), 
                    (SELECT COALESCE(SUM(asset.carrying_amount), 0) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id)
                    FROM asset_category AS categ"""

        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        return result

    @api.model
    def get_movable_asset_graph_details(self):
        sql_query = """SELECT categ.name, 
                    (SELECT COALESCE(SUM(asset.carrying_amount), 0) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id)
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
        sql_query = """SELECT categ.name, 
                        (SELECT COUNT(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified = false), 
                        (SELECT COALESCE(SUM(asset.carrying_amount), 0) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified = false OR asset.is_verified IS NULL),
                        (SELECT COUNT(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified = true), 
                        (SELECT COALESCE(SUM(asset.carrying_amount), 0) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified = true),
                        (SELECT COUNT(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id), 
                        (SELECT COALESCE(SUM(asset.carrying_amount), 0) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id)
                        FROM asset_category AS categ"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        return result

    @api.model
    def get_asset_verification_number(self):
        sql_query = """SELECT (SELECT Count(asset) FROM account_asset AS asset WHERE asset.is_verified = true),
                        (Count(asset) - (SELECT Count(asset) FROM account_asset AS asset WHERE asset.is_verified = true))
                        FROM account_asset AS asset"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        value = []
        for record in result:
            value.append(record[0])
            value.append(record[1])
        return {'key': ['verified', 'not_verified'], 'value': value}

    @api.model
    def get_asset_verification_carrying_value(self):
        sql_query = """SELECT (SELECT sum(asset.carrying_amount) FROM account_asset AS asset WHERE asset.is_verified = true), 
                        (SELECT sum(asset.carrying_amount) FROM account_asset AS asset WHERE asset.is_verified = false OR asset.is_verified IS NULL)
                        FROM account_asset AS asset
                        LIMIT 1"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        value = []
        for record in result:
            value.append(record[0])
            value.append(record[1])
        return {'key': ['verified', 'not_verified'], 'value': value}

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
        sql_query = """SELECT categ.name, 
                    (SELECT Count(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified is null OR asset.is_verified = false)
                    FROM asset_category AS categ"""
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
        sql_query = """SELECT asset.current_condition_this_year, count(asset)
                        FROM account_asset AS asset
                        where asset.is_verified = true
                        Group By asset.current_condition_this_year"""
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
    def get_asset_verification_progress(self):
        sql_query = """SELECT categ.name, 
                    (SELECT Count(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified is null OR asset.is_verified = false),
                    (SELECT Count(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified = true)
                    FROM asset_category AS categ"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        condition = []
        count = []
        count_verified = []
        for record in result:
            condition.append(record[0])
            count.append(record[1])
            count_verified.append(record[2])
        return {
            'condition': condition,
            'count': count,
            'count_verified': count_verified
        }

    @api.model
    def get_asset_verification_location(self):
        sql_query = """SELECT categ.name, 
                            (SELECT Count(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified is null OR asset.is_verified = false),
                            (SELECT Count(asset) FROM account_asset AS asset WHERE asset.asset_category_id = categ.id and asset.is_verified = true)
                            FROM asset_category AS categ"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        location = []
        count = []
        count_verified = []
        for record in result:
            location.append(record[0])
            count.append(record[1])
            count_verified.append(record[2])
        return {
            'location': location,
            'count': count,
            'count_verified': count_verified
        }
