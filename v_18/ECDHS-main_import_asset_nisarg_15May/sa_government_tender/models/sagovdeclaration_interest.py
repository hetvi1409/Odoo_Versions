# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DeclarationInterest(models.Model):
    """Declaration of Interest - Step 8 of Tender Process"""
    _name = 'sagovtender.declaration.interest'
    _description = 'Declaration of Interest'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.declaration')
    )
    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    user_id = fields.Many2one(
        'res.users',
        string='Declarant',
        required=True,
        tracking=True,
        help='Committee member making declaration'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    committee_id = fields.Many2one(
        'sagovtender.committee',
        string='Committee',
        required=True,
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    committee_role = fields.Char(
        string='Role in Committee',
        help='Role/position in the committee'
    )
    declaration_date = fields.Date(
        string='Declaration Date',
        default=fields.Date.today,
        tracking=True
    )

    # Declaration Questions
    has_conflict = fields.Boolean(
        string='Has Conflict of Interest',
        default=False,
        tracking=True,
        help='Does the declarant have any conflict of interest?'
    )
    conflict_details = fields.Text(
        string='Conflict Details',
        help='Details of any conflict of interest'
    )

    # Specific conflicts
    family_relationship = fields.Boolean(
        string='Family Relationship',
        help='Related to any bidder representative'
    )
    business_interest = fields.Boolean(
        string='Business Interest',
        help='Has business interest in any bidder'
    )
    financial_interest = fields.Boolean(
        string='Financial Interest',
        help='Has financial interest in any bidder'
    )
    other_conflict = fields.Boolean(
        string='Other Conflict',
        help='Any other conflict of interest'
    )

    # Related Bidders
    conflicted_partner_ids = fields.Many2many(
        'res.partner',
        string='Related Bidders',
        help='Bidders with whom there is a conflict'
    )

    # Declaration Statement
    declaration_statement = fields.Html(
        string='Declaration Statement',
        default=lambda self: self._default_declaration_statement()
    )
    declaration_acknowledged = fields.Boolean(
        string='Acknowledged',
        help='Declarant acknowledges the statement'
    )

    # Signature
    signature = fields.Binary(string='Signature')
    signature_date = fields.Datetime(string='Signature Date')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('recused', 'Recused from Evaluation'),
        ('cleared', 'Cleared to Participate'),
    ], string='Status', default='draft', required=True, tracking=True)

    notes = fields.Text(string='Additional Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    def _default_declaration_statement(self):
        """Default declaration statement"""
        return """
        <p><strong>DECLARATION OF INTEREST</strong></p>
        <p>I, the undersigned, hereby declare that:</p>
        <ol>
            <li>I have no direct or indirect personal or private business interest in any bidder
                or any of their parent or subsidiary companies, directors, or partners.</li>
            <li>I have no family relationship with any bidder, their directors, partners,
                or authorized representatives.</li>
            <li>I have no financial interest in the outcome of this tender process.</li>
            <li>I will recuse myself from the evaluation process if any conflict of interest arises.</li>
            <li>I understand that failure to declare a conflict of interest may result in
                criminal charges and/or disciplinary action.</li>
        </ol>
        <p>I understand that this declaration is made in terms of the PFMA, Treasury Regulations,
        and applicable Supply Chain Management policies.</p>
        """

    @api.onchange('family_relationship', 'business_interest',
                  'financial_interest', 'other_conflict')
    def _onchange_conflicts(self):
        """Auto-set has_conflict based on specific conflicts"""
        if any([self.family_relationship, self.business_interest,
                self.financial_interest, self.other_conflict]):
            self.has_conflict = True

    def action_submit(self):
        """Submit declaration"""
        for record in self:
            if not record.declaration_acknowledged:
                raise UserError('Please acknowledge the declaration statement.')

            if record.has_conflict and not record.conflict_details:
                raise UserError('Please provide details of the conflict of interest.')

            # Determine state based on conflict
            if record.has_conflict:
                new_state = 'recused'
                msg = 'Declaration submitted. Declarant recused from evaluation due to conflict.'
            else:
                new_state = 'cleared'
                msg = 'Declaration submitted. Declarant cleared to participate in evaluation.'

            record.write({
                'state': new_state,
                'signature_date': fields.Datetime.now()
            })
            record.message_post(body=msg)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Declaration of Interest'),
            'res_model': 'sagovtender.declaration.interest',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_reset_to_draft(self):
        """Reset to draft"""
        self.write({'state': 'draft'})
        self.message_post(body='Declaration reset to draft.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Declaration of Interest'),
            'res_model': 'sagovtender.declaration.interest',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',
            },
        }

    def action_print_declaration(self):
        """Print declaration form"""
        return self.env.ref('sa_government_tender.action_report_sagovdeclaration_interest').report_action(self)
