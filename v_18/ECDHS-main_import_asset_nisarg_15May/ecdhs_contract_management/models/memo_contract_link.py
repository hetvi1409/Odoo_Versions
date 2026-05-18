# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MemoContractLink(models.Model):
    _inherit = 'memo.memo'

    ecdhs_contract_ids = fields.One2many(
        'ecdhs.contract',
        'memo_id',
        string='Contracts Linked',
    )
    contract_selection_ids = fields.Many2many(
        'ecdhs.contract',
        string='Contracts Linked',
        compute='_compute_contract_selection_ids',
        inverse='_inverse_contract_selection_ids',
    )

    @api.depends('ecdhs_contract_ids')
    def _compute_contract_selection_ids(self):
        for memo in self:
            memo.contract_selection_ids = memo.ecdhs_contract_ids

    def _inverse_contract_selection_ids(self):
        for memo in self:
            selected = memo.contract_selection_ids
            currently_linked = memo.ecdhs_contract_ids

            to_link = selected - currently_linked
            to_unlink = currently_linked - selected

            if to_link:
                to_link.write({'memo_id': memo.id})
            if to_unlink:
                to_unlink.write({'memo_id': False})
