from odoo import models, api


class ClientSurvey(models.AbstractModel):
    _name = "report.internal_audit_management.report_client_template"
    _description = "Client Satisfaction Survey Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        model_id = data.get('model_id')
        data = self.env['client.survey'].browse(int(model_id))
        return {
            'data' : data,
        }