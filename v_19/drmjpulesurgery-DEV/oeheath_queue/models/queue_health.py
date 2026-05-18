from odoo import fields, models


class QueueHealth(models.Model):
    """Queue Health"""
    _name = "queue.health"
    _description = "Queue Health"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # chatter
    _order = 'appointment_date'
    _rec_name = 'appointment_id'

    appointment_id = fields.Many2one(
        'oeh.medical.appointment',
        string="Appointment",
        tracking=True,readonly=False)
    patient_id = fields.Many2one("oeh.medical.patient", string="Patient",readonly=False,related="appointment_id.patient")
    clinical_notes = fields.Text(string="Clinical Notes",related= "patient_id.clinical_notes")
    clinical_sketchpad = fields.Html(string="Clinical SketchPad",related= "patient_id.clinical_sketchpad")
    doctor_id = fields.Many2one("oeh.medical.physician", string="Doctor",readonly=False)
    appointment_date = fields.Datetime(string='Appointment Date', required=True)

    state = fields.Selection([
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='waiting', tracking=True)
    next = fields.Boolean(string="Next In the queue")
    active = fields.Boolean(default=True)

    def action_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'res_model': 'account.payment',
            'view_mode': 'form,list',
            'target': 'current',
            'context': {'default_partner_id': self.patient_id.commercial_partner_id.id},

        }

    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'
            queue = self.env['queue.health'].search([('state', '=', 'waiting')], limit=1)
            queue.next = True

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.next = False
            rec.action_archive()

    def action_sketchpad(self):
        print(self.patient_id.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sketch Notes',
            'res_model': 'patient.sketch.note',
            'view_mode': 'list,form',
            'target': 'current',
                'domain': [('patient_sketch_note_id', '=', self.patient_id.id)],
            'context': {'default_patient_sketch_note_id': self.patient_id.id},
        }

    def action_notepad(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Clinical Notes',
            'res_model': 'clinical.notes',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {'default_patient_id': self.patient_id.id},
        }

    def action_patient(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient',
            'res_model': 'oeh.medical.patient',
            'res_id': self.patient_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }

