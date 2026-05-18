from odoo import models

class AssetImpairmentReport(models.AbstractModel):
    _name = 'report.asset_impairment.report_asset_impairment'
    _description = 'Asset Impairment Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.asset'].browse(docids)
        return {
            'docs': docs,
        }
