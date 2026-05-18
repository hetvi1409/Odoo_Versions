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
    'name': 'oeHealth - Hospital Management System',
    'version': '19.0.1.0.0',
    'author': "Braincrew Apps",
    'category': 'Generic Modules/Medical',
    'summary': 'Odoo EMR & HIS based Medical, Health and Hospital Management Solutions',
    'depends': ['web', 'base', 'account', 'product', 'uom', 'hr', 'stock', 'account_edi'],
    'price': 300.00,
    'currency': 'EUR',
    'description': """
        Odoo Hospital Management System
        Hospital Management System
        Hospital Management
        Patient Management
        Patient Information Management
        Electronic Medical Records
        Electronic Health Records
        Medical Staff Management
        Doctors Management
        Therapists Management
        Nurses Management
        Appointment Scheduling
        Schedule Appointments
        Prescriptions Management
        E-prescription
        Generate Prescription
        Inpatient Admission
        Inpatient Management
        Inpatient Hospitalization
        Medical Billing
        Medical Invoicing
        EMR 
        EHR 
        Telemedicine 
        Skype
        Zoom
        Jitsi
        """,
    "website": "https://www.oehealth.in",
    "data": [

        # 'views/oehealth.xml',
        'security/oeh_security.xml',


        # 'oeh_settings/oeh_settings_view.xml',

        'oeh_navigation.xml',

        'oeh_medical/views/res_partner_view.xml',
        'oeh_medical/views/product_product_view.xml',
        'oeh_medical/views/oeh_medical_medicaments_view.xml',
        'oeh_medical/views/oeh_medical_pharmacy_view.xml',
        'oeh_medical/views/oeh_medical_healthcenters_view.xml',
        'oeh_medical/views/oeh_medical_pathology_view.xml',
        'oeh_medical/views/oeh_medical_inpatient_view.xml',
        'oeh_medical/views/oeh_medical_view.xml',
        'oeh_medical/views/account_invoice_view.xml',
        'oeh_medical/views/oeh_medical_insurance_view.xml',
        'oeh_medical/views/oeh_medical_ethnic_groups_view.xml',
        'oeh_medical/views/oeh_medical_genetics_view.xml',
        'oeh_medical/reports/report_patient_label.xml',
        'oeh_medical/reports/report_medical_staff_badge.xml',
        'oeh_medical/reports/report_patient_medicines.xml',
        'oeh_medical/reports/report_appointment_receipt.xml',
        'oeh_medical/reports/report_patient_prescriptions.xml',
        'oeh_medical/reports/report_patient_sick_note.xml',
        'oeh_medical/views/oeh_medical_report.xml',
        'oeh_medical/wizard/oeh_medical_inpatient_wizard_view.xml',
        'oeh_medical/wizard/oeh_medical_appointment_wizard_view.xml',
        'oeh_medical/wizard/oeh_telmedicine_source_wizard_view.xml',

        'oeh_evaluation/views/oeh_medical_evaluation_view.xml',

        'oeh_socioeconomics/views/oeh_medical_socioeconomics_view.xml',

        'oeh_gyneco/views/oeh_medical_gyneco_view.xml',

        'oeh_lifestyle/views/oeh_medical_lifestyle_view.xml',

        'oeh_telemedicine_sources/views/oeh_telemedicine_source_views.xml',

        'oeh_patient_examination/views/oeh_medical_injury_examination.xml',

        'oeh_patient_examination/wizard/oeh_medical_injury_wiz.xml',

        'oeh_patient_examination/reports/oeh_medical_report.xml',
        'oeh_patient_examination/reports/report_injury_examination.xml',

        'oeh_followup/views/oeh_followup_view.xml',
        'oeh_followup/wizard/oeh_followup_wizard_view.xml',

        'oeh_icd10pcs/views/oeh_icd10pcs_view.xml',
        'oeh_patient_medical_history/views/oeh_medical_patient_view.xml',

        'oeh_medical_certificate/views/oeh_medical_certificate_view.xml',
        'oeh_medical_certificate/views/oeh_medical_report.xml',
        'oeh_medical_certificate/views/report_medical_certificate.xml',



        #
        # # REST API
        # 'oeh_rest_api/data/api_token_data.xml',
        # 'oeh_rest_api/data/ir_cron_data.xml',
        # 'oeh_rest_api/views/api_view.xml',
        #
        # SECURITY FILES
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'sequence/oeh_sequence.xml',
        # 'security/oeh_menu_rights.xml',
        #
        # DATA FILES
        'oeh_medical/data/oeh_physician_specialities.xml',
        'oeh_medical/data/oeh_physician_degrees.xml',
        'oeh_medical/data/oeh_insurance_types.xml',
        'oeh_medical/data/oeh_ethnic_groups.xml',
        # 'oeh_medical/data/oeh_who_medicaments.xml',
        'oeh_medical/data/oeh_dose_units.xml',
        'oeh_medical/data/oeh_drug_administration_routes.xml',
        'oeh_medical/data/oeh_drug_form.xml',
        'oeh_medical/data/oeh_dose_frequencies.xml',
        'oeh_medical/data/oeh_genetic_risks.xml',
        # 'oeh_medical/data/oeh_prescription_email_template.xml',
        'oeh_socioeconomics/data/oeh_occupations.xml',
        'oeh_lifestyle/data/oeh_recreational_drugs.xml',
        'oeh_medical/data/oeh_disease_categories.xml',
        'oeh_medical/data/oeh_diseases.xml',
        'oeh_medical/data/oeh_meeting_email_template.xml',
        'oeh_icd10pcs/data/oeh_icd_10_pcs_2009_part1.xml',
        'oeh_icd10pcs/data/oeh_icd_10_pcs_2009_part2.xml',
        'oeh_icd10pcs/data/oeh_icd_10_pcs_2009_part3.xml',

    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'oehealth/static/src/css/oehealth.css',
    #         'oehealth/static/src/js/webcam.js',
    #         'oehealth/static/src/js/oehealth_webcam.js',
    #         'oehealth/static/src/xml/webcam.xml',
    #     ],
    #     # 'web.assets_qweb': [
    #     #     'oehealth/static/src/xml/webcam.xml',
    #     # ],
    # },
    'assets': {
        'web.assets_backend': [
            'oehealth/static/src/css/oehealth.css',
            # 'oehealth/static/src/**/**.scss',
            'oehealth/static/src/fields/image_field.css',
            'oehealth/static/src/fields/image_field.js',
            'oehealth/static/src/fields/image_field.xml',
        ],
    },
    "images": ['images/main_screenshot.png'],
    # 'qweb': [
    #     "static/src/xml/webcam.xml",
    # ],
    "active": False,
    'license': 'OEEL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
