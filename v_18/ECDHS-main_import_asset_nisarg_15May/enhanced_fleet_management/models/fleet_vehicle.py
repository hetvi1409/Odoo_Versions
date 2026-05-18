# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # Vehicle Category (from FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf)
    vehicle_category = fields.Selection([
        ('1', 'Category 1 - Sedans'),
        ('5', 'Category 5 - LDV 4x2 1 ton'),
        ('6', 'Category 6 - LDV 4x2 D/Cab'),
        ('11', 'Category 11 - LDV 4x4 1 ton light'),
        ('15', 'Category 15 - 16 Seater'),
        ('mm', 'MM - Ministerial Vehicles'),
    ], string='Vehicle Category', help='Vehicle category as per Fleet Register')

    # Maintenance Contract (from FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf)
    maintenance_contract_type = fields.Selection([
        ('fml', 'FML - Full Maintenance Lease'),
        ('mm', 'MM - Ministerial Maintenance'),
    ], string='Maintenance Contract Type')

    contract_term = fields.Integer(string='Contract Term (Months)', help='Contract term in months (e.g., 60 for FML)')
    contract_km_coverage = fields.Integer(string='Contract KM Coverage', help='KM coverage (e.g., 120,000 for MM)')
    monthly_cost = fields.Float(string='Monthly Cost (ZAR)', help='Monthly maintenance cost in South African Rand')

    # Fleet Register Information
    chassis_number = fields.Char(string='Chassis Number')
    date_received = fields.Date(string='Date Received')
    section_assignment = fields.Char(string='Section Assignment', help='Department/Section assigned to')
    cost_center = fields.Char(string='Cost Center')

    # Accessories (from FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf)
    has_radio = fields.Boolean(string='Radio', default=False)
    has_aircon = fields.Boolean(string='Air Conditioning', default=False)
    has_canopy = fields.Boolean(string='Canopy', default=False)

    # License and Registration
    license_renewal_date = fields.Date(string='License Disc Renewal Date')

    # Additional fields for enhanced fleet management
    insurance_company = fields.Char(string='Insurance Company')
    insurance_policy_number = fields.Char(string='Insurance Policy Number')
    insurance_expiry_date = fields.Date(string='Insurance Expiry Date')

    engine_number = fields.Char(string='Engine Number')

    alarm_fitted = fields.Boolean(string='Alarm System Fitted', default=False)
    tracking_device_fitted = fields.Boolean(string='Tracking Device Fitted', default=False)
    tracking_company = fields.Char(string='Tracking Company')

    # Relations to new modules
    transport_request_ids = fields.One2many(
        'fleet.transport.request',
        'vehicle_id',
        string='Transport Requests'
    )
    trip_authority_ids = fields.One2many(
        'fleet.trip.authority',
        'vehicle_id',
        string='Trip Authorities'
    )
    checklist_ids = fields.One2many(
        'fleet.vehicle.checklist',
        'vehicle_id',
        string='Vehicle Checklists'
    )
    lost_theft_ids = fields.One2many(
        'fleet.lost.theft',
        'vehicle_id',
        string='Lost/Theft Reports'
    )
    accident_report_ids = fields.One2many(
        'fleet.accident.report',
        'vehicle_id',
        string='Accident Reports'
    )
    relief_request_ids = fields.One2many(
        'fleet.vehicle.relief',
        'original_vehicle_id',
        string='Relief Requests'
    )
    odometer_reading_ids = fields.One2many(
        'fleet.odometer.reading',
        'vehicle_id',
        string='Odometer Readings'
    )

    # Computed fields for dashboard
    active_trips_count = fields.Integer(
        string='Active Trips',
        compute='_compute_trips_count'
    )
    pending_requests_count = fields.Integer(
        string='Pending Requests',
        compute='_compute_requests_count'
    )
    last_checklist_date = fields.Date(
        string='Last Checklist Date',
        compute='_compute_last_checklist'
    )
    vehicle_condition_status = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('unsafe', 'Unsafe'),
    ], string='Vehicle Condition', compute='_compute_vehicle_condition')

    @api.depends('trip_authority_ids.state')
    def _compute_trips_count(self):
        for vehicle in self:
            vehicle.active_trips_count = len(vehicle.trip_authority_ids.filtered(
                lambda t: t.state in ['issued', 'active']
            ))

    @api.depends('transport_request_ids.state')
    def _compute_requests_count(self):
        for vehicle in self:
            vehicle.pending_requests_count = len(vehicle.transport_request_ids.filtered(
                lambda r: r.state in ['submitted', 'approved']
            ))

    @api.depends('checklist_ids.inspection_date')
    def _compute_last_checklist(self):
        for vehicle in self:
            if vehicle.checklist_ids:
                vehicle.last_checklist_date = max(
                    vehicle.checklist_ids.mapped('inspection_date')
                )
            else:
                vehicle.last_checklist_date = False

    @api.depends('checklist_ids.overall_condition')
    def _compute_vehicle_condition(self):
        for vehicle in self:
            if vehicle.checklist_ids:
                latest_checklist = vehicle.checklist_ids.sorted(
                    'inspection_date', reverse=True
                )[:1]
                vehicle.vehicle_condition_status = latest_checklist.overall_condition
            else:
                vehicle.vehicle_condition_status = 'good'

    def action_view_transport_requests(self):
        """View transport requests for this vehicle"""
        self.ensure_one()
        return {
            'name': _('Transport Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.transport.request',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }

    def action_view_trip_authorities(self):
        """View trip authorities for this vehicle"""
        self.ensure_one()
        return {
            'name': _('Trip Authorities'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.trip.authority',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }

    def action_view_checklists(self):
        """View checklists for this vehicle"""
        self.ensure_one()
        return {
            'name': _('Vehicle Checklists'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.checklist',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }

    def action_create_checklist(self):
        """Create a new checklist for this vehicle"""
        self.ensure_one()
        return {
            'name': _('New Vehicle Checklist'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.checklist',
            'view_mode': 'form',
            'context': {
                'default_vehicle_id': self.id,
                'default_inspection_type': 'scheduled',
            },
            'target': 'new',
        }


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_fleet_driver = fields.Boolean(string='Is Fleet Driver', default=False)
    driver_license_number = fields.Char(string='Driver License Number')
    driver_license_expiry = fields.Date(string='Driver License Expiry Date')
    driver_license_category = fields.Char(string='License Category')

    # Relations
    transport_request_ids = fields.One2many(
        'fleet.transport.request',
        'driver_id',
        string='Transport Requests'
    )
    trip_authority_ids = fields.One2many(
        'fleet.trip.authority',
        'driver_id',
        string='Trip Authorities'
    )
