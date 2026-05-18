from odoo import http
from odoo.http import request
import json
import urllib.parse

class TimesheetWizardController(http.Controller):

    @http.route('/timesheet/review', type='http', auth='user')
    def review_timesheets(self, attendance_ids=None, **kw):
        # Clean the attendance_ids
        attendance_ids = [int(i) for i in attendance_ids.split(',') if i.strip()] if attendance_ids else []

        # Prepare context
        context = {
            'default_attendance_ids': attendance_ids,
            'form_view_ref': 'hr_attendence_updates.view_timesheet_approval_wizard',
        }

        # Get the action ID
        action = request.env.ref('hr_attendence_updates.action_timesheet_approval_wizard')
        action['context'] = context
        # Construct the proper URL manually
        base_url = "/web#"
        params = {
            "action": action.id,
            "model": "timesheet.approval.wizard",
            "view_type": "form",
            "context": json.dumps(context),
        }

        return request.redirect(base_url + urllib.parse.urlencode(params))
