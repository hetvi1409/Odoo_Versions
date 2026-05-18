from odoo import models
from datetime import datetime, timedelta

class CustomerCareCaseRegisterReport(models.AbstractModel):
    _name = 'report.customer_care.customer_care_case_register_report'

    def _get_report_values(self, docids, data=None):
        data = data or {}
        ticket_ids = data.get('ticket_ids') or []
        if ticket_ids:
            records = self.env['helpdesk.ticket'].browse(ticket_ids)
            return {
                'docs': records,
                'data': data,
            }

        quarter = data.get('quarter')
        year = int(data.get('year'))

        # Quarter month mapping
        quarter_map = {
            '1': (1, 3),
            '2': (4, 6),
            '3': (7, 9),
            '4': (10, 12),
        }

        start_month, end_month = quarter_map.get(quarter)

        # Start date
        date_from = datetime(year, start_month, 1, 0, 0, 0)

        # End date = last day of end_month
        if end_month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, end_month + 1, 1)

        date_to = next_month - timedelta(seconds=1)

        records = self.env['helpdesk.ticket'].search([
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to),
        ])

        return {
            'docs': records,
            'data': data,
        }