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
    'name': 'Nated System  - Pediatric Management',
    'version': '19.0.1.0.0',
    'category': 'Generic Modules/Medical',
    'author': 'Braincrew Apps',
    'website': 'https://www.oehealth.in',
    'depends': ['oehealth'],
    'description': """
        Pediatrics Management
        Pediatrics EMR
        Pediatrics EHR
        Children Hospital Software
        Newborns, Pediatric
        Pediatric Symptoms Checklist
        Pediatrics Growth Charts
        Manage childrens
        Manage pediatrics
        Manage newborns
        """,
    'summary': 'Hospital suite for Pediatrics, newborns, infants & childcare',
    'price': 30.00,
    'currency': 'EUR',
    'data': [
        'views/res_partner_view.xml',
        'views/oeh_medical_pediatrics_newborn_view.xml',
        'views/oeh_medical_pediatrics_pcs_view.xml',
        'views/oeh_medical_pediatrics_growth_chart_view.xml',
        'data/oeh_medical_wfa_boys_p.xml',
        'data/oeh_medical_wfa_boys_z.xml',
        'data/oeh_medical_wfa_girls_p.xml',
        'data/oeh_medical_wfa_girls_z.xml',
        'data/oeh_medical_lhfa_boys_p.xml',
        'data/oeh_medical_lhfa_boys_z.xml',
        'data/oeh_medical_lhfa_girls_p.xml',
        'data/oeh_medical_lhfa_girls_z.xml',
        'data/oeh_medical_bmi_boys_p.xml',
        'data/oeh_medical_bmi_boys_z.xml',
        'data/oeh_medical_bmi_girls_p.xml',
        'data/oeh_medical_bmi_girls_z.xml',
        'data/oeh_pediatrics_sequence.xml',
        'security/ir.rule.xml',
        'security/ir.model.access.csv'
    ],
    "images": ['images/main_screenshot.png'],
    'auto_install': False,
}
