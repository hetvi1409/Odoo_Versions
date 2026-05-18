from odoo import models, api
import re
import logging

_logger = logging.getLogger(__name__)

class ReportHelpdeskTicket(models.AbstractModel):
    _name = 'report.helpdesk_ticket_report.helpdesk_ticket_report_template'
    _description = 'Helpdesk Ticket Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        HelpdeskTicket = self.env['helpdesk.ticket']
        Department = self.env['hr.department']

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        report_type = data.get('report_type')
        _logger.info("Tickets data for report: %s", data)

        domain = []
        if start_date:
            domain.append(('create_date', '>=', start_date))
        if end_date:
            domain.append(('create_date', '<=', end_date))

        docs = []
        total_tickets = 0

        if report_type == 'by_department':
            # Count tickets per department
            departments = Department.sudo().search([])
            for dept in departments:
                count = HelpdeskTicket.sudo().search_count(domain + [('user_id.employee_id.department_id', '=', dept.id)])
                if count > 0:
                    docs.append({'department': dept.name, 'count': count})
                    total_tickets += count

            # Calculate percentage
            for doc in docs:
                doc['percentage'] = (doc['count'] / total_tickets * 100) if total_tickets else 0

        else:
            # All tickets or open tickets
            ticket_domain = domain.copy()
            if report_type == 'open_tickets':
                ticket_domain.append(('stage_id.name', 'not in', ['Approved', 'Solved', 'Canceled']))

            tickets = HelpdeskTicket.sudo().search(ticket_domain)
            clean_html = re.compile('<.*?>')
            for ticket in tickets:
                ticket.description = re.sub(clean_html, '', ticket.description or '')
            if tickets:
                docs.append({'department': 'All Tickets', 'tickets': tickets})

        _logger.info("Tickets fetched for report: %s", docs)

        return {
            'doc_ids': docids,
            'doc_model': 'helpdesk.ticket',
            'data': data,
            'docs': docs,
            'total_tickets': total_tickets,
        }
