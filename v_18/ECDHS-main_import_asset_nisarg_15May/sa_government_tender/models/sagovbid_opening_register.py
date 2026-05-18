# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BidOpeningRegister(models.Model):
    """Bid Opening Register - Step 6 of Tender Process"""
    _name = 'sagovtender.bid.opening.register'
    _description = 'Bid Opening Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Register Number',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.bid.opening')
    )
    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    opening_date = fields.Datetime(
        string='Opening Date/Time',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    opening_location = fields.Char(
        string='Opening Location',
        help='Physical location where bids were opened'
    )
    line_ids = fields.One2many(
        'sagovtender.bid.opening.line',
        'register_id',
        string='Opening Lines'
    )
    stakeholder_ids = fields.One2many(
        'sagovtender.opening.stakeholder',
        'register_id',
        string='Stakeholders Present'
    )
    all_signed = fields.Boolean(
        string='All Stakeholders Signed',
        compute='_compute_all_signed',
        store=True
    )
    published = fields.Boolean(
        string='Published Online',
        default=False,
        tracking=True
    )
    published_url = fields.Char(
        string='Published URL',
        help='URL where register is published'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('opened', 'Opened'),
        ('completed', 'Completed'),
        ('published', 'Published'),
    ], string='Status', default='draft', required=True, tracking=True)
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    @api.depends('stakeholder_ids.signed')
    def _compute_all_signed(self):
        """Check if all stakeholders have signed"""
        for record in self:
            if record.stakeholder_ids:
                record.all_signed = all(record.stakeholder_ids.mapped('signed'))
            else:
                record.all_signed = False

    def action_load_bids(self):
        """Load bids from tender"""
        self.ensure_one()
        # Clear existing lines
        self.line_ids.unlink()

        # Create lines for each bid
        for bid in self.tender_id.bid_ids.filtered(lambda b: b.state == 'submitted'):
            self.env['sagovtender.bid.opening.line'].create({
                'register_id': self.id,
                'bid_id': bid.id,
                'partner_id': bid.partner_id.id,
                'bid_amount': bid.bid_amount,
                'submission_date': bid.submission_date,
            })

        self.message_post(body='Bids loaded into opening register.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bid Opening Register'),
            'res_model': 'sagovtender.bid.opening.register',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',
            },
        }

    def action_conduct_opening(self):
        """Conduct bid opening"""
        self.ensure_one()
        if not self.line_ids:
            raise UserError('No bids to open. Please load bids first.')

        # Mark all bids as opened
        for line in self.line_ids:
            line.bid_id.action_open()

        self.write({
            'state': 'opened',
            'opening_date': fields.Datetime.now()
        })
        self.message_post(body='Bid opening conducted.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bid Opening Register'),
            'res_model': 'sagovtender.bid.opening.register',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',
            },
        }

    def action_complete(self):
        """Complete opening register"""
        self.ensure_one()
        if not self.all_signed:
            raise UserError('All stakeholders must sign before completing.')

        self.write({'state': 'completed'})
        self.message_post(body='Opening register completed.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bid Opening Register'),
            'res_model': 'sagovtender.bid.opening.register',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_publish(self):
        """Publish opening register online"""
        self.ensure_one()
        if self.state != 'completed':
            raise UserError('Register must be completed before publishing.')

        self.write({
            'state': 'published',
            'published': True
        })
        self.message_post(body='Opening register published online.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bid Opening Register'),
            'res_model': 'sagovtender.bid.opening.register',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_print_register(self):
        """Print opening register"""
        return self.env.ref('sa_government_tender.action_report_sagovbid_opening_register').report_action(self)


class BidOpeningLine(models.Model):
    """Bid Opening Register Lines"""
    _name = 'sagovtender.bid.opening.line'
    _description = 'Bid Opening Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    register_id = fields.Many2one(
        'sagovtender.bid.opening.register',
        string='Register',
        required=True,
        ondelete='cascade'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    bid_id = fields.Many2one(
        'sagovtender.bid',
        string='Bid',
        required=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    partner_id = fields.Many2one(
        'res.partner',
        string='Bidder',
        required=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    bid_amount = fields.Monetary(
        string='Bid Amount',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    submission_date = fields.Datetime(string='Submission Date')
    notes = fields.Text(string='Notes')


class OpeningStakeholder(models.Model):
    """Stakeholders Present at Opening"""
    _name = 'sagovtender.opening.stakeholder'
    _description = 'Opening Stakeholder'

    register_id = fields.Many2one(
        'sagovtender.bid.opening.register',
        string='Register',
        required=True,
        ondelete='cascade'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    name = fields.Char(string='Name', required=True)
    title = fields.Char(string='Title/Position')
    organization = fields.Char(string='Organization')
    stakeholder_type = fields.Selection([
        ('internal', 'Internal Staff'),
        ('audit', 'Internal Audit'),
        ('bidder', 'Bidder Representative'),
        ('public', 'Public Observer'),
        ('other', 'Other'),
    ], string='Type', required=True, default='internal')
    signed = fields.Boolean(string='Signed', default=False)
    signature = fields.Binary(string='Signature')
    signature_date = fields.Datetime(string='Signature Date')
