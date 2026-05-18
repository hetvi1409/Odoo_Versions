# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.addons.web.controllers.home import Home
# from odoo.addons.web.controllers.session import Session
import logging
from odoo.http import request
import random

_logger = logging.getLogger(__name__)


# class CustomSession(Session):
#     def get_session_info(self):
#         info = super().get_session_info()
#         info['auto_checkin_time'] = request.session.get('auto_checkin_time')
#         info['auto_checkin_name'] = request.session.get('auto_checkin_name')
#         return info


class CustomCheckinRedirect(Home):

    @http.route('/web/login', type='http', auth="none", sitemap=False, csrf=False)
    def web_login(self, redirect=None, **kw):
        response = super(CustomCheckinRedirect, self).web_login(redirect, **kw)
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(int(request.session.uid))
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', int(request.session.uid))], limit=1)
            if employee:
                # Set a random motivational message
                messages = [
                    "The early bird catches the worm!",
                    "Early to bed and early to rise, makes a man healthy, wealthy and wise!",
                    "An apple a day keeps the doctor away!",
                    "First come, first served!",
                    "If a job is worth doing, it is worth doing well!",
                    "Eat breakfast as a king, lunch as a merchant and supper as a beggar!"
                ]

                # Get the current hour
                now = fields.Datetime.now()
                hour = now.hour

                # Determine greeting
                if hour < 5:
                    greeting = "Good night"
                elif hour < 12:
                    if hour < 8 and random.random() < 0.3:
                        greeting = random.choice(
                            ["The early bird catches the worm", "First come, first served"])
                    else:
                        greeting = "Good morning"
                elif hour < 17:
                    greeting = "Good afternoon"
                elif hour < 23:
                    greeting = "Good evening"
                else:
                    greeting = "Good night"
                request.session['login_message'] = random.choice(messages)
                request.session['login_name'] = employee.name
                request.session['login_greeting'] = greeting
        if response.location == '/web' and request.params.get('login_success'):
            # --- Auto Check-in logic ---
            uid = request.session.uid
            if uid:
                try:
                    user = request.env['res.users'].sudo().browse(uid)
                    employee = request.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1)
                    auto_checkin_enabled = request.env['ir.config_parameter'].sudo().get_param('auto_attendance_flow.auto_checkin_enabled')
                    print("\n\n===auto_checkin_enabled===",auto_checkin_enabled)
                    if employee and auto_checkin_enabled:
                        attendance_model = request.env['hr.attendance'].sudo()
                        last_attendance = attendance_model.search(
                            [('employee_id', '=', employee.id)], order='check_in desc', limit=1)

                        if not last_attendance or last_attendance.check_out:
                            attendance_model.create({
                                'employee_id': employee.id,
                                'check_in': fields.Datetime.now(),
                            })
                            # session_info = request.env['ir.http'].get_frontend_session_info()
                            # session_info.update({
                            #     'login_message': random.choice(messages),
                            #     'login_name': employee.name,
                            #     'login_greeting': greeting,
                            #     'login_popup_shown': "no"
                            # })
                            _logger.info("\n\n Auto check-in for employee {} on login.".format(employee.name))

                except Exception as e:
                    _logger.info("\n\n Error : {}".format(str(e)))
                response.location = '/my/home'
        return response

    # @http.route('/web/get_login_response_value/call_kw', type='json', auth='public')
    # def get_login_response_value(self, user_id):
    #     vals = {}
    #     if user_id:
    #         user = request.env['res.users'].sudo().browse(int(user_id))
    #         employee = request.env['hr.employee'].sudo().search([('user_id', '=', int(user_id))], limit=1)
    #         if employee:
    #             messages = [
    #                 "The early bird catches the worm!",
    #                 "Early to bed and early to rise, makes a man healthy, wealthy and wise!",
    #                 "An apple a day keeps the doctor away!",
    #                 "First come, first served!",
    #                 "If a job is worth doing, it is worth doing well!",
    #                 "Eat breakfast as a king, lunch as a merchant and supper as a beggar!"
    #             ]
    #
    #             # Get the current hour
    #             now = fields.Datetime.now()
    #             hour = now.hour
    #
    #             # Determine greeting
    #             if hour < 5:
    #                 greeting = "Good night"
    #             elif hour < 12:
    #                 if hour < 8 and random.random() < 0.3:
    #                     greeting = random.choice(
    #                         ["The early bird catches the worm", "First come, first served"])
    #                 else:
    #                     greeting = "Good morning"
    #             elif hour < 17:
    #                 greeting = "Good afternoon"
    #             elif hour < 23:
    #                 greeting = "Good evening"
    #             else:
    #                 greeting = "Good night"
    #
    #             vals = {'login_message': random.choice(messages),
    #                     'login_name': employee.name,
    #                     'login_greeting': greeting,
    #                     }
    #             return vals
    #     return vals
