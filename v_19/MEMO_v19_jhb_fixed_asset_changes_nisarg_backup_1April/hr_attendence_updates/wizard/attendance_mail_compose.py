from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AttendanceMailComposeWizard(models.TransientModel):
    _name = 'attendance.mail.compose.wizard'
    _description = 'Attendance Mail Compose Wizard'

    template_id = fields.Many2one('mail.template', string='Email Template',
                                default=lambda self: self.env.ref('hr_attendence_updates.email_template_to_attendance'))
    recipient_ids = fields.Many2many('res.partner', string='Additional Recipients')
    attendance_ids = fields.Many2many('hr.attendance', string='Attendances')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        # Check if current user has employee record
        employee = self.env.user.employee_id
        if not employee:
            raise UserError(_("You don't have an employee record. Please contact HR to create one."))

        # Check if employee has manager
        if not employee.parent_id:
            raise UserError(_("Your employee record is not linked to any manager. Please contact HR to update your record."))

        # Set default recipient as employee's manager
        if employee.parent_id.user_id.partner_id:
            res['recipient_ids'] = [(4, employee.parent_id.user_id.partner_id.id)]

        if active_ids:
            res['attendance_ids'] = [(6, 0, active_ids)]

        return res

    def action_send_mail(self):
        self.ensure_one()
        if not self.attendance_ids:
            raise UserError(_("No attendance records selected."))

        # Get base URL and action ID
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # Use the correct XML ID path
        action = self.env.ref('hr_attendence_updates.action_timesheet_approval_wizard', raise_if_not_found=False)
        if not action:
            raise UserError(_("Action not found. Please contact your administrator."))

        # Prepare email values
        email_values = {
            'recipient_ids': [(6, 0, self.recipient_ids.ids)],
            'email_layout_xmlid': 'mail.mail_notification_light'
        }

        # Add attendance records and URL info to template context
        template = self.template_id.with_context(
            attendance_records=self.attendance_ids,
            employee_name=self.attendance_ids[0].employee_id.name,
            recipient_name=self.recipient_ids[0].name,
            base_url=base_url,
            action_id=action.id,
            attendance_ids=','.join(map(str, self.attendance_ids.ids))
        )

        # Send email
        template.send_mail(
            self.attendance_ids[0].id,
            force_send=True,
            email_values=email_values
        )

        return {'type': 'ir.actions.act_window_close'}