from geopy.geocoders import Nominatim
from odoo import api, fields, models, _
from odoo.tools import config


class CemeteryCemetery(models.Model):
    _name = 'cemetery.cemetery'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cemetery Cemetery'

    def _get_country_id(self):
        """Returns Country"""
        return self.env.ref('base.za').id

    def _get_province_data(self):
        """Returns province data"""
        return self.env.ref('cemetery_management.province_province_kwaZulu_natal').id

    def _get_municipality(self):
        """Returns municipality data"""
        municipality = self.env['municipality.municipality'].search([('company_id', '=', self.env.company.id)], limit=1)
        return municipality.id

    name = fields.Char(string='Cemetery Name', required=True)
    sections_count = fields.Integer(string='Number of Sections',
                                    compute='_compute_sections_count')
    graves_count = fields.Integer(string='Number of Graves',
                                  compute='_compute_graves_count')
    section_ids = fields.One2many('cemetery.section', 'cemetery_id',
                                  string='Sections', readonly=False)
    municipality_id = fields.Many2one('municipality.municipality',
                                      string="Municipality", required=True,
                                      default=_get_municipality,
                                      domain="[('province_id', '=?', province_id)]")
    square_meter = fields.Float(string="Area in Square Meter")
    state = fields.Selection([('active', "Active"), ('closed', "Closed")])
    tag_ids = fields.Many2many('cemetery.tag', string="Tag")
    province_id = fields.Many2one('province.province', string="Province",
                                  required=False, default=_get_province_data,
                                  domain="[('country_id', '=?', country_id)]")
    state_id = fields.Many2one('cemetery.tag', string="Status")
    street = fields.Char(string="Street",
                         help="Name of the street")
    street2 = fields.Char(string="Street 2",
                          help="Name of the street")
    zip = fields.Char(string="Zip", help="Zip code")
    city = fields.Char(string="City", help="Name of the city")
    ward_id = fields.Many2one('ward.ward', string="Ward",
                              help="Name of the Ward")
    # province_id = fields.Many2one('province.province', string="Province",
    #                               required=False,
    #                               domain="[('country_id', '=?', country_id)]")
    #
    country_state_id = fields.Many2one("res.country.state", string='State',
                                       ondelete='restrict',
                                       domain="[('country_id', '=?', country_id)]",
                                       help="Name of the State")
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict', default=_get_country_id,
                                 help="Name of the country")
    # Localization
    partner_latitude = fields.Float('Geo Latitude', digits=(10, 7))
    partner_longitude = fields.Float('Geo Longitude', digits=(10, 7))
    date_localization = fields.Date(string='Geolocation Date')
    location_url = fields.Char(string='Location URL')

    cemetery_id = fields.Char(string='Cemetery ID')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    elevation = fields.Char(string='Boundary Shape Files, Elevation')
    size = fields.Float(string="Size")
    size_unit = fields.Char(string='Size Unit')
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.company,
                                 help="Company")

    @api.depends('total_capacity', 'used_capacity')
    def _compute_remaining_capacity(self):
        for cemetery in self:
            cemetery.remaining_capacity = cemetery.total_capacity - cemetery.used_capacity

    @api.model
    def create(self, vals):
        vals['cemetery_id'] = self.env['ir.sequence'].next_by_code('cemetery.cemetery') or 'New'
        return super(CemeteryCemetery, self).create(vals)

    @api.depends('section_ids')
    def _compute_sections_count(self):
        for cemetery in self:
            cemetery.sections_count = len(cemetery.section_ids)

    @api.depends('section_ids.grave_ids')
    def _compute_graves_count(self):
        for cemetery in self:
            cemetery.graves_count = sum(
                len(section.grave_ids) for section in cemetery.section_ids)

    def action_view_section(self):
        """View the section details"""
        section = self.section_ids
        action = {
            'name': _('Assessment'),
            'type': 'ir.actions.act_window',
            'res_model': section._name,
            'context': {'create': False},
        }
        if len(section) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': section.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', section.ids)],
            })
        return action

    def action_view_grave(self):
        """View the Grave details"""
        section = self.section_ids
        grave = []
        for rec in section:
            grave = grave + rec.grave_ids.ids
        action = {
            'name': _('Assessment'),
            'type': 'ir.actions.act_window',
            'res_model': 'grave.grave',
            'context': {'create': False},
        }
        if len(grave) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': grave[0],
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', grave)],
            })
        return action

    @api.model
    def get_cemetery_details(self):
        """Returns the count f cemeteries"""
        cemetery_count = self.env[self._name].search_count([])
        cemetery_section_count = self.env['cemetery.section'].search_count([])
        grave_count = self.env['grave.grave'].search_count([])
        application_count = self.env['cemetery.application'].search_count([])
        submitted_application_count = self.env[
            'cemetery.application'].search_count([('state', '=', 'submitted')])
        approved_application_count = self.env[
            'cemetery.application'].search_count([('state', '=', 'approved')])
        burial_application_count = self.env[
            'cemetery.application'].search_count(
            [('interment_type', '=', 'burial')])
        cremation_application_count = self.env[
            'cemetery.application'].search_count(
            [('interment_type', '=', 'cremation')])
        grave_purchase_count = self.env['grave.booking'].search_count([('type', '=', 'purchase')])
        grave_lease_count = self.env['grave.booking'].search_count([('type', '=', 'lease')])
        submitted_grave_purchase_count = self.env['grave.booking'].search_count([('type', '=', 'purchase'), ('state', '=', 'submitted')])
        quotation_grave_purchase_count = self.env['grave.booking'].search_count([('type', '=', 'purchase'), ('state', '=', 'quotation')])
        approved_grave_purchase_count = self.env['grave.booking'].search_count([('type', '=', 'purchase'), ('state', '=', 'approved')])
        grave_submitted_lease_count = self.env['grave.booking'].search_count([('type', '=', 'lease'), ('state', '=', 'submitted')])
        grave_quotation_lease_count = self.env['grave.booking'].search_count([('type', '=', 'lease'), ('state', '=', 'quotation')])
        grave_approved_lease_count = self.env['grave.booking'].search_count([('type', '=', 'lease'), ('state', '=', 'approved')])
        return {
            'cemetery_count': cemetery_count,
            'cemetery_section_count': cemetery_section_count,
            'grave_count': grave_count,
            'application_count': application_count,
            'submitted_application_count': submitted_application_count,
            'approved_application_count': approved_application_count,
            'burial_application_count': burial_application_count,
            'grave_purchase_count': grave_purchase_count,
            'grave_lease_count': grave_lease_count,
            'submitted_grave_purchase_count': submitted_grave_purchase_count,
            'quotation_grave_purchase_count': quotation_grave_purchase_count,
            'approved_grave_purchase_count': approved_grave_purchase_count,
            'grave_submitted_lease_count': grave_submitted_lease_count,
            'grave_quotation_lease_count': grave_quotation_lease_count,
            'grave_approved_lease_count': grave_approved_lease_count,
            'cremation_application_count': cremation_application_count,
        }

    def geo_localize(self):
        """Returns Localizations.
        For getting the latitude and longitaude"""
        if not self._context.get('force_geo_localize') \
                and (self._context.get('import_file') \
                     or any(config[key] for key in
                            ['test_enable', 'test_file', 'init', 'update'])):
            return False
        for cemetery in self.with_context(lang='en_US'):
            geo_obj = self.env['base.geocoder']
            search = geo_obj.geo_query_address(street=cemetery.street,
                                               zip=cemetery.zip,
                                               city=cemetery.city,
                                               state=cemetery.country_state_id.name,
                                               country=cemetery.country_id.name)
            result = geo_obj.geo_find(search,
                                      force_country=cemetery.country_id.name)
            if result is None:
                search = geo_obj.geo_query_address(city=cemetery.city,
                                                   state=cemetery.country_state_id.name,
                                                   country=cemetery.country_id.name)
                result = geo_obj.geo_find(search,
                                          force_country=cemetery.country_id.name)
            if result:
                # create a geolocator object
                geolocator = Nominatim(user_agent='my-app')
                # get the location using the geolocator object
                location = geolocator.reverse(
                    str(result[0]) + ', ' + str(result[1]))
                address = ""
                if cemetery.street:
                    address += (cemetery.street).replace(' ', '+') + '+'
                if cemetery.street2:
                    address += (cemetery.street2).replace(' ', '+') + '+'
                if cemetery.city:
                    address += (cemetery.city).replace(' ', '+') + '+'
                # if cemetery.
                cemetery.write({
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.Date.context_today(cemetery),
                    'location_url': 'https://www.google.com/maps/search/?api=1&query=' + address
                })

            else:
                cemetery.write({
                    'partner_latitude': "",
                    'partner_longitude': "",
                    'date_localization': ""
                })
                self.env['bus.bus']._sendone(self.env.user.partner_id,
                                             'simple_notification',
                                             {'type': 'danger',
                                              'title': _("Warning"),
                                              'message': _(
                                                  'No match found for %(partner_names)s address.',
                                                  partner_names=(
                                                      self.name))
                                              })

    def action_open_map(self):
        """Open the map"""
        return {'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': self.location_url
                }
