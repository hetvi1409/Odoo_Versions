from odoo import api, fields, models


class CemeterySection(models.Model):
    _name = 'cemetery.section'
    _description = 'Cemetery Section'

    name = fields.Char(string='Section Name', required=True)
    cemetery_id = fields.Many2one('cemetery.cemetery', string='Cemetery', required=True)
    grave_ids = fields.One2many('grave.grave', 'section_id', string='Graves', readonly=False)
    square_meter = fields.Float(string="Area in Square Meter")
    graves_count = fields.Integer(string='Number of Graves', compute='_compute_graves_count')
    adult_graves_count = fields.Integer(string='Number of Adult Graves', compute='_compute_adult_graves_count')
    infant_graves_count = fields.Integer(string='Number of Infant Graves', compute='_compute_infant_graves_count')
    company_id = fields.Many2one('res.company', string="Company",
                                 help="Company", related="cemetery_id.company_id")

    @api.depends('grave_ids')
    def _compute_graves_count(self):
        for section in self:
            section.graves_count = len(section.grave_ids)

    @api.depends('grave_ids.grave_type')
    def _compute_adult_graves_count(self):
        for section in self:
            section.adult_graves_count = sum(1 for grave in section.grave_ids if grave.grave_type == 'adult')

    @api.depends('grave_ids.grave_type')
    def _compute_infant_graves_count(self):
        for section in self:
            section.infant_graves_count = sum(1 for grave in section.grave_ids if grave.grave_type == 'infant')

    @api.onchange('cemetery_id')
    def _onchange_company_id(self):
        """Updating the company values based on the cemetery company"""
        self.company_id = self.cemetery_id.company_id.id
