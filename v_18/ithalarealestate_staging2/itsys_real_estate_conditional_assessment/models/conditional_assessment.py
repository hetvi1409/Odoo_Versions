# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models
import datetime
from odoo.tools.translate import _
import calendar
from odoo.exceptions import UserError, AccessError
from datetime import time, datetime, date,timedelta

class ConditionalAssessment(models.Model):
    _name = "conditional.assessment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'property_id'

    property_id = fields.Many2one("building")
    partner_id = fields.Many2one("res.partner",related="property_id.partner_id")
    address = fields.Char(related="property_id.address")
    contact_person_id = fields.Many2one("res.partner")
    reason = fields.Many2one("reason.inspection")
    grade = fields.Many2one("building.grading")
    responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    items_to_repair = fields.Text()

    external_walls_grade = fields.Many2one("building.grading")
    external_walls_grade_name = fields.Char(related="external_walls_grade.name")
    total_points = fields.Integer(string="Total Points", compute="_compute_total_points", store=True)
    average_score = fields.Integer(string="Average Grade Point", store=True,compute='_compute_average_score')
    average_grade = fields.Char(string="Average Grade", store=True,compute='_compute_average_score')
    avg_score_lift = fields.Float(string="Average Lift Score", compute="_compute_average_score", store=True)
    avg_grade_lift = fields.Char(string="Average Lift Grade", compute="_compute_average_score", store=True)
    avg_score_security = fields.Float(string="Security Management Score", compute="_compute_average_score", store=True)
    avg_grade_security = fields.Char(string="Security Management Grade", compute="_compute_average_score", store=True)
    avg_score_hv = fields.Integer(string="Security Management Grade", compute="_compute_average_score", store=True)
    avg_grade_hv = fields.Char(string="Security Management Grade", compute="_compute_average_score", store=True)
    avg_score_lv = fields.Integer(string="Security Management Grade", compute="_compute_average_score", store=True)
    avg_grade_lv = fields.Char(string="Security Management Grade", compute="_compute_average_score", store=True)
    avg_score_units = fields.Integer(string="Power Supply Score", compute="_compute_average_score", store=True)
    avg_grade_units = fields.Char(string="Power Supply Grade", compute="_compute_average_score", store=True)
    avg_score_air_conditioning = fields.Integer(string="Air Conditioning Score", compute="_compute_average_score", store=True)
    avg_grade_air_conditioning = fields.Char(string="Air Conditioning Grade", compute="_compute_average_score", store=True)
    avg_score_water = fields.Integer(string="Water Reticulation Score", compute="_compute_average_score", store=True)
    avg_grade_water = fields.Char(string="Water Reticulation Grade", compute="_compute_average_score", store=True)
    avg_score_mechanical = fields.Integer(string="Mechanical Score", compute="_compute_average_score", store=True)
    avg_grade_mechanical = fields.Char(string="Mechanical Grade", compute="_compute_average_score", store=True)
    avg_score_canteen = fields.Integer(string="Canteen Score", compute="_compute_average_score", store=True)
    avg_grade_canteen = fields.Char(string="Canteen Grade", compute="_compute_average_score", store=True)
    avg_score_premises = fields.Integer(string="Premises Score", compute="_compute_average_score", store=True)
    avg_grade_premises = fields.Char(string="Premises Grade", compute="_compute_average_score", store=True)
    avg_score_landscaping = fields.Integer(string="Landscaping Score", compute="_compute_average_score", store=True)
    avg_grade_landscaping = fields.Char(string="LandscapingGrade", compute="_compute_average_score", store=True)
    avg_score_signage_media = fields.Integer(string="Building Signage Score", compute="_compute_average_score", store=True)
    avg_grade_signage_media = fields.Char(string="Building Signage", compute="_compute_average_score", store=True)
    avg_score_drainage = fields.Integer(string="Sewage and Drainage Score", compute="_compute_average_score", store=True)
    avg_grade_drainage = fields.Char(string="Sewage and Drainage  Signage", compute="_compute_average_score", store=True)
    avg_score_toilets = fields.Integer(string="Toilets Score", compute="_compute_average_score",store=True)
    avg_grade_toilets = fields.Char(string="Toilets Grade", compute="_compute_average_score",
                                     store=True)
    avg_score_designated_fuel = fields.Integer(string="Designated Fuel Score", compute="_compute_average_score", store=True)
    avg_grade_designated_fuel = fields.Char(string="Designated Fuel Grade", compute="_compute_average_score",
                                    store=True)
    avg_score_safety_equipment = fields.Integer(string="Safety Equipment Score", compute="_compute_average_score",
                                               store=True)
    avg_grade_safety_equipment = fields.Char(string="Safety Equipment Grade", compute="_compute_average_score",
                                            store=True)
    avg_score_perimeter = fields.Integer(string="Perimeter Score", compute="_compute_average_score",
                                               store=True)
    avg_grade_perimeter = fields.Char(string="Perimeter Grade", compute="_compute_average_score",
                                            store=True)
    avg_score_internal = fields.Integer(string="Internal Score", compute="_compute_average_score",
                                         store=True)
    avg_grade_internal = fields.Char(string="Internal Grade", compute="_compute_average_score",
                                      store=True)

    external_walls_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    # external_walls_responsible_person_type_name = fields.Char(related=external_walls_responsible_person_type.name)
    external_walls_responsible_person_type_name = fields.Char(string='Responsible person type name')
    total_average_score = fields.Float(string="Total Average Score", compute="_compute_average_score", store=True)
    total_average_grade = fields.Char(string="Total Average Grade", compute="_compute_average_score", store=True)

    external_walls_items_to_repair = fields.Text()

    external_doors_grade = fields.Many2one("building.grading")
    external_doors_grade_name =  fields.Char(related='external_doors_grade.name')

    external_doors_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    external_doors_items_to_repair = fields.Text()

    windows_grade = fields.Many2one("building.grading")
    windows_grade_name = fields.Char(related='windows_grade.name')
    windows_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                       'Responsible person', default='tenant')
    windows_items_to_repair = fields.Text()

    roof_grade = fields.Many2one("building.grading")
    roof_grade_name = fields.Char(related='roof_grade.name')
    roof_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                    'Responsible person', default='tenant')
    roof_items_to_repair = fields.Text()

    entrance_foyer_grade = fields.Many2one("building.grading")
    entrance_foyer_grade_name = fields.Char(related='entrance_foyer_grade.name')
    entrance_foyer_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    entrance_foyer_items_to_repair = fields.Text()

    floors_grade = fields.Many2one("building.grading")
    floors_grade_name = fields.Char(related='floors_grade.name')
    floors_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                      'Responsible person', default='tenant')
    floors_items_to_repair = fields.Text()

    ceilings_grade = fields.Many2one("building.grading")
    ceilings_grade_name = fields.Char(related='ceilings_grade.name')
    ceilings_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                        'Responsible person', default='tenant')
    ceilings_items_to_repair = fields.Text()

    internal_doors_grade = fields.Many2one("building.grading")
    internal_doors_grade_name = fields.Char(related='internal_doors_grade.name')
    internal_doors_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    internal_doors_items_to_repair = fields.Text()

    internal_walls_grade = fields.Many2one("building.grading")
    internal_walls_grade_name = fields.Char(related='internal_walls_grade.name')
    internal_walls_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    internal_walls_items_to_repair = fields.Text()

    blinds_grade = fields.Many2one("building.grading")
    blinds_grade_name = fields.Char(related="blinds_grade.name")
    blinds_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                      'Responsible person', default='tenant')
    blinds_items_to_repair = fields.Text()

    lifts_grade = fields.Many2one("building.grading")
    lifts_grade_name = fields.Char(related="lifts_grade.name")
    lifts_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                     'Responsible person', default='tenant')
    lifts_items_to_repair = fields.Text()

    wheelchair_lift_grade = fields.Many2one("building.grading")
    wheelchair_lift_grade_name = fields.Char(related='wheelchair_lift_grade.name')
    wheelchair_lift_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                               'Responsible person', default='tenant')
    wheelchair_lift_items_to_repair = fields.Text()

    lifting_docks_grade = fields.Many2one("building.grading")
    lifting_docks_grade_name = fields.Char(related="lifting_docks_grade.name")
    lifting_docks_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                             'Responsible person', default='tenant')
    lifting_docks_items_to_repair = fields.Text()

    guard_house_grade = fields.Many2one("building.grading")
    guard_house_grade_name = fields.Char(related="guard_house_grade.name")
    guard_house_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                           'Responsible person', default='tenant')
    guard_house_items_to_repair = fields.Text()

    cctv_grade = fields.Many2one("building.grading")
    cctv_grade_name = fields.Char(related="cctv_grade.name")
    cctv_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                    'Responsible person', default='tenant')
    cctv_items_to_repair = fields.Text()

    access_control_grade = fields.Many2one("building.grading")
    access_control_grade_name = fields.Char(related="access_control_grade.name")
    access_control_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    access_control_items_to_repair = fields.Text()

    booms_barriers_grade = fields.Many2one("building.grading")
    booms_barriers_grade_name = fields.Char(related='booms_barriers_grade.name')
    booms_barriers_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    booms_barriers_items_to_repair = fields.Text()

    electrical_fence_grade = fields.Many2one("building.grading")
    electrical_fence_grade_name = fields.Char(related='electrical_fence_grade.name')
    electrical_fence_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                'Responsible person', default='tenant')
    electrical_fence_items_to_repair = fields.Text()

    security_gates_grade = fields.Many2one("building.grading")
    security_gates_grade_name = fields.Char(related='security_gates_grade.name')
    security_gates_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    security_gates_items_to_repair = fields.Text()

    fencing_grade = fields.Many2one("building.grading")
    fencing_grade_name = fields.Char(related='fencing_grade.name')
    fencing_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                       'Responsible person', default='tenant')
    fencing_items_to_repair = fields.Text()

    sub_station_grade = fields.Many2one("building.grading")
    sub_station_grade_name = fields.Char(related="sub_station_grade.name")
    sub_station_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                           'Responsible person', default='tenant')
    sub_station_items_to_repair = fields.Text()

    transformer_grade = fields.Many2one("building.grading")
    transformer_grade_name = fields.Char(related="transformer_grade.name")
    transformer_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                           'Responsible person', default='tenant')
    transformer_items_to_repair = fields.Text()

    high_voltage_grade = fields.Many2one("building.grading")
    high_voltage_grade_name = fields.Char(related="high_voltage_grade.name")
    high_voltage_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                            'Responsible person', default='tenant')
    high_voltage_items_to_repair = fields.Text()

    low_voltage_grade = fields.Many2one("building.grading")
    low_voltage_grade_name = fields.Char(related="high_voltage_grade.name")
    low_voltage_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                           'Responsible person', default='tenant')
    low_voltage_items_to_repair = fields.Text()

    electrical_db_grade = fields.Many2one("building.grading")
    electrical_db_grade_name = fields.Char(related="electrical_db_grade.name")
    electrical_db_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                             'Responsible person', default='tenant')
    electrical_db_items_to_repair = fields.Text()

    plug_points_grade = fields.Many2one("building.grading")
    plug_points_grade_name = fields.Char(related="plug_points_grade.name")
    plug_points_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                           'Responsible person', default='tenant')
    plug_points_items_to_repair = fields.Text()

    lighting_grade = fields.Many2one("building.grading")
    lighting_grade_name = fields.Char(related="lighting_grade.name")
    lighting_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                        'Responsible person', default='tenant')
    lighting_items_to_repair = fields.Text()

    electrical_meter_grade = fields.Many2one("building.grading")
    electrical_meter_grade_name = fields.Char(related="electrical_meter_grade.name")
    electrical_meter_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                'Responsible person', default='tenant')
    electrical_meter_items_to_repair = fields.Text()

    illegal_connections_grade = fields.Many2one("building.grading")
    illegal_connections_grade_name = fields.Char(related="illegal_connections_grade.name")
    illegal_connections_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')])
    illegal_connections_items_to_repair = fields.Text()

    power_supply_units_inverters_grade = fields.Many2one("building.grading")
    power_supply_units_inverters_grade_name = fields.Char(related="power_supply_units_inverters_grade.name")
    power_supply_units_inverters_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    power_supply_units_inverters_items_to_repair = fields.Text()

    standby_generator_grade = fields.Many2one("building.grading")
    standby_generator_grade_name = fields.Char(related="standby_generator_grade.name")
    standby_generator_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                 'Responsible person', default='tenant')
    standby_generator_items_to_repair = fields.Text()

    air_conditioning_split_units_grade = fields.Many2one("building.grading")
    air_conditioning_split_units_grade_name = fields.Char(related="air_conditioning_split_units_grade.name")
    air_conditioning_split_units_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    air_conditioning_split_units_items_to_repair = fields.Text()

    air_conditioning_wall_units_grade = fields.Many2one("building.grading")
    air_conditioning_wall_units_grade_name = fields.Char(related="air_conditioning_wall_units_grade.name")
    air_conditioning_wall_units_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    air_conditioning_wall_units_items_to_repair = fields.Text()

    extraction_systems_grade = fields.Many2one("building.grading")
    extraction_systems_grade_name = fields.Char(related="extraction_systems_grade.name")
    extraction_systems_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                  'Responsible person', default='tenant')
    extraction_systems_items_to_repair = fields.Text()

    water_reticulation_pipes_entering_building_grade = fields.Many2one("building.grading")
    water_reticulation_pipes_entering_building_grade_name = fields.Char(related="water_reticulation_pipes_entering_building_grade.name")
    # water_reticulation_pipes_entering_building_responsible_person_type = fields.Selection(
    #     [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    water_reticulation_pipes_entering_building_items_to_repair = fields.Text()

    water_tank_grade = fields.Many2one("building.grading")
    water_tank_grade_name = fields.Char(related='water_tank_grade.name')
    water_tank_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                          'Responsible person', default='tenant')
    water_tank_items_to_repair = fields.Text()

    water_meter_grade = fields.Many2one("building.grading")
    water_meter_grade_name = fields.Char(related='water_meter_grade.name')
    water_meter_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                           'Responsible person', default='tenant')
    water_meter_items_to_repair = fields.Text()

    illegal_connections_water_grade = fields.Many2one("building.grading")
    illegal_connections_water_grade_name = fields.Char(related='illegal_connections_water_grade.name')
    illegal_connections_water_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                   'Responsible person', default='tenant')
    illegal_connections_water_items_to_repair = fields.Text()

    mechanical_boiler_grade = fields.Many2one("building.grading")
    mechanical_boiler_grade_name = fields.Char(related='mechanical_boiler_grade.name')
    mechanical_boiler_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                 'Responsible person', default='tenant')
    mechanical_boiler_items_to_repair = fields.Text()

    water_pumps_grade = fields.Many2one("building.grading")
    water_pumps_grade_name = fields.Char(related='water_pumps_grade.name')
    water_pumps_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                           'Responsible person', default='tenant')
    water_pumps_items_to_repair = fields.Text()

    canteen_equipment_stoves_ovens_grade = fields.Many2one("building.grading")
    canteen_equipment_stoves_ovens_grade_name = fields.Char(related='canteen_equipment_stoves_ovens_grade.name')
    canteen_equipment_stoves_ovens_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    canteen_equipment_stoves_ovens_items_to_repair = fields.Text()

    canopies_extraction_systems_grade = fields.Many2one("building.grading")
    canopies_extraction_systems_grade_name = fields.Char(related='canopies_extraction_systems_grade.name')
    canopies_extraction_systems_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    canopies_extraction_systems_items_to_repair = fields.Text()

    cold_rooms_grade = fields.Many2one("building.grading")
    cold_rooms_grade_name = fields.Char(related='cold_rooms_grade.name')
    cold_rooms_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                          'Responsible person', default='tenant')
    cold_rooms_items_to_repair = fields.Text()

    grease_traps_grade = fields.Many2one("building.grading")
    grease_traps_grade_name = fields.Char(related='grease_traps_grade.name')
    grease_traps_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                            'Responsible person', default='tenant')
    grease_traps_items_to_repair = fields.Text()

    premises_parking_areas_grade = fields.Many2one("building.grading")
    premises_parking_areas_grade_name = fields.Char(related='premises_parking_areas_grade.name')
    premises_parking_areas_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                      'Responsible person', default='tenant')
    premises_parking_areas_items_to_repair = fields.Text()

    carports_grade = fields.Many2one("building.grading")
    carports_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                        'Responsible person', default='tenant')
    carports_items_to_repair = fields.Text()

    roads_grade = fields.Many2one("building.grading")
    roads_grade_name = fields.Char(related='roads_grade.name')
    roads_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                     'Responsible person', default='tenant')
    roads_items_to_repair = fields.Text()

    walkways_grade = fields.Many2one("building.grading")
    walkways_grade_name = fields.Char(related="walkways_grade.name")
    walkways_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                        'Responsible person', default='tenant')
    walkways_items_to_repair = fields.Text()

    roadway_markings_grade = fields.Many2one("building.grading")
    roadway_markings_grade_name = fields.Char(related="roadway_markings_grade.name")
    roadway_markings_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                'Responsible person', default='tenant')
    roadway_markings_items_to_repair = fields.Text()

    landscaping_gardens_grade = fields.Many2one("building.grading")
    landscaping_gardens_grade_name = fields.Char(related="landscaping_gardens_grade.name")
    landscaping_gardens_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                   'Responsible person', default='tenant')
    landscaping_gardens_items_to_repair = fields.Text()

    irrigation_systems_grade = fields.Many2one("building.grading")
    irrigation_systems_grade_name = fields.Char(related='irrigation_systems_grade.name')
    irrigation_systems_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                  'Responsible person', default='tenant')
    irrigation_systems_items_to_repair = fields.Text()

    water_features_grade = fields.Many2one("building.grading")
    water_features_grade_name = fields.Char(related="water_features_grade.name")
    water_features_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    water_features_items_to_repair = fields.Text()

    building_signage_media_grade = fields.Many2one("building.grading")
    building_signage_media_grade_name = fields.Char(related="building_signage_media_grade.name")
    building_signage_media_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                      'Responsible person', default='tenant')
    building_signage_media_items_to_repair = fields.Text()

    bill_board_grade = fields.Many2one("building.grading")
    bill_board_grade_name = fields.Char(related="bill_board_grade.name")
    bill_board_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                          'Responsible person', default='tenant')
    bill_board_items_to_repair = fields.Text()

    video_walls_grade = fields.Many2one("building.grading")
    video_walls_grade_name = fields.Char(related="video_walls_grade.name")
    video_walls_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                           'Responsible person', default='tenant')
    video_walls_items_to_repair = fields.Text()

    pole_adds_grade = fields.Many2one("building.grading")
    pole_adds_grade_name = fields.Char(related="pole_adds_grade.name")
    pole_adds_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                         'Responsible person', default='tenant')
    pole_adds_items_to_repair = fields.Text()

    storm_water_drainage_systems_grade = fields.Many2one("building.grading")
    storm_water_drainage_systems_grade_name = fields.Char(related="storm_water_drainage_systems_grade.name")
    storm_water_drainage_systems_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    storm_water_drainage_systems_items_to_repair = fields.Text()

    sewage_systems_grade = fields.Many2one("building.grading")
    sewage_systems_grade_name = fields.Char(related="sewage_systems_grade.name")
    sewage_systems_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    sewage_systems_items_to_repair = fields.Text()

    toilets_hand_wash_basins_grade = fields.Many2one("building.grading")
    toilets_hand_wash_basins_grade_name = fields.Char(related="toilets_hand_wash_basins_grade.name")
    toilets_hand_wash_basins_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    toilets_hand_wash_basins_items_to_repair = fields.Text()

    toilets_grade = fields.Many2one("building.grading")
    toilets_grade_name = fields.Char(related="toilets_grade.name")
    toilets_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                       'Responsible person', default='tenant')
    toilets_items_to_repair = fields.Text()

    urinals_grade = fields.Many2one("building.grading")
    urinals_grade_name = fields.Char(related="urinals_grade.name")
    urinals_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                       'Responsible person', default='tenant')
    urinals_items_to_repair = fields.Text()

    taps_mixers_grade = fields.Many2one("building.grading")
    taps_mixers_grade_name = fields.Char(related="taps_mixers_grade.name")
    taps_mixers_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                           'Responsible person', default='tenant')
    taps_mixers_items_to_repair = fields.Text()

    hand_air_dryers_grade = fields.Many2one("building.grading")
    hand_air_dryers_grade_name = fields.Char(related = "hand_air_dryers_grade.name")
    hand_air_dryers_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                               'Responsible person', default='tenant')
    hand_air_dryers_items_to_repair = fields.Text()

    geysers_grade = fields.Many2one("building.grading")
    geysers_grade_name = fields.Char(related="geysers_grade.name")
    geysers_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                       'Responsible person', default='tenant')
    geysers_items_to_repair = fields.Text()

    water_piping_bottle_traps_grade = fields.Many2one("building.grading")
    water_piping_bottle_traps_grade_name = fields.Char(related="water_piping_bottle_traps_grade.name")
    water_piping_bottle_traps_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    water_piping_bottle_traps_items_to_repair = fields.Text()

    toilet_roll_holders_grade = fields.Many2one("building.grading")
    toilet_roll_holders_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                   'Responsible person', default='tenant')
    toilet_roll_holders_items_to_repair = fields.Text()

    soap_dispensers_grade = fields.Many2one("building.grading")
    soap_dispensers_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                               'Responsible person', default='tenant')
    soap_dispensers_items_to_repair = fields.Text()

    mirrors_grade = fields.Many2one("building.grading")
    mirrors_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                       'Responsible person', default='tenant')
    mirrors_items_to_repair = fields.Text()

    kitchens_wash_basins_grade = fields.Many2one("building.grading")
    kitchens_wash_basins_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                    'Responsible person', default='tenant')
    kitchens_wash_basins_items_to_repair = fields.Text()

    kitchens_taps_mixers_grade = fields.Many2one("building.grading")
    kitchens_taps_mixers_grade_name = fields.Char(related="kitchens_taps_mixers_grade.name")
    kitchens_taps_mixers_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                    'Responsible person', default='tenant')
    kitchens_taps_mixers_items_to_repair = fields.Text()

    kitchens_sinks_grade = fields.Many2one("building.grading")
    kitchens_sinks_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    kitchens_sinks_items_to_repair = fields.Text()

    kitchens_geysers_grade = fields.Many2one("building.grading")
    kitchens_geysers_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                'Responsible person', default='tenant')
    kitchens_geysers_items_to_repair = fields.Text()

    hydro_boiler_grade = fields.Many2one("building.grading")
    hydro_boiler_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                            'Responsible person', default='tenant')
    hydro_boiler_items_to_repair = fields.Text()

    water_piping_waste_traps_grade = fields.Many2one("building.grading")
    water_piping_waste_traps_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    water_piping_waste_traps_items_to_repair = fields.Text()

    designated_fuel_storage_area_grade = fields.Many2one("building.grading")
    designated_fuel_storage_area_grade_name = fields.Char(related="designated_fuel_storage_area_grade.name")
    designated_fuel_storage_area_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    designated_fuel_storage_area_items_to_repair = fields.Text()

    identified_fire_hydrants_grade = fields.Many2one("building.grading")
    identified_fire_hydrants_grade_name = fields.Char(related='identified_fire_hydrants_grade.name')
    identified_fire_hydrants_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    identified_fire_hydrants_items_to_repair = fields.Text()

    serviced_fire_hose_reels_grade = fields.Many2one("building.grading")
    serviced_fire_hose_reels_grade_name = fields.Char(related='serviced_fire_hose_reels_grade.name')

    serviced_fire_hose_reels_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    serviced_fire_hose_reels_items_to_repair = fields.Text()
    serviced_fire_extinguishers_grade_name = fields.Char(related="serviced_fire_extinguishers_grade.name")

    serviced_fire_extinguishers_grade = fields.Many2one("building.grading")
    serviced_fire_extinguishers_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    serviced_fire_extinguishers_items_to_repair = fields.Text()

    serviced_fire_sprinkler_system_grade = fields.Many2one("building.grading")
    serviced_fire_sprinkler_system_grade_name = fields.Char(related='serviced_fire_sprinkler_system_grade.name')
    serviced_fire_sprinkler_system_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    serviced_fire_sprinkler_system_items_to_repair = fields.Text()

    functional_fire_doors_grade = fields.Many2one("building.grading")
    functional_fire_doors_grade_name = fields.Char(related='functional_fire_doors_grade.name')
    functional_fire_doors_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                     'Responsible person', default='tenant')
    functional_fire_doors_items_to_repair = fields.Text()

    visible_fire_escape_route_signage_grade = fields.Many2one("building.grading")
    visible_fire_escape_route_signage_grade_name = fields.Char(related="visible_fire_escape_route_signage_grade.name")
    visible_fire_escape_route_signage_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    visible_fire_escape_route_signage_items_to_repair = fields.Text()

    first_aid_equipment_grade = fields.Many2one("building.grading")
    first_aid_equipment_grade_name = fields.Char(related='first_aid_equipment_grade.name')
    first_aid_equipment_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                   'Responsible person', default='tenant')
    first_aid_equipment_items_to_repair = fields.Text()

    first_aid_signage_grade = fields.Many2one("building.grading")
    first_aid_signage_grade_name = fields.Char(related="first_aid_signage_grade.name")
    first_aid_signage_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                 'Responsible person', default='tenant')
    first_aid_signage_items_to_repair = fields.Text()

    first_aid_rooms_grade = fields.Many2one("building.grading")
    first_aid_rooms_grade_name = fields.Char(related='first_aid_rooms_grade.name')
    first_aid_rooms_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                               'Responsible person', default='tenant')
    first_aid_rooms_items_to_repair = fields.Text()

    safety_officers_first_aiders_list_grade = fields.Many2one("building.grading")
    safety_officers_first_aiders_list_grade_name = fields.Char(related="safety_officers_first_aiders_list_grade.name")
    safety_officers_first_aiders_list_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    safety_officers_first_aiders_list_items_to_repair = fields.Text()

    emergency_contact_numbers_grade = fields.Many2one("building.grading")
    emergency_contact_numbers_grade_name = fields.Char(related='emergency_contact_numbers_grade.name')
    emergency_contact_numbers_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    emergency_contact_numbers_items_to_repair = fields.Text()

    visible_hazards_grade = fields.Many2one("building.grading")
    visible_hazards_grade_name = fields.Char(related="visible_hazards_grade.name")
    visible_hazards_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                               'Responsible person', default='tenant')
    visible_hazards_items_to_repair = fields.Text()

    perimeter_fencing_grade = fields.Many2one("building.grading")
    perimeter_fencing_grade_name = fields.Char(related="perimeter_fencing_grade.name")
    perimeter_fencing_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                 'Responsible person', default='tenant')
    perimeter_fencing_items_to_repair = fields.Text()

    informal_street_trading_grade = fields.Many2one("building.grading")
    informal_street_trading_grade_name = fields.Char(related="informal_street_trading_grade.name")
    informal_street_trading_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                       'Responsible person', default='tenant')
    informal_street_trading_items_to_repair = fields.Text()

    internal_grass_grade = fields.Many2one("building.grading")
    internal_grass_grade_name = fields.Char(related="internal_grass_grade.name")
    internal_grass_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    internal_grass_items_to_repair = fields.Text()

    trees_and_shrubs_grade = fields.Many2one("building.grading")
    trees_and_shrubs_grade_name = fields.Char(related="trees_and_shrubs_grade.name")
    trees_and_shrubs_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                'Responsible person', default='tenant')
    trees_and_shrubs_items_to_repair = fields.Text()

    dumping_grade = fields.Many2one("building.grading")
    dumping_grade_name = fields.Char(related="dumping_grade.name")
    dumping_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                       'Responsible person', default='tenant')
    dumping_items_to_repair = fields.Text()


    rubble_dumping_grade = fields.Many2one("building.grading")
    rubble_dumping_grade_name = fields.Char(related="rubble_dumping_grade.name")
    rubble_dumping_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                              'Responsible person', default='tenant')
    rubble_dumping_items_to_repair = fields.Text()

    illegal_structure_occupation_grade = fields.Many2one("building.grading")
    illegal_structure_occupation_grade_name= fields.Char(related="illegal_structure_occupation_grade.name")
    illegal_structure_occupation_responsible_person_type = fields.Selection(
        [('tenant', 'Tenant'), ('landlord', 'Landlord')], 'Responsible person', default='tenant')
    illegal_structure_occupation_items_to_repair = fields.Text()

    boarding_advertisements_grade = fields.Many2one("building.grading")
    boarding_advertisements_grade_name = fields.Char(related="boarding_advertisements_grade.name")
    boarding_advertisements_responsible_person_type = fields.Selection([('tenant', 'Tenant'), ('landlord', 'Landlord')],
                                                                       'Responsible person', default='tenant')
    boarding_advertisements_items_to_repair = fields.Text()

    external_walls_facade_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                string="External Walls / Facade Items",
                                                domain=[('inspection_item', '=', 'external_walls_facade')])
    external_doors_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="External Doors Items",
                                         domain=[('inspection_item', '=', 'external_doors')])
    windows_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Windows Items",
                                  domain=[('inspection_item', '=', 'windows')])
    roof_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Roof Items",
                               domain=[('inspection_item', '=', 'roof')])
    entrance_foyer_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Entrance Foyer Items",
                                         domain=[('inspection_item', '=', 'entrance_foyer')])
    floors_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Floors Items",
                                 domain=[('inspection_item', '=', 'floors')])
    ceilings_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Ceilings Items",
                                   domain=[('inspection_item', '=', 'ceilings')])
    internal_doors_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Internal Doors Items",
                                         domain=[('inspection_item', '=', 'internal_doors')])
    internal_walls_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Internal Walls Items",
                                         domain=[('inspection_item', '=', 'internal_walls')])
    blinds_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Blinds Items",
                                 domain=[('inspection_item', '=', 'blinds')])
    lifts_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Lifts Items",
                                domain=[('inspection_item', '=', 'lifts')])
    wheel_chair_lift_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                           string="Wheel Chair Lift Items",
                                           domain=[('inspection_item', '=', 'wheel_chair_lift')])
    lifting_docks_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Lifting Docks Items",
                                        domain=[('inspection_item', '=', 'lifting_docks')])
    guard_house_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Guard House Items",
                                      domain=[('inspection_item', '=', 'guard_house')])
    cctv_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="CCTV Items",
                               domain=[('inspection_item', '=', 'cctv')])
    access_control_system_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                string="Access Control System Items",
                                                domain=[('inspection_item', '=', 'access_control_system')])
    booms_barriers_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                         string="Booms & Barriers Items",
                                         domain=[('inspection_item', '=', 'booms_barriers')])
    electrical_fence_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                           string="Electrical Fence Items",
                                           domain=[('inspection_item', '=', 'electrical_fence')])
    security_gates_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Security Gates Items",
                                         domain=[('inspection_item', '=', 'security_gates')])
    fencing_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Fencing Items",
                                  domain=[('inspection_item', '=', 'fencing')])
    informal_street_trading_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                  string="Informal Street Trading Items",
                                                  domain=[('inspection_item', '=', 'informal_street_trading')])
    grass_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Grass Items",
                                domain=[('inspection_item', '=', 'grass')])
    trees_shrubs_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Trees and Shrubs Items",
                                       domain=[('inspection_item', '=', 'trees_shrubs')])
    rubble_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Rubble Items",
                                 domain=[('inspection_item', '=', 'rubble')])
    dumping_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Dumping Items",
                                  domain=[('inspection_item', '=', 'dumping')])
    illegal_structure_occupation_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                       string="Illegal Structure / Occupation Items", domain=[
            ('inspection_item', '=', 'illegal_structure_occupation')])
    boarding_advertisements_billboards_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                             string="Boarding / Advertisements / Bill Boards Items",
                                                             domain=[('inspection_item', '=',
                                                                      'boarding_advertisements_billboards')])
    sub_station_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Sub Station Items",
                                      domain=[('inspection_item', '=', 'sub_station')])
    transformer_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Transformer Items",
                                      domain=[('inspection_item', '=', 'transformer')])
    high_voltage_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="High Voltage Items",
                                       domain=[('inspection_item', '=', 'high_voltage')])
    low_voltage_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Low Voltage Items",
                                      domain=[('inspection_item', '=', 'low_voltage')])
    electrical_db_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Electrical DB Items",
                                        domain=[('inspection_item', '=', 'electrical_db')])
    plug_points_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Plug Points Items",
                                      domain=[('inspection_item', '=', 'plug_points')])
    lighting_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Lighting Items",
                                   domain=[('inspection_item', '=', 'lighting')])
    electrical_meter_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                           string="Electrical Meter Items",
                                           domain=[('inspection_item', '=', 'electrical_meter')])
    illegal_connections_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                              string="Illegal Connections Items",
                                              domain=[('inspection_item', '=', 'illegal_connections')])
    power_supply_units_inverters_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                       string="Power Supply Units Inverters Items", domain=[
            ('inspection_item', '=', 'power_supply_units_inverters')])
    standby_generator_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                            string="Standby Generator Items",
                                            domain=[('inspection_item', '=', 'standby_generator')])
    ac_split_units_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="AC Split Units Items",
                                         domain=[('inspection_item', '=', 'ac_split_units')])
    ac_wall_units_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="AC Wall Units Items",
                                        domain=[('inspection_item', '=', 'ac_wall_units')])
    extraction_systems_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                             string="Extraction Systems Items",
                                             domain=[('inspection_item', '=', 'extraction_systems')])
    water_reticulation_pipes_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                   string="Water Reticulation Pipes Items",
                                                   domain=[('inspection_item', '=', 'water_reticulation_pipes')])
    water_tank_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Water Tank Items",
                                     domain=[('inspection_item', '=', 'water_tank')])
    water_meter_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Water Meter Items",
                                      domain=[('inspection_item', '=', 'water_meter')])
    mechanical_boiler_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                            string="Mechanical Boiler Items",
                                            domain=[('inspection_item', '=', 'mechanical_boiler')])
    water_pumps_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Water Pumps Items",
                                      domain=[('inspection_item', '=', 'water_pumps')])
    canteen_equipment_stoves_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                   string="Canteen Equipment Stoves Items",
                                                   domain=[('inspection_item', '=', 'canteen_equipment_stoves')])
    canopies_extraction_systems_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                      string="Canopies & Extraction Systems Items",
                                                      domain=[('inspection_item', '=', 'canopies_extraction_systems')])
    cold_rooms_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Cold Rooms Items",
                                     domain=[('inspection_item', '=', 'cold_rooms')])
    grease_traps_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Grease Traps Items",
                                       domain=[('inspection_item', '=', 'grease_traps')])
    parking_areas_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Parking Areas Items",
                                        domain=[('inspection_item', '=', 'parking_areas')])
    carports_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Carports Items",
                                   domain=[('inspection_item', '=', 'carports')])
    roads_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Roads Items",
                                domain=[('inspection_item', '=', 'roads')])
    walkways_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Walkways Items",
                                   domain=[('inspection_item', '=', 'walkways')])
    roadway_markings_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                           string="Roadway Markings Items",
                                           domain=[('inspection_item', '=', 'roadway_markings')])
    landscaping_gardens_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                              string="Landscaping Gardens Items",
                                              domain=[('inspection_item', '=', 'landscaping_gardens')])
    irrigation_systems_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                             string="Irrigation Systems Items",
                                             domain=[('inspection_item', '=', 'irrigation_systems')])
    water_features_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Water Features Items",
                                         domain=[('inspection_item', '=', 'water_features')])
    building_signage_media_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                 string="Building Signage Media Items",
                                                 domain=[('inspection_item', '=', 'building_signage_media')])
    bill_board_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Bill Board Items",
                                     domain=[('inspection_item', '=', 'bill_board')])
    video_walls_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Video Walls Items",
                                      domain=[('inspection_item', '=', 'video_walls')])
    pole_adds_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Pole Adds Items",
                                    domain=[('inspection_item', '=', 'pole_adds')])
    storm_water_drainage_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                               string="Storm Water Drainage Items",
                                               domain=[('inspection_item', '=', 'storm_water_drainage')])
    sewage_systems_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Sewage Systems Items",
                                         domain=[('inspection_item', '=', 'sewage_systems')])
    hand_wash_basins_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                           string="Hand Wash Basins Items",
                                           domain=[('inspection_item', '=', 'hand_wash_basins')])
    toilets_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Toilets Items",
                                  domain=[('inspection_item', '=', 'toilets')])
    urinals_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Urinals Items",
                                  domain=[('inspection_item', '=', 'urinals')])
    taps_mixers_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Taps & Mixers Items",
                                      domain=[('inspection_item', '=', 'taps_mixers')])
    hand_air_dryers_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                          string="Hand Air Dryers Items",
                                          domain=[('inspection_item', '=', 'hand_air_dryers')])
    geysers_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Geysers Items",
                                  domain=[('inspection_item', '=', 'geysers')])
    water_piping_bottle_traps_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                    string="Water Piping & Bottle Traps Items",
                                                    domain=[('inspection_item', '=', 'water_piping_bottle_traps')])
    toilet_roll_holders_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                              string="Toilet Roll Holders Items",
                                              domain=[('inspection_item', '=', 'toilet_roll_holders')])
    soap_dispensers_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                          string="Soap Dispensers Items",
                                          domain=[('inspection_item', '=', 'soap_dispensers')])
    mirrors_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Mirrors Items",
                                  domain=[('inspection_item', '=', 'mirrors')])
    kitchens_wash_basins_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                               string="Kitchens Wash Basins Items",
                                               domain=[('inspection_item', '=', 'kitchens_wash_basins')])
    kitchens_taps_mixers_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                               string="Kitchens Taps & Mixers Items",
                                               domain=[('inspection_item', '=', 'kitchens_taps_mixers')])
    sinks_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Sinks Items",
                                domain=[('inspection_item', '=', 'sinks')])
    kitchens_geysers_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                           string="Kitchens Geysers Items",
                                           domain=[('inspection_item', '=', 'kitchens_geysers')])
    hydro_boiler_ids = fields.One2many('conditional.assessment.line', 'assessment_id', string="Hydro Boiler Items",
                                       domain=[('inspection_item', '=', 'hydro_boiler')])
    water_piping_waste_traps_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                   string="Water Piping & Waste Traps Items",
                                                   domain=[('inspection_item', '=', 'water_piping_waste_traps')])
    # Add One2many fields for Fire Equipment
    designated_fuel_storage_area_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                       string="Designated Fuel Storage Area Items", domain=[
            ('inspection_item', '=', 'designated_fuel_storage_area')])
    identified_fire_hydrants_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                   string="Identified Fire Hydrants Items",
                                                   domain=[('inspection_item', '=', 'identified_fire_hydrants')])
    serviced_fire_hose_reels_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                   string="Serviced Fire Hose Reels Items",
                                                   domain=[('inspection_item', '=', 'serviced_fire_hose_reels')])
    serviced_fire_extinguishers_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                      string="Serviced Fire Extinguishers Items",
                                                      domain=[('inspection_item', '=', 'serviced_fire_extinguishers')])
    serviced_fire_sprinkler_system_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                         string="Serviced Fire Sprinkler System Items", domain=[
            ('inspection_item', '=', 'serviced_fire_sprinkler_system')])
    functional_fire_doors_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                string="Functional Fire Doors Items",
                                                domain=[('inspection_item', '=', 'functional_fire_doors')])
    visible_fire_escape_route_signage_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                            string="Visible Fire and Escape Route Signage Items",
                                                            domain=[('inspection_item', '=',
                                                                     'visible_fire_escape_route_signage')])
    # Add One2many fields for Health & Safety Equipment
    availability_of_first_aid_equipment_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                              string="Availability of First Aid Equipment Items",
                                                              domain=[('inspection_item', '=',
                                                                       'availability_of_first_aid_equipment')])
    first_aid_signage_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                            string="First Aid Signage Items",
                                            domain=[('inspection_item', '=', 'first_aid_signage')])
    first_aid_rooms_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                          string="First Aid Rooms Items",
                                          domain=[('inspection_item', '=', 'first_aid_rooms')])
    presence_of_serviced_fire_horse_reels_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                          string="Presence of Serviced Fire Hose Reels",
                                          domain=[('inspection_item', '=', 'serviced_fire_hose_reels')])

    safety_officers_first_aiders_list_displayed_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                                      string="Safety Officers and First Aiders List Displayed Items",
                                                                      domain=[('inspection_item', '=',
                                                                               'safety_officers_first_aiders_list_displayed')])
    emergency_contact_numbers_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                    string="Emergency Contact Numbers Items",
                                                    domain=[('inspection_item', '=', 'emergency_contact_numbers')])
    any_other_visible_hazards_ids = fields.One2many('conditional.assessment.line', 'assessment_id',
                                                    string="Any Other Visible Hazards Items",
                                                    domain=[('inspection_item', '=', 'any_other_visible_hazards')])

    @api.depends('external_walls_grade')
    def _compute_total_points(self):
        """Compute total points from selected grades."""
        for record in self:
            grades = [
                record.external_walls_grade.points if record.external_walls_grade else 0,
                record.external_doors_grade.points if record.external_doors_grade else 0,
                record.windows_grade.points if record.windows_grade else 0,
                record.roof_grade.points if record.roof_grade else 0,
            ]
            record.total_points = sum(grades)
    #
    # @api.depends('external_walls_grade')
    # def _compute_total_points(self):
    #     """Compute total points from selected grades."""
    #     for record in self:
    #         grades = [
    #             record.external_walls_grade.points if record.external_walls_grade else 0,
    #             record.external_doors_grade.points if record.external_doors_grade else 0,
    #             record.windows_grade.points if record.windows_grade else 0,
    #             record.roof_grade.points if record.roof_grade else 0,
    #         ]
    #         record.total_points = sum(grades)

    @api.depends(
        'external_walls_grade', 'external_doors_grade', 'windows_grade',
        'roof_grade', 'entrance_foyer_grade', 'floors_grade',
        'ceilings_grade', 'internal_doors_grade', 'internal_walls_grade', 'blinds_grade',
        'lifting_docks_grade', 'wheelchair_lift_grade', 'lifts_grade',
        'guard_house_grade', 'cctv_grade', 'access_control_grade',
        'booms_barriers_grade', 'electrical_fence_grade', 'security_gates_grade', 'fencing_grade',
        'low_voltage_grade', 'high_voltage_grade', 'transformer_grade', 'sub_station_grade',
        'electrical_db_grade', 'plug_points_grade', 'lighting_grade','blinds_ids',
        'electrical_meter_grade', 'illegal_connections_grade',
        'standby_generator_grade', 'power_supply_units_inverters_grade',
        'extraction_systems_grade', 'air_conditioning_wall_units_grade', 'air_conditioning_split_units_grade',
        'illegal_connections_water_grade', 'water_meter_grade', 'water_tank_grade',
        'water_reticulation_pipes_entering_building_grade','internal_walls_ids',
        'mechanical_boiler_grade', 'water_pumps_grade',
        'canteen_equipment_stoves_ovens_grade', 'canopies_extraction_systems_grade',
        'cold_rooms_grade', 'grease_traps_grade',
        'roadway_markings_grade', 'walkways_grade', 'roads_grade', 'carports_grade', 'premises_parking_areas_grade',
        'water_features_grade','irrigation_systems_grade','landscaping_gardens_grade','pole_adds_grade','video_walls_grade',
        'bill_board_grade','building_signage_media_grade','storm_water_drainage_systems_grade','sewage_systems_grade',
        'toilets_hand_wash_basins_grade','toilets_grade','urinals_grade','hand_air_dryers_grade','taps_mixers_grade',
        'toilets_grade','toilets_hand_wash_basins_grade','visible_fire_escape_route_signage_grade','serviced_fire_sprinkler_system_grade',
        'serviced_fire_extinguishers_grade','serviced_fire_hose_reels_grade','identified_fire_hydrants_grade','designated_fuel_storage_area_grade',
        'functional_fire_doors_grade','first_aid_equipment_grade','first_aid_signage_grade','safety_officers_first_aiders_list_grade','visible_hazards_grade','emergency_contact_numbers_grade','first_aid_rooms_grade',
    'perimeter_fencing_grade','informal_street_trading_grade','boarding_advertisements_grade','illegal_structure_occupation_grade','rubble_dumping_grade','trees_and_shrubs_grade','internal_grass_grade'

    )
    def _compute_average_score(self):
        for rec in self:
            # General Score
            general_grades = [
                rec.external_walls_grade.points if rec.external_walls_grade else None,
                rec.external_doors_grade.points if rec.external_doors_grade else None,
                rec.windows_grade.points if rec.windows_grade else None,
                rec.roof_grade.points if rec.roof_grade else None,
                rec.entrance_foyer_grade.points if rec.entrance_foyer_grade else None,
                rec.floors_grade.points if rec.floors_grade else None,
                rec.ceilings_grade.points if rec.ceilings_grade else None,
                rec.internal_doors_grade.points if rec.internal_doors_grade else None,
                rec.internal_walls_grade.points if rec.internal_walls_grade else None,
                rec.blinds_grade.points if rec.blinds_grade else None
            ]
            rec.average_score = self._calculate_average(general_grades)
            rec.average_grade = self._get_grade(rec.average_score)

            # Lifting Score
            lift_grades = [
                rec.lifting_docks_grade.points if rec.lifting_docks_grade else None,
                rec.wheelchair_lift_grade.points if rec.wheelchair_lift_grade else None,
                rec.lifts_grade.points if rec.lifts_grade else None
            ]
            rec.avg_score_lift = self._calculate_average(lift_grades)
            rec.avg_grade_lift = self._get_grade(rec.avg_score_lift)

            # Security Score
            security_grades = [
                rec.guard_house_grade.points if rec.guard_house_grade else None,
                rec.cctv_grade.points if rec.cctv_grade else None,
                rec.access_control_grade.points if rec.access_control_grade else None,
                rec.booms_barriers_grade.points if rec.booms_barriers_grade else None,
                rec.electrical_fence_grade.points if rec.electrical_fence_grade else None,
                rec.security_gates_grade.points if rec.security_gates_grade else None,
                rec.fencing_grade.points if rec.fencing_grade else None
            ]
            rec.avg_score_security = self._calculate_average(security_grades)
            rec.avg_grade_security = self._get_grade(rec.avg_score_security)

            # High Voltage Score
            hv_grades = [
                rec.low_voltage_grade.points if rec.low_voltage_grade else None,
                rec.high_voltage_grade.points if rec.high_voltage_grade else None,
                rec.transformer_grade.points if rec.transformer_grade else None,
                rec.sub_station_grade.points if rec.sub_station_grade else None
            ]
            rec.avg_score_hv = self._calculate_average(hv_grades)
            rec.avg_grade_hv = self._get_grade(rec.avg_score_hv)

            internal_grades = [
                rec.boarding_advertisements_grade.points if rec.boarding_advertisements_grade else None,
                rec.illegal_structure_occupation_grade.points if rec.illegal_structure_occupation_grade else None,
                rec.rubble_dumping_grade.points if rec.rubble_dumping_grade else None,
                rec.trees_and_shrubs_grade.points if rec.trees_and_shrubs_grade else None,
                rec.internal_grass_grade.points if rec.internal_grass_grade else None
            ]

            rec.avg_score_internal = self._calculate_average(internal_grades)
            rec.avg_grade_internal = self._get_grade(rec.avg_score_internal)

            perimeter_grades = [
                rec.perimeter_fencing_grade.points if rec.perimeter_fencing_grade else None,
                rec.informal_street_trading_grade.points if rec.informal_street_trading_grade else None
            ]

            rec.avg_score_perimeter = self._calculate_average(perimeter_grades)
            rec.avg_grade_perimeter = self._get_grade(rec.avg_score_perimeter)

            signage_media_grades = [
                rec.pole_adds_grade.points if rec.pole_adds_grade else None,
                rec.video_walls_grade.points if rec.video_walls_grade else None,
                rec.bill_board_grade.points if rec.bill_board_grade else None,
                rec.building_signage_media_grade.points if rec.building_signage_media_grade else None  # Merged here
            ]
            rec.avg_score_signage_media = self._calculate_average(signage_media_grades)
            rec.avg_grade_signage_media = self._get_grade(rec.avg_score_signage_media)

            # Low Voltage Score
            lv_grades = [
                rec.electrical_db_grade.points if rec.electrical_db_grade else None,
                rec.plug_points_grade.points if rec.plug_points_grade else None,
                rec.lighting_grade.points if rec.lighting_grade else None,
                rec.electrical_meter_grade.points if rec.electrical_meter_grade else None,
                rec.illegal_connections_grade.points if rec.illegal_connections_grade else None
            ]
            rec.avg_score_lv = self._calculate_average(lv_grades)
            rec.avg_grade_lv = self._get_grade(rec.avg_score_lv)

            toilets_grades = [
                rec.toilets_grade.points if rec.toilets_grade else None,
                rec.toilets_hand_wash_basins_grade.points if rec.toilets_hand_wash_basins_grade else None,
                rec.urinals_grade.points if rec.urinals_grade else None,
                rec.hand_air_dryers_grade.points if rec.hand_air_dryers_grade else None,
                rec.taps_mixers_grade.points if rec.taps_mixers_grade else None
            ]
            rec.avg_score_toilets = self._calculate_average(toilets_grades)
            rec.avg_grade_toilets = self._get_grade(rec.avg_score_toilets)

            # Power Supply Units/Inverters Score
            power_units_grades = [
                rec.standby_generator_grade.points if rec.standby_generator_grade else None,
                rec.power_supply_units_inverters_grade.points if rec.power_supply_units_inverters_grade else None
            ]
            rec.avg_score_units = self._calculate_average(power_units_grades)
            rec.avg_grade_units = self._get_grade(rec.avg_score_units)

            premises_grades = [
                rec.roadway_markings_grade.points if rec.roadway_markings_grade else None,
                rec.walkways_grade.points if rec.walkways_grade else None,
                rec.roads_grade.points if rec.roads_grade else None,
                rec.carports_grade.points if rec.carports_grade else None,
                rec.premises_parking_areas_grade.points if rec.premises_parking_areas_grade else None
            ]
            rec.avg_score_premises = self._calculate_average(premises_grades)
            rec.avg_grade_premises = self._get_grade(rec.avg_score_premises)

            # Air Conditioning Score
            air_conditioning_grades = [
                rec.extraction_systems_grade.points if rec.extraction_systems_grade else None,
                rec.air_conditioning_wall_units_grade.points if rec.air_conditioning_wall_units_grade else None,
                rec.air_conditioning_split_units_grade.points if rec.air_conditioning_split_units_grade else None
            ]
            rec.avg_score_air_conditioning = self._calculate_average(air_conditioning_grades)
            rec.avg_grade_air_conditioning = self._get_grade(rec.avg_score_air_conditioning)

            safety_equipment_grades = [
                rec.first_aid_equipment_grade.points if rec.first_aid_equipment_grade else None,
                rec.first_aid_signage_grade.points if rec.first_aid_signage_grade else None,
                rec.safety_officers_first_aiders_list_grade.points if rec.safety_officers_first_aiders_list_grade else None,
                rec.visible_hazards_grade.points if rec.visible_hazards_grade else None,
                rec.emergency_contact_numbers_grade.points if rec.emergency_contact_numbers_grade else None,
                rec.first_aid_rooms_grade.points if rec.first_aid_rooms_grade else None
            ]

            rec.avg_score_safety_equipment = self._calculate_average(safety_equipment_grades)
            rec.avg_grade_safety_equipment = self._get_grade(rec.avg_score_safety_equipment)

            # Water System Score
            water_grades = [
                rec.illegal_connections_water_grade.points if rec.illegal_connections_water_grade else None,
                rec.water_meter_grade.points if rec.water_meter_grade else None,
                rec.water_tank_grade.points if rec.water_tank_grade else None,
                rec.water_reticulation_pipes_entering_building_grade.points if rec.water_reticulation_pipes_entering_building_grade else None
            ]
            rec.avg_score_water = self._calculate_average(water_grades)
            rec.avg_grade_water = self._get_grade(rec.avg_score_water)

            landscaping_grades = [
                rec.water_features_grade.points if rec.water_features_grade else None,
                rec.irrigation_systems_grade.points if rec.irrigation_systems_grade else None,
                rec.landscaping_gardens_grade.points if rec.landscaping_gardens_grade else None
            ]
            rec.avg_score_landscaping = self._calculate_average(landscaping_grades)
            rec.avg_grade_landscaping = self._get_grade(rec.avg_score_landscaping)

            designated_fuel_grades = [
                rec.visible_fire_escape_route_signage_grade.points if rec.visible_fire_escape_route_signage_grade else None,
                rec.serviced_fire_sprinkler_system_grade.points if rec.serviced_fire_sprinkler_system_grade else None,
                rec.serviced_fire_extinguishers_grade.points if rec.serviced_fire_extinguishers_grade else None,
                rec.serviced_fire_hose_reels_grade.points if rec.serviced_fire_hose_reels_grade else None,
                rec.identified_fire_hydrants_grade.points if rec.identified_fire_hydrants_grade else None,
                rec.designated_fuel_storage_area_grade.points if rec.designated_fuel_storage_area_grade else None
            ]
            rec.avg_score_designated_fuel = self._calculate_average(designated_fuel_grades)
            rec.avg_grade_designated_fuel = self._get_grade(rec.avg_score_designated_fuel)

            # Mechanical System Score
            mechanical_grades = [
                rec.mechanical_boiler_grade.points if rec.mechanical_boiler_grade else None,
                rec.water_pumps_grade.points if rec.water_pumps_grade else None
            ]
            rec.avg_score_mechanical = self._calculate_average(mechanical_grades)
            rec.avg_grade_mechanical = self._get_grade(rec.avg_score_mechanical)

            drainage_grades = [
                rec.storm_water_drainage_systems_grade.points if rec.storm_water_drainage_systems_grade else None,
                rec.sewage_systems_grade.points if rec.sewage_systems_grade else None
            ]
            rec.avg_score_drainage = self._calculate_average(drainage_grades)
            rec.avg_grade_drainage = self._get_grade(rec.avg_score_drainage)

            canteen_grades = [
                rec.canteen_equipment_stoves_ovens_grade.points if rec.canteen_equipment_stoves_ovens_grade else None,
                rec.canopies_extraction_systems_grade.points if rec.canopies_extraction_systems_grade else None,
                rec.cold_rooms_grade.points if rec.cold_rooms_grade else None,
                rec.grease_traps_grade.points if rec.grease_traps_grade else None
            ]
            rec.avg_score_canteen = self._calculate_average(canteen_grades)
            rec.avg_grade_canteen = self._get_grade(rec.avg_score_canteen)

            for rec in self:
                # Define all categories in a list
                grade_fields = [
                    "external_walls_grade", "external_doors_grade", "windows_grade", "roof_grade",
                    "entrance_foyer_grade", "floors_grade", "ceilings_grade", "internal_doors_grade",
                    "internal_walls_grade", "blinds_grade", "lifting_docks_grade", "wheelchair_lift_grade",
                    "lifts_grade", "guard_house_grade", "cctv_grade", "access_control_grade",'water_piping_bottle_traps_grade',
                    "booms_barriers_grade", "electrical_fence_grade", "security_gates_grade", "fencing_grade",
                    "low_voltage_grade", "high_voltage_grade", "transformer_grade", "sub_station_grade",
                    "boarding_advertisements_grade", "illegal_structure_occupation_grade", "rubble_dumping_grade",
                    "trees_and_shrubs_grade", "internal_grass_grade", "perimeter_fencing_grade",
                    "informal_street_trading_grade", "pole_adds_grade", "video_walls_grade", "bill_board_grade",
                    "building_signage_media_grade", "electrical_db_grade", "plug_points_grade", "lighting_grade",
                    "electrical_meter_grade", "illegal_connections_grade", "toilets_grade",
                    "toilets_hand_wash_basins_grade", "urinals_grade", "hand_air_dryers_grade",
                    "taps_mixers_grade", "standby_generator_grade", "power_supply_units_inverters_grade",
                    "roadway_markings_grade", "walkways_grade", "roads_grade", "carports_grade",
                    "premises_parking_areas_grade", "extraction_systems_grade",
                    "air_conditioning_wall_units_grade", "air_conditioning_split_units_grade",
                    "first_aid_equipment_grade", "first_aid_signage_grade",
                    "safety_officers_first_aiders_list_grade", "visible_hazards_grade",
                    "emergency_contact_numbers_grade", "first_aid_rooms_grade",
                    "illegal_connections_water_grade", "water_meter_grade", "water_tank_grade",
                    "water_reticulation_pipes_entering_building_grade", "water_features_grade",
                    "irrigation_systems_grade", "landscaping_gardens_grade",
                    "visible_fire_escape_route_signage_grade", "serviced_fire_sprinkler_system_grade",
                    "serviced_fire_extinguishers_grade", "serviced_fire_hose_reels_grade",
                    "identified_fire_hydrants_grade", "designated_fuel_storage_area_grade",
                    "mechanical_boiler_grade", "water_pumps_grade", "storm_water_drainage_systems_grade",
                    "sewage_systems_grade", "canteen_equipment_stoves_ovens_grade",
                    "canopies_extraction_systems_grade", "cold_rooms_grade", "grease_traps_grade"
                ]

                # Extract the points for each grade
                all_grades = [
                    getattr(getattr(rec, field, None), "points", None) for field in grade_fields
                ]

                # Filter out None values
                valid_scores = [score for score in all_grades if score is not None]

                # Compute total average score
                rec.total_average_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

                # Compute total average grade
                rec.total_average_grade = self._get_grade(rec.total_average_score)


    def _calculate_average(self, grades):
        """Helper function to calculate average score, ignoring None values."""
        valid_grades = [float(grade) for grade in grades if grade is not None]
        return sum(valid_grades) / len(valid_grades) if valid_grades else 0.0

    def _get_grade(self, score):
        """Helper function to determine grade based on score."""
        if score >= 4.5:
            return "Excellent"
        elif score >= 3.5:
            return "Good"
        elif score >= 2.5:
            return "Fair"
        elif score >= 1.5:
            return "Bad"
        else:
            return "Priority"

