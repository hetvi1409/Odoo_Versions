# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class FleetTripAuthority(models.Model):
    _name = 'fleet.trip.authority'
    _description = 'Trip Authority Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'departure_date desc, id desc'
    _rec_name = 'reference'

    # Basic Information
    reference = fields.Char(
        string='Authority Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True
    )

    trip_number = fields.Char(
        string='Trip Number',
        copy=False,
        readonly=True,
        index=True,
        help='Sequential trip number in format GGG145776/01/2024 (from MANUAL_TRIP_AUTHORISATION_2018.pdf)',
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    # Related Transport Request
    transport_request_id = fields.Many2one(
        'fleet.transport.request',
        string='Transport Request',
        tracking=True
    )

    # Employee & Vehicle Information
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True
    )
    employee_number = fields.Char(
        string='Employee Number',
        related='employee_id.barcode',
        store=True,
        help='Linked to the employee barcode since employee_number is not available.'
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        related='employee_id.job_id',
        store=True
    )

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
    driver_license_number = fields.Char(
        string='Driver License Number',
        related='driver_id.driver_license_number'
    )

    co_driver = fields.Boolean(string='Co-Driver Required',default=False,tracking=True)
    co_driver_id = fields.Many2one('res.partner',string='Co-Driver',domain=[('is_fleet_driver', '=', True)])
    co_driver_license_number = fields.Char(
        string='Co-Driver License Number',
        related='co_driver_id.driver_license_number'
    )

    # Trip Details
    departure_date = fields.Date(
        string='Departure Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    departure_time = fields.Float(
        string='Departure Time',
        help='Time in 24-hour format'
    )
    return_date = fields.Date(
        string='Expected Return Date',
        required=True,
        tracking=True
    )
    return_time = fields.Float(
        string='Expected Return Time',
        help='Time in 24-hour format'
    )
    actual_return_date = fields.Datetime(
        string='Actual Return Date',
        readonly=True
    )

    destination = fields.Char(
        string='Destination',
        required=True,
        tracking=True
    )
    route_description = fields.Text(
        string='Route Description',
        help='Detailed route or multiple stops'
    )
    purpose = fields.Text(
        string='Purpose of Trip',
        required=True,
        tracking=True
    )

    # Odometer Readings
    odometer_start = fields.Float(
        string='Odometer Start (KM)',
        tracking=True,
        help='Odometer reading at departure'
    )
    odometer_end = fields.Float(
        string='Odometer End (KM)',
        tracking=True,
        help='Odometer reading at return'
    )
    distance_travelled = fields.Float(
        string='Distance Travelled (KM)',
        compute='_compute_distance_travelled',
        store=True
    )

    @api.depends('odometer_start', 'odometer_end')
    def _compute_distance_travelled(self):
        for record in self:
            if record.odometer_end and record.odometer_start:
                record.distance_travelled = record.odometer_end - record.odometer_start
            else:
                record.distance_travelled = 0.0

    # Fuel Information
    fuel_level_start = fields.Selection([
        ('0', 'Empty'),
        ('25', '1/4 Tank'),
        ('50', '1/2 Tank'),
        ('75', '3/4 Tank'),
        ('100', 'Full Tank'),
    ], string='Fuel Level at Start')

    fuel_level_end = fields.Selection([
        ('0', 'Empty'),
        ('25', '1/4 Tank'),
        ('50', '1/2 Tank'),
        ('75', '3/4 Tank'),
        ('100', 'Full Tank'),
    ], string='Fuel Level at Return')

    fuel_cost = fields.Float(
        string='Fuel Cost',
        help='Total fuel cost for the trip'
    )
    fuel_receipts = fields.Binary(
        string='Fuel Receipts',
        attachment=True
    )

    # Authorization
    authorized_by_id = fields.Many2one(
        'res.users',
        string='Authorized By',
        tracking=True
    )
    authorization_date = fields.Date(
        string='Authorization Date',
        default=fields.Date.context_today
    )
    authorized_signature = fields.Binary(
        string='Authorized Signature',
        attachment=True
    )

    # Additional Information
    passengers_list = fields.Text(
        string='Passengers List',
        help='Names of all passengers'
    )
    number_of_passengers = fields.Integer(
        string='Number of Passengers',
        default=1
    )
    special_instructions = fields.Text(
        string='Special Instructions'
    )
    emergency_contact_name = fields.Char(
        string='Emergency Contact Name'
    )
    emergency_contact_phone = fields.Char(
        string='Emergency Contact Phone'
    )

    # Trip Completion
    trip_report = fields.Text(
        string='Trip Report',
        help='Summary report of the trip'
    )
    incidents_reported = fields.Text(
        string='Incidents/Issues Reported'
    )
    completed_by_id = fields.Many2one(
        'res.users',
        string='Completed By',
        readonly=True
    )
    completion_date = fields.Datetime(
        string='Completion Date',
        readonly=True
    )

    # Related Records
    vehicle_checklist_ids = fields.One2many(
        'fleet.vehicle.checklist',
        'trip_authority_id',
        string='Vehicle Checklists'
    )

    # Computed Fields
    duration_days = fields.Integer(
        string='Trip Duration (Days)',
        compute='_compute_duration',
        store=True
    )

    is_overdue = fields.Boolean(
        string='Overdue',
        compute='_compute_is_overdue',
        store=True
    )

    @api.depends('departure_date', 'return_date')
    def _compute_duration(self):
        for record in self:
            if record.departure_date and record.return_date:
                delta = record.return_date - record.departure_date
                record.duration_days = delta.days + 1
            else:
                record.duration_days = 0

    @api.depends('return_date', 'state', 'actual_return_date')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.state in ['issued', 'active'] and not record.actual_return_date:
                record.is_overdue = record.return_date < today
            else:
                record.is_overdue = False

    # Constraints
    @api.constrains('departure_date', 'return_date')
    def _check_dates(self):
        for record in self:
            if record.return_date < record.departure_date:
                raise ValidationError(_('Return date cannot be before departure date.'))

    @api.constrains('odometer_end', 'odometer_start')
    def _check_odometer(self):
        for record in self:
            if record.odometer_end and record.odometer_start:
                if record.odometer_end < record.odometer_start:
                    raise ValidationError(_('End odometer reading cannot be less than start reading.'))

    # CRUD Operations
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'fleet.trip.authority'
                ) or _('New')

            # Generate sequential trip number (format: GGG145776/01/2024)
            if not vals.get('trip_number'):
                # Get the last trip number to generate sequential number
                last_trip = self.search([], order='id desc', limit=1)
                if last_trip and last_trip.trip_number:
                    # Extract the base number and increment
                    try:
                        parts = last_trip.trip_number.split('/')
                        if len(parts) == 3:
                            base_num = int(parts[0][3:]) + 1  # Remove 'GGG' prefix and increment
                            month = parts[1]
                            year = parts[2]
                        else:
                            base_num = 145776
                            month = '01'
                            year = '2024'
                    except:
                        base_num = 145776
                        month = '01'
                        year = '2024'
                else:
                    base_num = 145776
                    month = '01'
                    year = '2024'

                # Generate trip number in format GGG145776/01/2024
                vals['trip_number'] = f'GGG{base_num:06d}/{month}/{year}'

        return super().create(vals_list)

    # Action Methods
    def action_issue(self):
        """Issue trip authority"""
        self.ensure_one()
        if not self.authorized_by_id:
            self.authorized_by_id = self.env.user
        self.write({
            'state': 'issued',
            'authorization_date': fields.Date.context_today(self),
        })
        # Create pre-trip checklist
        self._create_pre_trip_checklist()
        return True

    def action_activate(self):
        """Activate trip (vehicle has departed)"""
        self.ensure_one()
        if not self.odometer_start:
            raise UserError(_('Please record the starting odometer reading.'))
        self.write({'state': 'active'})
        return True

    def action_complete(self):
        """Complete the trip"""
        self.ensure_one()
        if not self.odometer_end:
            raise UserError(_('Please record the ending odometer reading.'))
        # Create post-trip checklist
        self._create_post_trip_checklist()
        self.write({
            'state': 'completed',
            'actual_return_date': fields.Datetime.now(),
            'completed_by_id': self.env.user.id,
            'completion_date': fields.Datetime.now(),
        })
        # Update transport request
        if self.transport_request_id:
            self.transport_request_id.action_complete()
        return True

    def action_cancel(self):
        """Cancel the trip authority"""
        self.ensure_one()
        self.write({'state': 'cancelled'})
        return True

    def _create_pre_trip_checklist(self):
        """Create pre-trip vehicle checklist"""
        self.ensure_one()
        checklist = self.env['fleet.vehicle.checklist'].create({
            'trip_authority_id': self.id,
            'transport_request_id': self.transport_request_id.id,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'inspector_id': self.env.user.employee_id.id,
            'inspection_type': 'pre_trip',
            'inspection_date': fields.Date.context_today(self),
        })
        return checklist

    def _create_post_trip_checklist(self):
        """Create post-trip vehicle checklist"""
        self.ensure_one()
        checklist = self.env['fleet.vehicle.checklist'].create({
            'trip_authority_id': self.id,
            'transport_request_id': self.transport_request_id.id,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'inspector_id': self.env.user.employee_id.id,
            'inspection_type': 'post_trip',
            'inspection_date': fields.Date.context_today(self),
        })
        return checklist

    def action_print_authority(self):
        """Print Trip Authority Report"""
        return self.env.ref('enhanced_fleet_management.action_report_trip_authority').report_action(self)

    def action_view_checklists(self):
        """View related vehicle checklists"""
        self.ensure_one()
        return {
            'name': _('Vehicle Checklists'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.checklist',
            'view_mode': 'list,form',
            'domain': [('trip_authority_id', '=', self.id)],
            'context': {
                'default_trip_authority_id': self.id,
                'default_vehicle_id': self.vehicle_id.id,
                'default_driver_id': self.driver_id.id,
            }
        }
