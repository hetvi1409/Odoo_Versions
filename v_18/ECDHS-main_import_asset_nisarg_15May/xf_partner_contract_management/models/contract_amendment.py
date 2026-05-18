# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ContractAmendment(models.Model):
    _name = 'contract.amendment'
    _description = 'Contract Amendment'
    _order = 'version_number desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Amendment Reference',
        required=True,
        copy=False,
        default='New',
    )
    contract_id = fields.Many2one(
        'xf.partner.contract', string='Contract',
        required=True, ondelete='cascade', index=True,
        tracking=True,
    )
    version_number = fields.Integer(
        string='Version No.', default=1, readonly=True, copy=False,
    )
    amendment_type = fields.Selection(
        selection=[
            ('variation_order', 'Variation Order'),
            ('extension_of_time', 'Extension of Time'),
            ('cession', 'Cession'),
            ('addendum', 'Addendum'),
            ('scope_change', 'Scope Change'),
            ('other', 'Other'),
        ],
        string='Amendment Type',
        required=True,
        tracking=True,
    )
    requested_by = fields.Selection(
        selection=[
            ('internal', 'Internal (Department)'),
            ('provider', 'Service Provider'),
        ],
        string='Requested By',
        required=True,
        default='internal',
    )
    description = fields.Html(string='Description / Motivation', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', string='Supporting Documents',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        readonly=True,
    )
    approved_by = fields.Many2one(
        'res.users', string='Approved By', readonly=True,
    )
    date_approved = fields.Date(string='Date Approved', readonly=True)
    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        related='contract_id.company_id', store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'contract.amendment'
                ) or 'New'
            # auto-increment version based on existing amendments on same contract
            if vals.get('contract_id'):
                existing = self.search_count([
                    ('contract_id', '=', vals['contract_id']),
                ])
                vals['version_number'] = existing + 1
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft amendments can be submitted.'))
            rec.state = 'submitted'

    def action_approve(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_('Only submitted amendments can be approved.'))
            rec.write({
                'state': 'approved',
                'approved_by': self.env.uid,
                'date_approved': fields.Date.today(),
            })
            # Notify via chatter on the contract
            rec.contract_id.message_post(
                body=_('Amendment %s (%s) approved.') % (rec.name, rec.amendment_type),
            )

    def action_reject(self):
        for rec in self:
            if rec.state not in ('submitted', 'draft'):
                raise UserError(_('Only draft or submitted amendments can be rejected.'))
            rec.state = 'rejected'

    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'rejected':
                rec.state = 'draft'
