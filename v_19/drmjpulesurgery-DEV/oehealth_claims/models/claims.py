from odoo import models, fields,_
from odoo.exceptions import UserError


class HealthClaim(models.Model):
    _name = "health.claim"
    _description = "Health Claim"
    _rec_name = "patient_id"
    _inherit = "mail.thread", "mail.activity.mixin"

    patient_id = fields.Many2one("oeh.medical.patient", string="Patient",required=True)
    doctor_id = fields.Many2one("oeh.medical.physician", string="Doctor")
    referring_doctor_id = fields.Many2one("oeh.medical.physician", string="Referring Doctor")
    claim_date = fields.Date(string="Visit Date", default=fields.Date.today)
    claim_count = fields.Integer(compute='_claim_count', string="Appointments")


    icd10_type = fields.Selection([
        ('full', 'Full List'),
        ('common', 'Common List'),
    ], string="Type", default='full')

    qty = fields.Integer(string="Quantity", default=1)
    icd10_id = fields.Integer(string="ICD10")
    code = fields.Char(string="Code")
    tariff = fields.Float(string="Tariff", default=0.0)
    charged = fields.Float(string="Charged", default=0.0)
    notes = fields.Text(string="Notes")
    id_number=fields.Integer(string="ID Number")
    medical_aid_option=fields.Integer(string="Medical AID Option")
    medical_aid_number=fields.Integer(string="Medical AID Number")
    dob=fields.Date(string="Date of Birth")
    visit_line_ids = fields.One2many(
        "health.claim.visit",
        "claim_id",
        string="Visit Information"
    )
    gender=fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string="Gender")
    medical_aid = fields.Selection([
        ('private', 'Private'),
        ('government', 'Government'),
    ], string="medical_aid")

    # For totals
    total_claim_amount = fields.Float(
        string="Total Claim Amount",
        compute="_compute_total",
        store=True
    )
    def _claim_count(self):
        for pa in self:
            pa.claim_count = self.env['account.move'].search_count([('partner_id', '=', pa.patient_id.commercial_partner_id.id)])

    def action_create_claim_invoice(self):
        """Create customer invoice from claim"""
        self.ensure_one()
        if not self.patient_id:
            raise UserError(_("Please set a patient before creating invoice."))
        # if self.claim_count == 1:
        #     raise UserError(_("Invoice is already created for this claim."))

        # create invoice
        invoice = self.env["account.move"].sudo().create({
            "move_type": "out_invoice",
            "partner_id": self.patient_id.commercial_partner_id.id,
            "ref": f"Claim/{self.medical_aid_number or ''}",
            "invoice_payment_term_id": self.env.ref("account.account_payment_term_immediate").id,

            # "invoice_origin": self.name,
            "invoice_line_ids": [
                (0, 0, {
                    "name": "Medical Service",
                    "quantity": line.qty,
                    "price_unit": line.charged or 0.0,
                }) for line in self.visit_line_ids
            ],
        })

        # return action to open invoice
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": invoice.id,
        }

    def action_claim_invoice(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Invoices",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.patient_id.commercial_partner_id.id)],
            # "context": {"default_partner_id": self.patient_id.id},
        }



    def _compute_total(self):
        for rec in self:
            rec.total_claim_amount = rec.charged or 0.0

    # claim_date = fields.Date(string="Claim Date")
    # patient_name = fields.Many2one('oeh.medical.patient',string="Patient Name",required=True)
    # id_number = fields.Char(string="ID Number")
    # insurer = fields.Many2one('hr.employee',string="Insurer")
    # medical_aid = fields.Char(string="Medical Aid #")
    # account_no = fields.Char(string="Account No")
    # charge_amount = fields.Float(string="MA. Charge")

    def action_claim_sketchpad(self):
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

    def action_edit_claim(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Claim',
            'res_model': 'health.claim',
            'view_mode': 'form,list',
            'target': 'current',
            'res_id': self.id,
        }
    def action_new_claim(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Claim',
            'res_model': 'health.claim',
            'view_mode': 'form,list',
            'target': 'current',
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

    def action_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'res_model': 'account.payment',
            'view_mode': 'form,list',
            'target': 'current',
            'context': {'default_partner_id': self.patient_id.commercial_partner_id.id},

        }

    class HealthClaimVisit(models.Model):
        _name = "health.claim.visit"
        _description = "Health Claim Visit Line"

        claim_id = fields.Many2one("health.claim", string="Claim", ondelete="cascade")
        visit_date = fields.Date(string="Visit Date", default=fields.Date.today)

        type = fields.Selection([
            ('full', 'Full List'),
            ('common', 'Common List'),
        ], string="Type", default="full")

        qty = fields.Integer(string="Quantity", default=1)
        icd10_id = fields.Integer(string="ICD10")
        code = fields.Char(string="Code")
        tariff = fields.Float(string="Tariff", default=0.0)
        charged = fields.Float(string="Charged", default=0.0)
        notes = fields.Text(string="Notes")

    # def record_audio_action(self):
    #     # This can trigger JS via `widget` or just return True
    #     return True
