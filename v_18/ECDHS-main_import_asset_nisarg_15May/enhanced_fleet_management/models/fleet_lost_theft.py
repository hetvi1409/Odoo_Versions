# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class FleetLostTheft(models.Model):
    _name = 'fleet.lost.theft'
    _description = 'Fleet Lost and Theft Checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'incident_date desc, id desc'
    _rec_name = 'reference'

    # Basic Information
    reference = fields.Char(
        string='Case Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('reported', 'Reported'),
        ('under_investigation', 'Under Investigation'),
        ('police_reported', 'Reported to Police'),
        ('insurance_claimed', 'Insurance Claimed'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    incident_type = fields.Selection([
        ('theft', 'Theft'),
        ('lost', 'Lost/Missing'),
        ('hijacking', 'Hijacking'),
        ('burglary', 'Burglary from Vehicle'),
        ('vandalism', 'Vandalism'),
        ('other', 'Other'),
    ], string='Incident Type', required=True, tracking=True)

    # Vehicle Information
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        required=True,
        tracking=True
    )
    license_plate = fields.Char(
        string='License Plate',
        related='vehicle_id.license_plate',
        store=True
    )
    vehicle_model = fields.Char(
        string='Vehicle Model',
        related='vehicle_id.model_id.name',
        store=True
    )
    vehicle_vin = fields.Char(
        string='VIN Number',
        related='vehicle_id.vin_sn',
        store=True,
        help='Pulled from fleet.vehicle.vin_sn (VIN); avoids missing field errors on installs.'
    )
    engine_number = fields.Char(
        string='Engine Number',
        related='vehicle_id.engine_number'
    )

    # Incident Details
    incident_date = fields.Datetime(
        string='Date & Time of Incident',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    discovered_date = fields.Datetime(
        string='Date & Time Discovered',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    incident_location = fields.Char(
        string='Location of Incident',
        required=True,
        tracking=True
    )
    incident_address = fields.Text(
        string='Detailed Address',
        help='Full address where incident occurred'
    )
    incident_coordinates = fields.Char(
        string='GPS Coordinates',
        help='Latitude and Longitude if available'
    )

    # Person Reporting
    reported_by_id = fields.Many2one(
        'res.users',
        string='Reported By',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    reporter_employee_id = fields.Many2one(
        'hr.employee',
        string='Reporter Employee',
        related='reported_by_id.employee_id',
        store=True
    )
    reporter_phone = fields.Char(
        string='Reporter Phone',
        required=True
    )
    reporter_email = fields.Char(
        string='Reporter Email'
    )

    # Driver Information (at time of incident)
    driver_id = fields.Many2one(
        'res.partner',
        string='Driver',
        tracking=True,
        domain=[('is_fleet_driver', '=', True)]
    )
    driver_name = fields.Char(
        string='Driver Name',
        help='Driver name if not in system'
    )
    driver_contact = fields.Char(
        string='Driver Contact Number'
    )
    driver_license_number = fields.Char(
        string='Driver License Number'
    )
    was_driver_present = fields.Boolean(
        string='Was Driver Present?',
        default=True
    )

    # Trip Information
    trip_authority_id = fields.Many2one(
        'fleet.trip.authority',
        string='Related Trip Authority',
        tracking=True
    )
    was_vehicle_in_use = fields.Boolean(
        string='Was Vehicle In Use?',
        default=False
    )
    trip_purpose = fields.Text(
        string='Trip Purpose',
        help='Purpose if vehicle was in use'
    )
    last_known_location = fields.Char(
        string='Last Known Location'
    )

    # Incident Description
    incident_description = fields.Text(
        string='Detailed Description of Incident',
        required=True,
        help='Provide a comprehensive description of what happened'
    )
    circumstances = fields.Text(
        string='Circumstances',
        help='What were the circumstances leading to the incident?'
    )
    witness_present = fields.Boolean(
        string='Were There Witnesses?',
        default=False
    )
    witness_details = fields.Text(
        string='Witness Details',
        help='Names and contact details of witnesses'
    )

    # Items Lost/Stolen
    vehicle_stolen = fields.Boolean(
        string='Vehicle Stolen',
        default=False
    )
    items_stolen = fields.Boolean(
        string='Items Stolen from Vehicle',
        default=False
    )
    items_description = fields.Text(
        string='Description of Stolen/Lost Items',
        help='List all items stolen or lost'
    )
    estimated_value = fields.Float(
        string='Estimated Value of Loss',
        help='Total estimated value in currency'
    )

    # Vehicle Condition Before Incident
    odometer_reading = fields.Float(
        string='Odometer Reading',
        help='Last known odometer reading'
    )
    fuel_level = fields.Selection([
        ('0', 'Empty'),
        ('25', '1/4 Tank'),
        ('50', '1/2 Tank'),
        ('75', '3/4 Tank'),
        ('100', 'Full Tank'),
    ], string='Fuel Level')
    vehicle_keys_status = fields.Selection([
        ('with_driver', 'With Driver'),
        ('in_vehicle', 'Left in Vehicle'),
        ('secured', 'Secured Separately'),
        ('lost', 'Lost/Stolen'),
    ], string='Vehicle Keys Status')
    vehicle_documents_status = fields.Selection([
        ('with_driver', 'With Driver'),
        ('in_vehicle', 'Left in Vehicle'),
        ('secured', 'Secured at Office'),
        ('lost', 'Lost/Stolen'),
    ], string='Vehicle Documents Status')

    # Security Measures
    was_vehicle_locked = fields.Boolean(
        string='Was Vehicle Locked?',
        default=True
    )
    alarm_fitted = fields.Boolean(
        string='Alarm System Fitted?',
        related='vehicle_id.alarm_fitted'
    )
    was_alarm_active = fields.Boolean(
        string='Was Alarm Active?'
    )
    tracking_device_fitted = fields.Boolean(
        string='Tracking Device Fitted?',
        related='vehicle_id.tracking_device_fitted'
    )
    tracking_company = fields.Char(
        string='Tracking Company Name'
    )
    tracking_reference = fields.Char(
        string='Tracking Reference Number'
    )

    # Police Report
    police_reported = fields.Boolean(
        string='Reported to Police?',
        default=False,
        tracking=True
    )
    police_station = fields.Char(
        string='Police Station'
    )
    police_case_number = fields.Char(
        string='Police Case/Docket Number',
        tracking=True
    )
    police_officer_name = fields.Char(
        string='Investigating Officer Name'
    )
    police_officer_contact = fields.Char(
        string='Officer Contact Number'
    )
    police_report_date = fields.Date(
        string='Date Reported to Police',
        tracking=True
    )
    police_report_attachment = fields.Binary(
        string='Police Report Copy',
        attachment=True
    )
    items_are_state_property = fields.Boolean(
        string='Are Stolen Items State Property?',
        default=False
    )
    entrance_of_building = fields.Boolean(
        string='Was the Building Entrance Secured?',
        default=False
    )
    cupboard_locked = fields.Boolean(
        string='Was the Cupboard Locked?',
        default=False
    )
    office_dor_locked = fields.Boolean(
        string='Was the Office Door Locked?',
        default=False
    )
    drawer_locked = fields.Boolean(
        string='Was the Drawer Locked?',
        default=False
    )
    cabinet_locked = fields.Boolean(
        string='Was the Cabinet Locked?',
        default=False
    )
    safebox_locked = fields.Boolean(
        string='Was the Safebox Locked?',
        default=False
    )

    # Signatures
    reporter_signature = fields.Binary(
        string='Reporter Signature',
        attachment=True
    )
    fleet_manager_signature = fields.Binary(
        string='Fleet Manager Signature',
        attachment=True
    )
    transport_manager_signature = fields.Binary(
        string='Transport Manager Signature',
        attachment=True
    )

    # Insurance Claim
    insurance_notified = fields.Boolean(
        string='Insurance Notified?',
        default=False,
        tracking=True
    )
    insurance_company = fields.Char(
        string='Insurance Company',
        related='vehicle_id.insurance_company'
    )
    insurance_policy_number = fields.Char(
        string='Insurance Policy Number',
        related='vehicle_id.insurance_policy_number'
    )
    insurance_claim_number = fields.Char(
        string='Insurance Claim Number',
        tracking=True
    )
    insurance_contact_person = fields.Char(
        string='Insurance Contact Person'
    )
    insurance_contact_phone = fields.Char(
        string='Insurance Contact Phone'
    )
    insurance_claim_date = fields.Date(
        string='Insurance Claim Date',
        tracking=True
    )
    insurance_assessor = fields.Char(
        string='Insurance Assessor Name'
    )
    insurance_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid Out'),
    ], string='Insurance Claim Status')
    insurance_payout_amount = fields.Float(
        string='Insurance Payout Amount'
    )

    # Recovery Information
    vehicle_recovered = fields.Boolean(
        string='Vehicle Recovered?',
        default=False,
        tracking=True
    )
    recovery_date = fields.Date(
        string='Recovery Date',
        tracking=True
    )
    recovery_location = fields.Char(
        string='Recovery Location'
    )
    recovery_condition = fields.Text(
        string='Condition Upon Recovery',
        help='Describe the condition of vehicle when recovered'
    )
    recovery_damage_estimated = fields.Float(
        string='Estimated Recovery Damage Cost'
    )

    # Investigation
    investigation_officer_id = fields.Many2one(
        'res.users',
        string='Investigation Officer',
        tracking=True
    )
    investigation_notes = fields.Text(
        string='Investigation Notes'
    )
    investigation_findings = fields.Text(
        string='Investigation Findings'
    )
    cctv_footage_available = fields.Boolean(
        string='CCTV Footage Available?',
        default=False
    )
    cctv_footage_description = fields.Text(
        string='CCTV Footage Description'
    )

    # Resolution
    resolution_date = fields.Date(
        string='Resolution Date',
        tracking=True
    )
    resolution_description = fields.Text(
        string='Resolution Description'
    )
    lessons_learned = fields.Text(
        string='Lessons Learned',
        help='What can be learned to prevent future incidents?'
    )
    preventive_actions = fields.Text(
        string='Preventive Actions Taken',
        help='What actions have been implemented to prevent recurrence?'
    )

    # Financial Impact
    total_financial_loss = fields.Float(
        string='Total Financial Loss',
        compute='_compute_total_loss',
        store=True
    )
    insurance_recovery = fields.Float(
        string='Insurance Recovery Amount'
    )
    net_loss = fields.Float(
        string='Net Loss',
        compute='_compute_net_loss',
        store=True
    )

    @api.depends('estimated_value', 'recovery_damage_estimated')
    def _compute_total_loss(self):
        for record in self:
            record.total_financial_loss = record.estimated_value + record.recovery_damage_estimated

    @api.depends('total_financial_loss', 'insurance_recovery')
    def _compute_net_loss(self):
        for record in self:
            record.net_loss = record.total_financial_loss - record.insurance_recovery

    # Attachments & Evidence
    attachments_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
        help='Photos, documents, and other evidence'
    )

    # Notes
    internal_notes = fields.Text(
        string='Internal Notes',
        help='Internal notes not for external reports'
    )

    # Constraints
    @api.constrains('incident_date', 'discovered_date')
    def _check_dates(self):
        for record in self:
            if record.discovered_date < record.incident_date:
                raise ValidationError(_('Discovery date cannot be before incident date.'))

    # CRUD Operations
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'fleet.lost.theft'
                ) or _('New')
        return super().create(vals_list)

    # Action Methods
    def action_report_incident(self):
        """Report the incident"""
        self.ensure_one()
        self.write({'state': 'reported'})
        # Send notification to fleet manager
        self._send_incident_notification()
        return True

    def action_start_investigation(self):
        """Start investigation"""
        self.ensure_one()
        if not self.investigation_officer_id:
            self.investigation_officer_id = self.env.user
        self.write({'state': 'under_investigation'})
        return True

    def action_report_police(self):
        """Mark as reported to police"""
        self.ensure_one()
        if not self.police_case_number:
            raise UserError(_('Please enter the police case number.'))
        self.write({
            'state': 'police_reported',
            'police_reported': True,
            'police_report_date': fields.Date.context_today(self),
        })
        return True

    def action_claim_insurance(self):
        """Submit insurance claim"""
        self.ensure_one()
        if not self.police_reported:
            raise UserError(_('Please report to police first before claiming insurance.'))
        self.write({
            'state': 'insurance_claimed',
            'insurance_notified': True,
            'insurance_claim_date': fields.Date.context_today(self),
        })
        return True

    def action_resolve(self):
        """Resolve the case"""
        self.ensure_one()
        self.write({
            'state': 'resolved',
            'resolution_date': fields.Date.context_today(self),
        })
        return True

    def action_close(self):
        """Close the case"""
        self.ensure_one()
        if not self.resolution_description:
            raise UserError(_('Please provide resolution description before closing.'))
        self.write({'state': 'closed'})
        return True

    def _send_incident_notification(self):
        """Send email notification about incident"""
        self.ensure_one()
        template = self.env.ref(
            'enhanced_fleet_management.email_template_lost_theft_incident',
            raise_if_not_found=False
        )
        if template:
            template.send_mail(self.id, force_send=True)

    def action_print_report(self):
        """Print Lost/Theft Report"""
        return self.env.ref('enhanced_fleet_management.action_report_lost_theft').report_action(self)
