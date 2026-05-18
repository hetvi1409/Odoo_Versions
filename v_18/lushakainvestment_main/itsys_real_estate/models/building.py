# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from odoo.exceptions import ValidationError
from odoo import api, fields, models, tools, _

class building(models.Model):
    _name = "building"
    _description = "Building"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('building')
        new_id = super(building, self).create(vals)
        return new_id

    attach_line= fields.One2many("building.attachment.line", "building_attach_id", "Documents")
    # rental_document_ids = fields.Many2many(
    #     'rental.attachment.line',string="Rental Documents")
    rental_attachment_document_ids = fields.Many2many(
            'rental.attachment.line',string="Rental Documents")


    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    region_id= fields.Many2one('regions','Project', )
    account_income= fields.Many2one('account.account','Income Account', )
    account_analytic_id= fields.Many2one('account.analytic.account', 'Analytic Account')
    active= fields.Boolean ('Active', help="If the active field is set to False, it will allow you to hide the top without removing it.",default=True)
    alarm= fields.Boolean ('Alarm')
    old_building= fields.Boolean ('Old Property')
    constructed= fields.Date ('Construction Date')
    no_of_floors= fields.Integer ('# Floors')
    props_per_floors= fields.Integer ('# Unit per Floor')
    # category= fields.Char    ('Category', size=16)
    description= fields.Char    ('Room')
    floor= fields.Char    ('Floor', size=16)
    pricing= fields.Integer   ('Price',)
    balcony= fields.Integer   ('Balconies m²',)
    building_area= fields.Integer   ('Property Area m²',)
    land_area= fields.Integer   ('Land Area m²',)
    garden= fields.Integer   ('Garden m²',)
    terrace= fields.Integer   ('Terraces m²',)
    garage= fields.Integer ('Garage included')
    carport= fields.Integer ('Carport included')
    parking_place_rentable= fields.Boolean ('Parking rentable', help="Parking rentable in the location if available")
    handicap= fields.Boolean ('Handicap Accessible')
    heating= fields.Selection([('unknown','unknown'),
                                           ('none','none'),
                                           ('tiled_stove', 'tiled stove'),
                                           ('stove', 'stove'),
                                           ('central','central heating'),
                                           ('self_contained_central','self-contained central heating')], 'Heating')
    heating_source= fields.Selection([('unknown','unknown'),
                                           ('electricity','Electricity'),
                                           ('wood','Wood'),
                                           ('pellets','Pellets'),
                                           ('oil','Oil'),
                                           ('gas','Gas'),
                                           ('district','District Heating')], 'Heating Source')
    internet= fields.Boolean ('Internet')
    lease_target= fields.Integer   ('Target Lease', )
    lift= fields.Integer ('# Passenger Elevators')
    lift_f= fields.Integer ('# Freight Elevators')
    name= fields.Char    ('ERF Number', required=True)
    code= fields.Char    ('Code', size=16)
    note= fields.Html    ('Notes')
    note_sales= fields.Text    ('Note Sales Folder')
    partner_id= fields.Many2one('res.partner','Owner', required=False )
    type= fields.Many2one('building.type','Type', )
    status= fields.Many2one('building.status','Property Status', )
    purchase_date= fields.Date    ('Purchase Date')
    launch_date= fields.Date    ('Launching Date')
    rooms= fields.Char    ('Rooms', size=32 )
    solar_electric= fields.Boolean ('Solar Electric System')
    solar_heating= fields.Boolean ('Solar Heating System')
    staircase= fields.Char    ('Staircase', size=8)
    surface= fields.Integer   ('Surface')
    telephon= fields.Boolean ('Telephon')
    tv_cable= fields.Boolean ('Cable TV')
    tv_sat= fields.Boolean ('SAT TV')
    usage= fields.Selection([('unlimited','unlimited'),
                                          ('office','Office'),
                                           ('shop','Shop'),
                                           ('flat','Flat'),
                                            ('rural','Rural Property'),
                                           ('parking','Parking')], 'Usage')
    sort= fields.Integer ('Sort')
    sequence= fields.Integer ('Sequ.')
    air_condition= fields.Selection([('unknown','Unknown'),
                                           ('central','Central'),
                                           ('partial','Partial'),
                                           ('none', 'None'),
                                           ], 'Air Condition' )
    address= fields.Text    ('Address')
    license_code= fields.Char    ('License Code', size=16)
    license_date= fields.Date    ('License Date')
    date_added= fields.Date    ('Date Added to Notarization')
    license_location= fields.Char    ('License Notarization')
    electricity_meter= fields.Char    ('Electricity meter', size=16)
    water_meter= fields.Char    ('Water meter', size=16)
    north= fields.Char    ('Northen border by:')
    south= fields.Char    ('Southern border by:')
    east= fields.Char    ('Eastern border  by: ')
    west= fields.Char    ('Western border by: ')
    unit_ids= fields.Many2many('product.template', string='Properties')
    property_floor_plan_image_ids = fields.One2many('floor.plans', 'building_id', string="Floor Plans", copy=True)
    building_image_ids = fields.One2many('building.images', 'building_id', string="Building Images", copy=True)

    sg_code  = fields.Char("SG Code")
    farm_erf  = fields.Char("Farm ERF")
    web_link = fields.Char('Web Link')
    property_desc_id = fields.Many2one('property.desc','Property Desc')
    property_ref_id = fields.Many2one('property.ref','Property Ref')
    pq_cost_ratio = fields.Float('PQ Cost Ratio %')
    pq_vote_ratio = fields.Float('PQ Vote Ratio %')

    title_deed_no = fields.Char("Title Deed Number")
    internal_area_1 = fields.Float(string="Internal Area 1(m2)")
    internal_area_2 = fields.Float(string="Internal Area 2(m2)")
    total_area = fields.Float(string="Total Area(m2)")
    main_section_area = fields.Float(string="Total Main Section Area(m2)")
    section_ratio = fields.Float(
        compute="_compute_section_ratio",
        string="Section Ratio (%)",
        store=True
    )

    parking_bay_count = fields.Integer(
        string="Parking Bay Count",
        help="Total number of available parking bays."
    )

    parking_bay_location_number = fields.Integer(
        string="Parking Bay Location Number",
        help="List of parking bay location numbers."
    )

    property_inclusions = fields.Text("Property Inclusions")

    # ---------------------------------------------------------
    # MUNICIPAL ACCOUNTS / METER NUMBERS
    # ---------------------------------------------------------
    rates_account_1 = fields.Char("Rates Account 1 No.")
    rates_account_2 = fields.Char("Rates Account 2 No.")
    water_meter_1 = fields.Char("Water Meter 1 No.")
    water_meter_2 = fields.Char("Water Meter 2 No.")
    gas_meter_1 = fields.Char("Gas Meter 1 No.")
    gas_meter_2 = fields.Char("Gas Meter 2 No.")
    electricity_1 = fields.Char("Electricity 1 No.")
    electricity_2 = fields.Char("Electricity 2 No.")

    # ---------------------------------------------------------
    # ATTACHMENTS BY CATEGORY
    # ---------------------------------------------------------
    image_ids = fields.Many2many(
        'ir.attachment',
        'building_image_rel',
        'building_id',
        string="Images",
        help="Land pictures, Google Earth images…"
    )
    layout_plan_ids = fields.Many2many(
        'ir.attachment',
        'building_layout_plan_rel',
        'building_id',
        string="Layout Plans"
    )
    area_picture_ids = fields.Many2many(
        'ir.attachment',
        'building_picture_rel',
        'building_id',
        string="Area Pictures"
    )
    design_plan_ids = fields.Many2many(
        'ir.attachment',
        'building_plan_rel',
        'building_id',
        string="Design Plans"
    )
    video_ids = fields.Many2many(
        'ir.attachment',
        'building_video_rel',
        'building_id',
        string="Videos"
    )
    document_ids = fields.Many2many(
        'ir.attachment',
        'building_doc_rel',
        'building_id',
        string="Documents"
    )

    @api.depends("internal_area_1", "internal_area_2", "main_section_area")
    def _compute_section_ratio(self):
        for rec in self:
            internal_1 = rec.internal_area_1 or 0.0
            internal_2 = rec.internal_area_2 or 0.0
            main_area = rec.main_section_area or 0.0

            if main_area > 0:
                rec.section_ratio = ((internal_1 + internal_2) / main_area) * 100
            else:
                rec.section_ratio = 0.0

    def update_farm_erf(self):
        """"""
        for rec in self:
            if not rec.farm_erf:
                rec.farm_erf = rec.name.replace('erf ', '')

    def _get_default_lease_doc(self):

        rental = self.env['rental.contract'].search([('building', '=', self.id)])
        self.rental_document_ids= rental.ids

    def action_create_units(self):
        property_pool = self.env['product.template']
        props=[]
        if self.no_of_floors and self.props_per_floors:
            i=1
            while i<=self.no_of_floors:
                j=1
                while j<=self.props_per_floors:
                    vals={
                        'name':self.code+' - '+str(i)+' - '+str(j),
                        'code':self.code+' - '+str(i)+' - '+str(j),
                        'building_id':self.id,
                        'floor':str(i),
                        'is_property': True,
                    }
                    prop_id= property_pool.create(vals)
                    props.append(prop_id.id)
                    j+=1
                i+=1

            self.unit_ids=[(6, 0, props)]
        else:
            raise ValidationError(
                _("Please set valid number for number of floors and units per floor"))

    _sql_constraints = [
        ('unique_building_code', 'UNIQUE (code,region_id)', 'Building code must be unique!'),
    ]


class building_attachment_line(models.Model):
    _name = 'building.attachment.line'

    name= fields.Char    ('Name', required=True)
    file= fields.Binary    ('File', required=True)
    building_attach_id= fields.Many2one('building', '',ondelete='cascade', readonly=True)

    def download_file(self):
        self.env.cr.execute("select id from ir_attachment where res_model='"+str(self._name)+"' and res_id="+str(self.id))
        attachment_id= self.env.cr.fetchone()[0] or None
        if attachment_id:
            attachment = self.env['ir.attachment'].sudo().browse(attachment_id)
            if attachment:
                action = {
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=ir.attachment&id=" + str(attachment.id) + "&filename_field=name&field=datas&download=true&name=" + str(attachment.store_fname),
                    'target': 'self'
                }
                return action
