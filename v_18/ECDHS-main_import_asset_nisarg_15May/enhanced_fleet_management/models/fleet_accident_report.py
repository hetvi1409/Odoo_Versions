# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class FleetAccidentReport(models.Model):
    """RT46 Accident Report Form - Official accident reporting and investigation"""
    _name = 'fleet.accident.report'
    _description = 'Fleet Accident Report (RT46)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'accident_date desc, id desc'

    # Basic Information
    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                           default=lambda self: 'New')
    name = fields.Char(string='Report Title', compute='_compute_name', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reported', 'Reported'),
        ('investigation', 'Under Investigation'),
        ('claim_filed', 'Claim Filed'),
        ('claim_approved', 'Claim Approved'),
        ('claim_rejected', 'Claim Rejected'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, required=True)

    # Accident Details
    accident_date = fields.Datetime(string='Accident Date & Time', required=True, tracking=True)
    accident_location = fields.Char(string='Location of Accident', required=True, tracking=True)
    accident_address = fields.Text(string='Full Address')
    weather_conditions = fields.Selection([
        ('clear', 'Clear'),
        ('rain', 'Rain'),
        ('fog', 'Fog'),
        ('snow', 'Snow'),
        ('wind', 'Windy'),
        ('other', 'Other')
    ], string='Weather Conditions', tracking=True)
    road_conditions = fields.Selection([
        ('dry', 'Dry'),
        ('wet', 'Wet'),
        ('icy', 'Icy'),
        ('muddy', 'Muddy'),
        ('other', 'Other')
    ], string='Road Conditions', tracking=True)
    accident_type = fields.Selection([
        ('collision', 'Vehicle Collision'),
        ('pedestrian', 'Pedestrian Involved'),
        ('rollover', 'Rollover'),
        ('property', 'Property Damage'),
        ('single', 'Single Vehicle'),
        ('other', 'Other')
    ], string='Accident Type', required=True, tracking=True)

    # Vehicle Information
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle Involved', required=True,
                                 tracking=True, ondelete='restrict')
    vehicle_registration = fields.Char(related='vehicle_id.license_plate', string='Registration No.')
    vehicle_vin = fields.Char(related='vehicle_id.vin_sn', string='VIN/Chassis No.')
    vehicle_make = fields.Char(related='vehicle_id.model_id.brand_id.name', string='Make')
    vehicle_model = fields.Char(related='vehicle_id.model_id.name', string='Model')

    # Driver Information
    driver_id = fields.Many2one('res.partner', string='Driver', required=True,
                                domain=[('is_fleet_driver', '=', True)], tracking=True)
    driver_license = fields.Char(related='driver_id.driver_license_number', string='License Number')
    driver_phone = fields.Char(related='driver_id.phone', string='Driver Phone')
    driver_injured = fields.Boolean(string='Driver Injured', tracking=True)
    driver_injury_details = fields.Text(string='Driver Injury Details')
    odometer_reading = fields.Float(string='Odometer Reading (km)', related='vehicle_id.odometer', readonly=True)
    # department_id = fields.Many2one('hr.department', string='Department', related='driver_id.department_id', readonly=True)
    component_id = fields.Many2one('res.company', string='Company', related='vehicle_id.company_id', readonly=True)
    # rank_id = fields.Many2one('hr.job', string='Rank/Job Title', related='driver_id.job_id', readonly=True)
    driver_email = fields.Char(related='driver_id.email', string='Driver Email')
    driver_mobile = fields.Char(related='driver_id.mobile', string='Driver Mobile')
    driver_country_id = fields.Many2one('res.country', string='Driver Country', related='driver_id.country_id', readonly=True)

    # Passengers
    passenger_count = fields.Integer(string='Number of Passengers', default=0)
    passenger_details = fields.Text(string='Passenger Details')
    passengers_injured = fields.Boolean(string='Passengers Injured', tracking=True)
    passenger_injury_details = fields.Text(string='Passenger Injury Details')

    # Third Party Information
    third_party_involved = fields.Boolean(string='Third Party Involved', tracking=True)
    third_party_name = fields.Char(string='Third Party Name')
    third_party_contact = fields.Char(string='Third Party Contact')
    third_party_vehicle_reg = fields.Char(string='Third Party Vehicle Reg.')
    third_party_insurance = fields.Char(string='Third Party Insurance')
    third_party_injured = fields.Boolean(string='Third Party Injured', tracking=True)
    third_party_injury_details = fields.Text(string='Third Party Injury Details')

    # Accident Description
    accident_description = fields.Text(string='Accident Description', required=True)
    damage_description = fields.Text(string='Damage Description', required=True)
    speed_at_accident = fields.Integer(string='Estimated Speed (km/h)')
    witness_present = fields.Boolean(string='Witnesses Present', tracking=True)
    witness_details = fields.Text(string='Witness Details')

    consumption_of_substances = fields.Selection([
        ('none', 'None'),
        ('alcohol', 'Alcohol'),
        ('drugs', 'Drugs'),
        ('both', 'Both Alcohol and Drugs')
    ], string='Substance Consumption by Driver', tracking=True)
    substance_test_conducted = fields.Boolean(string='Substance Test Conducted', tracking=True)
    substance_test_results = fields.Selection([
        ('negative', 'Negative'),
        ('positive_alcohol', 'Positive for Alcohol'),
        ('positive_drugs', 'Positive for Drugs'),
        ('positive_both', 'Positive for Both')
    ], string='Substance Test Results', tracking=True)

    animal_involved = fields.Boolean(string='Animal Involved', tracking=True)
    animal_type = fields.Char(string='Type of Animal')
    animal_outcome = fields.Selection([
        ('escaped', 'Escaped'),
        ('injured', 'Injured'),
        ('killed', 'Killed')
    ], string='Outcome for Animal', tracking=True)
    animal_owner_details = fields.Text(string='Animal Owner Details')


    # Police & Emergency Services
    police_notified = fields.Boolean(string='Police Notified', tracking=True)
    police_station = fields.Char(string='Police Station')
    police_case_number = fields.Char(string='Police Case Number', tracking=True)
    police_officer_name = fields.Char(string='Attending Officer Name')
    police_report_date = fields.Date(string='Police Report Date')
    ambulance_called = fields.Boolean(string='Ambulance Called', tracking=True)
    hospital_name = fields.Char(string='Hospital Name')

    # Insurance & Claims
    insurance_company_id = fields.Many2one('res.partner', string='Insurance Company',
                                          domain=[('is_company', '=', True)])
    insurance_policy_number = fields.Char(related='vehicle_id.insurance_policy_number',
                                         string='Policy Number')
    insurance_notified = fields.Boolean(string='Insurance Notified', tracking=True)
    insurance_notification_date = fields.Date(string='Insurance Notification Date')
    claim_number = fields.Char(string='Claim Number', tracking=True)
    claim_amount = fields.Monetary(string='Claim Amount', currency_field='currency_id')
    excess_amount = fields.Monetary(string='Excess Amount', currency_field='currency_id')
    claim_status = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid')
    ], string='Claim Status', tracking=True)

    # Vehicle Damage Assessment
    vehicle_driveable = fields.Boolean(string='Vehicle Driveable', tracking=True)
    vehicle_towed = fields.Boolean(string='Vehicle Towed', tracking=True)
    towing_company = fields.Char(string='Towing Company')
    tow_destination = fields.Char(string='Towed To')
    estimated_repair_cost = fields.Monetary(string='Estimated Repair Cost',
                                           currency_field='currency_id')
    actual_repair_cost = fields.Monetary(string='Actual Repair Cost',
                                        currency_field='currency_id')

    # Investigation
    investigation_notes = fields.Text(string='Investigation Notes')
    investigation_officer_id = fields.Many2one('res.users', string='Investigation Officer')
    investigation_date = fields.Date(string='Investigation Date')
    fault_determination = fields.Selection([
        ('driver', 'Our Driver at Fault'),
        ('third_party', 'Third Party at Fault'),
        ('shared', 'Shared Fault'),
        ('no_fault', 'No Fault'),
        ('pending', 'Pending Determination')
    ], string='Fault Determination', tracking=True)
    fault_percentage = fields.Integer(string='Our Fault %', default=0)

    # Documents & Photos
    photo_ids = fields.Many2many('ir.attachment', 'fleet_accident_photo_rel',
                                'accident_id', 'attachment_id',
                                string='Accident Photos')
    photo_count = fields.Integer(compute='_compute_photo_count', string='Photo Count')
    document_ids = fields.Many2many('ir.attachment', 'fleet_accident_document_rel',
                                   'accident_id', 'attachment_id',
                                   string='Supporting Documents')

    # Administrative
    reported_by_id = fields.Many2one('res.users', string='Reported By', required=True,
                                    default=lambda self: self.env.user,
                                    readonly=True, tracking=True)
    reported_date = fields.Datetime(string='Report Date', default=fields.Datetime.now,
                                   readonly=True)
    approved_by_id = fields.Many2one('res.users', string='Approved By', tracking=True)
    approved_date = fields.Datetime(string='Approval Date', tracking=True)
    closed_by_id = fields.Many2one('res.users', string='Closed By', tracking=True)
    closed_date = fields.Datetime(string='Closed Date', tracking=True)

    # Related Records
    trip_authority_id = fields.Many2one('fleet.trip.authority', string='Related Trip Authority')
    lost_theft_id = fields.Many2one('fleet.lost.theft', string='Related Theft Report')

    # Computed Fields
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    total_injuries = fields.Integer(compute='_compute_total_injuries', store=True,
                                   string='Total Injuries')
    severity_level = fields.Selection([
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('fatal', 'Fatal')
    ], compute='_compute_severity_level', store=True, string='Severity Level')
    days_since_accident = fields.Integer(compute='_compute_days_since_accident',
                                        string='Days Since Accident')
    company_id = fields.Many2one('res.company', string='Company',
                                default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('fleet.accident.report') or 'New'
        return super(FleetAccidentReport, self).create(vals)

    @api.depends('reference', 'vehicle_id', 'accident_date')
    def _compute_name(self):
        for record in self:
            if record.vehicle_id and record.accident_date:
                record.name = f"{record.reference} - {record.vehicle_id.license_plate} - {record.accident_date.strftime('%Y-%m-%d')}"
            else:
                record.name = record.reference or 'New Accident Report'

    @api.depends('photo_ids')
    def _compute_photo_count(self):
        for record in self:
            record.photo_count = len(record.photo_ids)

    @api.depends('driver_injured', 'passengers_injured', 'third_party_injured')
    def _compute_total_injuries(self):
        for record in self:
            injuries = 0
            if record.driver_injured:
                injuries += 1
            if record.passengers_injured:
                injuries += record.passenger_count
            if record.third_party_injured:
                injuries += 1
            record.total_injuries = injuries

    @api.depends('total_injuries', 'driver_injured', 'passengers_injured',
                 'third_party_injured', 'estimated_repair_cost')
    def _compute_severity_level(self):
        for record in self:
            if any([record.driver_injured, record.passengers_injured, record.third_party_injured]):
                if record.total_injuries > 3:
                    record.severity_level = 'fatal'
                elif record.total_injuries > 1:
                    record.severity_level = 'major'
                else:
                    record.severity_level = 'moderate'
            elif record.estimated_repair_cost > 100000:
                record.severity_level = 'major'
            elif record.estimated_repair_cost > 50000:
                record.severity_level = 'moderate'
            else:
                record.severity_level = 'minor'

    @api.depends('accident_date')
    def _compute_days_since_accident(self):
        for record in self:
            if record.accident_date:
                delta = datetime.now() - record.accident_date
                record.days_since_accident = delta.days
            else:
                record.days_since_accident = 0

    def action_report_accident(self):
        """Report the accident"""
        self.write({
            'state': 'reported',
            'reported_date': fields.Datetime.now()
        })
        self._send_accident_notification()

    def action_start_investigation(self):
        """Start investigation"""
        self.write({
            'state': 'investigation',
            'investigation_date': fields.Date.today(),
            'investigation_officer_id': self.env.user.id
        })

    def action_file_claim(self):
        """File insurance claim"""
        if not self.insurance_company_id:
            raise ValidationError("Please specify the insurance company before filing a claim.")
        self.write({
            'state': 'claim_filed',
            'insurance_notified': True,
            'insurance_notification_date': fields.Date.today()
        })

    def action_approve_claim(self):
        """Approve insurance claim"""
        self.write({
            'state': 'claim_approved',
            'claim_status': 'approved'
        })

    def action_reject_claim(self):
        """Reject insurance claim"""
        self.write({
            'state': 'claim_rejected',
            'claim_status': 'rejected'
        })

    def action_close_report(self):
        """Close the accident report"""
        self.write({
            'state': 'closed',
            'closed_by_id': self.env.user.id,
            'closed_date': fields.Datetime.now()
        })

    def action_cancel(self):
        """Cancel the report"""
        self.write({'state': 'cancelled'})

    def action_view_photos(self):
        """View accident photos"""
        return {
            'name': 'Accident Photos',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.photo_ids.ids)],
            'context': {'default_res_model': self._name, 'default_res_id': self.id}
        }

    def _send_accident_notification(self):
        """Send email notification about the accident"""
        template = self.env.ref('enhanced_fleet_management.email_template_accident_report',
                               raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    @api.constrains('accident_date')
    def _check_accident_date(self):
        for record in self:
            if record.accident_date and record.accident_date > fields.Datetime.now():
                raise ValidationError("Accident date cannot be in the future.")

    @api.constrains('fault_percentage')
    def _check_fault_percentage(self):
        for record in self:
            if record.fault_percentage < 0 or record.fault_percentage > 100:
                raise ValidationError("Fault percentage must be between 0 and 100.")
