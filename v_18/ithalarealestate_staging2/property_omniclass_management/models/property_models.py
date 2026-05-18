# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PropertyLand(models.Model):
    _name = "property.land"
    _description = "Land / Property"
    _inherit = ["mail.thread"]
    name = fields.Char(string="Property / Land Name", required=True, index=True)
    location = fields.Char(string="Location / Address")
    full_extent_sqm = fields.Float(string="Full Extent (sqm)")
    omniclass_code_91 = fields.Many2one("omniclass.properties", string="OmniClass Table 91 (Property)")
    building_ids = fields.One2many("building", "land_id", string="Buildings")

    # aggregated numbers
    total_building_area = fields.Float(string="Total Building Area (sqm)", compute="_compute_totals")
    total_lettable_area = fields.Float(string="Total Lettable Area (sqm)", compute="_compute_totals")

    def action_view_buildings(self):
        return {
            "name": "Buildings",
            "type": "ir.actions.act_window",
            "res_model": "building",
            "view_mode": "list,form",
            "domain": [("land_id", "=", self.id)],
        }

    @api.depends("building_ids.gross_building_area_sqm", "building_ids.unit_ids.gross_lettable_area_sqm")
    def _compute_totals(self):
        for rec in self:
            rec.total_building_area = sum(rec.building_ids.mapped("gross_building_area_sqm") or [])
            rec.total_lettable_area = sum(rec.building_ids.mapped("unit_ids.gross_lettable_area_sqm") or [])


class PropertyBuilding(models.Model):
    _inherit = "building"
    _description = "Building"

    land_id = fields.Many2one("property.land", string="Land / Site", ondelete="cascade", index=True, required=True)
    gross_building_area_sqm = fields.Float(string="Gross Building Area (sqm)")
    omniclass_code_11 = fields.Many2one("omniclass.function", string="OmniClass Table 11 (Function)")
    omniclass_code_21 = fields.Many2one("omniclass.space", string="OmniClass Table 21 (Space)")
    omniclass_code_22 = fields.Many2one("omniclass.element", string="OmniClass Table 22 (Element)")
    unit_ids = fields.One2many("property.unit", "building_id", string="Units")

    def action_view_units(self):
        return {
            "name": "Units",
            "type": "ir.actions.act_window",
            "res_model": "property.unit",
            "view_mode": "list,form",
            "domain": [("building_id", "=", self.id)],
        }


class PropertyUnit(models.Model):
    _name = "property.unit"
    _description = "Unit"
    _inherit = ["mail.thread"]
    name = fields.Char(string="Unit Name", required=True, index=True)
    building_id = fields.Many2one("building", string="Building", ondelete="cascade", required=True)
    unit_type = fields.Selection(
        [
            ("factory", "Factory"),
            ("shop", "Shop"),
            ("moorage", "Moorage"),
            ("office", "Office"),
            ("other", "Other"),
        ],
        string="Unit Type",
        default="other",
    )
    gross_lettable_area_sqm = fields.Float(string="Gross Lettable Area (sqm)")
    omniclass_code_21 = fields.Many2one("omniclass.space", string="OmniClass Table 21 (Space)")
    omniclass_code_22 = fields.Many2one("omniclass.element", string="OmniClass Table 22 (Element)")
    omniclass_code_31 = fields.Many2one("omniclass.product", string="OmniClass Table 31 (Product)")
    omniclass_code_33 = fields.Many2one("omniclass.material", string="OmniClass Table 33 (Material)")

    # keep land relation for search convenience (computed & stored)
    land_id = fields.Many2one("property.land", string="Land", compute="_compute_land", store=True)

    @api.depends("building_id")
    def _compute_land(self):
        for rec in self:
            rec.land_id = rec.building_id.land_id
