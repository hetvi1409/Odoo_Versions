# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError  # ValidationError kept for sequence guard


class EcdhsContractSignatory(models.Model):
    _name = 'ecdhs.contract.signatory'
    _description = 'Contract Signatory'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence', default=10)
    is_service_provider = fields.Boolean(
        'Service Provider', default=False,
        help='Auto-set when this row represents the contract service provider.',
    )
    contract_id = fields.Many2one(
        'ecdhs.contract', string='Contract', ondelete='cascade', required=True)
    # SP rows use partner_id; internal signatories use user_id.
    partner_id = fields.Many2one(
        'res.partner', string='Signatory (Partner)', readonly=True,
        help='Set automatically from the contract Service Provider.',
    )
    user_id = fields.Many2one(
        'res.users', string='Signatory',
        domain="[('id', 'not in', existing_user_ids)]")
    role_designation = fields.Char(string='Role/Designation')
    existing_user_ids = fields.Many2many(
        'res.users', compute='_compute_existing_user_ids')
    required = fields.Boolean(string='Required', default=True)
    status = fields.Selection([
        ('Signed', 'Signed'),
        ('Pending', 'Pending'),
        ('Declined', 'Declined'),
    ], string='Status', default='Pending')
    comment = fields.Text('Comment')
    date = fields.Datetime('Signed On', readonly=True, copy=False)
    sign_initials = fields.Binary('Digital Initials', copy=False)
    sign_request_item_id = fields.Many2one(
        'sign.request.item',
        string='Sign Request Item',
        readonly=True,
        copy=False,
        ondelete='set null',
        help='Linked sign.request.item record for this signatory.',
    )

    @api.depends('contract_id.signatory_ids.user_id')
    def _compute_existing_user_ids(self):
        for rec in self:
            rec.existing_user_ids = rec.contract_id.signatory_ids.mapped('user_id')

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------

    @api.constrains('sequence', 'is_service_provider')
    def _check_sp_sequence(self):
        for rec in self:
            if rec.is_service_provider and rec.sequence != 1:
                raise ValidationError(_(
                    'The Service Provider signatory must remain at position 1 '
                    'and cannot be resequenced.'
                ))

    # -------------------------------------------------------------------------
    # ORM overrides
    # -------------------------------------------------------------------------

    def write(self, vals):
        for rec in self:
            if rec.is_service_provider:
                if 'sequence' in vals and vals['sequence'] != 1:
                    raise UserError(_(
                        'The Service Provider signatory is locked at position 1 '
                        'and cannot be moved.'
                    ))
                if 'is_service_provider' in vals and not vals['is_service_provider']:
                    raise UserError(_(
                        'Cannot remove the Service Provider flag from this signatory.'
                    ))
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get('_bypass_sp_unlink'):
            for rec in self:
                if rec.is_service_provider:
                    raise UserError(_(
                        'The Service Provider signatory cannot be deleted manually. '
                        'Change or clear the Service Provider on the contract instead.'
                    ))
        return super().unlink()

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def action_sign_line(self):
        """Allow the assigned signatory to sign and capture the date."""
        for rec in self:
            if rec.is_service_provider:
                raise UserError(_(
                    'The Service Provider signatory must sign through the provider signing process, not the backend sign button.'
                ))
            if not rec.user_id:
                raise UserError(_(
                    'Assign a signatory user before signing this line.'
                ))
            if rec.env.user != rec.user_id:
                raise UserError(_(
                    'Only the assigned signatory user (%(user)s) can sign this line.',
                    user=rec.user_id.display_name,
                ))
            if rec.status == 'Signed' and rec.sign_initials:
                continue

            rec.write({
                'date': fields.Datetime.now(),
                'status': 'Signed',
                'sign_initials': rec.env.user.partner_id.avatar_128,
            })

        return {'type': 'ir.actions.client', 'tag': 'reload'}
