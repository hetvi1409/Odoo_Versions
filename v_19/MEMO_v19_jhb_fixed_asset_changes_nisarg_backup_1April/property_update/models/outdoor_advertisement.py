from odoo import api, fields, models, _


class OutdoorAdvertisement(models.Model):
    """Outdoor advertisement"""
    _name = 'outdoor.advertisement'
    _description = 'Outdoor advertisement'

    name = fields.Char(string="Name")
    sequence = fields.Char(string="Sequence")

    address = fields.Char(string="Site Location/Address ")
    erf = fields.Char(string="Erf Details", required=True)
    township_id = fields.Many2one('township.township', string='Township Id')
    format = fields.Char(string="Format")
    region_id = fields.Many2one('regions', string='Region', required=True)
    ward = fields.Char(string="Ward")
    zoning_id = fields.Many2one('property.zoning', string="Zoning ID")
    owned_id = fields.Many2one('res.partner', string="Owned")
    jmc_number = fields.Char(string="JMC Number")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    day_notice = fields.Char(string="60 Days Notice")
    rental = fields.Char(string="Rental")
    renewal = fields.Char(string="Renewal")
    company_id = fields.Many2one('res.partner', string="Company", )
    building_id = fields.Many2one('building', string="Building",
                                  compute="_compute_building")
    #
    ref = fields.Char(string="Reference")
    #
    no_of_structure = fields.Char(string="No. of Structures")
    #
    #
    surbub = fields.Char(string="Surbub")
    #Outsmart
    facility = fields.Char(string="Facility")

    # Property Details
    property_type_id = fields.Many2one('building.type', string='Property Type')
    diagram_deed_number = fields.Char(string='Diagram Deed Number')
    township = fields.Char(string='Township')
    local_authority = fields.Char(string='Local Authority')
    erf_number = fields.Char(string='Erf Number')
    def _get_province_data(self):
        """Returns Country"""
        country = self.env.ref('base.za').id
        return [('country_id', '=', country)]

    province_id = fields.Many2one('res.country.state', ondelete='restrict',
                               string='Province', domain=_get_province_data)
    portion_number = fields.Char(string='Portion Number')
    extent = fields.Float(string='Extent')
    registration_division = fields.Char(string='Registration Division')
    lpi_code = fields.Char(string='LPI Code')

    # Ownership
    person_type = fields.Selection(
        [('individual', 'Individual'), ('company', 'Company')],
        string='Person Type')
    id_number = fields.Char(string='ID Number')
    owner_name = fields.Char(string='Owner Name')
    multiple_owners = fields.Boolean(string='Multiple Owners')
    multiple_properties = fields.Boolean(string='Multiple Properties')
    share_percentage = fields.Float(string='Share (%)')
    ownership_document = fields.Binary(string='Ownership Document')
    microfilm_scanned_date = fields.Date(string='Ownership Microfilm / Scanned Date')
    purchase_price = fields.Float(string='Purchase Price (R)')
    purchase_date_ownership = fields.Date(string='Purchase Date')
    registration_date_ownership = fields.Date(string='Registration Date')

    # Endorsements
    endorsement_document = fields.Binary(string='Endorsements Document')
    institution = fields.Char(string='Institution')
    endorsement_amount = fields.Float(string='Amount (R)')
    endorsement_microfilm_date = fields.Date(string='Endorsements Microfilm / Scanned Date')

    # History of Documents
    history_document = fields.Binary(string='History Document')
    history_institution = fields.Char(string='History Institution')
    history_amount = fields.Float(string='Amount (R)')
    history_microfilm_date = fields.Date(string='History Microfilm / Scanned Date')

    # Geolocation
    address = fields.Char(string='Address')
    property_condition = fields.Selection([('very_good', 'Very Good'),
                                           ('good', 'Good'), ('fair', 'Fair'),
                                           ('poor', 'Poor'),
                                           ('very_poor', 'Very Poor')],
                                          string="Condition of property")
    ward = fields.Char(string="Ward")
    zoning_id = fields.Many2one('property.zoning', string="Zoning ID")
    latitude = fields.Float("Latitude", digits=(9, 6), required=True)
    longitude = fields.Float("Longitude", digits=(9, 6), required=True)
    sg_id = fields.Char(string="SG ID")
    department_id = fields.Many2one('property.department',
                                    string="User Department")
    category_id = fields.Many2one('property.category', string="Category")
    category_amp_id = fields.Many2one('property.category.amp',
                                      string="Category AMP")
    current_use = fields.Char(string="Current Use")
    # Images
    building_image_ids = fields.One2many('building.images', 'outdoor_id', string="Building Images", copy=True)
    # Documents
    attach_line_ids = fields.One2many("building.attachment.line", "outdoor_id", "Documents")
    rental_count = fields.Integer(string="Rental Count", compute="_compute_rental_contract")

    @api.model
    def create(self, values):
        """Method for generating consumer number for the contacts"""
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code(
                'outdoor.advertisement') or _('New')
        return super(OutdoorAdvertisement, self).create(values)

    @api.depends('jmc_number')
    def _compute_building(self):
        """Method for generating Building"""
        for rec in self:
            buildings = self.env['building'].search([('jmc_number', '=', rec.jmc_number)], limit=1)
            rec.building_id = buildings.id if buildings else None

    def action_open_rental(self):
        """Method for getting rental contract details"""
        rental = self.env['rental.contract']
        if self.building_id.id:
            rental = self.env['rental.contract'].search([('building', '=', self.building_id.id), ('lease_type','=', 'outdoor_lease')])
        if self.jmc_number:
            rental += self.env['rental.contract'].search(
                [('jmc_number', '=', self.jmc_number),
                 ('lease_type', '=', 'outdoor_lease')])
        rental += self.env['rental.contract'].search([('outdoor_advertisement_id', '=', self.id), ('lease_type','=', 'outdoor_lease')])

        action = {
            'name': _('Budget'),
            'type': 'ir.actions.act_window',
            'res_model': 'rental.contract',
            'context': {'create': False},
        }
        if len(rental) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': rental.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', rental.ids)],
            })
        return action

    def _compute_rental_contract(self):
        """Compute the rental contract count"""
        for rec in self:
            rental_count = 0
            rental = self.env['rental.contract']
            if rec.building_id.id:
                rental = self.env['rental.contract'].search(
                    [('building', '=', rec.building_id.id),
                     ('lease_type', '=', 'outdoor_lease')])
            if rec.jmc_number:
                rental += self.env['rental.contract'].search(
                    [('jmc_number', '=', rec.jmc_number),
                     ('lease_type', '=', 'outdoor_lease')])
            rental += self.env['rental.contract'].search(
                [('outdoor_advertisement_id', '=', rec.id),
                 ('lease_type', '=', 'outdoor_lease')])
            rec.rental_count = len(rental)
