from odoo import http
from odoo.http import request

class HelpdeskCustomValidation(http.Controller):

    @http.route('/get_helpdesk_team', type='jsonrpc', auth='public', website=True)
    def get_helpdesk_team(self, team_id):
        team = request.env['helpdesk.team'].sudo().browse(team_id)
        return {'id': team.id, 'name': team.name} if team.exists() else {}

    @http.route('/check_employee_email', type='jsonrpc', auth='public', website=True)
    def check_employee_email(self, email):
        employee = request.env['hr.employee'].sudo().search([('work_email', '=', email)], limit=1)
        return bool(employee)
