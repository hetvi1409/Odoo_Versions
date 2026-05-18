from odoo import fields, models, api, _
from pytz import timezone
from odoo.tools.intervals import Intervals
from collections import defaultdict
from odoo.osv.expression import AND, OR
from datetime import datetime, time, timedelta
from werkzeug import urls

class HrAttendance(models.Model):
    _name = 'hr.attendance'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'hr.attendance']

    timesheet_status = fields.Selection([
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Timesheet Status', default='to_approve', tracking=True)

    # Add missing fields
    overtime_approved = fields.Boolean(
        string='Overtime Approved',
        tracking=True,
        help='Technical field to track if overtime has been approved'
    )

    def _get_employee_calendar(self):
        self.ensure_one()
        return self.employee_id.resource_calendar_id or self.employee_id.company_id.resource_calendar_id


    def get_list_url(self):
        """Returns the url for the list view"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,'web#id=%s&model=hr.attendance&view_type=form' % self.id)
        return Urls


    def action_approve_overtime(self):
        self._linked_overtimes().action_approve()

    def action_refuse_overtime(self):
        self._linked_overtimes().action_refuse()

    def action_send_attendance(self):
        manager_group = self.env.ref('hr_attendance.group_hr_attendance_manager')
        template = self.env.ref('hr_attendence_updates.email_template_to_attendance')

        for attendance in self:
            # Prepare recipient emails
            mail_values = {}
            partners = manager_group.user_ids.mapped('partner_id')
            for partner in partners:
                if partner.email:
                    mail_values = {
                        'email_to': partner.email,
                    }

            # Send email for this record
            template.send_mail(attendance.id, force_send=True, email_values=mail_values)

            # Post message to chatter
            message_body = f"Asset {attendance.employee_id.name} has sent the mail."
            asset_manager_group = self.env.ref('asset_approval.group_asset_manager')
            partner_ids = asset_manager_group.user_ids.mapped('partner_id.id')
            attendance.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=partner_ids,
            )

    def _apply_4pm_overtime_rule(self):
        overtime_lines = self.env['hr.attendance.overtime.line'].search([
            ('employee_id', 'in', self.employee_id.ids),
            ('date', 'in', self.mapped('date')),
        ])

        for ot in overtime_lines:
            attendances = self.search([
                ('employee_id', '=', ot.employee_id.id),
                ('date', '=', ot.date),
                ('check_out', '!=', False),
            ], order='check_in')

            overtime_seconds = 0
            for att in attendances:
                cutoff = datetime.combine(att.check_in.date(), time(16, 0))
                if att.check_out > cutoff:
                    overtime_seconds += (att.check_out - max(att.check_in, cutoff)).total_seconds()

            ot.write({
                'duration': round(overtime_seconds / 3600, 2),
                'manual_duration': round(overtime_seconds / 3600, 2),
            })

    def _update_overtime(self, attendance_domain=None):
        super()._update_overtime(attendance_domain)

        # Apply custom cutoff logic AFTER Odoo computes overtime
        self._apply_4pm_overtime_rule()

    def action_open_send_mail_wizard(self):
        """Open the mail compose wizard"""
        return {
            'name': _('Send Attendance Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'attendance.mail.compose.wizard',
            'target': 'new',
            'context': {
                'default_template_id': self.env.ref('hr_attendence_updates.email_template_to_attendance').id,
                'default_attendance_ids': [(6, 0, self.ids)],
            }
        }

    def action_approve_timesheet(self):
        """Approve timesheet status"""
        for record in self:
            record.write({
                'timesheet_status': 'approved'
            })
        return True

    def action_decline_timesheet(self):
        """Decline timesheet status"""
        for record in self:
            record.write({
                'timesheet_status': 'refused'
            })
        return True

    def action_open_approval_wizard(self):
        """Open the timesheet approval wizard directly"""
        # if not self:
        #     raise UserError(_("Please select attendance records to review."))

        return {
            'name': _('Review Timesheets'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'timesheet.approval.wizard',
            'target': 'new',
            'context': {
                'default_attendance_ids': self.ids,
                'form_view_ref': 'hr_attendence_updates.view_timesheet_approval_wizard',
            }
        }

