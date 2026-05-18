from odoo import models,api

class TruckFormReport(models.AbstractModel):
    _name = "report.oi_risk_management_report.risk_report_view"

    @api.model
    def _get_report_values(self, docids, data=None):
        risk_ids = data.get('risk_ids', [])
        risks = self.env['oi_risk_management.risk'].browse(risk_ids)
        return {
            'doc_ids': risk_ids,
            'doc_model': 'oi_risk_management.risk',
            'docs': risks,
            'data': data,
        }