from odoo import models, fields, api

class CustomerCareSummaryReportWizard(models.TransientModel):
    _name = 'customer.care.summary.report.wizard'
    _description = 'Customer Care Summary Report Wizard'


    quarter = fields.Selection([
        ('1', '1st Quarter'),
        ('2', '2nd Quarter'),
        ('3', '3rd Quarter'),
        ('4', '4th Quarter'),
        ('all', 'All Quarters')
    ], string='Quarter', required=True, default='1')
    year = fields.Integer(string='Year', required=True, default=lambda self: fields.Date.today().year)


    def generate_report(self):

        quarter_dates = {
            '1': ('01-01', '03-31'),
            '2': ('04-01', '06-30'),
            '3': ('07-01', '09-30'),
            '4': ('10-01', '12-31'),
            'all': ('01-01', '12-31')
        }

        start_date = f"{self.year}-{quarter_dates[self.quarter][0]}"
        end_date = f"{self.year}-{quarter_dates[self.quarter][1]}"

        # Filter helpdesk.ticket records based on date range
        domain = [
            ('create_date', '>=', start_date),
            ('create_date', '<=', end_date)
        ]

        filtered_tickets = self.env['helpdesk.ticket'].search(domain)

        data = {
            'quarter': self.quarter,
            'year': self.year,
            'start_date': start_date,
            'end_date': end_date,
            'ticket_ids': filtered_tickets.ids
        }
        if self.env.context.get('case_register'):
            return self.env.ref('customer_care.action_customer_care_case_register_report').report_action(self, data=data)
        if self.env.context.get('summary_report'):
            return self.env.ref('customer_care.customer_care_summary_report_action').report_action(self, data=data)