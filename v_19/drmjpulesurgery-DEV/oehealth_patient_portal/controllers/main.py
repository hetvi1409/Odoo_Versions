# -*- coding: utf-8 -*-
##############################################################################
#    Copyright (C) 2020 Braincrew Apps (<http://www.braincrewapps.com>). All Rights Reserved

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################
# -*- coding: utf-8 -*-
import base64

import odoo
from odoo import http, SUPERUSER_ID, _
from odoo.http import request, content_disposition
import werkzeug.utils
from odoo.exceptions import UserError
from odoo.exceptions import AccessError
from odoo.exceptions import MissingError
import io
from odoo.addons.auth_signup.models.res_users import SignupError
# from odoo.addons.web.controllers.main import Home
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as ASH,Home
from odoo.addons.portal.controllers.portal import CustomerPortal
import dateutil.parser


import logging

_logger = logging.getLogger(__name__)


class CustomerPortalINH(CustomerPortal):
    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        if partner.email:
            search_patient_family = request.env['oeh.medical.patient.family'].sudo().search([
                ('email', '=', partner.email),
            ], limit=1)
            # if search_patient_family:
            #     values['family_responsible'] = search_patient_family.patient_id.name
        return request.render("portal.portal_my_home", values)


class AuthSignupHomeINH(ASH):
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if request.httprequest.method == 'POST':
            patient_id = kw.get('patient_id')
            dob = kw.get('birth_date')
            search_patient = request.env['oeh.medical.patient'].sudo().search([
                ('identification_code', '=', patient_id),
                ('dob', '=', dob)
            ], limit=1)
            if not search_patient:
                qcontext['error'] = _("Patient verification failed !")
            else:
                email = kw.get('login')
                # search_patient_family = request.env['oeh.medical.patient.family'].sudo().search([
                #     ('email', '=', email),
                #     ('patient_id', '=', search_patient.id)
                # ], limit=1)
                # if search_patient_family:
                #     search_patient_family.sudo().write({'family_responsible': True})
                # else:
                check_if_patient_exists = request.env['oeh.medical.patient'].sudo().search([('email', '=', email)],
                                                                                           limit=1)
                if not check_if_patient_exists:
                    family_values = {
                        'name': kw.get('name'),
                        'email': email,
                        # 'family_responsible': True,
                        'patient_id': search_patient.id,
                        'age': kw.get('age')
                    }
                    if 'relation' in kw and kw.get('relation'):
                        family_values['relation'] = kw.get('relation')
                        family_values['age'] = kw.get('age')
                    request.env['oeh.medical.patient.family'].sudo().create(family_values)

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    User = request.env['res.users']
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                    )
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class AuthSignupHome(Home):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang

        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    def _signup_with_values(self, token, values):
        patient_token = values.get('patient_token')
        find_patient_id = request.env['oeh.medical.patient'].sudo().search(
            [('patient_token', '=', patient_token)], limit=1)
        values.pop('patient_token')
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password)

        if not uid:
            raise SignupError(_('Authentication Failed.'))
        else:
            params = dict(request.params)

            if params.get("patient_token", False) != "False":
                user = request.env['res.users'].sudo().browse(int(uid))
                patient = request.env['oeh.medical.patient'].sudo().browse(int(find_patient_id))

                if user:
                    group_employee_id = request.env.ref('base.group_portal').id
                    user_values = {
                        'group_ids': [(6, 0, [group_employee_id])]
                    }
                    user.sudo().write(user_values)
                    patient_values = {
                        'oeh_patient_user_id': user.id
                    }

                    patient.sudo().write(patient_values)

    @http.route(['/patient/registration/<patient_token>'], type='http', auth="public",
                website=True)
    def health_center_signup_form(self, patient_token=None, *args, **kw):
        print('\n\n\n HEALTH_CENTER_SIGNUP_FORM--->',self)
        find_patient_id = request.env['oeh.medical.patient'].sudo().search([('patient_token', '=', patient_token)],
                                                                           limit=1)
        print('\n\n\n find_patient_id--->',find_patient_id)
        # find_patient_id---> oeh.medical.patient(1,)

        qcontext = self.get_auth_signup_qcontext()
        print('qcontext--->',qcontext)
         # qcontext---> {'disable_database_manager': False, 'signup_enabled': False, 'reset_password_enabled': True}

        qcontext['patient_token'] = patient_token
        print('qcontext--->',qcontext)
        print('\n\n request.httprequest.method--->',request.httprequest.method)

        if request.httprequest.method == "POST":
            print('\n\n\n INSIDE POST--->',kw)
            patient_id = kw.get('patient_id')
            dob = kw.get('dob')
            search_patient = request.env['oeh.medical.patient'].sudo().search([
                ('identification_code', '=', patient_id),
                ('dob', '=', dob)
            ], limit=1)
            if not search_patient:
                qcontext['error'] = _("Patient verification failed !")
        if request.httprequest.method != 'POST':
            print('\n\n inside this if----->')
            qcontext.update({'signup_from_patient_registration_page': True})
            qcontext.update({'signup_enabled': True})
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        if kw.get("name", False):
            if 'error' not in qcontext and request.httprequest.method == 'POST':
                try:
                    # qcontext.update({'find_patient_id': find_patient_id})
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                except UserError as e:
                    qcontext['error'] = e.name or e.value
                except (SignupError, AssertionError) as e:
                    if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                        qcontext["error"] = _("Another user is already registered using this email address.")
                    else:
                        _logger.error("%s", e)
                        qcontext['error'] = _("Could not create a new account.")
            if kw.get("signup_from_patient_registration_page", False) == "true":
                qcontext.pop("error")
                qcontext.update({'hide_top_menu': True})
        print('\n\n rendef--->',qcontext)

        return request.render('oehealth_patient_portal.patient_web_registration', qcontext)


