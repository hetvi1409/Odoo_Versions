from odoo import models, api


class ProjectChecklist(models.AbstractModel):
    _name = "report.internal_audit_management.report_project_checklist"
    _description = "Project Checklist"

    @api.model
    def _get_report_values(self, docids, data=None):
        model_id = data.get('model_id')
        data = self.env['project.checklist'].browse(int(model_id))
        return {
            'data' : data,
        }