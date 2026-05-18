# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class FleetAccidentReport(models.Model):
    _name = "fleet.accident.report"
    _description = 'Fleet Accident Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    # --- Insurer Section ---
    insurer = fields.Char(string="Insurer")  # From header
    broker_agent = fields.Char(string="Broker/Agent")  # African Dawn Risk Solutions
    policy = fields.Char(string="Policy")

    # --- Insured Section ---
    insured_name = fields.Char(string="Insured Name")  # City of Johannesburg Metropolitan Municipality
    insured_department = fields.Char(string="Department / Entity")
    insured_region = fields.Char(string="Region/Depot")
    insured_address = fields.Char(string="Insured Address")
    insured_phone = fields.Char(string="Day Phone No")
    insured_email = fields.Char(string="Email Address")

    # --- Vehicle Section ---
    finance_company = fields.Char(string="Finance Company")
    vehicle_make = fields.Char(string="Vehicle Make")
    vehicle_registration = fields.Char(string="Registration No")
    vehicle_value = fields.Float(string="Value")
    vehicle_model_year = fields.Char(string="Model and Year")
    vehicle_purchase_date = fields.Date(string="Date of Purchase")
    vehicle_price_paid = fields.Float(string="Price Paid")
    vehicle_tar = fields.Char(string="Taro")
    vehicle_gross_mass = fields.Float(string="Gross Vehicle Mass")
    vehicle_kilometres = fields.Float(string="Kilometres Completed")
    vehicle_registered_name = fields.Char(string="Registered Owner")

    # --- Damage Section ---
    damage_description = fields.Text(string="Damage to Own Vehicle")
    repair_estimate = fields.Float(string="Estimate Cost for Repairs")
    repairer_details = fields.Char(string="Repairer's Name/Address/Phone")
    inspection_location = fields.Char(string="Inspection Location")

    # --- Driver Section ---
    driver_name = fields.Char(string="Driver Full Name")
    driver_address = fields.Char(string="Driver Address")
    driver_occupation = fields.Char(string="Occupation")
    driver_phone = fields.Char(string="Phone No")
    driver_identity = fields.Char(string="Identity Number")
    driver_license_no = fields.Char(string="Driving Licence No")
    driver_license_date = fields.Date(string="Licence Date")
    driver_license_code = fields.Char(string="Licence Code")
    driver_license_type = fields.Selection([
        ('full', 'Full'),
        ('learner', 'Learner')
    ], string="Licence Type")
    vehicle_usage = fields.Text(string="Purpose of Vehicle Use")
    permission = fields.Boolean(string="Driving with Permission?")
    employed = fields.Boolean(string="Driver in Employ?")
    other_vehicle_owner = fields.Boolean(string="Owns Another Vehicle?")
    other_vehicle_insurer = fields.Char(string="Other Vehicle Insurer")
    other_vehicle_policy = fields.Char(string="Other Vehicle Policy No")
    convictions = fields.Text(string="Convictions for Motoring Offences")
    licence_endorsed = fields.Boolean(string="Licence Endorsed?")
    physical_defects = fields.Text(string="Physical Defects")
    previous_accidents = fields.Text(string="Previous Accidents")

    # --- Passengers Section ---
    passenger_name = fields.Char(string="Passenger Name")
    passenger_address = fields.Char(string="Passenger Address")
    passenger_injury = fields.Text(string="Passenger Injury")
    passenger_purpose = fields.Text(string="Purpose Carried")
    passenger_employee = fields.Boolean(string="Passenger is Employee?")

    # --- Other Vehicles Section ---
    other_vehicle_registration = fields.Char(string="Other Vehicle Registration")
    other_vehicle_make = fields.Char(string="Other Vehicle Make")
    other_vehicle_owner_driver = fields.Char(string="Other Vehicle Owner/Driver")
    other_vehicle_damage = fields.Text(string="Other Vehicle Damage")

    # --- Other Party Section ---
    other_property_owner = fields.Char(string="Other Property Owner")
    other_property_damage = fields.Text(string="Other Property Damage")

    # --- Personal Injuries Section ---
    injury_name = fields.Char(string="Injured Person Name")
    injury_relationship = fields.Char(string="Relationship to Accident")
    injury_details = fields.Text(string="Injury Details")
    injury_hospital = fields.Char(string="Hospital Name")

    # --- Witnesses Section ---
    witness1 = fields.Char(string="Witness 1 Name/Address/Phone")
    witness2 = fields.Char(string="Witness 2 Name/Address/Phone")
    witness3 = fields.Char(string="Witness 3 Name/Address/Phone")

    # --- Accident Details Section ---
    accident_date = fields.Date(string="Accident Date")
    accident_time = fields.Char(string="Accident Time")
    accident_place = fields.Char(string="Accident Place")
    speed_before = fields.Float(string="Speed Before Accident (kph)")
    speed_impact = fields.Float(string="Speed at Impact (kph)")
    weather_conditions = fields.Char(string="Weather Conditions")
    visibility = fields.Char(string="Visibility")
    road_surface = fields.Char(string="Road Surface")
    road_width = fields.Char(string="Road Width")
    vehicle_lights = fields.Char(string="Vehicle Lights On")
    street_lighting = fields.Char(string="Street Lighting")
    warning_given = fields.Char(string="Warning Given (Hooting/Indication)")
    police_officer = fields.Char(string="Police Officer Name")
    police_station = fields.Char(string="Police Station")
    police_reference = fields.Char(string="Police Reference No")
    alcohol_tested = fields.Boolean(string="Driver Tested for Alcohol/Drugs?")
    accident_description = fields.Text(string="Accident Description")
    accident_sketch = fields.Binary(string="Accident Sketch")

    # --- Licence Inspection Section ---
    licence_endorsement_status = fields.Char(string="Licence Endorsement Status")
    driver_signature = fields.Char(string="Driver Signature")
    driver_capacity = fields.Char(string="Driver Capacity")
    driver_signature_date = fields.Date(string="Driver Signature Date")
    insured_signature = fields.Char(string="Insured Signature")
    insured_capacity = fields.Char(string="Insured Capacity")
    insured_signature_date = fields.Date(string="Insured Signature Date")
