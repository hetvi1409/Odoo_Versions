from odoo import models, fields, api

class ClinicalNotes(models.Model):
    _name = "patient.sketch.note"
    _description = "Clinical sketch Notes"

    patient_sketch_note_id = fields.Many2one(
        "oeh.medical.patient",string="Patient",required=True)
    sketch_note_date = fields.Date(string="Date",required=True, default=lambda self: fields.Date.today())
    sketch_notes = fields.Html(string="Notes")