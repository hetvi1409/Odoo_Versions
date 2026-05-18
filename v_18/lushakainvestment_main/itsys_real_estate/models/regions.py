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
from odoo.tools.translate import _
from odoo import api, fields, models 

class regions(models.Model):
    _name = "regions"
    _description = "Project"
    _parent_name = "region_id"
    _parent_store = True
    _order = 'complete_name'
    _rec_name = 'complete_name'
    _inherit = ['mail.thread']

    @api.depends('name', 'region_id')
    def _compute_complete_name(self):
        """ Forms complete name of region from region to child region. """
        name = self.name
        current = self
        while current.region_id:
            current = current.region_id
            name = '%s/%s' % (current.name, name)
        self.complete_name = name


    @api.depends('name', 'region_id.complete_name')
    def _compute_complete_name(self):
        """ Forms complete name of location from parent location to child location. """
        if self.region_id.complete_name:
            self.complete_name = '%s/%s' % (self.region_id.complete_name, self.name)
        else:
            self.complete_name = self.name

    name= fields.Char ('Name',required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    child_ids= fields.One2many('regions', 'region_id', 'Contains')
    parent_left= fields.Integer('Left Parent')
    parent_right= fields.Integer('Right Parent')
    account= fields.Many2one('account.account','Discount Account', )
    account_me= fields.Many2one('account.account','Managerial Expenses Account', )
    region_id= fields.Many2one('regions','Parent Project', ondelete='cascade')
    parent_path = fields.Char(index=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    latlng_ids= fields.One2many('latlng.line', 'region_id', string='LatLng List',copy=True)
    map= fields.Char('Map', digits=(9, 6))
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=lambda self: self.env['res.country'].search([('code', '=', 'ZA')], limit=1))
    country_code = fields.Char(related='country_id.code', string="Country Code")

    
    # -----------------------------------------------
    # ADD FIELD EXTENSIONS TO SUPPORT NEW XML
    # -----------------------------------------------

    # Project Classification (Existing M2O models already exist)
    project_stage_id = fields.Many2one(
        "property.project.stage",
        string="Project Status",
        tracking=True
    )
    project_type_id = fields.Many2one(
        "property.project.type",
        string="Project Type"
    )
    power_supplier_id = fields.Many2one(
        "property.power.supplier",
        string="Power Supplier"
    )

    # Legal + Zoning Fields
    title_deed_no = fields.Char("Title Deed Number")
    erf_no = fields.Char("Erf Number")
    stand_details = fields.Char("Stand Details")
    sg_code = fields.Char("SG Code")

    # Land & Development Fields
    land_area = fields.Float("Land Area (m²)")
    far = fields.Float("FAR")

    total_build_area = fields.Float(
        compute="_compute_total_build_area",
        string="Total Build Area (m²)",
        store=True
    )
    building_line = fields.Float("Building Line (m)")
    coverage_percent = fields.Float("Coverage %")
    height_floors = fields.Integer("Height (Floors)")
    servitudes = fields.Boolean("Servitudes")

    # Financial Fields
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )
    purchase_price = fields.Monetary(
        "Purchase Price",
        currency_field="currency_id"
    )
    vat_percent = fields.Float("VAT %")
    agent = fields.Char('Agent Name')
    agent_comm_percent = fields.Float("Agent Commission %")
    agent_comm_amount = fields.Monetary(
        compute="_compute_agent_commission",
        string="Agent Commission Amount",
        currency_field="currency_id",
        store=True
    )
    purchase_date = fields.Date("Purchase Date")
    transfer_date = fields.Date("Transfer Date")

    # Municipality Additional Info (Existing model)
    municipality_id = fields.Many2one(
        "res.municipality",
        string="Municipality"
    )

    # Notes Tab
    note = fields.Text("Notes")
    # ---------------------------------------------------------
    # SELLER & PURCHASER DETAILS
    # ---------------------------------------------------------
    # seller_name = fields.Char("Seller Name")
    seller_name = fields.Many2one("res.partner","Seller Name")
    purchaser_name = fields.Many2one("res.partner","Purchaser Name")
    # purchaser_name = fields.Char("Purchaser Name")
    purchaser_number = fields.Char("Purchaser Registration No")

   
    # ---------------------------------------------------------
    # PROPERTY RIGHTS + SPECIAL CONDITIONS
    # ---------------------------------------------------------
    property_rights = fields.Text("Property Rights")
    special_conditions = fields.Text("Special Conditions")

    # ---------------------------------------------------------
    # PROPERTY INCLUSIONS (same as Component List)
    # Components already stored on product.template linked via region_id
    # So we provide a text summary OR use M2M if needed later
    property_inclusions = fields.Text("Property Inclusions")

    # ---------------------------------------------------------
    # PROFESSIONALS (Name, Mobile, Email, Specialisation, Notes)
    # ---------------------------------------------------------
    professional_ids = fields.One2many(
        "property.professional",
        "region_id",
        string="Professionals",
        copy=True
    )

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
    
    # ---------------------------------------------------------
    image_ids = fields.Many2many(
        'ir.attachment',
        'regions_image_attachment_rel',
        'region_id',
        'attachment_id',
        string="Images",
        help="Land pictures, Google Earth images…"
    )

    layout_plan_ids = fields.Many2many(
        'ir.attachment',
        'regions_layoutplan_attachment_rel',
        'region_id',
        'attachment_id',
        string="Layout Plans"
    )

    area_picture_ids = fields.Many2many(
        'ir.attachment',
        'regions_area_attach_rel',
        'region_id',
        'attachment_id',
        string="Area Pictures"
    )

    design_plan_ids = fields.Many2many(
        'ir.attachment',
        'regions_designplan_attachment_rel',
        'region_id',
        'attachment_id',
        string="Design Plans"
    )

    video_ids = fields.Many2many(
        'ir.attachment',
        'regions_video_attach_rel',
        'region_id',
        'attachment_id',
        string="Videos"
    )

    document_ids = fields.Many2many(
        'ir.attachment',
        'regions_document_attach_rel',
        'region_id',
        'attachment_id',
        string="Documents"
    )


    # -----------------------------
    # COMPUTE METHODS
    # -----------------------------

     # ---------------------------------------------------------
    # FINANCIAL COMPUTATIONS
    # ---------------------------------------------------------
    @api.depends('purchase_price', 'agent_comm_percent')
    def _compute_agent_commission(self):
        for rec in self:
            if rec.purchase_price and rec.agent_comm_percent:
                rec.agent_comm_amount = rec.purchase_price * (rec.agent_comm_percent / 100)
            else:
                rec.agent_comm_amount = 0.0

    @api.depends("purchase_price", "agent_comm_percent")
    def _compute_agent_commission(self):
        for rec in self:
            rec.agent_comm_amount = (
                (rec.purchase_price or 0) *
                (rec.agent_comm_percent or 0) / 100
            )


    @api.depends("land_area", "far")
    def _compute_total_build_area(self):
        for rec in self:
            rec.total_build_area = (rec.land_area or 0) * (rec.far or 0)

    def unit_status(self, unit_id):
        self.env.cr.execute("select state from building_unit where id = "+str(int(unit_id)))
        res = self.env.cr.dictfetchone()
        if res:
            if res["state"]:
                return res["state"]

    def action_open_property(self):
        """Open a property"""
        return {
            'name': _('Property'),
            'domain': [('region_id', '=', self.id)],
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'building',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'view_id': False,
            'target': 'current',
        }


class latlng_line(models.Model):
    _name = "latlng.line"
    lat = fields.Float('Latitude', digits=(9, 6), required=True)
    lng = fields.Float('Longitude', digits=(9, 6), required=True)
    url = fields.Char('URL', digits=(9, 6), required=True)
    region_id = fields.Many2one('regions', 'Project')
    unit_id = fields.Many2one('product.template', 'Unit', domain=[('is_property', '=', True)], required=True)
    state = fields.Selection(string='State', related='unit_id.state', store=True, readonly=True)

    @api.onchange('unit_id')
    def onchange_unit(self):
        action_id = self.env.ref('itsys_real_estate.building_unit_act1').id
        '#id=33&cids=1&action=317&model=product.template&view_type=form&menu_id=205'
        link = '#id=%s&action=%s&model=product.template&view_type=form' % (
            self.unit_id.id, action_id)
        self.url = link

    @api.onchange('url')
    def onchange_url(self):
        if self.url:
            url = self.url
            self.unit_id = int(((url.split("#")[1]).split("&")[0]).split("=")[1])
        else:
            self.unit_id = None
            self.state = None