#     for record in self:
    #         record.external_walls_grade_name = grade_mapping.get(record.external_walls_grade_integer, "Unknown")
    #         record.external_doors_name = grade_mapping.get(record.external_walls_grade_integer, "Unknown")

            # elif record.external_walls_grade_integer == 4:
                #     record.external_walls_grade_name = "Good"
                # elif record.external_walls_grade_integer == 3:
                #     record.external_walls_grade_name = "Fair"
                # elif record.external_walls_grade_integer == 2:
                #     record.external_walls_grade_name = "Bad"
                # elif record.external_walls_grade_integer == 1:
                #     record.external_walls_grade_name = "Priority"
                # else:
                #     record.external_walls_grade_name = "Unknown"
        # """Compute average score."""
        # for record in self:
        #     if record.external_walls_grade:
        #         record.average_score = record.total_points  # Since it's a single grade per record
        #     else:
        #         record.average_score = 0
        #

class ReasonInspection(models.Model):
    _name = 'reason.inspection'
    _description = 'Reason Inspection'

    name = fields.Char(string='Reason', required=True)


class BuildingGrading(models.Model):
    _name = 'building.grading'
    _description = 'Building Grading'
    _rec_name = 'points'

    name = fields.Char(string='Name', required=True)
    points = fields.Integer(string="Points", required=True)
    color = fields.Integer(string='Color')

    def _compute_color(self):
        """Compute the color based on the grade"""
        for record in self:
            if record.grade == 'A':
                record.color = 10  # Green
            elif record.grade == 'B':
                record.color = 2  # Yellow
            elif record.grade == 'C':
                record.color = 1  #


