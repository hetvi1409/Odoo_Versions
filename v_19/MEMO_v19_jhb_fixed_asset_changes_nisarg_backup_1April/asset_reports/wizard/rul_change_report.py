from odoo import api, fields, models


class AssetRULChangeReports(models.TransientModel):
    _name = 'asset.rul.reports'
    _description = "Asset RUL Change reports"
    """Assets RUL Change reports"""

    to_date = fields.Date(string="To Date", help="To date")
    from_date = fields.Date(string="From Date", help="From date")

    def print_sample_report(self):
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date
        }
        return self.env.ref(
            'asset_reports.action_report_asset_rul').report_action(None, data=data)
