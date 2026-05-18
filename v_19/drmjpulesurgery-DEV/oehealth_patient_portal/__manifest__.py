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


{
    'name': 'Nated System - Patient Portal Management',
    'version': '19.0.1.0.0',
    'category': 'Generic Modules/Medical',
    'summary': 'Give secure access to your patients to view their details and download their medical information',
    'description': """
        Customer Portal Management
        Portal
        Patient Portal
        Patient details
        Patient Records Management
        Patient Record management
        HMS Portal Management
        HMS Patient Portal

    """,
    'author': 'Braincrew Apps',
    'price': 99.00,
    'currency': 'EUR',
    "website": "https://www.oehealth.in",
    'depends': [
        'oehealth',
        'portal',
        'website',
    ],
    'data': [
        'views/oeh_patient_portal.xml',
        'views/oeh_patient_details_template.xml',
        'views/oeh_patient_profile_form.xml',
        'views/oeh_registration_templates.xml',
        'data/oeh_patient_portal_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'oehealth_patient_portal/static/src/js/add_detail.js',
            'oehealth_patient_portal/static/src/scss/style.scss'
        ],
    },
    "images": ['images/main_screenshot.png'],
    'auto_install': False,
}