class ConditionalAssessmentImages(models.Model):
    _name = "conditional.assessment.line"
    _description = "Conditional Assessment"

    name = fields.Char(string="Image Description")
    image = fields.Binary(string="Image", attachment=True,store=True)
    assessment_id = fields.Many2one('conditional.assessment', string="Conditional Assessment")
    section = fields.Selection([
        ('illegal_connections', 'Illegal Connections'),
        ('boarding_advertisements', 'Boarding Advertisements'),
        # Add other sections here
    ], string="Section")
    inspection_item = fields.Selection([
        ('external_walls_facade', 'External Walls / Facade'),
        ('external_doors', 'External Doors'),
        ('windows', 'Windows'),
        ('roof', 'Roof'),
        ('entrance_foyer', 'Entrance Foyer'),
        ('floors', 'Floors'),
        ('ceilings', 'Ceilings'),
        ('internal_doors', 'Internal Doors'),
        ('internal_walls', 'Internal Walls'),
        ('blinds', 'Blinds'),
        ('lifts', 'Lifts'),
        ('wheel_chair_lift', 'Wheel Chair Lift'),
        ('lifting_docks', 'Lifting Docks'),
        ('guard_house', 'Guard House'),
        ('cctv', 'CCTV'),
        ('access_control_system', 'Access Control System'),
        ('booms_barriers', 'Booms & Barriers'),
        ('electrical_fence', 'Electrical Fence'),
        ('security_gates', 'Security Gates'),
        ('fencing', 'Fencing'),
        ('sub_station', 'Sub Station'),
        ('transformer', 'Transformer'),
        ('high_voltage', 'High Voltage'),
        ('low_voltage', 'Low Voltage'),
        ('electrical_db', 'Electrical DB'),
        ('plug_points', 'Plug Points'),
        ('lighting', 'Lighting'),
        ('electrical_meter', 'Electrical Meter'),
        ('illegal_connections', 'Illegal Connections'),
        ('power_supply_units_inverters', 'Power Supply Units Inverters'),
        ('standby_generator', 'Standby Generator'),
        ('ac_split_units', 'AC Split Units'),
        ('ac_wall_units', 'AC Wall Units'),
        ('extraction_systems', 'Extraction Systems'),
        ('water_reticulation_pipes', 'Water Reticulation Pipes Entering Building'),
        ('water_tank', 'Water Tank'),
        ('water_meter', 'Water Meter'),
        ('mechanical_boiler', 'Mechanical Boiler'),
        ('water_pumps', 'Water Pumps'),
        ('canteen_equipment_stoves', 'Canteen Equipment Stoves & Ovens'),
        ('canopies_extraction_systems', 'Canopies & Extraction Systems'),
        ('cold_rooms', 'Cold Rooms'),
        ('grease_traps', 'Grease Traps'),
        ('parking_areas', 'Parking Areas'),
        ('carports', 'Carports'),
        ('roads', 'Roads'),
        ('walkways', 'Walkways'),
        ('roadway_markings', 'Roadway Markings'),
        ('landscaping_gardens', 'Landscaping Gardens'),
        ('irrigation_systems', 'Irrigation Systems'),
        ('water_features', 'Water Features'),
        ('building_signage_media', 'Building Signage Media'),
        ('bill_board', 'Bill Board'),
        ('video_walls', 'Video Walls'),
        ('pole_adds', 'Pole Adds'),
        ('storm_water_drainage', 'Storm Water Drainage Systems'),
        ('sewage_systems', 'Sewage Systems'),
        ('hand_wash_basins', 'Hand Wash Basins'),
        ('toilets', 'Toilets'),
        ('urinals', 'Urinals'),
        ('taps_mixers', 'Taps & Mixers'),
        ('hand_air_dryers', 'Hand Air Dryers'),
        ('geysers', 'Geysers'),
        ('water_piping_bottle_traps', 'Water Piping & Bottle Traps'),
        ('toilet_roll_holders', 'Toilet Roll Holders'),
        ('soap_dispensers', 'Soap Dispensers'),
        ('mirrors', 'Mirrors'),
        ('kitchens_wash_basins', 'Kitchens Wash Basins'),
        ('kitchens_taps_mixers', 'Taps & Mixers'),
        ('sinks', 'Sinks'),
        ('kitchens_geysers', 'Kitchens Geysers'),
        ('hydro_boiler', 'Hydro Boiler'),
        ('water_piping_waste_traps', 'Water Piping & Waste Traps'),
        ('designated_fuel_storage_area', 'Designated Fuel Storage Area'),
        ('identified_fire_hydrants', 'Identified Fire Hydrants'),
        ('serviced_fire_hose_reels', 'Presence of Serviced Fire Hose Reels'),
        ('serviced_fire_extinguishers', 'Serviced Fire Extinguishers'),
        ('serviced_fire_sprinkler_system', 'Serviced Fire Sprinkler System'),
        ('functional_fire_doors', 'Functional Fire Doors'),
        ('visible_fire_escape_route_signage', 'Visible Fire and Escape Route Signage'),
        # New Health & Safety Equipment Items
        ('availability_of_first_aid_equipment', 'Availability of First Aid Equipment'),
        ('first_aid_signage', 'First Aid Signage'),
        ('first_aid_rooms', 'First Aid Rooms'),
        ('safety_officers_first_aiders_list_displayed', 'Safety Officers and First Aiders List Displayed'),
        ('emergency_contact_numbers', 'Emergency Contact Numbers'),
        ('any_other_visible_hazards', 'Any Other Visible Hazards'),
        ('fencing', 'Fencing'),  # New: Fencing
        ('informal_street_trading', 'Informal Street Trading'),  # New: Informal Street Trading
        ('grass', 'Grass'),  # New: Grass
        ('trees_shrubs', 'Trees and Shrubs'),  # New: Trees and Shrubs
        ('rubble', 'Rubble'),  # New: Rubble
        ('dumping', 'Dumping'),  # New: Dumping
        ('illegal_structure_occupation', 'Illegal Structure / Occupation'),  # New: Illegal Structure / Occupation
        ('boarding_advertisements', 'Boarding / Advertisements / Bill Boards')
    ], string="Inspection Item")
