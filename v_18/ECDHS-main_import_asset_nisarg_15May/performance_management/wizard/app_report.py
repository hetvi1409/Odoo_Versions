from odoo import models, fields

class AppReportWizard(models.TransientModel):
    _name = 'app.report.wizard'
    _description = 'App Report Wizard'

    portfolio_id=fields.Many2one('performance.programme',string="Programme")


    def action_print_report(self):

        data = {
                'id': self.id,
                'portfolio_id': self.portfolio_id.id,
                'portfolio_name': self.portfolio_id.name,
                'description': self.portfolio_id.description,
                # 'outcomes':outcome,
        }
        return self.env.ref('performance_management.action_report_app_report').report_action(self,data=data)
