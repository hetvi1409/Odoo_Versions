# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class FleetTransportRequest(models.Model):
    _name = 'fleet.transport.request'
    _description = 'Transport Request Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_required desc, id desc'
    _rec_name = 'reference'

    # Basic Information
    reference = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('vehicle_assigned', 'Vehicle Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    # Requester Information
    requester_id = fields.Many2one(
        'res.users',
        string='Requester',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        related='requester_id.employee_id',
        store=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        tracking=True
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        related='employee_id.job_id',
        store=True
    )
    phone = fields.Char(
        string='Contact Phone',
        related='employee_id.work_phone',
        store=True
    )
    email = fields.Char(
        string='Contact Email',
        related='employee_id.work_email',
        store=True
    )

    # Trip Details
    date_required = fields.Date(
        string='Date Required',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    time_required = fields.Float(
        string='Time Required',
        required=True,
        help='Time in 24-hour format (e.g., 14.5 for 2:30 PM)'
    )
    pickup_location = fields.Char(
        string='Pickup Location',
        required=True,
        tracking=True
    )
    destination = fields.Char(
        string='Destination',
        required=True,
        tracking=True
    )
    distance_km = fields.Float(
        string='Estimated Distance (KM)',
        help='Estimated distance in kilometers'
    )
    purpose = fields.Text(
        string='Purpose of Trip',
        required=True,
        tracking=True
    )
    number_of_passengers = fields.Integer(
        string='Number of Passengers',
        default=1,
        required=True
    )
    passenger_names = fields.Text(
        string='Passenger Names',
        help='List of passenger names'
    )

    passenger_id_documents = fields.Binary(
        string='Passenger ID Documents',
        help='Attach scanned copies of passenger ID documents'
    )
    passenger_id_filenames = fields.Char(
        string='Passenger ID Filenames',
        help='Filenames of the attached passenger ID documents'
    )

    # Transport Type
    transport_type = fields.Selection([
        ('one_way', 'One Way'),
        ('return', 'Return Trip'),
        ('multi_stop', 'Multiple Stops'),
    ], string='Transport Type', required=True, default='return', tracking=True)

    return_date = fields.Date(
        string='Return Date',
        tracking=True
    )
    return_time = fields.Float(
        string='Return Time',
        help='Return time in 24-hour format'
    )

    # Vehicle & Driver Assignment
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Assigned Vehicle',
        tracking=True,
        domain=[('active', '=', True)]
    )
    driver_id = fields.Many2one(
        'res.partner',
        string='Assigned Driver',
        tracking=True,
        domain=[('is_fleet_driver', '=', True)]
    )

    # Approval Workflow
    manager_id = fields.Many2one(
        'res.users',
        string='Department Manager',
        tracking=True
    )
    manager_approval_date = fields.Datetime(
        string='Manager Approval Date',
        readonly=True
    )
    manager_comments = fields.Text(
        string='Manager Comments'
    )

    fleet_manager_id = fields.Many2one(
        'res.users',
        string='Fleet Manager',
        tracking=True
    )
    fleet_approval_date = fields.Datetime(
        string='Fleet Manager Approval Date',
        readonly=True
    )
    fleet_manager_comments = fields.Text(
        string='Fleet Manager Comments'
    )

    # Additional Information
    special_requirements = fields.Text(
        string='Special Requirements',
        help='Any special requirements or notes'
    )
    is_urgent = fields.Boolean(
        string='Urgent Request',
        default=False,
        tracking=True
    )
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority', default='1', tracking=True)

    # Related Records
    trip_authority_id = fields.Many2one(
        'fleet.trip.authority',
        string='Trip Authority',
        readonly=True
    )
    vehicle_checklist_ids = fields.One2many(
        'fleet.vehicle.checklist',
        'transport_request_id',
        string='Vehicle Checklists'
    )

    # Computed Fields
    duration_days = fields.Integer(
        string='Duration (Days)',
        compute='_compute_duration',
        store=True
    )

    @api.depends('date_required', 'return_date')
    def _compute_duration(self):
        for record in self:
            if record.date_required and record.return_date:
                delta = record.return_date - record.date_required
                record.duration_days = delta.days + 1
            else:
                record.duration_days = 1

    # Constraints
    @api.constrains('date_required', 'return_date')
    def _check_dates(self):
        for record in self:
            if record.return_date and record.return_date < record.date_required:
                raise ValidationError(_('Return date cannot be before the required date.'))
            if record.date_required < fields.Date.context_today(self):
                raise ValidationError(_('Required date cannot be in the past.'))

    @api.constrains('number_of_passengers')
    def _check_passengers(self):
        for record in self:
            if record.number_of_passengers < 1:
                raise ValidationError(_('Number of passengers must be at least 1.'))

    # CRUD Operations
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'fleet.transport.request'
                ) or _('New')
        return super().create(vals_list)

    # Action Methods
    def action_submit(self):
        """Submit transport request for approval"""
        self.ensure_one()
        if not self.manager_id:
            self.manager_id = self.department_id.manager_id.user_id
        self.write({'state': 'submitted'})
        self._send_notification('submitted')
        return True

    def action_approve_manager(self):
        """Manager approval"""
        self.ensure_one()
        self.write({
            'state': 'approved',
            'manager_approval_date': fields.Datetime.now(),
        })
        self._send_notification('manager_approved')
        return True

    def action_approve_fleet(self):
        """Fleet manager approval and vehicle assignment"""
        self.ensure_one()
        if not self.vehicle_id:
            raise UserError(_('Please assign a vehicle before approving.'))
        self.write({
            'state': 'vehicle_assigned',
            'fleet_approval_date': fields.Datetime.now(),
        })
        # Create Trip Authority
        self._create_trip_authority()
        self._send_notification('fleet_approved')
        return True

    def action_start_trip(self):
        """Start the trip"""
        self.ensure_one()
        self.write({'state': 'in_progress'})
        return True

    def action_complete(self):
        """Complete the trip"""
        self.ensure_one()
        self.write({'state': 'completed'})
        return True

    def action_cancel(self):
        """Cancel the request"""
        self.ensure_one()
        self.write({'state': 'cancelled'})
        self._send_notification('cancelled')
        return True

    def action_reset_to_draft(self):
        """Reset to draft"""
        self.ensure_one()
        self.write({'state': 'draft'})
        return True

    def _create_trip_authority(self):
        """Create Trip Authority record"""
        self.ensure_one()
        trip_authority = self.env['fleet.trip.authority'].create({
            'transport_request_id': self.id,
            'employee_id': self.employee_id.id,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'departure_date': self.date_required,
            'return_date': self.return_date or self.date_required,
            'destination': self.destination,
            'purpose': self.purpose,
            'authorized_by_id': self.fleet_manager_id.id,
        })
        self.trip_authority_id = trip_authority.id
        return trip_authority

    def _send_notification(self, notification_type):
        """Send email notifications"""
        self.ensure_one()
        template_ref = f'enhanced_fleet_management.email_template_transport_request_{notification_type}'
        template = self.env.ref(template_ref, raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def action_print_request(self):
        """Print Transport Request Report"""
        return self.env.ref('enhanced_fleet_management.action_report_transport_request').report_action(self)
