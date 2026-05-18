# -*- coding: utf-8 -*-
# Clause matrix lines linked to each contract document.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EcdhsContractClause(models.Model):
    _name = 'ecdhs.contract.clause'
    _description = 'Contract Mandatory Clause'
    _order = 'contract_id, sequence, id'

    contract_id = fields.Many2one(
        'ecdhs.contract', string='Contract',
        required=True, ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char('Clause Name', required=True)
    legislative_reference = fields.Char('Legislative Reference')
    required = fields.Boolean('Mandatory', default=True)
    confirmed = fields.Boolean('Confirmed Included')
    evidence_reference = fields.Char(
        'Evidence / Clause Reference',
        help='Clause number or section in the draft contract where this requirement is addressed.',
    )
    notes = fields.Text('Notes')

    @api.constrains('contract_id', 'name')
    def _check_unique_clause_per_contract(self):
        for line in self:
            if not line.contract_id or not line.name:
                continue
            duplicate = self.search_count([
                ('id', '!=', line.id),
                ('contract_id', '=', line.contract_id.id),
                ('name', '=', line.name),
            ])
            if duplicate:
                raise ValidationError(_(
                    'Clause "%(name)s" already exists on contract %(contract)s.',
                    name=line.name,
                    contract=line.contract_id.display_name,
                ))
