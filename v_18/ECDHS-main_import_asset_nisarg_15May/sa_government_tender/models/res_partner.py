# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """Extend res.partner for SA Government vendor requirements"""
    _inherit = 'res.partner'

    # Company Registration
    company_registration_number = fields.Char(
        string='Company Registration Number',
        help='Company/Organization registration number (e.g., 2021/123456/07)'
    )

    # CSD Registration
    csd_registered = fields.Boolean(
        string='CSD Registered',
        help='Registered on Central Supplier Database'
    )
    csd_number = fields.Char(
        string='CSD Number',
        help='Central Supplier Database registration number'
    )
    csd_registration_date = fields.Date(string='CSD Registration Date')

    # Tax Compliance
    tax_clearance_number = fields.Char(string='Tax Clearance Number')
    tax_clearance_expiry = fields.Date(string='Tax Clearance Expiry')
    tax_compliant = fields.Boolean(
        string='Tax Compliant',
        compute='_compute_tax_compliant',
        help='Valid tax clearance certificate'
    )

    # COID
    coid_number = fields.Char(
        string='COID Number',
        help='Compensation for Occupational Injuries and Diseases number'
    )
    coid_compliant = fields.Boolean(
        string='COID Compliant',
        default=False
    )

    # B-BBEE
    bbbee_level = fields.Selection([
        ('1', 'Level 1'),
        ('2', 'Level 2'),
        ('3', 'Level 3'),
        ('4', 'Level 4'),
        ('5', 'Level 5'),
        ('6', 'Level 6'),
        ('7', 'Level 7'),
        ('8', 'Level 8'),
        ('0', 'Non-Compliant'),
    ], string='B-BBEE Level', help='Broad-Based Black Economic Empowerment Level')
    bbbee_certificate_number = fields.Char(string='B-BBEE Certificate Number')
    bbbee_certificate_date = fields.Date(string='B-BBEE Certificate Date')
    bbbee_expiry_date = fields.Date(string='B-BBEE Expiry Date')
    bbbee_valid = fields.Boolean(
        string='B-BBEE Valid',
        compute='_compute_bbbee_valid'
    )

    # Blacklisting
    is_blacklisted = fields.Boolean(
        string='Blacklisted',
        default=False,
        help='Blacklisted by National Treasury'
    )
    blacklist_reason = fields.Text(string='Blacklist Reason')
    blacklist_date = fields.Date(string='Blacklist Date')

    # Tender Statistics
    sagovtender_bid_ids = fields.One2many(
        'sagovtender.bid',
        'partner_id',
        string='Tender Bids'
    )
    sagovtender_bid_count = fields.Integer(
        string='# of Bids',
        compute='_compute_tender_stats'
    )
    sagovtender_award_count = fields.Integer(
        string='Tenders Won',
        compute='_compute_tender_stats'
    )
    total_tender_value = fields.Monetary(
        string='Total Tender Value',
        compute='_compute_tender_stats',
        currency_field='currency_id'
    )

    @api.depends('tax_clearance_expiry')
    def _compute_tax_compliant(self):
        """Check if tax clearance is valid"""
        for record in self:
            if record.tax_clearance_expiry:
                record.tax_compliant = fields.Date.today() <= record.tax_clearance_expiry
            else:
                record.tax_compliant = False

    @api.constrains('email')
    def _check_email_format(self):
        """Validate email format"""
        import re
        for record in self:
            if record.email:
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(pattern, record.email):
                    raise ValidationError(_("Invalid email format for %s") % record.name)

    @api.constrains('csd_number')
    def _check_csd_number_unique(self):
        """Ensure CSD number uniqueness"""
        for record in self:
            if record.csd_number:
                existing = self.search([
                    ('csd_number', '=', record.csd_number),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_(
                        "CSD Number %s is already registered to %s"
                    ) % (record.csd_number, existing[0].name))

    @api.constrains('company_registration_number')
    def _check_company_reg_unique(self):
        """Ensure company registration number uniqueness"""
        for record in self:
            if record.company_registration_number:
                existing = self.search([
                    ('company_registration_number', '=', record.company_registration_number),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_(
                        "Company Registration Number %s is already registered to %s"
                    ) % (record.company_registration_number, existing[0].name))
                record.tax_compliant = record.tax_clearance_expiry >= fields.Date.today()
            else:
                record.tax_compliant = False

    @api.constrains('csd_number', 'company_registration_number', 'email')
    def _check_unique_supplier_identifiers(self):
        """Ensure CSD number, Company Registration number, and Email are unique for suppliers"""
        for record in self:
            # Only check for suppliers (supplier_rank > 0)
            if record.supplier_rank > 0:
                # Check CSD Number uniqueness
                if record.csd_number:
                    duplicate = self.search([
                        ('id', '!=', record.id),
                        ('csd_number', '=', record.csd_number),
                        ('csd_number', '!=', False)
                    ], limit=1)
                    if duplicate:
                        raise ValidationError(
                            f"A supplier with CSD Number '{record.csd_number}' already exists: {duplicate.name} (ID: {duplicate.id})"
                        )

                # Check Company Registration Number uniqueness
                if record.company_registration_number:
                    duplicate = self.search([
                        ('id', '!=', record.id),
                        ('company_registration_number', '=', record.company_registration_number),
                        ('company_registration_number', '!=', False)
                    ], limit=1)
                    if duplicate:
                        raise ValidationError(
                            f"A supplier with Company Registration Number '{record.company_registration_number}' already exists: {duplicate.name} (ID: {duplicate.id})"
                        )

                # Check Email uniqueness for suppliers
                if record.email:
                    duplicate = self.search([
                        ('id', '!=', record.id),
                        ('email', '=', record.email),
                        ('email', '!=', False),
                        ('supplier_rank', '>', 0)
                    ], limit=1)
                    if duplicate:
                        raise ValidationError(
                            f"A supplier with email '{record.email}' already exists: {duplicate.name} (ID: {duplicate.id})"
                        )

                # Check if this partner is linked to another user account
                if record.user_ids:
                    for user in record.user_ids:
                        # Check if another partner has a user with the same login
                        if user.login and user.login == record.email:
                            other_users = self.env['res.users'].search([
                                ('id', '!=', user.id),
                                ('login', '=', user.login),
                                ('partner_id', '!=', record.id)
                            ], limit=1)
                            if other_users:
                                raise ValidationError(
                                    f"A user account with email '{user.login}' is already linked to another supplier: {other_users.partner_id.name} (ID: {other_users.partner_id.id})"
                                )

    @api.depends('bbbee_expiry_date')
    def _compute_bbbee_valid(self):
        """Check if B-BBEE certificate is valid"""
        for record in self:
            if record.bbbee_expiry_date:
                record.bbbee_valid = record.bbbee_expiry_date >= fields.Date.today()
            else:
                record.bbbee_valid = False

    @api.depends('sagovtender_bid_ids')
    def _compute_tender_stats(self):
        """Calculate tender statistics"""
        for record in self:
            bids = record.sagovtender_bid_ids
            record.sagovtender_bid_count = len(bids)
            awarded_bids = bids.filtered(lambda b: b.state == 'awarded')
            record.sagovtender_award_count = len(awarded_bids)
            record.total_tender_value = sum(awarded_bids.mapped('bid_amount'))

    def action_view_sagovtender_bids(self):
        """View partner's tender bids"""
        self.ensure_one()
        return {
            'name': 'Tender Bids',
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.bid',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
