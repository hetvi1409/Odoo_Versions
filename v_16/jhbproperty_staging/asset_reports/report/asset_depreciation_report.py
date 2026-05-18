from odoo import api, models


class AssetDepreciationReport(models.AbstractModel):
    _name = 'report.asset_reports.report_asset_depreciation'
    _description = 'Asset Depreciation Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        sql_query = """SELECT a.identification_number, aa.code, aa.name, aml.ref, aml.debit, aml.credit
                        FROM account_asset AS a
                        Join account_move as am ON am.asset_id = a.id
                        Join account_move_line as aml on aml.move_id = am.id
                        Join account_account as aa on aa.id = aml.account_id
                        WHERE a.state != 'model' """
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
