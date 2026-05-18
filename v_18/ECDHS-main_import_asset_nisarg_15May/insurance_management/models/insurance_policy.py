# models/insurance_policy.py
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

INSURANCE_TYPES = [
    ('property', 'Property'),
    ('asset', 'Asset'),
    ('vehicle', 'Vehicle'),
    ('tenant', 'Tenant'),
    ('liability', 'Liability'),
    ('public_liability', 'Public Liability'),
]

POLICY_STATUS = [
    ('active', 'Active'),
    ('expired', 'Expired'),
    ('cancelled', 'Cancelled'),
    ('suspended', 'Suspended'),
]

CLAIM_STATUS = [
    ('open', 'Open'),
    ('in_review', 'In Review'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('paid', 'Paid'),
]

RISK_RATING = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]


class InsurancePolicy(models.Model):
    _name = "insurance.policy"
    _description = "Insurance Policy"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Policy Number", index=True, copy=False)
    insurance_type = fields.Selection(INSURANCE_TYPES, string="Insurance Type", required=True, default='property')
    insurer_id = fields.Many2one("res.partner", string="Insurer (Provider)", domain="[('is_company','=',True)]")
    broker_id = fields.Many2one("res.partner", string="Broker")
    policy_start_date = fields.Date(string="Start Date")
    policy_end_date = fields.Date(string="Expiry Date")
    status = fields.Selection(POLICY_STATUS, string="Policy Status", default='active', track_visibility='onchange')
    sum_insured = fields.Monetary(string="Sum Insured")
    premium_amount = fields.Monetary(string="Premium Amount")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    payment_frequency = fields.Selection([('monthly','Monthly'),('quarterly','Quarterly'),('annual','Annual')],
                                         string="Payment Frequency")
    payment_method = fields.Selection([('eft','EFT'),('debit','Debit Order'),('cash','Cash')], string="Payment Method")
    excess_amount = fields.Monetary(string="Excess / Deductible")

    # Document / attachments: we'll reference ir.attachment via domain
    # Not stored: compute counts for smart button
    attachment_count = fields.Integer(string="Documents", compute='_compute_counts')
    payment_count = fields.Integer(string="Payments", compute='_compute_counts')
    claim_count = fields.Integer(string="Claims", compute='_compute_counts')
    linked_count = fields.Integer(string="Linked Items", compute='_compute_counts')

    # Notes / doc binary
    policy_document = fields.Binary(string="Policy Document")
    policy_document_name = fields.Char(string="Policy Document Filename")

    notes = fields.Text(string="Notes")

    # --- Property section
    property_id = fields.Many2one('building', string="Property (Register)", help="If you store properties in partners")
    property_ref = fields.Char(string="Property Code / Ref")
    property_address = fields.Text(string="Physical Address")
    property_type = fields.Selection([('commercial','Commercial'),('retail','Retail'),
                                      ('residential','Residential'),('industrial','Industrial')], string="Property Type")
    building_size = fields.Float(string="Building Size (m²)")
    construction_type = fields.Selection([('brick','Brick'),('timber','Timber'),('mixed','Mixed')], string="Construction Type")
    replacement_value = fields.Monetary(string="Replacement Value")

    # --- Asset section (simple link)
    asset_ref = fields.Many2one('account.asset', string="Asset Reference / Tag")
    asset_category_id = fields.Many2one('asset.category', string="Asset Category")
    asset_serial = fields.Char(string="Asset Serial Number")
    asset_value = fields.Monetary(string="Asset Value")
    asset_location = fields.Many2one('res.partner', string="Asset Location")
    asset_condition = fields.Selection([('new','New'),('good','Good'),('fair','Fair'),('poor','Poor')],
                                       string="Asset Condition")

    # --- Vehicle section
    vehicle_registration = fields.Char(string="Vehicle Registration")
    vehicle_make_model = fields.Char(string="Make & Model")
    vin_number = fields.Char(string="VIN Number")
    engine_number = fields.Char(string="Engine Number")
    vehicle_year = fields.Integer(string="Year")
    driver_id = fields.Many2one('hr.employee', string="Assigned Driver")

    # --- Tenant section
    tenant_id = fields.Many2one('res.partner', string="Tenant")
    lease_ref = fields.Many2one('account.move', string="Lease Reference")  # example
    tenant_cover_type = fields.Selection([('contents','Contents'),('liability','Liability'),
                                          ('business','Business Interruption')], string="Type of Cover")
    required_by_landlord = fields.Boolean(string="Required by Landlord")

    # Coverage & Risk
    risks_covered = fields.Many2many('res.partner.category', string="Risks Covered",
                                     help="Use categories to store risk types OR replace with a selection/m2m model.")
    exclusions = fields.Text(string="Exclusions Summary")
    geographical_coverage = fields.Char(string="Geographical Coverage")
    special_conditions = fields.Text(string="Special Conditions")
    reinstatement_clause = fields.Boolean(string="Reinstatement Value Clause")

    # Claims information - key fields, details in insurance.claim
    claims_contact_person = fields.Char(string="Claims Contact Person")
    claims_contact_number = fields.Char(string="Claims Contact Number")
    claims_contact_email = fields.Char(string="Claims Contact Email")

    # Compliance & Monitoring
    pfma_compliant = fields.Boolean(string="PFMA / GIAMA Compliant")
    insurance_verified = fields.Boolean(string="Insurance Verified")
    verified_by = fields.Many2one('res.users', string="Verified By")
    verification_date = fields.Date(string="Verification Date")
    renewal_reminder_enabled = fields.Boolean(string="Renewal Reminder Enabled")
    days_before_expiry_reminder = fields.Integer(string="Days Before Expiry Reminder")
    risk_rating = fields.Selection(RISK_RATING, string="Risk Rating")
    audit_comments = fields.Text(string="Audit Comments")

    # Automation / system
    auto_renewal = fields.Boolean(string="Auto Renewal")
    renewal_in_progress = fields.Boolean(string="Renewal In Progress")
    last_renewal_date = fields.Date(string="Last Renewal Date")
    next_review_date = fields.Date(string="Next Review Date")
    responsible_officer = fields.Many2one('hr.employee', string="Responsible Officer")
    department_id = fields.Many2one('hr.department', string="Department")
    linked_vendor = fields.Many2one('res.partner', string="Linked Vendor")

    # relations
    claim_ids = fields.One2many('insurance.claim', 'policy_id', string="Claims")

    # audit system columns are available from mail.thread
    # ----
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            print("\n\n===vals_list===",vals_list,vals)
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('insurance.policy') or 'New'
        return super(InsurancePolicy, self).create(vals_list)

    @api.depends('insurer_id')
    def _compute_counts(self):
        for rec in self:
            # Documents: attachments linked by res_model/res_id
            rec.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'insurance.policy'),
                ('res_id', '=', rec.id),
            ])
            # Payments: account.move with partner = insurer
            rec.payment_count = self.env['account.move'].search_count([
                ('partner_id', '=', rec.insurer_id.id)
            ]) if rec.insurer_id else 0
            rec.claim_count = len(rec.claim_ids)
            # linked items heuristic: property/asset/vehicle/tenant set
            linked = 0
            rec.linked_count = self.env['building'].search_count([('id', '=', rec.property_id.id)]) if rec.property_id else 0

            if rec.asset_ref: linked += 1
            if rec.vehicle_registration: linked += 1
            if rec.tenant_id: linked += 1

    # ----- Smart-button actions -----
    def action_open_attachments(self):
        self.ensure_one()
        return {
            'name': _('Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'views': [(self.env.ref('base.view_attachment_tree').id, 'list'), (self.env.ref('base.view_attachment_form').id, 'form')],
            'domain': [('res_model', '=', 'insurance.policy'), ('res_id', '=', self.id)],
            'target': 'current',
        }

    def action_open_payments(self):
        self.ensure_one()
        return {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'views': [(self.env.ref('account.view_move_tree').id, 'list'), (self.env.ref('account.view_move_form').id, 'form')],
            'domain': [('partner_id', '=', self.insurer_id.id)],
            'target': 'current',
        }

    def action_open_claims(self):
        self.ensure_one()
        return {
            'name': _('Claims'),
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.claim',
            'views': [(self.env.ref('insurance_management.view_insurance_claim_list').id, 'list'),
                      (self.env.ref('insurance_management.view_insurance_claim_form').id, 'form')],
            'domain': [('policy_id', '=', self.id)],
            'target': 'current',
        }

    def action_open_linked(self):
        self.ensure_one()
        # simple action: open properties (if property chosen) or show form of this policy
        if self.property_id:
            return {
                'name': _('Linked Property'),
                'type': 'ir.actions.act_window',
                'res_model': 'building',
                'views': [(self.env.ref('itsys_real_estate.building_list').id, 'list'), (self.env.ref('itsys_real_estate.building_form').id, 'form')],
                'domain': [('id', '=', self.property_id.id)],
            }
        return {'type': 'ir.actions.act_window', 'res_model': 'insurance.policy', 'view_mode': 'form', 'res_id': self.id}

    @api.constrains('policy_end_date', 'policy_start_date')
    def _check_dates(self):
        for rec in self:
            if rec.policy_start_date and rec.policy_end_date and rec.policy_end_date < rec.policy_start_date:
                raise ValidationError(_('Expiry date must be after start date.'))
