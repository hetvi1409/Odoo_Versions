from odoo import models, fields

class AppReportWizard(models.TransientModel):
    _name = 'app.quarterly.report.wizard'
    _description = 'App Report Wizard'

    portfolio_id=fields.Many2one('performance.programme',string="Programme",required=True)
    target=fields.Many2one('target.targets',string="Target Period",required=True)

    def action_print_quarterly_report(self):

        data = {
                'id': self.id,
               'target_name': self.target.name,
               'target_id': self.target.id,
            'programe' : self.portfolio_id.id
        }
        return self.env.ref('performance_management.action_quaterely_report_app_report').report_action(self,data=data)
