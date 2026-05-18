from odoo import models, fields, api

class HelpdeskTicketReportWizard(models.TransientModel):
    _name = 'helpdesk.ticket.report.wizard'
    _description = 'Helpdesk Ticket Report Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    report_type = fields.Selection([
        ('by_department', 'By Department'),
        ('open_tickets', 'Open Tickets'),
        ('all_tickets', 'All Tickets')
    ], string='Report Type', required=True, default='all_tickets')

    def action_print_report(self):
        """Trigger report with wizard data"""
        data = {
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else '',
            'report_type': self.report_type,
        }
        return self.env.ref('helpdesk_ticket_report.action_helpdesk_ticket_report').report_action(None, data=data)
