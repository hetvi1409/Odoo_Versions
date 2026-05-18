# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BACReview(models.Model):
    """BAC Review - Step 10 of Tender Process"""
    _name = 'sagovtender.bac.review'
    _description = 'BAC Review'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.bac.review')
    )
    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    committee_id = fields.Many2one(
        'sagovtender.committee',
        string='BAC Committee',
        required=True,
        domain=[('committee_type', '=', 'bac')],
        tracking=True,
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    review_date = fields.Date(
        string='Review Date',
        default=fields.Date.today,
        tracking=True
    )

    # BEC Evaluation Summary
    bec_report_id = fields.Many2one(
        'ir.attachment',
        string='BEC Report',
        help='BEC evaluation report document',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    bec_recommendation_id = fields.Many2one(
        'sagovtender.bid',
        string='BEC Recommended Bid',
        domain="[('tender_id', '=', tender_id)]",
        help='Bid recommended by BEC',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    bec_recommendation_notes = fields.Text(
        string='BEC Recommendation Summary'
    )

    # BAC Review
    review_notes = fields.Html(
        string='Review Notes',
        help='BAC review findings and comments'
    )
    bac_recommendation = fields.Selection([
        ('approve', 'Approve BEC Recommendation'),
        ('reject', 'Reject Recommendation'),
        ('refer_back', 'Refer Back to BEC'),
        ('cancel_tender', 'Cancel Tender'),
    ], string='BAC Recommendation', tracking=True)
    recommendation_reason = fields.Text(
        string='Recommendation Reason',
        help='Reason for BAC recommendation'
    )

    # BAC Decision
    approved_bid_id = fields.Many2one(
        'sagovtender.bid',
        string='Approved Bid',
        tracking=True,
        help='Bid approved by BAC for award'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    approval_notes = fields.Text(string='Approval Notes')

    # BAC Report
    bac_report_id = fields.Many2one(
        'ir.attachment',
        string='BAC Report',
        help='BAC report document'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    report_signed = fields.Boolean(
        string='Report Signed',
        default=False
    )
    signature_type = fields.Selection([
        ('chairperson', 'Chairperson Only'),
        ('all_members', 'All Committee Members'),
    ], string='Signature Type', default='chairperson')

    # Signatories
    signatory_ids = fields.One2many(
        'sagovtender.bac.signatory',
        'review_id',
        string='Signatories'
    )
    all_signed = fields.Boolean(
        string='All Required Signatures',
        compute='_compute_all_signed',
        store=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('completed', 'Completed'),
        ('referred_back', 'Referred Back to BEC'),
    ], string='Status', default='draft', required=True, tracking=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    @api.depends('signatory_ids.signed', 'signature_type', 'report_signed')
    def _compute_all_signed(self):
        """Check if all required signatures are obtained"""
        for record in self:
            if not record.report_signed:
                record.all_signed = False
                continue

            if record.signature_type == 'chairperson':
                # Check if chairperson signed
                chairperson = record.signatory_ids.filtered(
                    lambda s: s.is_chairperson
                )
                record.all_signed = bool(chairperson and chairperson.signed)
            else:  # all_members
                # Check if all members signed
                if record.signatory_ids:
                    record.all_signed = all(record.signatory_ids.mapped('signed'))
                else:
                    record.all_signed = False

    def action_start_review(self):
        """Start BAC review"""
        self.ensure_one()
        if not self.tender_id.bec_completed:
            raise UserError('BEC evaluation must be completed first.')

        # Load BEC recommendation
        top_evaluation = self.tender_id.evaluation_ids.filtered(
            lambda e: e.state == 'completed' and e.functionality_passed
        ).sorted(key=lambda e: e.total_score, reverse=True)

        if top_evaluation:
            self.bec_recommendation_id = top_evaluation[0].bid_id

        # Create signatory records
        self._create_signatories()

        self.write({'state': 'review'})
        self.message_post(body='BAC review started.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('BAC Review'),
            'res_model': 'sagovtender.bac.review',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'edit',
            },
        }

    def action_approve_bec(self):
        """Approve BEC recommendation"""
        self.ensure_one()
        if not self.bec_recommendation_id:
            raise UserError('No BEC recommendation to approve.')

        self.write({
            'bac_recommendation': 'approve',
            'approved_bid_id': self.bec_recommendation_id.id,
            'state': 'completed'
        })

        # Update tender
        self.tender_id.write({
            'bac_recommendation': 'approve'
        })

        self.message_post(body='BEC recommendation approved by BAC.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('BAC Review'),
            'res_model': 'sagovtender.bac.review',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_reject(self):
        """Reject BEC recommendation"""
        self.write({
            'bac_recommendation': 'reject',
            'state': 'completed'
        })
        self.tender_id.write({'bac_recommendation': 'reject'})
        self.message_post(body='BEC recommendation rejected by BAC.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('BAC Review'),
            'res_model': 'sagovtender.bac.review',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_refer_back(self):
        """Refer back to BEC"""
        self.write({
            'bac_recommendation': 'refer_back',
            'state': 'referred_back'
        })
        self.tender_id.write({
            'state': 'evaluation',
            'bac_recommendation': 'refer_back'
        })
        self.message_post(body='Tender referred back to BEC for re-evaluation.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('BAC Review'),
            'res_model': 'sagovtender.bac.review',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_recommend_cancel(self):
        """Recommend tender cancellation"""
        self.write({
            'bac_recommendation': 'cancel_tender',
            'state': 'completed'
        })
        self.tender_id.write({'bac_recommendation': 'cancel_tender'})
        self.message_post(body='BAC recommends cancellation of sagovtender.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('BAC Review'),
            'res_model': 'sagovtender.bac.review',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def action_finalize(self):
        """Finalize BAC review"""
        self.ensure_one()
        if not self.all_signed:
            raise UserError('All required signatures must be obtained.')
        if not self.bac_recommendation:
            raise UserError('Please provide BAC recommendation.')

        self.write({'state': 'completed'})
        self.message_post(body='BAC review finalized.')
        return {
            'type': 'ir.actions.act_window',
            'name': _('BAC Review'),
            'res_model': 'sagovtender.bac.review',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
        }

    def _create_signatories(self):
        """Create signatory records for BAC members"""
        self.ensure_one()
        # Clear existing
        self.signatory_ids.unlink()

        # Create for each committee member
        for member in self.committee_id.member_ids:
            self.env['sagovtender.bac.signatory'].create({
                'review_id': self.id,
                'user_id': member.user_id.id,
                'is_chairperson': member.is_chairperson,
            })

    def action_print_report(self):
        """Print BAC report"""
        return self.env.ref('sa_government_tender.action_report_sagovbac_review').report_action(self)


class BACSignatory(models.Model):
    """BAC Report Signatories"""
    _name = 'sagovtender.bac.signatory'
    _description = 'BAC Signatory'

    review_id = fields.Many2one(
        'sagovtender.bac.review',
        string='BAC Review',
        required=True,
        ondelete='cascade'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    user_id = fields.Many2one(
        'res.users',
        string='Committee Member',
        required=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    is_chairperson = fields.Boolean(
        string='Chairperson',
        default=False
    )
    is_secretary = fields.Boolean(
        string='Secretary',
        default=False
    )
    signed = fields.Boolean(
        string='Signed',
        default=False
    )
    signature = fields.Binary(string='Signature')
    signature_date = fields.Datetime(string='Signature Date')
    comments = fields.Text(string='Comments')
