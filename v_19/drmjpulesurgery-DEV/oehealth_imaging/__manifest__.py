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
    'name': 'Nated System - Imaging Management',
    'version': '19.0.1.0.0',
    'category': 'Generic Modules/Medical',
    'author': 'Braincrew Apps',
    'website': 'https://www.oehealth.in',
    'depends': ['oehealth'],
    'price': 30.00,
    'currency': 'EUR',
    'summary': 'Carry out all the necessary Imaging tests that are need of the hour for patients.',
    'description': """
        Radiology
        Imaging
        Imaging tests
        Imaging Management System
        X-ray
        CT Scan
        MRI
        PET Scan
        Perform Imaging Test
        Imaging test reports
        Imaging test system
        """,
    'data': [
        'views/oeh_medical_imaging_report.xml',
        'views/oeh_medical_imaging_view.xml',
        'views/report_patient_imaging.xml',
        'data/oeh_imaging_test_types.xml',
        'data/oeh_imaging_sequence.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
    ],
    "images": ['images/main_screenshot.png'],
    'auto_install': False,
}
