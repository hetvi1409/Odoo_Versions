from odoo import fields, models


class RiskDashboardDepartmentWizard(models.TransientModel):
    _name = 'risk.report.wizard'
    _description = 'Risk Report'

    department_id = fields.Many2one('hr.department')
    risk_type_id = fields.Many2one('risk.type')

    def action_print_report(self):
        # risks = self.env['oi_risk_management.risk'].search([])
        # datas = {
        #     'data': {  # match the key name to template
        #         'risks': risks
        #     }
        # }
        domain = []
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))
        if self.risk_type_id:
            domain.append(('risk_type_id', '=', self.risk_type_id.id))
        print(domain, 'domainsd')
        risks = self.env['oi_risk_management.risk'].search(domain)
        datas = {'risk_ids': risks.ids}
        return self.env.ref(
            'oi_risk_management_report.report_risk_report').report_action(self,
                                                                          data=datas)
        return self.env.ref(
            'oi_risk_management_report.report_risk_report').report_action(self,
                                                                          data=datas)
