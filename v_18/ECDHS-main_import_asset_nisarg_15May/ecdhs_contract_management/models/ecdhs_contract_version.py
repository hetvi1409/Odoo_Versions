# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.exceptions import UserError


class EcdhsContractVersion(models.Model):
    _name = 'ecdhs.contract.version'
    _description = 'Contract Version'
    _order = 'id desc'

    contract_id = fields.Many2one('ecdhs.contract', string='Contract', required=True, ondelete='cascade')
    version_number = fields.Char(string='Version', required=True)
    contract_name = fields.Char(string='Contract Reference')
    comment = fields.Text(string='Comment')
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
    contract_terms_summary = fields.Html(string='Contract Terms Snapshot')

    def action_revert_version(self):
        self.ensure_one()
        locked_states = ('fully_signed', 'cover_letter_sent', 'cover_letter_signed', 'active', 'expiring', 'terminated', 'cancelled')
        if self.contract_id.state in locked_states:
            raise UserError(_('You cannot revert contract terms in the current status.'))

        self.contract_id.write({'contract_terms_summary': self.contract_terms_summary})
        self.contract_id.message_post(
            body=_('Contract terms were reverted to version <strong>%s</strong>.', self.version_number),
            subtype_xmlid='mail.mt_note',
        )
        return True
