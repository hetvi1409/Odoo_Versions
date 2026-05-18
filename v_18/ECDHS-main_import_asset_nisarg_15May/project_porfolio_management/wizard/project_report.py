from odoo import fields, models


class ProjectReport(models.TransientModel):
    _name = "project.report"

    project_ids = fields.Many2many('project.project')

    def action_print(self):
        datas = {'projects': self.project_ids.ids}
        return self.env.ref(
            'project_porfolio_management.alert_reminder_report_cation').report_action(self,
                                                                          data=datas)
