# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FleetVehicleChecklist(models.Model):
    _name = 'fleet.vehicle.checklist'
    _description = 'Vehicle Inspection Checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'inspection_date desc, id desc'
    _rec_name = 'reference'

    # Basic Information
    reference = fields.Char(
        string='Checklist Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('issues_found', 'Issues Found'),
        ('approved', 'Approved'),
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    # Related Records
    transport_request_id = fields.Many2one(
        'fleet.transport.request',
        string='Transport Request',
        tracking=True
    )
    trip_authority_id = fields.Many2one(
        'fleet.trip.authority',
        string='Trip Authority',
        tracking=True
    )

    # Vehicle & Personnel
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
        domain=[('active', '=', True)]
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

    driver_id = fields.Many2one(
        'res.partner',
        string='Driver',
        required=True,
        tracking=True,
        domain=[('is_fleet_driver', '=', True)]
    )
    inspector_id = fields.Many2one(
        'hr.employee',
        string='Inspector',
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True
    )

    # Inspection Details
    inspection_type = fields.Selection([
        ('pre_trip', 'Pre-Trip Inspection'),
        ('post_trip', 'Post-Trip Inspection'),
        ('scheduled', 'Scheduled Maintenance'),
        ('random', 'Random Inspection'),
    ], string='Inspection Type', required=True, default='pre_trip', tracking=True)

    inspection_date = fields.Date(
        string='Inspection Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    inspection_time = fields.Float(
        string='Inspection Time',
        help='Time in 24-hour format'
    )

    odometer_reading = fields.Float(
        string='Odometer Reading (KM)',
        required=True,
        tracking=True
    )

    # EXTERIOR CHECKS
    # Body & Paintwork
    body_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], string='Body Condition', default='good')
    body_damage = fields.Boolean(string='Body Damage')
    body_damage_description = fields.Text(string='Body Damage Description')

    # Lights
    headlights = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Headlights', default='ok')
    taillights = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Taillights', default='ok')
    indicators = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Indicators/Turn Signals', default='ok')
    brake_lights = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Brake Lights', default='ok')
    hazard_lights = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Hazard Lights', default='ok')

    # Mirrors & Windows
    mirrors = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Mirrors (All)', default='ok')
    windscreen = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Windscreen', default='ok')
    windows = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Windows', default='ok')
    wipers = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Wipers', default='ok')

    # Tyres & Wheels
    tyre_front_left = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Tyre - Front Left', default='ok')
    tyre_front_right = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Tyre - Front Right', default='ok')
    tyre_rear_left = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Tyre - Rear Left', default='ok')
    tyre_rear_right = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Tyre - Rear Right', default='ok')
    spare_tyre = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Spare Tyre', default='ok')

    # UNDER THE HOOD
    engine_oil_level = fields.Selection([
        ('ok', 'OK'),
        ('low', 'Low'),
        ('na', 'N/A'),
    ], string='Engine Oil Level', default='ok')
    coolant_level = fields.Selection([
        ('ok', 'OK'),
        ('low', 'Low'),
        ('na', 'N/A'),
    ], string='Coolant Level', default='ok')
    brake_fluid_level = fields.Selection([
        ('ok', 'OK'),
        ('low', 'Low'),
        ('na', 'N/A'),
    ], string='Brake Fluid Level', default='ok')
    power_steering_fluid = fields.Selection([
        ('ok', 'OK'),
        ('low', 'Low'),
        ('na', 'N/A'),
    ], string='Power Steering Fluid', default='ok')
    windscreen_washer_fluid = fields.Selection([
        ('ok', 'OK'),
        ('low', 'Low'),
        ('na', 'N/A'),
    ], string='Windscreen Washer Fluid', default='ok')
    battery_condition = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Battery Condition', default='ok')

    # Leaks
    oil_leaks = fields.Boolean(string='Oil Leaks')
    coolant_leaks = fields.Boolean(string='Coolant Leaks')
    fuel_leaks = fields.Boolean(string='Fuel Leaks')
    other_leaks = fields.Boolean(string='Other Leaks')
    leaks_description = fields.Text(string='Leaks Description')

    # INTERIOR CHECKS
    seats_condition = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Seats Condition', default='ok')
    seatbelts = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Seatbelts (All)', default='ok')
    dashboard_instruments = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Dashboard Instruments', default='ok')
    horn = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Horn', default='ok')
    air_conditioning = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Air Conditioning', default='ok')
    heater = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Heater', default='ok')
    interior_lights = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Interior Lights', default='ok')
    radio_sound_system = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('na', 'N/A'),
    ], string='Radio/Sound System', default='ok')

    # SAFETY EQUIPMENT
    fire_extinguisher = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('missing', 'Missing'),
    ], string='Fire Extinguisher', default='ok')
    first_aid_kit = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('missing', 'Missing'),
    ], string='First Aid Kit', default='ok')
    warning_triangle = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('missing', 'Missing'),
    ], string='Warning Triangle', default='ok')
    jack_tools = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('missing', 'Missing'),
    ], string='Jack & Tools', default='ok')
    reflective_vest = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('missing', 'Missing'),
    ], string='Reflective Vest', default='ok')

    # DOCUMENTS
    license_disc = fields.Selection([
        ('ok', 'OK'),
        ('expired', 'Expired'),
        ('missing', 'Missing'),
    ], string='License Disc', default='ok')
    vehicle_registration = fields.Selection([
        ('ok', 'OK'),
        ('expired', 'Expired'),
        ('missing', 'Missing'),
    ], string='Vehicle Registration', default='ok')
    insurance_certificate = fields.Selection([
        ('ok', 'OK'),
        ('expired', 'Expired'),
        ('missing', 'Missing'),
    ], string='Insurance Certificate', default='ok')
    service_book = fields.Selection([
        ('ok', 'OK'),
        ('not_ok', 'Not OK'),
        ('missing', 'Missing'),
    ], string='Service Book', default='ok')

    # FUEL
    fuel_level = fields.Selection([
        ('0', 'Empty'),
        ('25', '1/4 Tank'),
        ('50', '1/2 Tank'),
        ('75', '3/4 Tank'),
        ('100', 'Full Tank'),
    ], string='Fuel Level', required=True, default='50')

    # CLEANLINESS
    exterior_cleanliness = fields.Selection([
        ('clean', 'Clean'),
        ('fair', 'Fair'),
        ('dirty', 'Dirty'),
    ], string='Exterior Cleanliness', default='clean')
    interior_cleanliness = fields.Selection([
        ('clean', 'Clean'),
        ('fair', 'Fair'),
        ('dirty', 'Dirty'),
    ], string='Interior Cleanliness', default='clean')

    # OVERALL ASSESSMENT
    overall_condition = fields.Selection([
        ('excellent', 'Excellent - No Issues'),
        ('good', 'Good - Minor Issues'),
        ('fair', 'Fair - Some Issues'),
        ('poor', 'Poor - Major Issues'),
        ('unsafe', 'Unsafe - Do Not Use'),
    ], string='Overall Vehicle Condition', compute='_compute_overall_condition', store=True)

    issues_found = fields.Boolean(
        string='Issues Found',
        compute='_compute_issues_found',
        store=True
    )
    issues_count = fields.Integer(
        string='Number of Issues',
        compute='_compute_issues_found',
        store=True
    )

    defects_description = fields.Text(
        string='Defects/Issues Description',
        help='Detailed description of all defects and issues found'
    )
    recommendations = fields.Text(
        string='Recommendations',
        help='Recommended actions for repairs or maintenance'
    )
    immediate_action_required = fields.Boolean(
        string='Immediate Action Required',
        help='Check if vehicle requires immediate attention'
    )
    vehicle_roadworthy = fields.Boolean(
        string='Vehicle Roadworthy',
        default=True,
        help='Is the vehicle safe to use?'
    )

    # Signatures & Approval
    inspector_signature = fields.Binary(
        string='Inspector Signature',
        attachment=True
    )
    driver_signature = fields.Binary(
        string='Driver Signature',
        attachment=True
    )
    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        tracking=True
    )
    approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True
    )

    # Additional Information
    notes = fields.Text(string='Additional Notes')
    attachments_ids = fields.Many2many(
        'ir.attachment',
        string='Photos/Attachments',
        help='Photos of vehicle condition or issues'
    )

    @api.depends('headlights', 'taillights', 'indicators', 'brake_lights',
                 'tyre_front_left', 'tyre_front_right', 'tyre_rear_left', 'tyre_rear_right',
                 'engine_oil_level', 'coolant_level', 'brake_fluid_level',
                 'seatbelts', 'fire_extinguisher', 'first_aid_kit')
    def _compute_issues_found(self):
        for record in self:
            issues = 0
            # Check all critical fields
            critical_fields = [
                'headlights', 'taillights', 'indicators', 'brake_lights',
                'tyre_front_left', 'tyre_front_right', 'tyre_rear_left', 'tyre_rear_right',
                'seatbelts', 'fire_extinguisher'
            ]
            for field in critical_fields:
                if record[field] in ['not_ok', 'missing']:
                    issues += 1

            # Check fluid levels
            fluid_fields = ['engine_oil_level', 'coolant_level', 'brake_fluid_level']
            for field in fluid_fields:
                if record[field] == 'low':
                    issues += 1

            record.issues_count = issues
            record.issues_found = issues > 0

    @api.depends('issues_count', 'vehicle_roadworthy')
    def _compute_overall_condition(self):
        for record in self:
            if not record.vehicle_roadworthy:
                record.overall_condition = 'unsafe'
            elif record.issues_count == 0:
                record.overall_condition = 'excellent'
            elif record.issues_count <= 2:
                record.overall_condition = 'good'
            elif record.issues_count <= 5:
                record.overall_condition = 'fair'
            else:
                record.overall_condition = 'poor'

    # CRUD Operations
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'fleet.vehicle.checklist'
                ) or _('New')
        return super().create(vals_list)

    # Action Methods
    def action_start_inspection(self):
        """Start inspection"""
        self.ensure_one()
        self.write({'state': 'in_progress'})
        return True

    def action_complete_inspection(self):
        """Complete inspection"""
        self.ensure_one()
        if self.issues_found:
            self.write({'state': 'issues_found'})
        else:
            self.write({'state': 'completed'})
        return True

    def action_approve(self):
        """Approve checklist"""
        self.ensure_one()
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approval_date': fields.Datetime.now(),
        })
        return True

    def action_print_checklist(self):
        """Print Vehicle Checklist Report"""
        return self.env.ref('enhanced_fleet_management.action_report_vehicle_checklist').report_action(self)
