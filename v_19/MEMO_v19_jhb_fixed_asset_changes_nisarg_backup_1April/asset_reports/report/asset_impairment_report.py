from odoo import api, models


class AssetImpairmentReport(models.AbstractModel):
    _name = 'report.asset_reports.report_asset_impairment'
    _description = 'Asset Impairment Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        sql_query = """SELECT a.barcode, a.name,
                        a.book_value, 
                             p.name,  a.state
                        FROM account_asset AS a
						JOIN
                       res_users AS u ON u.id = a.create_uid
					   JOIN res_partner as p ON p.id = u.partner_id
                        WHERE
                        a.state != 'model'  """
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
            # 'service': data['leads'],
            # 'groups': data['groups'],
        }
