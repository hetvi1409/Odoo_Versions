from odoo import models, api


class AlertReminderReport(models.AbstractModel):
    _name = "report.project_porfolio_management.alert_reminder_report"
    _description = "Project Checklist"

    @api.model
    def _get_report_values(self, docids, data=None):
        projects = data.get('projects')
        if projects:
            data = self.env['project.project'].browse(projects)
        else:
            data = self.env['project.project'].search([])
        return {
            'data' : data,
            'docids': data,
            'docs': data
        }