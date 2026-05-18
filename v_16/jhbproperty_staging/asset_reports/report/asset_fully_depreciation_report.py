from odoo import api, models


class AssetFullyDepreciationReport(models.AbstractModel):
    _name = 'report.asset_reports.report_asset_fully_depreciation'
    _description = 'Asset Depreciation Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        sql_query = """SELECT a.acquisition_date, a.identification_number, a.name, a.description, c.name, '', a.book_value
                        FROM account_asset AS a
                        Join asset_category as c ON c.id = a.asset_category_id
                        WHERE
                        a.state != 'model'"""
        if data['from_date']:
            sql_query = sql_query + """ AND a.acquisition_date > '%s'""" %(data['from_date'])
        if data['to_date']:
            sql_query = sql_query + """ AND a.acquisition_date < '%s'""" %(data['to_date'])

        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        docs = self.env['account.asset'].search([])
        return {
            'doc_ids': docs,
            'doc_model': 'account.asset',
            'docs': docs,
            'data': result,
            'to_date': data['to_date'],
            'from_date': data['from_date']
        }
