# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author:Anjhana A K(<https://www.cybrosys.com>)
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
"""model for inspection requests """
from datetime import timedelta
from odoo import api, fields, models


class InspectionRequests(models.Model):
    """create inspection requests"""
    _name = 'inspection.request'
    _description = 'Inspection Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(readonly=True, store=True,
                       help='Inspection Request name',
                       string='Inspection Request name')
    inspection_id = fields.Many2one('vehicle.inspection',
                                    required=True,
                                    help='Select Vehicle Inspection',
                                    string='Select Vehicle Inspection')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',
                                 help='Select Vehicle for inspection')
    vehicle_model_id = fields.Many2one('fleet.vehicle.model',
                                       string='Model',
                                       related="vehicle_id.model_id",
                                       readonly=False,
                                       store=True, help='Vehicle model')
    license_plate = fields.Char(string='License Plate',
                                related="vehicle_id.license_plate", store=True,
                                readonly=False, help='vehicle license plate')
    date_create = fields.Date(string='Inspection Create Date',
                              help='Inspection Create Date',
                              default=lambda self: fields.Date.today())
    inspection_date = fields.Date(string='Inspection Date',
                                  help='Vehicle inspection date',
                                  default=lambda self: fields.Date.today())
    inspection_end_date = fields.Date(
        string='Inspection End Date',
        compute='_compute_inspection_end_date',
        store=True,
    )
    user_id = fields.Many2one('res.users',
                              string='Inspection Supervisor',
                              related='inspection_id.user_id', readonly=False,
                              store=True, help='Inspection supervisor')
    company_id = fields.Many2one('res.company', string='Company',
                                 help='Company',
                                 default=lambda self: self.env.company)
    image_128 = fields.Image(related='vehicle_model_id.image_128',
                             help='Vehicle Image', string='Image')
    inspection_result = fields.Char(string='Inspection Result',
                                    help='Vehicle inspection result')
    internal_note = fields.Html(string='Internal Note', help='Internal note')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('new', 'New'),
         ('inspection_started', 'Inspection Started'),
         ('inspection_finished', 'Inspection Finished'), ],
        default='draft', copy=False, required=True, tracking=True,
        help='Status of Inspection', string='Status of Inspection')
    inspection_image_ids = fields.One2many('inspection.images',
                                           'inspection_id',
                                           help='Add Inspection Images',
                                           string='Add Inspection Images')
    inspection_line_reference = fields.Integer(string='Inspection Reference',
                                               help='Inspection Line')
    service_reference = fields.Integer(string='Service Reference',
                                       help='Service Reference')
    service_active = fields.Boolean('Service active', default=False,
                                    help='Active Service smart button',
                                    compute='_compute_service_active')
    fleet_active = fields.Boolean('Service active', default=False,
                                  help='Active Service smart button',
                                  compute='_compute_fleet_active')
    YES_NO_SELECTION = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    # exterior
    exterior_visible_damage_check = fields.Selection(YES_NO_SELECTION,
                                                     string='Is the vehicle exterior free of visible damage?')
    exterior_four_tyres_inflated_check = fields.Selection(YES_NO_SELECTION,
                                                          string='Do all four tyres look to be properly inflated?')
    exterior_fluid_leakage_check = fields.Selection(YES_NO_SELECTION,
                                                    string='Are there any signs of fluid leakage underneath vehicle?')
    exterior_clean_appearance_check = fields.Selection(YES_NO_SELECTION, string='Is the vehicle clean in appearance?')
    exterior_four_tyres_inflated_gauge_check = fields.Selection(YES_NO_SELECTION,
                                                                string='Are all four tyres inflated by gauge? PSI?')
    exterior_tread_depth_check = fields.Selection(YES_NO_SELECTION,
                                                  string='Is tyre tread depth & tread wearing acceptable?')
    exterior_wiper_blades_check = fields.Selection(YES_NO_SELECTION, string='Are wiper blades adequate?')

    # Interior
    interior_clean_check = fields.Selection(YES_NO_SELECTION, string="Is the vehicle's interior clean of debris?")
    interior_visible_damage_check = fields.Selection(YES_NO_SELECTION,
                                                     string='Is the interior of the vehicle free of visible damage?')
    interior_safety_belts_check = fields.Selection(YES_NO_SELECTION, string='Are safety belts working properly?')
    interior_first_aid_kit_check = fields.Selection(YES_NO_SELECTION, string='Is a first aid kit available?')
    interior_emergency_kit_check = fields.Selection(YES_NO_SELECTION, string='Is the emergency kit available?')
    interior_registration_accessible_check = fields.Selection(YES_NO_SELECTION,
                                                              string='Is the vehicle registration easily accessible?')
    interior_insurance_accessible_check = fields.Selection(YES_NO_SELECTION,
                                                           string='Is the vehicle insurance information accessible?')
    interior_spare_tyre_check = fields.Selection(YES_NO_SELECTION, string='Is spare tyre available & inflated?')
    interior_jack_system_check = fields.Selection(YES_NO_SELECTION, string='Is jack system available?')
    interior_owner_manual_check = fields.Selection(YES_NO_SELECTION, string="Is owner's manual available?")
    interior_accident_kit_check = fields.Selection(YES_NO_SELECTION, string="Is accident kit available?")

    # operating
    operating_headlights_check = fields.Selection(YES_NO_SELECTION, string='Are the head lights working?')
    operating_taillights_check = fields.Selection(YES_NO_SELECTION, string='Are the tail lights working?')
    operating_brake_lights_check = fields.Selection(YES_NO_SELECTION, string='Are the brake lights working?')
    operating_backup_lights_check = fields.Selection(YES_NO_SELECTION, string='Are the backup lights working?')
    operating_interior_lights_check = fields.Selection(YES_NO_SELECTION, string='Are the interior lights working?')
    operating_windscreen_wipers_check = fields.Selection(YES_NO_SELECTION, string='Are the windscreen wipers working?')
    operating_horn_check = fields.Selection(YES_NO_SELECTION, string='Is the horn working?')
    operating_mirrors_check = fields.Selection(YES_NO_SELECTION,
                                               string='Are the proper mirrors available? (rear, side, instructor)')
    operating_parking_brake_check = fields.Selection(YES_NO_SELECTION, string='Is the parking brake working?')
    operating_turn_signals_check = fields.Selection(YES_NO_SELECTION, string='Are the turn signals working?')
    operating_sun_visor_check = fields.Selection(YES_NO_SELECTION, string='Is the sun visor operable?')
    operating_heating_cooling_check = fields.Selection(YES_NO_SELECTION,
                                                       string='Does the heating/cooling system work properly?')
    operating_fuel_tank_check = fields.Selection(YES_NO_SELECTION, string='Is the fuel tank at least 1/2 full?')

    # under-hood
    underhood_engine_oil_check = fields.Selection(YES_NO_SELECTION, string='Is the engine oil within range?')
    underhood_windshield_fluid_check = fields.Selection(YES_NO_SELECTION,
                                                        string='Is the windshield wiper fluid within range?')
    underhood_power_steering_fluid_check = fields.Selection(YES_NO_SELECTION,
                                                            string='Is the power steering fluid within range?')
    underhood_transmission_fluid_check = fields.Selection(YES_NO_SELECTION,
                                                          string='Is the transmission fluid within range & a reddish colour?')
    underhood_brake_fluid_check = fields.Selection(YES_NO_SELECTION, string='Is the brake fluid within proper levels?')
    underhood_coolant_level_check = fields.Selection(YES_NO_SELECTION, string='Is coolant within proper levels?')
    underhood_belt_condition_check = fields.Selection(YES_NO_SELECTION, string='Do all belts appear in good condition?')

    # post-trip
    posttrip_vehicle_operate_check = fields.Selection(YES_NO_SELECTION, string='Did vehicle operate correctly?')
    posttrip_warning_lights_check = fields.Selection(YES_NO_SELECTION,
                                                     string='Was the vehicle free of warning lights coming on during operation?')
    posttrip_warning_light_display_check = fields.Selection(YES_NO_SELECTION, string='Did any warning lights display?')

    @api.model
    def create(self, vals):
        """generate vehicle inspection sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'inspection.request') or 'New'
        result = super(InspectionRequests, self, ).create(vals)
        return result

    @api.depends('service_active')
    def _compute_service_active(self):
        """To set service active value """
        service_count = self.env['fleet.service.inspection'].search_count([
            ('inspection_reference', '=', self.id)])
        if service_count != 0:
            self.service_active = True
        else:
            self.service_active = False

    @api.depends('fleet_active')
    def _compute_fleet_active(self):
        """To set fleet active value"""
        if self.vehicle_id:
            self.fleet_active = True
        else:
            self.fleet_active = False

    @api.depends('inspection_date')
    def _compute_inspection_end_date(self):
        """Mirror inspection_date for calendar date_stop."""
        for rec in self:
            rec.inspection_end_date = rec.inspection_date

    def action_confirm_inspection(self):
        """button to confirm inspection request"""
        self.write({'state': 'new'})
        inspection_request_line = self.env['inspection.request.line'].search([
            ('inspection_request_reference', '=', self.id)
        ])
        if not inspection_request_line:
            self.env['inspection.request.line'].create({
                'fleet_vehicle_id': self.vehicle_id.id,
                'description': self.inspection_id.name,
                'inspection_id': self.inspection_id.id,
                'inspection_period': self.inspection_id.inspection_period,
                'reminder_notification':
                    self.inspection_id.reminder_notification_days,
                'user_id': self.user_id,
                'next_inspection_date': self.inspection_date,
            })

    def action_print_report(self):
        """ print pdf report"""
        images = []
        for rec in self.inspection_image_ids:
            images.append(rec.image)
        inspection_request = self.env['inspection.request'].search([
            ('name', '=', self.name)
        ])
        data = {
            'logo': self.vehicle_id.model_id.image_128,
            'vehicle_model_id': self.vehicle_id.model_id.name,
            'records': self.read(),
            'license_plate': self.vehicle_id.license_plate,
            'user_id': inspection_request.user_id.name,
            'images': images,
        }
        return self.env.ref(
            'fleet_vehicle_inspection_management.action_report_vehicle_inspection').report_action(
            self, data=data)

    def action_start_inspection(self):
        """button to  start vehicle inspection"""
        self.write({'state': 'inspection_started'})

    def action_finish_inspection(self):
        """button to make inspection finished"""
        self.write({'state': 'inspection_finished'})

    def action_create_service(self):
        """opens wizard to create service"""
        self.ensure_one()
        wizard = self.env['fleet.service.inspection'].browse(
            self.service_reference
        ).exists()
        if not wizard:
            wizard = self.env['fleet.service.inspection'].create({
                'inspection_reference': self.id,
                'vehicle_id': self.vehicle_id.id,
                'odometer': self.vehicle_id.odometer,
            })
            self.service_reference = wizard.id
        action = self.env.ref(
            'fleet_vehicle_inspection_management.fleet_service_inspection_action'
        ).read()[0]
        action.update({
            'res_id': wizard.id,
            'context': {
                'default_inspection_reference': self.id,
                'default_vehicle_id': self.vehicle_id.id,
                'default_odometer': self.vehicle_id.odometer,
            },
        })
        return action

    def action_create_inspection_request(self):
        """automatically create inspection request and send reminder email"""

        vehicle_inspection_lines = self.env['inspection.request.line'].search(
            [])
        for lines in vehicle_inspection_lines:
            reminder_day = lines.next_inspection_date - timedelta(
                days=lines.reminder_notification)
            if reminder_day == fields.Date.today():
                inspection_line_id = self.env['inspection.request'].search([
                    ('inspection_line_reference', '=', lines.id)])
                if not inspection_line_id:
                    create_id = self.env['inspection.request'].create({
                        'inspection_id': lines.inspection_id.id,
                        'inspection_line_reference': lines.id,
                        'vehicle_id': lines.fleet_vehicle_id.id,
                        'vehicle_model_id': lines.fleet_vehicle_id.model_id.id,
                        'license_plate': lines.fleet_vehicle_id.license_plate,
                        'date_create': lines.create_date,
                        'inspection_date': lines.next_inspection_date,
                        'user_id': lines.user_id.id,
                        'company_id': self.env.company.id,
                        'image_128': lines.fleet_vehicle_id.model_id.image_128,
                    })
                    create_id.write({'state': 'new'})
                    lines.inspection_request_reference = create_id.id
                    next_inspection = lines.next_inspection_date + timedelta(
                        days=lines.inspection_period)
                    lines.last_inspection_date = lines.next_inspection_date
                    lines.next_inspection_date = next_inspection
                    mail_template_id = self.env.ref(
                        'fleet_vehicle_inspection_management.vehicle_inspection_reminder_email_template')
                    mail_template_id.send_mail(create_id.id)

    def get_vehicle_service(self):
        """vehicle service smart button"""
        service_id = self.env['fleet.service.inspection'].search([
            ('inspection_reference', '=', self.id)])
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Service log',
            'view_mode': 'list,form',
            'context': {'create': False},
            'res_model': 'vehicle.service.log',
            'domain': [('service_reference', '=', service_id.id)],
        }

    def get_fleet_vehicle(self):
        """fleet vehicle smart button"""

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fleet Vehicle',
            'view_mode': 'list,form',
            'res_model': 'fleet.vehicle',
            'domain': [('id', '=', self.vehicle_id.id)],
        }
