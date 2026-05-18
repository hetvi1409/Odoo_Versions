from odoo import models, api
from datetime import date,datetime
import base64

class HelpdeskReportScheduler(models.Model):
    _inherit = 'helpdesk.ticket'

    def _generate_and_send_report(self, template_xml_id, report_ref, report_type, data):
        """Generate PDF report and send via email properly using report ref."""

        # Get the mail template
        mail_template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if not mail_template:
            raise ValueError(f"Mail template not found: {template_xml_id}")

        # Create wizard record (report uses wizard model)
        wizard = self.env['helpdesk.ticket.report.wizard'].create({
            'start_date': datetime.strptime(data.get('start_date'), '%Y-%m-%d').strftime('%Y-%m-%d') if data.get('start_date') else '',
            'end_date': datetime.strptime(data.get('end_date'), '%Y-%m-%d').strftime('%Y-%m-%d') if data.get('start_date') else '',
            'report_type': data.get('report_type'),
        })

        # ✅ Correct way to render report PDF by XML ID string
        report_pdf, _ = self.env['ir.actions.report']._render_qweb_pdf(
            report_ref, [wizard.id],data=data
        )

        pdf_base64 = base64.b64encode(report_pdf)

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f"{report_type.capitalize()}_Helpdesk_Report_{date.today()}.pdf",
            'type': 'binary',
            'datas': pdf_base64,
            'mimetype': 'application/pdf',
            'res_model': 'helpdesk.ticket.report.wizard',
            'res_id': wizard.id,
        })

        # Send email with attachment
        mail_template.attachment_ids = [(6, 0, [attachment.id])]
        mail_template.with_context(today=date.today()).send_mail(wizard.id, force_send=True)

    # --------------------------
    # Scheduler methods
    # --------------------------

    @api.model
    def send_daily_open_tickets_report(self):
        """Send daily report of open tickets."""
        today = date.today()
        data = {
            'start_date': today.strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d'),
            'report_type': 'open_tickets',
        }
        self._generate_and_send_report(
            'helpdesk_ticket_report.email_template_daily_helpdesk_report',
            'helpdesk_ticket_report.action_helpdesk_ticket_report',
            'daily',
            data
        )

    @api.model
    def send_weekly_all_tickets_report(self):
        """Send weekly report of all tickets created this month."""
        today = date.today()
        start_date = today.replace(day=1)
        data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d'),
            'report_type': 'all_tickets',
        }
        self._generate_and_send_report(
            'helpdesk_ticket_report.email_template_weekly_helpdesk_report',
            'helpdesk_ticket_report.action_helpdesk_ticket_report',
            'weekly',
            data
        )

    @api.model
    def send_monthly_by_department_report(self):
        """Send monthly report grouped by department."""
        today = date.today()
        start_date = today.replace(day=1)
        data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d'),
            'report_type': 'by_department',
        }
        self._generate_and_send_report(
            'helpdesk_ticket_report.email_template_monthly_helpdesk_report',
            'helpdesk_ticket_report.action_helpdesk_ticket_report',
            'monthly',
            data
        )
