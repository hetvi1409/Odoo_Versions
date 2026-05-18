from odoo import fields, models


class AssetImpairmentReports(models.TransientModel):
    _name = 'asset.impairment.reports'
    _description = "Asset Impairment reports"
    """Assets impairment reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_sample_report(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return self.env.ref(
            'asset_reports.action_report_asset_impairment').report_action(None, data=data)
