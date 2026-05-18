from odoo import models, fields


class Crematorium(models.Model):
    _name = 'crematorium.crematorium'
    _description = 'Crematorium'
    _rec_name = 'name'

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

    name = fields.Char(string='Name', required=True)
    street = fields.Char(string="Street", help="Name of the street")
    street2 = fields.Char(string="Street 2", help="Additional address line")
    postal_code = fields.Char(string="Postal Code", help="Postal code")
    city = fields.Char(string="City", help="Name of the city")
    municipality_id = fields.Many2one('municipality.municipality',
                                      string="Municipality", default=_get_municipality,
                                      domain="[('province_id', '=?', province_id)]")
    province_id = fields.Many2one('province.province', string="Province", default=_get_province_data, domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', default=_get_country_id, ondelete='restrict', help="Name of the country")

    # @api.onchange('municipality_id')
    # def _onchange_municipality_id(self):
    #     """Adding values to """
    #     self.province_id = self.municipality_id.province_id
    #     self.country_id = self.municipality_id.country_id
