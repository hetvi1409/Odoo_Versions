from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_blacklisted = fields.Boolean(string='Blacklisted')
    csd_number = fields.Char(string='CSD Number', help='Central Supplier Database Number')
    company_registration_number = fields.Char(string='Company Registration Number')

    @api.constrains('csd_number')
    def _check_unique_csd_number(self):
        """Ensure CSD number is unique"""
        for record in self:
            if record.csd_number:
                existing = self.search([
                    ('id', '!=', record.id),
                    ('csd_number', '=', record.csd_number)
                ], limit=1)
                if existing:
                    raise ValidationError(
                        _('A supplier with CSD Number "%s" already exists: %s') %
                        (record.csd_number, existing.name)
                    )

    @api.constrains('company_registration_number')
    def _check_unique_company_registration(self):
        """Ensure company registration number is unique"""
        for record in self:
            if record.company_registration_number:
                existing = self.search([
                    ('id', '!=', record.id),
                    ('company_registration_number', '=', record.company_registration_number)
                ], limit=1)
                if existing:
                    raise ValidationError(
                        _('A company with Registration Number "%s" already exists: %s') %
                        (record.company_registration_number, existing.name)
                    )

    @api.constrains('email')
    def _check_unique_supplier_email(self):
        """Ensure email is unique for suppliers"""
        for record in self:
            if record.email and record.supplier_rank > 0:
                existing = self.search([
                    ('id', '!=', record.id),
                    ('email', '=', record.email),
                    ('supplier_rank', '>', 0)
                ], limit=1)
                if existing:
                    raise ValidationError(
                        _('A supplier with email "%s" already exists: %s') %
                        (record.email, existing.name)
                    )
