# -*- coding: utf-8 -*-
##############################################################################
#    Copyright (C) 2015 - Present, oeHealth (<https://www.oehealth.in>). All Rights Reserved
#    oeHealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, oeHealth.in, braincrewapps.com, or if you have received a written
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


from odoo import fields, models, api, _
from werkzeug.urls import url_encode
import random, string


class OeHealthMedicalPatient(models.Model):
    _inherit = 'oeh.medical.patient'

    patient_token = fields.Char(string="Patient Token")
    patient_url = fields.Char(string="Patient URL", compute="_get_patient_url")
    is_portal_access = fields.Boolean(string='Is having Portal Access?', default=False)
    base_url = fields.Char(string='Base URL')

    @api.model
    def create(self, vals):
        if isinstance(vals, dict):
            vals['patient_token'] = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return super(OeHealthMedicalPatient, self).create(vals)

    def change_grant_access(self):
        print('\n\n change_grant_access---->',self)
        for patient in self:
            if patient.is_portal_access:
                patient.is_portal_access = False
            else:
                patient.is_portal_access = True
            print('\n\n PATIENT_PORTAL_ACCESS---->', patient.is_portal_access)

    def _get_patient_url(self):
        for patient in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            patient.patient_url = base_url + '/patient/portal/%s' % patient.patient_token

    def send_patient_portal(self):
        print("\n\n\n send_patient_portal---->",self)
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('oehealth_patient_portal.oeh_email_template_patient_portal',
                                                                raise_if_not_found=False)
        ctx = {
            'default_model': 'oeh.medical.patient',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            # 'custom_layout': "mail.mail_notification_paynow",
            'proforma': True,
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


    # def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
    #     """
    #         Get a portal url for this model, including access_token.
    #         The associated route must handle the flags for them to have any effect.
    #         - suffix: string to append to the url, before the query string
    #         - report_type: report_type query string, often one of: html, pdf, text
    #         - download: set the download query string to true
    #         - query_string: additional query string
    #         - anchor: string to append after the anchor #
    #     """
    #     self.ensure_one()
    #
    #     url = '/patient/portal/s9KLQzCgtK18qv53' + '%s?access_token=%s%s%s%s%s' % (
    #         suffix if suffix else '',
    #         self._portal_ensure_token(),
    #         '&report_type=%s' % report_type if report_type else '',
    #         '&download=true' if download else '',
    #         query_string if query_string else '',
    #         '#%s' % anchor if anchor else ''
    #     )
    #     return url

    # def preview_invoice(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'target': 'self',
    #         'url': self.get_portal_url(),
    #     }

    # def _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=False):
    #     self.ensure_one()
    #     auth_param = url_encode(self.partner_id.signup_get_auth_param()[self.partner_id.id])
    #     return self.get_portal_url(query_string='&%s' % auth_param)