class OehPatientPortal(http.Controller):

    def get_time_string(self, duration):
        currentHours = int(duration // 1)
        currentMinutes = int(round(duration % 1 * 60))
        if (currentHours <= 9):
            currentHours = "0" + str(currentHours)
        if (currentMinutes <= 9):
            currentMinutes = "0" + str(currentMinutes)
        return str(currentHours), str(currentMinutes)

    def time_string_to_decimals(self, time_string):
        fields = time_string.split(":")
        hours = fields[0] if len(fields) > 0 else 0.0
        minutes = fields[1] if len(fields) > 1 else 0.0
        seconds = fields[2] if len(fields) > 2 else 0.0
        return float(hours) + (float(minutes) / 60.0) + (float(seconds) / pow(60.0, 2))

    @http.route(['/patient/portal/<patient_token>'], type='http', auth="user", website=True)
    def patient_details(self, patient_token=None, report_type=None, download=False, **post):
        print('\n\n\n patient_details---->',self)
        if not patient_token:
            patient = request.env['oeh.medical.patient'].sudo().search(
                [('oeh_patient_user_id', '=', request.env.user.id)])
        else:
            patient = request.env['oeh.medical.patient'].sudo().search([('patient_token', '=', patient_token)])
        print('patient--->',patient)
        values = {}
        if patient and patient.oeh_patient_user_id:
            values['patient'] = patient
            values['upcoming_appointments'] = upcoming_appointments = request.env[
                'oeh.medical.appointment'].sudo().search(
                [('patient', '=', patient.id), ('appointment_date', '>', datetime.today().strftime(DF))], limit=3)
            values['past_appointments'] = past_appointments = request.env[
                'oeh.medical.appointment'].sudo().search(
                [('patient', '=', patient.id), ('appointment_date', '<', datetime.today().strftime(DF))], limit=3)
            values['today_appointments'] = today_appointments = request.env['oeh.medical.appointment'].sudo().search(
                [('patient', '=', patient.id),
                 ('appointment_date', '>', datetime.today().strftime('%Y-%m-%d 00:01:01')),
                 ('appointment_date', '<', datetime.today().strftime('%Y-%m-%d 11:59:59'))], limit=3)
            if len(upcoming_appointments) > 0 or len(today_appointments) > 0 or len(past_appointments) > 0:
                values['appointments_available'] = True
            else:
                values['appointments_available'] = False

            return request.render("oehealth_patient_portal.patient_detail_form", values)
        else:
            return request.redirect('/patient/registration/%s' % patient_token)

    @http.route(
        ['/patient/portal/card/<int:patient_id>'],
        type='http', auth='user', website=True)
    def print_patient_card(self, patient_id=False):
        if patient_id:
            card = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            report_ref = 'oehealth.action_report_patient_label'
            report_sudo = request.env.ref(report_ref).sudo()
            if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
                raise UserError(_("%s is not the reference of a report") % report_ref)
            method_name = '_render_qweb_pdf'
            report = getattr(report_sudo, method_name)([patient_id], data={'report_type': 'pdf'})[0]
            reporthttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(report)),
            ]
            filename = "Patient Card - %s.pdf" % str(card.identification_code)
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
            return request.make_response(report, headers=reporthttpheaders)
        else:
            return request.redirect('/patient/portal')

    @http.route('/patients', type='http', auth="user", website=True)
    def patient_doctor_details(self, **kwargs):
        values = {}
        if 'search' not in kwargs or kwargs.get('search') == '':
            patients = request.env['oeh.medical.patient'].sudo().search([])
            values['patients'] = patients
            values['search'] = ''
        else:
            search_term = kwargs.get('search')
            patients = request.env['oeh.medical.patient'].sudo().search(
                ['|', '|', ('name', 'ilike', search_term), ('identification_code', 'ilike', search_term),
                 ('email', 'ilike', search_term)])
            values['patients'] = patients
            values['search'] = search_term
        return request.render("oehealth_patient_portal.patient_doctor_detail_form", values)

    @http.route('/health/create_health_center', type='http', auth="user", website=True)
    def post_health_center(self, **kwargs):
        print("\n\n\n post_health_center--->",self)
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        return request.render("oehealth_patient_portal.post_health_center_organization", {})

    @http.route('/health/create_health_center/thankyou', methods=['POST'], type='http', auth="user", website=True)
    def health_center_thankyou(self, **kwargs):
        healthcenter = request.env['oeh.medical.health.center']
        health_center_name = kwargs.get('name')
        company = request.env['res.company'].sudo().create({
            'name': health_center_name,
            'street': kwargs.get('street'),
            'city': kwargs.get('city'),
            'zip': kwargs.get('zip'),
            'country_id': int(kwargs.get('country_id')),
            'email': kwargs.get('notify_email'),
            'logo': base64.b64encode(kwargs.get('image_1920').read()),
        })
        if company:
            vals3 = {
                'name': health_center_name,
                'company_id': company.id,
                'email': kwargs.get('notify_email'),
                'health_center_type': kwargs.get('health_center_type') or 'Hospital',
                'street': kwargs.get('street'),
                'city': kwargs.get('city'),
                'zip': kwargs.get('zip'),
                'country_id': int(kwargs.get('country_id')),
                'image_1920': base64.b64encode(kwargs.get('image_1920').read()),
            }
            health_center_id = healthcenter.sudo().create(vals3)
            return request.render("oehealth_patient_portal.health_center_thankyou", {
                'email': kwargs.get('notify_email'),
            })
        else:
            return request.redirect('/')

    @http.route('/health/create_test_center', type='http', auth="user", website=True)
    def post_test_center(self, **kwargs):
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        return request.render("oehealth_patient_portal.post_test_center_organization", {})

    @http.route('/health/create_test_center/thankyou', methods=['POST'], type='http', auth="user", website=True)
    def test_center_thankyou(self, **kwargs):
        testcenter = request.env['africsys.test.center']
        test_center_name = kwargs.get('name')
        company = request.env['res.company'].sudo().create({
            'name': test_center_name
        })
        if company:
            vals3 = {
                'name': test_center_name,
                'company_id': company.id,
                'email': kwargs.get('notify_email'),
                'info': kwargs.get('info'),
                'street': kwargs.get('street'),
                'city': kwargs.get('city'),
                'zip': kwargs.get('zip'),
                'country_id': int(kwargs.get('country_id')),
            }
            test_center_id = testcenter.sudo().create(vals3)
            if test_center_id:
                test_center_id.partner_id.sudo().write({
                    'image_1920': base64.b64encode(kwargs.get('image_1920').read()),
                })
            return request.render("oehealth_patient_portal.test_center_thankyou", {
                'email': kwargs.get('notify_email'),
            })
        else:
            return request.redirect('/')

    @http.route("/test/center/list", type='http', auth="public", website=True)
    def view_test_center(self, **kwargs):
        test_center = request.env["africsys.test.center"].sudo().search([])
        return request.render("oehealth_patient_portal.test_center_list", {'test_center': test_center})

    @http.route("/health/center/list", type='http', auth="public", website=True)
    def view_health_center(self, **kwargs):
        health_center = request.env["oeh.medical.health.center"].sudo().search([])
        return request.render("oehealth_patient_portal.health_center_list", {'health_center': health_center})

    @http.route("/health/center/<int:id>", type='http', auth="user", website=True)
    def view_health_center_detail(self, id=0, **kwargs):
        # health_center = request.env["oeh.medical.health.center"].sudo().search([("id", "=", str(id))], limit=1)
        return request.render("oehealth_patient_portal.edit_health_center", {'institution': id})

    @http.route("/health/center/<institution>/buildings/list", type='http', auth="user", website=True)
    def view_buildings(self, institution=0, **kwargs):
        buildings = request.env["oeh.medical.health.center.building"].sudo().search(
            [("institution", "=", int(institution))])
        return request.render("oehealth_patient_portal.buildings_list",
                              {'buildings': buildings, 'institution': int(institution)})

    @http.route("/health/center/<institution>/buildings/<int:id>", type='http', auth="user", website=True)
    def view_buildings_detail(self, institution=0, id=0, **kwargs):
        building = request.env["oeh.medical.health.center.building"].sudo().search([('id', "=", int(id))], limit=1)
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', '=', int(institution))])
        return request.render("oehealth_patient_portal.edit_building",
                              {'building': building, 'health_center': health_center})

    @http.route("/health/center/building/<int:id>/edit/submit", type='http', auth="user", website=True)
    def edit_buildings_detail(self, id=0, **kwargs):
        name = kwargs.get('name')
        institution = kwargs.get('institution')
        code = kwargs.get('code')
        building = request.env["oeh.medical.health.center.building"].sudo().search([("id", "=", str(id))], limit=1)
        building.sudo().write({
            'name': name,
            'institution': int(institution) if institution else False,
            'code': code
        })
        return request.redirect('/health/center/%s/buildings/list' % (int(building.institution.id)))

    @http.route("/health/center/<int:id>/buildings/create", type='http', auth="user", website=True)
    def create_buildings_detail(self, id=0, **kwargs):
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', '=', int(id))], limit=1)
        return request.render("oehealth_patient_portal.create_building", {'health_center': health_center})

    @http.route("/health/center/building/create/submit", type='http', auth="user", website=True)
    def create_buildings_detail_submit(self, **kwargs):
        name = kwargs.get('name')
        institution = kwargs.get('institution')
        code = kwargs.get('code')
        building = request.env["oeh.medical.health.center.building"]
        b1 = building.sudo().create({
            'name': name,
            'institution': int(institution) if institution else False,
            'code': code
        })
        return request.redirect('/health/center/%s/buildings/list' % (int(b1.institution.id)))

    @http.route("/health/center/<int:institution>/wards/list", type='http', auth="user", website=True)
    def view_wards(self, institution=0, **kwargs):
        wards = request.env["oeh.medical.health.center.ward"].sudo().search([("institution", "=", int(institution))])
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        return request.render("oehealth_patient_portal.wards_list", {'wards': wards, 'health_center': health_center})

    @http.route("/health/center/<int:institution>/wards/<int:id>", type='http', auth="user", website=True)
    def view_wards_detail(self, institution=0, id=0, **kwargs):
        wards = request.env["oeh.medical.health.center.ward"].sudo().search([('id', "=", int(id))], limit=1)
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        building = request.env["oeh.medical.health.center.building"].sudo().search(
            [('institution', "=", int(institution))])
        return request.render("oehealth_patient_portal.edit_wards",
                              {'wards': wards, 'building': building, 'health_center': health_center})

    @http.route("/health/center/wards/<int:id>/edit/submit", type='http', auth="user", website=True)
    def edit_wards_detail(self, id=0, **kwargs):
        name = kwargs.get('name')
        institution = kwargs.get('institution')
        building = kwargs.get('building')
        floor = kwargs.get('floor')
        gender = kwargs.get('gender')
        private = kwargs.get('private')
        bio_hazard = kwargs.get('bio_hazard')
        telephone = kwargs.get('telephone')
        tv = kwargs.get('tv')
        ac = kwargs.get('ac')
        private_bathroom = kwargs.get('private_bathroom')
        guest_sofa = kwargs.get('guest_sofa')
        internet = kwargs.get('internet')
        refrigerator = kwargs.get('refrigerator')
        microwave = kwargs.get('microwave')
        wards = request.env["oeh.medical.health.center.ward"].sudo().search([("id", "=", str(id))], limit=1)
        wards.sudo().write({
            'name': name,
            'institution': int(institution) if institution else False,
            'building': int(building) if building else False,
            'floor': floor,
            'gender': gender,
            'private': private,
            'bio_hazard': bio_hazard,
            'telephone': telephone,
            'ac': ac,
            'private_bathroom': private_bathroom,
            'guest_sofa': guest_sofa,
            'tv': tv,
            'internet': internet,
            'refrigerator': refrigerator,
            'microwave': microwave,
        })
        return request.redirect('/health/center/%s/wards/list' % (int(wards.institution.id)))

    @http.route("/health/center/<int:institution>/wards/create", type='http', auth="user", website=True)
    def create_wards_detail(self, institution=0, **kwargs):
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        building = request.env["oeh.medical.health.center.building"].sudo().search(
            [('institution', "=", int(institution))])
        return request.render("oehealth_patient_portal.create_wards",
                              {'building': building, 'health_center': health_center})

    @http.route("/health/center/wards/create/submit", type='http', auth="user", website=True)
    def create_wards_detail_submit(self, **kwargs):
        name = kwargs.get('name')
        institution = kwargs.get('institution')
        building = kwargs.get('building')
        floor = kwargs.get('floor')
        gender = kwargs.get('gender')
        private = kwargs.get('private')
        bio_hazard = kwargs.get('bio_hazard')
        telephone = kwargs.get('telephone')
        tv = kwargs.get('tv')
        ac = kwargs.get('ac')
        private_bathroom = kwargs.get('private_bathroom')
        guest_sofa = kwargs.get('guest_sofa')
        internet = kwargs.get('internet')
        refrigerator = kwargs.get('refrigerator')
        microwave = kwargs.get('microwave')
        wards = request.env["oeh.medical.health.center.ward"]
        w1 = wards.sudo().create({
            'name': name,
            'institution': int(institution) if institution else False,
            'building': int(building) if building else False,
            'floor': floor,
            'gender': gender,
            'private': private,
            'bio_hazard': bio_hazard,
            'telephone': telephone,
            'ac': ac,
            'private_bathroom': private_bathroom,
            'guest_sofa': guest_sofa,
            'tv': tv,
            'internet': internet,
            'refrigerator': refrigerator,
            'microwave': microwave,
        })
        return request.redirect('/health/center/%s/wards/list' % (int(w1.institution.id)))

    @http.route("/health/center/<int:institution>/beds/list", type='http', auth="user", website=True)
    def view_beds(self, institution=0, **kwargs):
        beds = request.env["oeh.medical.health.center.beds"].sudo().search([("institution", "=", int(institution))])
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        return request.render("oehealth_patient_portal.beds_list", {'beds': beds, 'health_center': health_center})

    @http.route("/health/center/<int:institution>/beds/<int:id>", type='http', auth="user", website=True)
    def view_beds_detail(self, institution=0, id=0, **kwargs):
        beds = request.env["oeh.medical.health.center.beds"].sudo().search([("id", "=", str(id))], limit=1)
        wards = request.env["oeh.medical.health.center.ward"].sudo().search([('institution', "=", int(institution))])
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        building = request.env["oeh.medical.health.center.building"].sudo().search(
            [('institution', "=", int(institution))])
        return request.render("oehealth_patient_portal.edit_beds",
                              {'beds': beds, 'wards': wards, 'building': building, 'health_center': health_center})

    @http.route("/health/center/beds/<int:id>/edit/submit", type='http', auth="user", website=True)
    def edit_beds_detail(self, id=0, **kwargs):
        name = kwargs.get('name')
        institution = kwargs.get('institution')
        ward = kwargs.get('ward')
        building = kwargs.get('building')
        list_price = kwargs.get('list_price')
        telephone_number = kwargs.get('telephone_number')
        bed_type = kwargs.get('bed_type')
        change_bed_status = kwargs.get('change_bed_status')
        beds = request.env["oeh.medical.health.center.beds"].sudo().search([("id", "=", str(id))], limit=1)
        beds.sudo().write({
            'name': name,
            'ward': int(ward) if ward else False,
            'institution': int(institution) if institution else False,
            'building': int(building) if building else False,
            'list_price': list_price,
            'bed_type': bed_type,
            'telephone_number': telephone_number,
            'change_bed_status': change_bed_status,
        })
        return request.redirect('/health/center/%s/beds/list' % (int(beds.institution.id)))

    @http.route("/health/center/<int:institution>/beds/create", type='http', auth="user", website=True)
    def create_beds_detail(self, institution=0, **kwargs):
        wards = request.env["oeh.medical.health.center.ward"].sudo().search([('institution', "=", int(institution))])
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        building = request.env["oeh.medical.health.center.building"].sudo().search(
            [('institution', "=", int(institution))])
        return request.render("oehealth_patient_portal.create_beds",
                              {'wards': wards, 'building': building, 'health_center': health_center})

    @http.route("/health/center/beds/create/submit", type='http', auth="user", website=True)
    def create_beds_detail_submit(self, **kwargs):
        name = kwargs.get('name')
        institution = kwargs.get('institution')
        ward = kwargs.get('ward')
        building = kwargs.get('building')
        list_price = kwargs.get('list_price')
        telephone_number = kwargs.get('telephone_number')
        bed_type = kwargs.get('bed_type')
        change_bed_status = kwargs.get('change_bed_status')
        beds = request.env["oeh.medical.health.center.beds"]
        b1 = beds.sudo().create({
            'name': name,
            'ward': int(ward) if ward else False,
            'institution': int(institution) if institution else False,
            'building': int(building) if building else False,
            'list_price': list_price,
            'bed_type': bed_type,
            'telephone_number': telephone_number,
            'change_bed_status': change_bed_status,
        })
        return request.redirect('/health/center/%s/beds/list' % (int(b1.institution.id)))

    @http.route("/health/center/<int:institution>/ot/list", type='http', auth="user", website=True)
    def view_ot(self, institution=0, **kwargs):
        ot = request.env["oeh.medical.health.center.ot"].sudo().search(
            [("building.institution", "=", int(institution))])
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        return request.render("oehealth_patient_portal.ot_list", {'ot': ot, 'health_center': health_center})

    @http.route("/health/center/<int:institution>/ot/<int:id>", type='http', auth="public", website=True)
    def view_ot_detail(self, institution=0, id=0, **kwargs):
        ot = request.env["oeh.medical.health.center.ot"].sudo().search([('id', '=', int(id))], limit=1)
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        building = request.env["oeh.medical.health.center.building"].sudo().search(
            [('institution', "=", int(institution))])
        return request.render("oehealth_patient_portal.edit_ot",
                              {'ot': ot, 'building': building, 'health_center': health_center})

    @http.route("/health/center/ot/<int:id>/edit/submit", type='http', auth="user", website=True)
    def edit_ot_detail(self, id=0, **kwargs):
        name = kwargs.get('name')
        building = kwargs.get('building')
        ot = request.env["oeh.medical.health.center.ot"].sudo().search([("id", "=", str(id))], limit=1)
        ot.sudo().write({
            'name': name,
            'building': int(building) if building else False,
        })
        return request.redirect('/health/center/%s/ot/list' % (int(ot.building.institution.id)))

    @http.route("/health/center/<int:institution>/ot/create", type='http', auth="user", website=True)
    def create_ot_detail(self, institution=0, **kwargs):
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        building = request.env["oeh.medical.health.center.building"].sudo().search(
            [('institution', "=", int(institution))])
        return request.render("oehealth_patient_portal.create_ot",
                              {'building': building, 'health_center': health_center})

    @http.route("/health/center/ot/create/submit", type='http', auth="public", website=True)
    def create_ot_detail_submit(self, **kwargs):
        name = kwargs.get('name')
        building = kwargs.get('building')
        ot = request.env["oeh.medical.health.center.ot"]
        o = ot.sudo().create({
            'name': name,
            'building': int(building) if building else False,
        })
        return request.redirect('/health/center/%s/ot/list' % (int(o.building.institution.id)))

    @http.route("/health/center/<int:institution>/pharmacies/list", type='http', auth="user", website=True)
    def view_pharmacies(self, institution=0, **kwargs):
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        pharmacy = request.env["oeh.medical.health.center.pharmacy"].sudo().search(
            [("institution", "=", int(institution))])
        return request.render("oehealth_patient_portal.pharmacy_list",
                              {'pharmacy': pharmacy, 'health_center': health_center})

    @http.route("/health/center/<int:institution>/pharmacies/<int:id>", type='http', auth="public", website=True)
    def view_pharmacies_detail(self, institution=0, id=0, **kwargs):
        pharmacy = request.env["oeh.medical.health.center.pharmacy"].sudo().search([("id", "=", str(id))], limit=1)
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        state_id = request.env["res.country.state"].sudo().search([])
        country_id = request.env["res.country"].sudo().search([])
        return request.render("v.edit_pharmacy",
                              {'pharmacy': pharmacy, 'health_center': health_center, 'state_id': state_id,
                               'country_id': country_id, 'institution': int(institution)})

    @http.route("/health/center/pharmacy/<int:id>/edit/submit", type='http', auth="user", website=True)
    def edit_pharmacies_detail(self, id=0, **kwargs):
        name = kwargs.get('name')
        institution = kwargs.get('institution')
        pharmacist_name = kwargs.get('pharmacist_name')
        street = kwargs.get('street')
        street2 = kwargs.get('street2')
        city = kwargs.get('city')
        state_id = kwargs.get('state_id')
        zip = kwargs.get('zip')
        country_id = kwargs.get('country_id')
        phone = kwargs.get('phone')
        mobile = kwargs.get('mobile')
        email = kwargs.get('email')
        website = kwargs.get('website')
        pharmacy = request.env["oeh.medical.health.center.pharmacy"].sudo().search([("id", "=", str(id))], limit=1)

        if institution:
            health_center_id = request.env['oeh.medical.health.center'].sudo().browse(int(institution))
        else:
            health_center_id = False

        search_pharmacist = request.env['oeh.medical.physician'].sudo().search(
            [('name', '=', str(pharmacist_name)), ('is_pharmacist', '=', True)], limit=1)
        if search_pharmacist:
            pharmacist_id = search_pharmacist
            if health_center_id:
                pharmacist_id.sudo().write({
                    'company_id': health_center_id and health_center_id.company_id and health_center_id.company_id.id or False
                })
        else:
            pharmacist_id = request.env['oeh.medical.physician'].sudo().create({
                'name': str(pharmacist_name),
                'is_pharmacist': True,
                'company_id': health_center_id and health_center_id.company_id and health_center_id.company_id.id or False
            })

        pharmacy.sudo().write({
            'name': name,
            'institution': health_center_id and health_center_id.id or False,
            'pharmacist_name': pharmacist_id.id,
            'street': street,
            'street2': street2,
            'city': city,
            'state_id': int(state_id) if state_id else False,
            'zip': zip,
            'phone': phone,
            'mobile': mobile,
            'email': email,
            'country_id': int(country_id) if country_id else False,
            'website': website,
        })
        return request.redirect('/health/center/%s/pharmacies/list' % (int(pharmacy.institution.id)))

    @http.route("/health/center/<int:institution>/pharmacies/create", type='http', auth="user", website=True)
    def create_pharmacies_detail(self, institution=0, **kwargs):
        physician = request.env["oeh.medical.physician"].sudo().search([])
        health_center = request.env["oeh.medical.health.center"].sudo().search([('id', "=", int(institution))], limit=1)
        state_id = request.env["res.country.state"].sudo().search([])
        country_id = request.env["res.country"].sudo().search([])
        return request.render("oehealth_patient_portal.create_pharmacy",
                              {'physician': physician, 'health_center': health_center, 'state_id': state_id,
                               'country_id': country_id, })

    @http.route("/health/center/pharmacies/create/submit", type='http', auth="user", website=True)
    def create_pharmacies_detail_submit(self, **kwargs):
        name = kwargs.get('name')
        institution = kwargs.get('institution')
        pharmacist_name = kwargs.get('pharmacist_name')
        street = kwargs.get('street')
        street2 = kwargs.get('street2')
        city = kwargs.get('city')
        state_id = kwargs.get('state_id')
        zip = kwargs.get('zip')
        country_id = kwargs.get('country_id')
        phone = kwargs.get('phone')
        mobile = kwargs.get('mobile')
        email = kwargs.get('email')
        website = kwargs.get('website')
        pharmacy = request.env["oeh.medical.health.center.pharmacy"]

        if institution:
            health_center_id = request.env['oeh.medical.health.center'].sudo().browse(int(institution))
        else:
            health_center_id = False

        search_pharmacist = request.env['oeh.medical.physician'].sudo().search(
            [('name', '=', str(pharmacist_name)), ('is_pharmacist', '=', True)], limit=1)
        if search_pharmacist:
            pharmacist_id = search_pharmacist
        else:
            pharmacist_id = request.env['oeh.medical.physician'].sudo().create({
                'name': str(pharmacist_name),
                'is_pharmacist': True,
                'company_id': health_center_id and health_center_id.company_id and health_center_id.company_id.id or False
            })

        p1 = pharmacy.sudo().create({
            'name': name,
            'institution': health_center_id and health_center_id.id or False,
            'pharmacist_name': pharmacist_id.id,
            'street': street,
            'street2': street2,
            'city': city,
            'state_id': int(state_id) if state_id else False,
            'zip': zip,
            'phone': phone,
            'mobile': mobile,
            'email': email,
            'country_id': int(country_id) if country_id else False,
            'website': website,
        })
        return request.redirect('/health/center/%s/pharmacies/list' % (int(p1.institution.id)))

    @http.route(['/patient/portal/update/img'], type='http', auth="user", website=True)
    def update_patient_profile_img(self, **post):
        files = request.httprequest.files.getlist('attachment')
        partner_id = int(post.get('partner_id'))
        patient = request.env['oeh.medical.patient'].sudo().search([('partner_id', '=', partner_id)])
        if partner_id:
            for file in files:
                Attachments = request.env['ir.attachment'].sudo().search([('res_model', '=', 'res.partner'),
                                                                          ('res_id', '=', partner_id)])
                attachment = file.read()
                encode = base64.encodebytes(attachment)
                partner = request.env['res.partner'].sudo().browse(partner_id)
                if partner:
                    partner.write({'image_1920': base64.encodebytes(attachment)})
                    request.env.user.image_1920 = base64.encodebytes(attachment)
        if 'patient' in post and post.get('patient') != '':
            # return request.redirect('/patient/portal/%s' % int(post.get('patient')))
            return request.redirect('/patient/portal/%s' % patient.patient_token)
        else:
            return request.redirect('/patient/portal/%s' % patient.patient_token)

    @http.route(['/patient/portal/remove/img'], type='http', auth="user", website=True)
    def remove_patient_profile_img(self, **post):
        partner_id = int(post.get('partner_id'))
        partner = request.env['res.partner'].sudo().browse(partner_id)
        patient = request.env['oeh.medical.patient'].sudo().search([('partner_id', '=', partner_id)])
        if partner:
            partner.write({'image_1920': ''})
            request.env.user.image_1920 = ''
        return request.redirect('/patient/portal/%s' % patient.patient_token)

    @http.route('/patient/portal/account/update/<int:patient_id>', type='http', auth="user", website=True)
    def open_patient_edit_form(self, patient_id=False, **post):
        values = {}
        if patient_id:
            patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['patient'] = patient
            values['doctors'] = request.env['oeh.medical.physician'].sudo().search([('is_pharmacist', '=', False)])
            values['ethnicities'] = request.env['oeh.medical.ethnicity'].sudo().search([])
            values['insurances'] = request.env['oeh.medical.insurance'].sudo().search(
                [('patient', '=', patient.id), ('state', '=', 'Active')])
            values['states'] = request.env['res.country.state'].sudo().search([])
            values['countries'] = request.env['res.country'].sudo().search([])
        else:
            return request.redirect('/')
        return request.render("oehealth_patient_portal.patient_my_account", values)

    @http.route('/patient/portal/account/<int:patient_id>/edit', type='http', auth="user", website=True)
    def update_patient_details(self, patient_id=False, **post):
        patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
        if patient_id:
            if 'country_id' in post and post.get('country_id') != '':
                post['country_id'] = int(post.get('country_id'))
            if 'state_id' in post and post.get('state_id') != '':
                post['state_id'] = int(post.get('state_id'))
            request.env['oeh.medical.patient'].sudo().browse(int(patient_id)).write(post)
            # return request.redirect('/patient/portal/%s' % int(patient_id))
            return request.redirect('/patient/portal/%s' % patient.patient_token)
        else:
            return request.redirect('/patient/portal/%s' % patient.patient_token)

    @http.route(['/patient/portal/<int:patient_id>/family', '/patient/portal/<int:patient_id>/family/<int:family_id>'],
                type='http', auth="user", website=True)
    def add_patient_family(self, patient_id=False, family_id=False, **post):
        values = {}
        # patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
        # print("===========================875==================",patient)
        if patient_id:
            print("==========================877==", patient_id)
            values['patient'] = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            if family_id:
                values['family'] = request.env['oeh.medical.patient.family'].sudo().browse(int(family_id))
                values['form_action'] = _("/patient/portal/family/%s/edit") % int(family_id)
            else:
                values['family'] = False
                values['form_action'] = "/patient/portal/family/add"
        else:
            return request.redirect('/patient/portal/%s/view/family' % patient_id)
        return request.render("oehealth_patient_portal.patient_manage_family", values)

    @http.route(['/patient/portal/<int:patient_id>/view/family'],
                type='http', auth="user", website=True)
    def view_patient_family(self, patient_id=False, family_id=False, **post):
        values = {}
        values['patient'] = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
        # values['family'] = family = request.env['oeh.medical.patient.family'].sudo().browse(int(family_id))
        values['family'] = family = request.env['oeh.medical.patient.family'].sudo().search(
            [('patient_id', '=', patient_id)])
        print("====================891===========", family)
        if family:
            values['family_member_available'] = True
        else:
            values['family_member_available'] = False
        return request.render("oehealth_patient_portal.view_patient_family_members", values)

    @http.route('/patient/portal/family/add', type='http', auth="user", website=True)
    def create_patient_family(self, **post):
        print("================884==========", post)
        patient = request.env['oeh.medical.patient'].sudo().browse(int(post.get('patient_id')))
        if 'deceased' in post and post.get('deceased') == 'Yes':
            post['deceased'] = True
        else:
            post['deceased'] = False
        # if 'family_responsible' in post and post.get('family_responsible') == 'Yes':
        #     post['family_responsible'] = True
        # else:
        #     post['family_responsible'] = False
        request.env['oeh.medical.patient.family'].sudo().create(post)
        return request.redirect('/patient/portal/%s/view/family' % patient.id)

    @http.route('/patient/portal/family/<int:family_id>/edit', type='http', auth="user", website=True)
    def update_patient_family(self, family_id=False, **post):
        patient = request.env['oeh.medical.patient'].sudo().browse(int(post.get('patient_id')))
        if family_id:
            if 'deceased' in post and post.get('deceased') == 'Yes':
                post['deceased'] = True
            else:
                post['deceased'] = False
            # if 'family_responsible' in post and post.get('family_responsible') == 'Yes':
            #     post['family_responsible'] = True
            # else:
            #     post['family_responsible'] = False
            request.env['oeh.medical.patient.family'].sudo().browse(int(family_id)).write(post)
        return request.redirect('/patient/portal/%s/view/family' % patient.id)

    @http.route('/patient/portal/family/<int:family_id>/remove', type='http', auth="user", website=True)
    def delete_patient_family_member(self, family_id=False, **post):
        if family_id:
            family = request.env['oeh.medical.patient.family'].sudo().browse(int(family_id))
            token = family.patient_id
            family.sudo().unlink()
            # patient = request.env['oeh.medical.patient'].sudo().browse(int(post.get('toke?n')))
        return request.redirect('/patient/portal/%s/view/family' % token.id)

    @http.route(['/patient/portal/<int:patient_id>/appointments'], type='http', auth="user", website=True)
    def view_patient_appointments(self, patient_id=False, **post):
        values = {}
        values['patient'] = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
        values['upcoming_appointments'] = upcoming_appointments = request.env[
            'oeh.medical.appointment'].sudo().search(
            [('patient', '=', patient_id), ('appointment_date', '>', datetime.today().strftime(DF))], limit=3)
        values['past_appointments'] = past_appointments = request.env[
            'oeh.medical.appointment'].sudo().search(
            [('patient', '=', patient_id), ('appointment_date', '<', datetime.today().strftime(DF))], limit=3)
        values['today_appointments'] = today_appointments = request.env['oeh.medical.appointment'].sudo().search(
            [('patient', '=', patient_id), ('appointment_date', '>', datetime.today().strftime('%Y-%m-%d 00:01:01')),
             ('appointment_date', '<', datetime.today().strftime('%Y-%m-%d 11:59:59'))], limit=3)
        if len(upcoming_appointments) > 0 or len(today_appointments) > 0 or len(past_appointments) > 0:
            values['appointments_available'] = True
        else:
            values['appointments_available'] = False
        return request.render("oehealth_patient_portal.view_patient_appointments", values)

    @http.route(['/patient/portal/<int:patient_id>/appointment',
                 '/patient/portal/<int:patient_id>/appointment/<int:appointment_id>'],
                type='http', auth="user", website=True)
    def add_patient_appointment(self, patient_id=False, appointment_id=False, **post):
        values = {}
        if 'error_message' in post:
            values['error_message'] = post.get('error_message')
        if patient_id:
            values['patient'] = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['doctors'] = request.env['oeh.medical.physician'].sudo().search([('is_pharmacist', '=', False)])
            values['institutions'] = request.env['oeh.medical.health.center'].sudo().search([])
            print("=============", values['institutions'])
            if appointment_id:
                appointment = request.env['oeh.medical.appointment'].sudo().browse(int(appointment_id))
                appointment_date = dateutil.parser.parse(
                    appointment.appointment_date.strftime("%Y-%m-%d %H:%M")).isoformat()
                values['appointment'] = appointment
                values['appointment_date'] = appointment_date
                values['form_action'] = _("/patient/portal/appointment/%s/edit") % int(appointment_id)
                values['duration_hour'], values['duration_minute'] = self.get_time_string(appointment.duration)
            else:
                values['appointment'] = False
                values['appointment_date'] = False
                values['duration_hour'] = 0
                values['duration_minute'] = 30
                values['form_action'] = "/patient/portal/appointment/add"
        else:
            return request.redirect('/patient/portal/%s' % values['patient'])
        return request.render("oehealth_patient_portal.patient_manage_appointment", values)

    @http.route('/patient/portal/appointment/add', type='http', auth="user", website=True)
    def create_patient_appointment(self, **post):
        try:
            patient = request.env['oeh.medical.patient'].sudo().browse(int(post.get('patient')))
            # appointment_date = str(post.get('appointment_date')) + " " + str(post.get('appointment_hour')) + ":" + str(
            #     post.get('appointment_minute'))
            duration_str = str(post.get('duration_hour')) + ":" + str(post.get('duration_minute'))
            post['duration'] = self.time_string_to_decimals(duration_str)
            post['patient'] = int(post.get('patient'))
            # post['appointment_date'] = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
            # del post['appointment_hour']
            # del post['appointment_minute']
            post['appointment_date'] = dateutil.parser.parse(post.get('appointment_date'))
            del post['duration_hour']
            del post['duration_minute']
            request.env['oeh.medical.appointment'].sudo().create(post)
        except UserError as e:
            return request.redirect(
                '/patient/portal/%s/appointment?error_message=%s' % (int(post.get('patient')), str(e.value)))
        # return request.redirect('/patient/portal/%s' % int(post.get('patient')))
        print("==================================983==============", patient.patient_token)
        return request.redirect('/patient/portal/%s' % patient.patient_token)

    @http.route('/patient/portal/appointment/<int:appointment_id>/edit', type='http', auth="user", website=True)
    def update_patient_appointment(self, appointment_id=False, **post):
        if appointment_id:
            patient = request.env['oeh.medical.patient'].sudo().browse(int(post.get('patient')))
            print("=================1018===========", patient)
            # appointment_date = str(post.get('appointment_date')) + " " + str(post.get('appointment_hour')) + ":" + str(post.get('appointment_minute'))
            duration_str = str(post.get('duration_hour')) + ":" + str(post.get('duration_minute'))
            post['duration'] = self.time_string_to_decimals(duration_str)
            post['appointment_date'] = dateutil.parser.parse(post.get('appointment_date'))
            # post['appointment_date'] = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
            # del post['appointment_hour']
            # del post['appointment_minute']
            del post['duration_hour']
            del post['duration_minute']
            request.env['oeh.medical.appointment'].sudo().browse(int(appointment_id)).write(post)
        # return request.redirect('/patient/portal/%s' % int(post.get('patient')))
        return request.redirect('/patient/portal/%s' % patient.patient_token)

    @http.route('/patient/portal/<int:patient_id>/appointment/<int:appointment_id>/remove', type='http', auth="user",website=True)
    def delete_patient_appointment(self, patient_id=False, appointment_id=False, **post):
        print("==============1037=====================")
        if appointment_id:
            appointment = request.env['oeh.medical.appointment'].sudo().browse(int(appointment_id))
            token = appointment.patient.patient_token
            print("=================1040=============",token)
            appointment.sudo().unlink()
        # return request.redirect('/patient/portal/%s' % int(patient_id))
        return request.redirect('/patient/portal/%s' % token)

    @http.route(['/patient/portal/<int:patient_id>/family_members'], type='http', auth="user", website=True)
    def view_patient_family_members(self, patient_id=False, **post):
        values = {}
        values['patient'] = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
        values['derfat_'] = upcoming_appointments = request.env[
            'oeh.medical.appointment'].sudo().search(
            [('patient', '=', patient_id), ('appointment_date', '>', datetime.today().strftime(DF))], limit=3)
        values['past_appointments'] = past_appointments = request.env[
            'oeh.medical.appointment'].sudo().search(
            [('patient', '=', patient_id), ('appointment_date', '<', datetime.today().strftime(DF))], limit=3)
        values['today_appointments'] = today_appointments = request.env['oeh.medical.appointment'].sudo().search(
            [('patient', '=', patient_id), ('appointment_date', '>', datetime.today().strftime('%Y-%m-%d 00:01:01')),
             ('appointment_date', '<', datetime.today().strftime('%Y-%m-%d 11:59:59'))], limit=3)
        if len(upcoming_appointments) > 0 or len(today_appointments) > 0 or len(past_appointments) > 0:
            values['appointments_available'] = True
        else:
            values['appointments_available'] = False
        return request.render("oehealth_patient_portal.view_patient_appointments", values)

    @http.route('/patient/portal/<int:patient_id>/socioeconomics', type='http', auth='user', website=True)
    def patient_socioeconomics(self, patient_id=False):
        values = {}
        values['occupations'] = request.env['oeh.medical.occupation'].sudo().search([])
        if patient_id:
            patient_rec = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['patient'] = patient_rec
        else:
            return request.redirect('/patient/portal')
        return request.render("oehealth_patient_portal.patient_socioeconomics", values)

    @http.route('/patient/portal/<int:patient_id>/socioeconomics/update', type='http', auth='user', website=True)
    def update_patient_socioeconomics(self, patient_id=False, **post):
        if patient_id:
            boolean_keys = [
                'works_at_home',
                'hostile_area',
                'sewers',
                'gas',
                'water',
                'telephone',
                'trash',
                'television',
                'electricity',
                'internet',
                'single_parent',
                'drug_addiction',
                'domestic_violence',
                'school_withdrawal',
                'teenage_pregnancy',
                'working_children',
                'prison_past',
                'prison_current',
                'sexual_abuse',
                'relative_in_prison'
            ]
            for key, value in post.items():
                if key in boolean_keys:
                    if value == 'Yes':
                        post[key] = True
                    else:
                        post[key] = False

            request.env['oeh.medical.patient'].sudo().browse(int(patient_id)).write(post)

            # return request.redirect('/patient/portal/%s' % int(patient_id))
            return request.redirect('/patient/portal/%s', )
        else:
            return request.redirect('/patient/portal')

    @http.route('/patient/portal/<int:patient_id>/lifestyle', type='http', auth='user', website=True)
    def patient_lifestyle(self, patient_id=0):
        values = {}
        if patient_id:
            patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['patient'] = patient
        else:
            return request.redirect('/patient/portal')
        return request.render("oehealth_patient_portal.patient_lifestyle", values)

    @http.route(['/health/patient/<int:patient_id>/hospital',
                 '/health/patient/<int:patient_id>/hospital/<int:hospital_id>'],
                type='http', auth="user", website=True)
    def add_patient_hospital(self, patient_id=False, hospital_id=False, **post):
        values = {}
        if 'error_message' in post and post.get('error_message') != '':
            values['error_message'] = post.get('error_message')
        if patient_id:
            values['patient'] = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['hospitals'] = request.env['oeh.medical.health.center'].sudo().search([])
            if hospital_id:
                values['hospital'] = hospital = request.env['oeh.medical.patient.hospitals'].sudo().browse(
                    int(hospital_id))
                values['hospital_id'] = hospital.name.id
                values['primary_hospital'] = hospital.primary_hospital
                values['form_action'] = _("/health/patient/hospital/%s/edit") % int(hospital_id)
            else:
                values['hospital'] = False
                values['hospital_id'] = False
                values['primary_hospital'] = False
                values['form_action'] = "/health/patient/hospital/add"
        else:
            return request.redirect('/patients')
        return request.render("oehealth_patient_portal.patient_manage_hospital", values)

    @http.route('/health/patient/hospital/add', type='http', auth="user", website=True)
    def create_patient_hospital(self, **post):
        if 'primary_hospital' in post and post.get('primary_hospital') == 'Yes':
            search_primary_hospital = request.env['oeh.medical.patient.hospitals'].sudo().search([
                ('patient', '=', int(post.get('patient'))),
                ('primary_hospital', '=', True),
                ('name', '!=', int(post.get('name')))
            ], limit=1)
            if not search_primary_hospital:
                post['primary_hospital'] = True
            else:
                error_message = 'Only single hospital can be set as Primary hospital.'
                return request.redirect(
                    '/health/patient/%s/hospital?error_message=%s' % (int(post.get('patient')), str(error_message)))
        else:
            post['primary_hospital'] = False
        request.env['oeh.medical.patient.hospitals'].sudo().create(post)
        # return request.redirect('/patient/portal/%s' % int(post.get('patient')))
        return request.redirect('/patient/portal')

    @http.route('/health/patient/hospital/<int:hospital_id>/edit', type='http', auth="user", website=True)
    def update_patient_hospital(self, hospital_id=False, **post):
        if hospital_id:
            try:
                if 'primary_hospital' in post and post.get('primary_hospital') == 'Yes':
                    search_primary_hospital = request.env['oeh.medical.patient.hospitals'].sudo().search([
                        ('patient', '=', int(post.get('patient'))),
                        ('primary_hospital', '=', True),
                        ('name', '!=', int(post.get('name')))
                    ], limit=1)
                    if not search_primary_hospital:
                        post['primary_hospital'] = True
                    else:
                        error_message = 'Only single hospital can be set as Primary hospital.'
                        return request.redirect(
                            '/health/patient/%s/hospital?error_message=%s' % (
                                int(post.get('patient')), str(error_message)))
                else:
                    post['primary_hospital'] = False
                request.env['oeh.medical.patient.hospitals'].sudo().browse(int(hospital_id)).write(post)
            except UserError as e:
                return request.redirect(
                    '/health/patient/%s/hospital?error_message=%s' % (int(post.get('patient')), str(e.value)))

        # return request.redirect('/patient/portal/%s' % int(post.get('patient')))
        return request.redirect('/patient/portal')

    @http.route('/health/patient/<int:patient_id>/hospital/<int:hospital_id>/remove', type='http', auth="user",
                website=True)
    def delete_patient_hospital(self, patient_id=False, hospital_id=False, **post):
        if hospital_id:
            request.env['oeh.medical.patient.hospitals'].sudo().browse(int(hospital_id)).sudo().unlink()
        return request.redirect('/health/patient/%s' % int(patient_id))

    @http.route('/health/patient/<int:patient_id>/call-logs', type='http', auth='user', website=True)
    def patient_call_logs(self, patient_id=False):
        values = {}
        if patient_id:
            patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['patient'] = patient
            values['call_logs'] = request.env['oeh.medical.patient.call.log'].sudo().search([
                ('patient', '=', int(patient_id))
            ])
        else:
            return request.redirect('/patients')
        return request.render("oehealth_patient_portal.view_patient_call_logs", values)

    @http.route(
        ['/health/patient/<int:patient_id>/call-log', '/health/patient/<int:patient_id>/call-log/<int:call_log_id>'],
        type='http', auth='user', website=True)
    def add_patient_call_logs(self, patient_id=False, call_log_id=False):
        values = {}
        if patient_id:
            patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['patient'] = patient
            if call_log_id:
                call_log = request.env['oeh.medical.patient.call.log'].sudo().browse(int(call_log_id))
                log_date = dateutil.parser.parse(call_log.log_date.strftime("%Y-%m-%d %H:%M")).isoformat()
                values['call_log'] = call_log
                values['log_date'] = log_date
                values['form_action'] = _("/health/patient/call-log/%s/edit") % int(call_log_id)
            else:
                values['call_log'] = False
                values['log_date'] = False
                values['form_action'] = '/health/patient/call-log/add'
        else:
            return request.redirect('/patients')
        return request.render("oehealth_patient_portal.add_patient_call_log", values)

    @http.route('/health/patient/call-log/add', type='http', auth="user", website=True)
    def create_patient_call_log(self, **post):
        # call_log_date = str(post.get('log_date')) + " " + str(post.get('log_hour')) + ":" + str(post.get('log_minute'))
        # post['log_date'] = datetime.strptime(call_log_date, "%Y-%m-%d %H:%M")
        # del post['log_hour']
        # del post['log_minute']
        post['log_date'] = dateutil.parser.parse(post.get('log_date'))
        request.env['oeh.medical.patient.call.log'].sudo().create(post)
        return request.redirect('/health/patient/%s/call-logs' % int(post.get('patient')))

    @http.route('/health/patient/call-log/<int:call_log_id>/edit', type='http', auth="user", website=True)
    def update_patient_call_log(self, call_log_id=False, **post):
        if call_log_id:
            # call_log_date = str(post.get('log_date')) + " " + str(post.get('log_hour')) + ":" + str(post.get('log_minute'))
            # post['log_date'] = datetime.strptime(call_log_date, "%Y-%m-%d %H:%M")
            # post['person_in_charge'] = request.env.user.id
            # del post['log_hour']
            # del post['log_minute']
            post['log_date'] = dateutil.parser.parse(post.get('log_date'))
            request.env['oeh.medical.patient.call.log'].sudo().browse(int(call_log_id)).write(post)
        if 'patient' in post and post.get('patient') != '':
            return request.redirect('/health/patient/%s/call-logs' % int(post.get('patient')))
        else:
            return request.redirect('/patients')

    @http.route('/health/patient/<int:patient_id>/call-log/<int:call_log_id>/remove', type='http', auth="user",
                website=True)
    def delete_patient_call_log(self, patient_id=False, call_log_id=False, **post):
        if call_log_id:
            request.env['oeh.medical.patient.call.log'].sudo().browse(int(call_log_id)).sudo().unlink()
        if patient_id:
            return request.redirect('/health/patient/%s/call-logs' % int(patient_id))
        else:
            return request.redirect('/patients')

    @http.route('/patient/portal/<int:patient_id>/medical-history', type='http', auth='user', website=True)
    def patient_medical_history(self, patient_id=False):
        values = {}
        if patient_id:
            patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['patient'] = patient
        else:
            return request.redirect('/patient/portal')
        return request.render("oehealth_patient_portal.patient_medical_history", values)

    @http.route('/patient/portal/<int:patient_id>/medical-history/update', type='http', auth="user", website=True)
    def update_patient_medical_history(self, patient_id=False, **post):

        if patient_id:
            boolean_keys = [
                'hbv_infection_chk',
                'dm_chk',
                'ihd_chk',
                'cold_chk',
                'hypertension_chk',
                'surgery_chk',
                'nsaids_chk',
                'aspirin_chk',
                'laxative_chk',
                'menorrhagia_chk',
                'lmp_chk',
                'dysmenorrhoea_chk',
                'bleeding_pv_chk',
                'last_pap_smear_chk'
            ]
            for key, value in post.items():
                if key in boolean_keys:
                    if value == 'Yes':
                        post[key] = True
                    else:
                        post[key] = False

            patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            patient.write(post)
            token = patient.patient_token
            # return request.redirect('/patient/portal/%s' % int(patient_id))
            return request.redirect('/patient/portal/%s' % token)
        else:
            return request.redirect('/')

    @http.route('/patient/portal/<int:patient_id>/lifestyle/update', type='http', auth="user", website=True)
    def update_patient_life_style(self, patient_id=False, **post):
        if patient_id:
            boolean_keys = [
                'exercise',
                'sleep_during_daytime',
                'soft_drinks',
                'eats_alone',
                'salt',
                'coffee',
                'diet',
                'smoking',
                'ex_smoker',
                'second_hand_smoker',
                'alcohol',
                'ex_alcoholic',
                'drug_usage',
                'drug_iv',
                'ex_drug_addict',
                'prostitute',
                'sex_with_prostitutes',
                'motorcycle_rider',
                'car_seat_belt',
                'helmet',
                'car_child_safety',
                'home_safety',
                'traffic_laws',
                'car_revision'
            ]
            for key, value in post.items():
                if key in boolean_keys:
                    if value == 'Yes':
                        post[key] = True
                    else:
                        post[key] = False

            request.env['oeh.medical.patient'].sudo().browse(int(patient_id)).write(post)
        return request.redirect('/patient/portal')

    @http.route('/patient/portal/<int:patient_id>/evaluations', type='http', auth='user', website=True)
    def patient_evaluations(self, patient_id=False):
        values = {}
        if patient_id:
            values['patient'] = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['evaluations'] = request.env['oeh.medical.evaluation'].sudo().search([
                ('patient', '=', int(patient_id))
            ])
        else:
            return request.redirect('/patient/portal')
        return request.render("oehealth_patient_portal.view_patient_evaluations", values)

    @http.route(
        ['/patient/portal/<int:patient_id>/evaluation/<int:evaluation_id>'],
        type='http', auth='user', website=True)
    def view_patient_evaluation(self, patient_id=False, evaluation_id=False, **post):
        values = {}
        if patient_id:
            values['patient'] = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
        values['evaluation'] = request.env['oeh.medical.evaluation'].sudo().browse(int(evaluation_id))
        return request.render("oehealth_patient_portal.view_patient_evaluation_details", values)

    @http.route(
        ['/patient/portal/medical-certificate/<int:cert_id>'],
        type='http', auth='user', website=True)
    def print_patient_certificate(self, cert_id=False):
        if cert_id:
            cert = request.env['oeh.medical.patient.medical.cert'].sudo().browse(int(cert_id))
            report_ref = 'oehealth.action_report_oeh_medical_patient_medical_cert'
            report_sudo = request.env.ref(report_ref).sudo()
            if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
                raise UserError(_("%s is not the reference of a report") % report_ref)
            method_name = '_render_qweb_pdf'
            report = getattr(report_sudo, method_name)([cert_id], data={'report_type': 'pdf'})[0]
            reporthttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(report)),
            ]
            filename = "Medical Certificate - %s.pdf" % str(cert.name)
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
            return request.make_response(report, headers=reporthttpheaders)
        else:
            return request.redirect('/patient/portal')

    @http.route(
        ['/patient/portal/<int:patient_id>/medical-certificate',
         '/patient/portal/<int:patient_id>/medical-certificate/<int:cert_id>'],
        type='http', auth='user', website=True)
    def add_patient_certi(self, patient_id=False, cert_id=False, doctor=False):
        # print("===============================================1389", post)
        values = {}
        if patient_id:
            doctor = request.env['oeh.medical.physician'].sudo().search([])
            values['doctor'] = doctor
            patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
            values['patient'] = patient
            health_center = request.env["oeh.medical.health.center"].sudo().search([])
            values['health_center'] = health_center

            if cert_id:
                cert = request.env['oeh.medical.patient.medical.cert'].sudo().browse(int(cert_id))
                mc_issue_date = dateutil.parser.parse(cert.issue_date.strftime("%Y-%m-%d %H:%M")).isoformat()
                values['cert_id'] = cert
                values['mc_issue_date'] = mc_issue_date
                values['form_action'] = _("/patient/portal/%s/medical-certificate/%s/edit") % (
                    int(patient_id), int(cert_id))
            else:
                values['cert_id'] = False
                values['mc_issue_date'] = False
                values['form_action'] = _('/patient/portal/%s/medical-certificate/add') % int(patient_id)
        else:
            return request.redirect('/patient/portal')
        return request.render("oehealth_patient_portal.patient_manage_medical_certificates", values)

    @http.route('/patient/portal/<int:patient_id>/medical-certificate/add', type='http', auth="user", website=True)
    def create_patient_certi(self, patient_id=False, **post):

        patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
        post['issue_date'] = dateutil.parser.parse(post.get('issue_date'))
        request.env['oeh.medical.patient.medical.cert'].sudo().create(post)
        # return request.redirect('/patient/portal/%s' % int(patient_id))
        return request.redirect('/patient/portal/%s' % patient.patient_token)

    @http.route('/patient/portal/<int:patient_id>/medical-certificate/<int:cert_id>/edit', type='http', auth="user",
                website=True)
    def update_patient_certi(self, patient_id=False, cert_id=False, **post):

        patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
        if cert_id:
            post['issue_date'] = dateutil.parser.parse(post.get('issue_date'))
            request.env['oeh.medical.patient.medical.cert'].sudo().browse(int(cert_id)).write(post)
        # return request.redirect('/patient/portal/%s' % int(patient_id))
        return request.redirect('/patient/portal/%s' % patient.patient_token)

    @http.route('/patient/portal/<int:patient_id>/medical-certificate/<int:cert_id>/remove', type='http', auth="user",
                website=True)
    def delete_patient_certi(self, patient_id=False, cert_id=False, **post):
        if cert_id:
            request.env['oeh.medical.patient.medical.cert'].sudo().browse(int(cert_id)).sudo().unlink()
            patient = request.env['oeh.medical.patient'].sudo().browse(int(patient_id))
        # return request.redirect('/patient/portal/%s' % int(patient_id))
        return request.redirect('/patient/portal/%s' % patient.patient_token)

    @http.route('/opinion/<request_name>', type='http', auth="public", website=True)
    def view_opinion_request(self, request_name='', **post):
        values = {}
        if request_name and request_name != '':
            opinion = request.env['oeh.medical.doctor.opinion'].sudo().search([('name', '=', request_name)], limit=1)
            if opinion:
                values['opinion'] = opinion
                opinion.sudo().write({'state': 'seen'})
                return request.render("oehealth_patient_portal.view_opinion_request", values)
        return request.redirect('/')

    @http.route('/opinion/<int:opinion_id>/send', type='http', auth="public",
                website=True)
    def save_opinion_request(self, opinion_id=False, **post):
        values = {}
        if opinion_id:
            values['advice'] = post.get('advice')
            values['state'] = 'answered'
            request.env['oeh.medical.doctor.opinion'].sudo().browse(int(opinion_id)).write(values)
        return request.render("oehealth_patient_portal.opinion_thankyou", values)
