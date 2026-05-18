# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TenderCommittee(models.Model):
    """Tender Committees (BEC and BAC)"""
    _name = 'sagovtender.committee'
    _description = 'Tender Committee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Committee Name',
        required=True,
        tracking=True
    )
    committee_type = fields.Selection([
        ('bec', 'Bid Evaluation Committee (BEC)'),
        ('bac', 'Bid Adjudication Committee (BAC)'),
        ('other', 'Other Committee'),
    ], string='Committee Type', required=True, default='bec', tracking=True)
    code = fields.Char(string='Committee Code')
    description = fields.Text(string='Description')

    # Members
    member_ids = fields.One2many(
        'sagovtender.committee.member',
        'committee_id',
        string='Committee Members'
    )
    chairperson_id = fields.Many2one(
        'res.users',
        string='Chairperson',
        compute='_compute_chairperson',
        store=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    member_count = fields.Integer(
        string='Number of Members',
        compute='_compute_member_count'
    )

    # Dates
    date_established = fields.Date(
        string='Date Established',
        default=fields.Date.today
    )
    date_expire = fields.Date(string='Expiry Date')

    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', default='draft', required=True, tracking=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    @api.depends('member_ids.is_chairperson', 'member_ids.user_id')
    def _compute_chairperson(self):
        """Get committee chairperson"""
        for record in self:
            chairperson = record.member_ids.filtered(lambda m: m.is_chairperson)
            record.chairperson_id = chairperson[0].user_id if chairperson else False

    @api.depends('member_ids')
    def _compute_member_count(self):
        """Count committee members"""
        for record in self:
            record.member_count = len(record.member_ids)

    def action_activate(self):
        """Activate committee"""
        self.write({'state': 'active', 'active': True})

    def action_deactivate(self):
        """Deactivate committee"""
        self.write({'state': 'inactive', 'active': False})


class TenderCommitteeMember(models.Model):
    """Committee Members"""
    _name = 'sagovtender.committee.member'
    _description = 'Committee Member'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    committee_id = fields.Many2one(
        'sagovtender.committee',
        string='Committee',
        required=True,
        ondelete='cascade'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    user_id = fields.Many2one(
        'res.users',
        string='Member',
        required=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    role = fields.Char(
        string='Role',
        help='Role or designation in the committee'
    )
    is_chairperson = fields.Boolean(
        string='Chairperson',
        default=False
    )
    is_secretary = fields.Boolean(
        string='Secretary',
        default=False
    )
    date_joined = fields.Date(
        string='Date Joined',
        default=fields.Date.today
    )
    date_left = fields.Date(string='Date Left')
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Notes')
