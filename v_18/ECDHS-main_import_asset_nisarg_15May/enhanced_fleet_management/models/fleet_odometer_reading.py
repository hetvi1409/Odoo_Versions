# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetOdometerReading(models.Model):
    """Regular Odometer Reading Tracking"""
    _name = 'fleet.odometer.reading'
    _description = 'Fleet Odometer Reading'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reading_date desc, id desc'

    # Basic Information
    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                           default=lambda self: 'New')
    name = fields.Char(string='Reading Title', compute='_compute_name', store=True)

    # Reading Details
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True,
                                tracking=True, ondelete='restrict')
    vehicle_registration = fields.Char(related='vehicle_id.license_plate', string='Registration')
    driver_id = fields.Many2one('res.partner', string='Driver',
                               domain=[('is_fleet_driver', '=', True)], tracking=True)
    reading_date = fields.Datetime(string='Reading Date', required=True,
                                   default=fields.Datetime.now, tracking=True)
    odometer_reading = fields.Integer(string='Odometer Reading (km)', required=True, tracking=True)
    previous_reading = fields.Integer(compute='_compute_previous_reading',
                                     string='Previous Reading', store=True)
    distance_traveled = fields.Integer(compute='_compute_distance_traveled',
                                      string='Distance Traveled', store=True)

    # Location
    location = fields.Char(string='Location', tracking=True)
    gps_coordinates = fields.Char(string='GPS Coordinates')

    # Fuel Information
    fuel_level = fields.Selection([
        ('empty', 'Empty'),
        ('quarter', '1/4 Tank'),
        ('half', '1/2 Tank'),
        ('three_quarter', '3/4 Tank'),
        ('full', 'Full Tank')
    ], string='Fuel Level', tracking=True)
    fuel_percentage = fields.Integer(string='Fuel %', help='Fuel level percentage')

    # Condition Notes
    vehicle_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string='Vehicle Condition', default='good', tracking=True)
    issues_noted = fields.Boolean(string='Issues Noted', tracking=True)
    issue_description = fields.Text(string='Issue Description')

    # Type & Purpose
    reading_type = fields.Selection([
        ('routine', 'Routine Reading'),
        ('departure', 'Departure'),
        ('arrival', 'Arrival'),
        ('maintenance', 'Before Maintenance'),
        ('post_maintenance', 'After Maintenance'),
        ('fuel', 'Refueling'),
        ('inspection', 'Inspection'),
        ('other', 'Other')
    ], string='Reading Type', default='routine', required=True, tracking=True)

    # Related Records
    trip_authority_id = fields.Many2one('fleet.trip.authority', string='Related Trip')
    maintenance_id = fields.Many2one('fleet.vehicle.log.services', string='Related Maintenance')

    # Photo Evidence
    photo_ids = fields.Many2many('ir.attachment', 'fleet_odometer_photo_rel',
                                'reading_id', 'attachment_id',
                                string='Reading Photos')
    photo_count = fields.Integer(compute='_compute_photo_count', string='Photo Count')

    # Administrative
    recorded_by_id = fields.Many2one('res.users', string='Recorded By',
                                    default=lambda self: self.env.user,
                                    required=True, tracking=True)
    verified = fields.Boolean(string='Verified', tracking=True)
    verified_by_id = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Date(string='Verification Date')
    notes = fields.Text(string='Additional Notes')

    # Validation
    is_suspicious = fields.Boolean(compute='_compute_is_suspicious',
                                   string='Suspicious Reading', store=True)
    warning_message = fields.Text(compute='_compute_is_suspicious', string='Warning')

    company_id = fields.Many2one('res.company', string='Company',
                                default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('fleet.odometer.reading') or 'New'

        # Sync with fleet.vehicle odometer
        if vals.get('vehicle_id') and vals.get('odometer_reading'):
            vehicle = self.env['fleet.vehicle'].browse(vals['vehicle_id'])
            if vals['odometer_reading'] > vehicle.odometer:
                vehicle.odometer = vals['odometer_reading']

        return super(FleetOdometerReading, self).create(vals)

    @api.depends('reference', 'vehicle_id', 'reading_date')
    def _compute_name(self):
        for record in self:
            if record.vehicle_id and record.reading_date:
                record.name = f"{record.reference} - {record.vehicle_id.license_plate} - {record.reading_date.strftime('%Y-%m-%d %H:%M')}"
            else:
                record.name = record.reference or 'New Reading'

    @api.depends('vehicle_id', 'reading_date')
    def _compute_previous_reading(self):
        for record in self:
            if record.vehicle_id and record.reading_date:
                previous = self.search([
                    ('vehicle_id', '=', record.vehicle_id.id),
                    ('reading_date', '<', record.reading_date),
                    ('id', '!=', record.id)
                ], order='reading_date desc', limit=1)
                record.previous_reading = previous.odometer_reading if previous else 0
            else:
                record.previous_reading = 0

    @api.depends('odometer_reading', 'previous_reading')
    def _compute_distance_traveled(self):
        for record in self:
            if record.odometer_reading and record.previous_reading:
                record.distance_traveled = record.odometer_reading - record.previous_reading
            else:
                record.distance_traveled = 0

    @api.depends('photo_ids')
    def _compute_photo_count(self):
        for record in self:
            record.photo_count = len(record.photo_ids)

    @api.depends('distance_traveled', 'reading_date', 'previous_reading', 'odometer_reading')
    def _compute_is_suspicious(self):
        """Detect suspicious readings"""
        for record in self:
            warnings = []
            is_suspicious = False

            # Check for negative distance
            if record.distance_traveled < 0:
                warnings.append("Odometer reading is less than previous reading!")
                is_suspicious = True

            # Check for unrealistic distance in short time
            if record.vehicle_id and record.reading_date and record.previous_reading:
                previous_reading_rec = self.search([
                    ('vehicle_id', '=', record.vehicle_id.id),
                    ('reading_date', '<', record.reading_date),
                    ('id', '!=', record.id)
                ], order='reading_date desc', limit=1)

                if previous_reading_rec:
                    time_diff = (record.reading_date - previous_reading_rec.reading_date).total_seconds() / 3600  # hours
                    if time_diff > 0:
                        speed = record.distance_traveled / time_diff
                        if speed > 150:  # Average speed > 150 km/h
                            warnings.append(f"Unrealistic average speed: {speed:.1f} km/h")
                            is_suspicious = True

            # Check for zero movement over long period
            if record.distance_traveled == 0 and record.previous_reading > 0:
                warnings.append("No distance traveled since last reading")

            record.is_suspicious = is_suspicious
            record.warning_message = '\n'.join(warnings) if warnings else False

    def action_verify(self):
        """Verify the reading"""
        self.write({
            'verified': True,
            'verified_by_id': self.env.user.id,
            'verification_date': fields.Date.today()
        })

    def action_view_photos(self):
        """View reading photos"""
        return {
            'name': 'Reading Photos',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.photo_ids.ids)],
            'context': {'default_res_model': self._name, 'default_res_id': self.id}
        }

    @api.constrains('odometer_reading')
    def _check_odometer_reading(self):
        for record in self:
            if record.odometer_reading < 0:
                raise ValidationError("Odometer reading cannot be negative.")

            # Check against previous reading
            if record.previous_reading and record.odometer_reading < record.previous_reading:
                if not self.env.user.has_group('enhanced_fleet_management.group_fleet_manager'):
                    raise ValidationError(
                        f"Odometer reading ({record.odometer_reading} km) is less than "
                        f"previous reading ({record.previous_reading} km). "
                        "Only fleet managers can override this validation."
                    )

    @api.constrains('fuel_percentage')
    def _check_fuel_percentage(self):
        for record in self:
            if record.fuel_percentage and (record.fuel_percentage < 0 or record.fuel_percentage > 100):
                raise ValidationError("Fuel percentage must be between 0 and 100.")
