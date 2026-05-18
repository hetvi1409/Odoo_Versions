from odoo import fields, models, _
from odoo.exceptions import UserError


class Building(models.Model):
    _inherit = 'building'

    asset_condition = fields.Many2one('asset.condition', string="Asset Condition", help="Asset Condition",copy=True)
    current_use = fields.Char(related="building.current_use",string="Current Use")
    user_department = fields.Char(related="department_id.name",string="User Department")
    longitude = fields.Float(related="building.longitude",string="Longitude")
    latitude = fields.Float(related="building.latitude",string="Latitude")
    category = fields.Char(related="category_id.name",string="Category")
    map = fields.Char(related="region_id.map",string="Map")
    ward = fields.Char(related="building.ward",string="Ward")
    category_amp = fields.Char(related="category_amp_id.name",string="Category AMP")
    property_status = fields.Char(related="status.name",string="Property Status")
    sg_id = fields.Char(related="building.sg_id",string="SG ID")
    zoning = fields.Char(related="zoning_id.name",string="Zoning")
    title_deed_number = fields.Char(string="Title Deed Number",store=True)
    property_department_id = fields.Many2one('property.department',string="Property Department")
    property_zoning_id = fields.Many2one('property.zoning',string="Property Zoning")


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    new_image = fields.Binary(string="New Image", help="New Image", copy=True)
    original_useful_life_in_years = fields.Char(string="Original Useful Life in Years", help="Original Useful Life in Years", copy=True)
    remaining_useful_life_in_years = fields.Char(string="Remaining Useful Life in Years", help="Remaining Useful Life in Years", copy=True)


class SETAKPILine(models.Model):
    _inherit = 'seta.kpi.line'

    new_checkbox = fields.Boolean(string="New Checkbox", help="New Checkbox", copy=True,store=True)


class RentalContract(models.Model):
    _inherit = 'rental.contract'

    vacate_date = fields.Date(string="Vacate Date", help="Vacate Date", copy=True,store=True)