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
    'name': 'Nated System : Laboratory Information System',
    'version': '19.0.1.0.0',
    'category': 'Generic Modules/Medical',
    'summary': 'Your assistant for performing hassle free pathology laboratory related activities',
    'author': 'Braincrew Apps',
    'website': "https://www.oehealth.in",
    'depends': [
        'oehealth',
        'oehealth_patient_portal'
    ],
    'price': 50.00,
    'currency': 'EUR',
    'description': """
        lab management
        laboratory management
        lab tests
        lab tests management
        lab test management
        pathology lab
        Lab Information Management
        Pathology lab management
        Laboratory Information Management
        Pathology Laboratory Management
        Laboratory Information System
        Lab Information System
        """,
    'data': [
        'views/oeh_medical_lab_view.xml',
        'security/lab_menu_right.xml',
        'security/ir.rule.xml',
        'data/oeh_lab_test_units.xml',
        'data/oeh_lab_test_types.xml',
        'data/oeh_lab_sequence.xml',
        'data/oeh_sample_types.xml',
        'views/oeh_medical_lab_report.xml',
        'views/report_patient_labtest.xml',
        'views/oeh_medical_master_sample.xml',
        'views/oeh_medical_sample_view.xml',
        'views/oeh_medical_patient_portal.xml',
        'wizard/oeh_medical_add_sample.xml',
        'security/ir.model.access.csv',

    ],
    'assets': {
        'web.assets_frontend': [
            'oehealth_lab/static/src/js/lab_req.js'
        ],
    },
    "images": ['images/main_screenshot.png'],
    'auto_install': False,
}
