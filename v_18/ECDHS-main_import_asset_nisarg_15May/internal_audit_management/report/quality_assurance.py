from odoo import models, api


class QualityAssurance(models.AbstractModel):
    _name = "report.internal_audit_management.report_quality_assurance"
    _description = "Quality Assurance"

    @api.model
    def _get_report_values(self, docids, data=None):
        model_id = data.get('model_id')
        data = self.env['quality.assurance'].browse(int(model_id))
        return {
            'data' : data,
        }