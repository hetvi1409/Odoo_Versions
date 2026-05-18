from numpy.f2py.crackfortran import requiredpattern

from odoo import models, fields, api

class ClinicalNotes(models.Model):
    _name = "clinical.notes"
    _description = "Clinical Notes"

    patient_id = fields.Many2one(
        "oeh.medical.patient",string="Patient",required=True)
    note_date = fields.Date(string="Date",required=True, default=lambda self: fields.Date.today())
    notes = fields.Html(string="Notes")