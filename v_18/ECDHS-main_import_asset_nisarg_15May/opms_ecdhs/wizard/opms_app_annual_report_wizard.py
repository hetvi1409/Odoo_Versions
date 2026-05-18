from odoo import fields, models


class OpmsAppAnnualReportWizard(models.TransientModel):
    _name = "opms.app.annual.report.wizard"
    _description = "OPMS APP Annual Report Wizard"

    programme_id = fields.Many2one("opms.programme", string="Programme", required=True)

    def action_print_report(self):
        self.ensure_one()
        data = {
            "wizard_id": self.id,
            "programme_id": self.programme_id.id,
            "programme_name": self.programme_id.name,
            "programme_code": self.programme_id.code or "",
        }
        return self.env.ref("opms_ecdhs.action_report_opms_app_annual_report").report_action(self, data=data)
