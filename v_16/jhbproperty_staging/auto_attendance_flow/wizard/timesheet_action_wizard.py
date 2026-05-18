from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from markupsafe import Markup
import re
from PyPDF2 import PdfReader
from odoo.tools import pdf
import logging

_logger = logging.getLogger(__name__)


class TimesheetActionWizard(models.TransientModel):
    _name = 'timesheet.action.wizard'
    _description = 'Timesheet Action Wizard'

    timesheet_generator_id = fields.Many2one('hr.timesheet.generator', string="Timesheet", required=True)
    action_type = fields.Selection([('reject', 'Reject'), ('change', 'Change Request')], required=True)
    reject_reason = fields.Text("Rejection Reason")
    change_reason = fields.Text("Change Request Reason")

    def confirm_action(self):
        self.ensure_one()
        timesheet = self.timesheet_generator_id

        if self.action_type == 'reject':
            if not self.reject_reason:
                raise ValidationError("Please provide a rejection reason.")
            if not self.reject_reason or not re.search(r'\w+', self.reject_reason):
                raise UserError("You must provide a valid comment before rejecting.")

            base_url = timesheet.get_base_url()
            url = f"{base_url}/web#id={timesheet.id}&model=hr.timesheet.generator&view_type=form"
            partner_ids = [timesheet.create_uid.partner_id.id]
            if timesheet.employee_id:
                partner_ids.extend([timesheet.employee_id.user_partner_id.id])
            if timesheet.employee_id.parent_id:
                partner_ids.extend([timesheet.employee_id.parent_id.user_partner_id.id])
            timesheet.message_post(
                body=Markup(
                    '<p>The Timesheet application <strong>{name}</strong> has rejected.</p><p><b>Requested By:</b> {user}</p><p><b>Reason:</b> {reason}</p><p>You can view it by clicking the link below:</p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Timesheet</a></p> <br/>').format(
                    name=timesheet.name,
                    user=self.env.user.name,
                    reason=self.reject_reason,
                    link=url
                ),
                partner_ids=partner_ids,
                subject="Timesheet Rejected",
                email_from=self.env.user.partner_id.email or '',
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )

            timesheet.state = 'rejected'
            timesheet.rejection_reason = self.reject_reason
            timesheet.sudo().attendance_ids.write({'timesheet_status': 'refused'})
