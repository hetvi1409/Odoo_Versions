from odoo import api, fields, models, _
from odoo.exceptions import UserError

class TimesheetApprovalWizard(models.TransientModel):
    _name = 'timesheet.approval.wizard'
    _description = 'Timesheet Approval Wizard'

    attendance_ids = fields.Many2many('hr.attendance', string='Attendances')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get('default_attendance_ids'):
            # Handle both string and list formats
            attendance_ids = self.env.context.get('default_attendance_ids')
            if isinstance(attendance_ids, str):
                # Convert string of IDs to list of integers
                try:
                    attendance_ids = [int(id) for id in attendance_ids.split(',')]
                except ValueError:
                    attendance_ids = []
            res['attendance_ids'] = [(6, 0, attendance_ids)]
        return res

    def action_approve_all(self):
        # if not self.attendance_ids:
        #     raise UserError(_("No timesheet records selected."))
        self.attendance_ids.write({'timesheet_status': 'approved'})
        self._send_response_email()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {
                'menu_id': self.env.ref('hr_attendance.menu_hr_attendance_root').id
            }
        }

    def action_decline_all(self):
        # if not self.attendance_ids:
        #     raise UserError(_("No timesheet records selected."))
        self.attendance_ids.write({'timesheet_status': 'refused'})
        self._send_response_email()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {
                'menu_id': self.env.ref('hr_attendance.menu_hr_attendance_root').id
            }
        }

    def _send_response_email(self):
        if not self.attendance_ids:
            return

        template = self.env.ref('hr_attendence_updates.email_template_attendance_response')

        # Group attendances by employee
        attendances_by_employee = {}
        for attendance in self.attendance_ids:
            if attendance.employee_id not in attendances_by_employee:
                attendances_by_employee[attendance.employee_id] = self.env['hr.attendance']
            attendances_by_employee[attendance.employee_id] |= attendance

        # Send one email per employee with their consolidated records
        for employee, employee_attendances in attendances_by_employee.items():
            if not employee.user_id.partner_id:
                continue

            template.with_context(
                employee_name=employee.name,
                attendance_records=employee_attendances,
            ).send_mail(
                employee_attendances[0].id,
                force_send=True,
                email_values={
                    'recipient_ids': [(6, 0, [employee.user_id.partner_id.id])]
                }
            )
