# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class FleetVehicleRelief(models.Model):
    """GFMS Vehicle Relief Form - Vehicle replacement/substitute management"""
    _name = 'fleet.vehicle.relief'
    _description = 'Fleet Vehicle Relief Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc, id desc'

    # Basic Information
    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                           default=lambda self: 'New')
    name = fields.Char(string='Relief Title', compute='_compute_name', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('relief_assigned', 'Relief Vehicle Assigned'),
        ('active', 'Active'),
        ('returned', 'Original Vehicle Returned'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, required=True)

    # Request Details
    request_date = fields.Date(string='Request Date', default=fields.Date.today,
                              required=True, tracking=True)
    requester_id = fields.Many2one('res.users', string='Requested By',
                                   default=lambda self: self.env.user,
                                   required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)

    # Original Vehicle
    original_vehicle_id = fields.Many2one('fleet.vehicle', string='Original Vehicle',
                                         required=True, tracking=True, ondelete='restrict')
    original_registration = fields.Char(related='original_vehicle_id.license_plate',
                                       string='Original Registration')
    original_vehicle_make = fields.Char(related='original_vehicle_id.model_id.brand_id.name',
                                       string='Original Make')
    original_vehicle_model = fields.Char(related='original_vehicle_id.model_id.name',
                                        string='Original Model')

    # Relief Reason
    relief_reason = fields.Selection([
        ('maintenance', 'Scheduled Maintenance'),
        ('repair', 'Repair Required'),
        ('accident', 'Accident Damage'),
        ('breakdown', 'Breakdown'),
        ('inspection', 'Safety Inspection'),
        ('service', 'Service'),
        ('other', 'Other')
    ], string='Relief Reason', required=True, tracking=True)
    reason_description = fields.Text(string='Reason Description', required=True)

    # Related Records
    accident_report_id = fields.Many2one('fleet.accident.report', string='Related Accident Report')
    maintenance_id = fields.Many2one('fleet.vehicle.log.services', string='Related Maintenance')

    # Period
    start_date = fields.Date(string='Relief Start Date', required=True, tracking=True)
    expected_end_date = fields.Date(string='Expected End Date', required=True, tracking=True)
    actual_end_date = fields.Date(string='Actual End Date', tracking=True)
    relief_duration = fields.Integer(compute='_compute_relief_duration',
                                    string='Duration (Days)', store=True)

    # Relief Vehicle
    relief_vehicle_id = fields.Many2one('fleet.vehicle', string='Relief Vehicle',
                                       tracking=True, ondelete='restrict')
    relief_registration = fields.Char(related='relief_vehicle_id.license_plate',
                                     string='Relief Registration')
    relief_vehicle_make = fields.Char(related='relief_vehicle_id.model_id.brand_id.name',
                                     string='Relief Make')
    relief_vehicle_model = fields.Char(related='relief_vehicle_id.model_id.name',
                                      string='Relief Model')
    relief_assigned_date = fields.Date(string='Relief Assigned Date', tracking=True)

    # Driver Assignment
    driver_id = fields.Many2one('res.partner', string='Assigned Driver',
                               domain=[('is_fleet_driver', '=', True)], tracking=True)
    driver_license = fields.Char(related='driver_id.driver_license_number',
                                string='Driver License')
    driver_contact = fields.Char(related='driver_id.phone', string='Driver Contact')

    # Vehicle Condition (Handover)
    handover_odometer = fields.Integer(string='Handover Odometer Reading')
    handover_fuel_level = fields.Selection([
        ('empty', 'Empty'),
        ('quarter', '1/4 Tank'),
        ('half', '1/2 Tank'),
        ('three_quarter', '3/4 Tank'),
        ('full', 'Full Tank')
    ], string='Handover Fuel Level')
    handover_condition = fields.Text(string='Vehicle Condition at Handover')
    handover_checklist_id = fields.Many2one('fleet.vehicle.checklist',
                                           string='Handover Checklist')

    # Vehicle Condition (Return)
    return_odometer = fields.Integer(string='Return Odometer Reading')
    return_fuel_level = fields.Selection([
        ('empty', 'Empty'),
        ('quarter', '1/4 Tank'),
        ('half', '1/2 Tank'),
        ('three_quarter', '3/4 Tank'),
        ('full', 'Full Tank')
    ], string='Return Fuel Level')
    return_condition = fields.Text(string='Vehicle Condition at Return')
    return_checklist_id = fields.Many2one('fleet.vehicle.checklist',
                                         string='Return Checklist')

    # Costs
    daily_rate = fields.Monetary(string='Daily Rate', currency_field='currency_id')
    total_cost = fields.Monetary(compute='_compute_total_cost', string='Total Cost',
                                currency_field='currency_id', store=True)
    additional_costs = fields.Monetary(string='Additional Costs', currency_field='currency_id')
    cost_notes = fields.Text(string='Cost Notes')

    # Approval
    approved_by_id = fields.Many2one('res.users', string='Approved By', tracking=True)
    approval_date = fields.Date(string='Approval Date', tracking=True)
    approval_notes = fields.Text(string='Approval Notes')

    # Administrative
    notes = fields.Text(string='Additional Notes')
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='normal', tracking=True)

    # Computed Fields
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    is_overdue = fields.Boolean(compute='_compute_is_overdue', store=True, string='Overdue')
    company_id = fields.Many2one('res.company', string='Company',
                                default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('fleet.vehicle.relief') or 'New'
        return super(FleetVehicleRelief, self).create(vals)

    @api.depends('reference', 'original_vehicle_id', 'relief_reason')
    def _compute_name(self):
        for record in self:
            if record.original_vehicle_id:
                reason = dict(record._fields['relief_reason'].selection).get(record.relief_reason, '')
                record.name = f"{record.reference} - {record.original_vehicle_id.license_plate} - {reason}"
            else:
                record.name = record.reference or 'New Relief Request'

    @api.depends('start_date', 'expected_end_date', 'actual_end_date')
    def _compute_relief_duration(self):
        for record in self:
            if record.start_date and record.expected_end_date:
                end_date = record.actual_end_date or record.expected_end_date
                delta = end_date - record.start_date
                record.relief_duration = delta.days
            else:
                record.relief_duration = 0

    @api.depends('daily_rate', 'relief_duration', 'additional_costs')
    def _compute_total_cost(self):
        for record in self:
            base_cost = (record.daily_rate or 0) * (record.relief_duration or 0)
            record.total_cost = base_cost + (record.additional_costs or 0)

    @api.depends('expected_end_date', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' and record.expected_end_date:
                record.is_overdue = record.expected_end_date < today
            else:
                record.is_overdue = False

    def action_submit(self):
        """Submit relief request for approval"""
        self._validate_dates()
        self.write({'state': 'submitted'})

    def action_approve(self):
        """Approve relief request"""
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approval_date': fields.Date.today()
        })
        self._send_approval_notification()

    def action_assign_relief(self):
        """Assign relief vehicle"""
        if not self.relief_vehicle_id:
            raise ValidationError("Please select a relief vehicle before assigning.")

        # Create handover checklist
        checklist = self.env['fleet.vehicle.checklist'].create({
            'vehicle_id': self.relief_vehicle_id.id,
            'driver_id': self.driver_id.id if self.driver_id else False,
            'checklist_type': 'pre_trip',
            'notes': f'Handover checklist for relief request {self.reference}'
        })

        self.write({
            'state': 'relief_assigned',
            'relief_assigned_date': fields.Date.today(),
            'handover_checklist_id': checklist.id
        })

    def action_activate(self):
        """Activate relief period"""
        self.write({'state': 'active'})

    def action_return_original(self):
        """Return original vehicle"""
        if not self.actual_end_date:
            self.actual_end_date = fields.Date.today()

        # Create return checklist
        if self.relief_vehicle_id:
            checklist = self.env['fleet.vehicle.checklist'].create({
                'vehicle_id': self.relief_vehicle_id.id,
                'driver_id': self.driver_id.id if self.driver_id else False,
                'checklist_type': 'post_trip',
                'notes': f'Return checklist for relief request {self.reference}'
            })
            self.return_checklist_id = checklist.id

        self.write({'state': 'returned'})

    def action_close(self):
        """Close relief request"""
        if not self.actual_end_date:
            self.actual_end_date = fields.Date.today()
        self.write({'state': 'closed'})

    def action_cancel(self):
        """Cancel relief request"""
        self.write({'state': 'cancelled'})

    def _validate_dates(self):
        """Validate date logic"""
        if self.start_date and self.expected_end_date:
            if self.expected_end_date < self.start_date:
                raise ValidationError("Expected end date cannot be before start date.")

        if self.actual_end_date and self.start_date:
            if self.actual_end_date < self.start_date:
                raise ValidationError("Actual end date cannot be before start date.")

    def _send_approval_notification(self):
        """Send approval notification"""
        template = self.env.ref('enhanced_fleet_management.email_template_relief_approved',
                               raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    @api.constrains('start_date', 'expected_end_date', 'actual_end_date')
    def _check_dates(self):
        for record in self:
            record._validate_dates()
