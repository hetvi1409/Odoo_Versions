# -*- coding: utf-8 -*-

from odoo import fields, models


class EcdhsContractSignatureSection(models.Model):
    _name = 'ecdhs.contract.signature.section'
    _description = 'Contract Section Signature'
    _order = 'contract_id, sequence, id'

    contract_id = fields.Many2one(
        'ecdhs.contract', string='Contract', required=True, ondelete='cascade'
    )
    sequence = fields.Integer(default=10)
    name = fields.Char('Section Name', required=True)
    section_reference = fields.Char('Section Reference')

    provider_signature_required = fields.Boolean('Provider Signature Required', default=True)
    provider_signed = fields.Boolean('Provider Signed')
    provider_signed_on = fields.Datetime('Provider Signed On')
    provider_signatory_name = fields.Char('Provider Signatory Name')

    internal_signature_required = fields.Boolean('Internal Signature Required', default=True)
    internal_signed = fields.Boolean('Internal Signed')
    internal_signed_on = fields.Datetime('Internal Signed On')
    internal_signatory_id = fields.Many2one('res.users', string='Internal Signatory')

    signed_section_file = fields.Binary('Signed Section Extract', attachment=True)
    signed_section_filename = fields.Char('Signed Section Filename')
