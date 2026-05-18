from odoo import api, fields, models, _



class building(models.Model):
    _inherit = "product.template"

    property_type = fields.Selection([
        ('industrial_smme', 'Industrial SMME'),
        ('industrial_light', 'Industrial - Light'),
        ('industrial_large', 'Industrial - Large'),
        ('retail', 'Retail'),
        ('mooring', 'Mooring'),
        ('commercial_office', 'Commercial / Office'),
        ('residential', 'Residential'),
    ], string="Property Type", tracking=True)

    # 4.4 Mooring dropdowns
    mooring_length = fields.Selection([
        ('5m', '5 m'),
        ('10m', '10 m'),
        ('15m', '15 m'),
        ('20m', '20 m'),
        ('25m', '25 m'),
    ], string="Mooring Length", help="Select the mooring length (in meters)")

    mooring_width = fields.Selection([
        ('2m', '2 m'),
        ('3m', '3 m'),
        ('4m', '4 m'),
        ('5m', '5 m'),
    ], string="Mooring Width", help="Select the mooring width (in meters)")

    # 4.5 For other property types
    min_area = fields.Float(string="Minimum Area (m²)")
    max_area = fields.Float(string="Maximum Area (m²)")
    tenant_id = fields.Many2one('res.partner', string="Tenant")

    province_id = fields.Many2one('res.province', string="Province")
    district_id = fields.Many2one('res.district', domain="[('country_id', '=?', country_id)]", required=True)
    city_id = fields.Many2one('res.district.city', domain="[('district_id', '=?', district_id)]", required=True)

    # Property Facilities

    swimming_pool = fields.Char(string="Swimming Pool")
    generator = fields.Char(string="Generator")
    water_storage = fields.Char(string="Water Storage ")
    conceige = fields.Char(string="Conceige")
    security = fields.Char(string="Security")
    basement_parking = fields.Char(string="Basement Parking")
    park = fields.Char(string="Park")
    open_parking = fields.Char(string="Open Parking")
    children_facilities = fields.Char(string="Children Facilities")
    gym = fields.Char(string="Gym")
    residential_lifts = fields.Char(string="Residential Lifts")
    fireman_service_lift = fields.Char(string="Fireman/Service Lift")
