# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_sequence = fields.Char(string="Partner Sequence", readonly=True, copy=False, store=True)

    @api.model
    def create(self, vals):
        parent_id = vals.get('parent_id')
        if parent_id:
            parent = self.env['res.partner'].browse(parent_id)
            vals['mobile'] = parent.mobile
            if parent:
                # Copy data from parent
                vals['x_studio_groupement'] = parent.x_studio_groupement
                vals['x_studio_paiement'] =  parent.x_studio_paiement
                vals['x_studio_note'] = parent.x_studio_note
                vals['partner_sequence'] = parent.partner_sequence
                vals['country_id'] = parent.country_id.id
                vals['email'] = parent.email
                vals['phone'] = parent.phone
                vals['lang'] = parent.lang
                vals['vat'] =  parent.vat
                vals['mobile'] = parent.mobile
                vals['function'] = parent.function
                vals['website'] = parent.website
                vals['title'] = parent.title.id

                if not vals.get('category_id'):
                    vals['category_id'] = [(6, 0, parent.category_id.ids)]

            return super().create(vals)

        if not vals.get('country_id'):
            raise ValidationError(_("Country is required to create customer."))

        partner = super(ResPartner, self).create(vals)

        if not partner.partner_sequence:
            partner._assign_state_sequence()

        return partner


    def _assign_state_sequence(self):
        for partner in self:
            if partner.parent_id and partner.company_type == 'person':
                # If partner has a parent, use parent's sequence
                partner.partner_sequence = partner.parent_id.partner_sequence

            elif partner.country_id:
                # If no parent but has a country, generate sequence
                country_code = partner.country_id.code or 'XXX'
                seq_code = f'partner.seq.{country_code.lower()}'

                sequence = self.env['ir.sequence'].sudo().search([('code', '=', seq_code)], limit=1)
                if not sequence:
                    sequence = self.env['ir.sequence'].sudo().create({
                        'name': f'{country_code} Partner Sequence',
                        'code': seq_code,
                        'prefix': f'{country_code}',
                        'padding': 4,
                        'number_next': 1,
                        'implementation': 'standard',
                    })

                partner.partner_sequence = self.env['ir.sequence'].next_by_code(seq_code)

    @api.model
    def _assign_custom_ref_to_existing_partners(self):
        partners = self.search([
            ('country_id', '!=', False),
            ('partner_sequence', '=', False)
        ])
        for partner in partners:
            partner._assign_state_sequence()

    @api.model
    def cron_clear_partner_sequences(self):
        partners = self.search([('partner_sequence', '!=', False)])
        partners.write({'partner_sequence': False})