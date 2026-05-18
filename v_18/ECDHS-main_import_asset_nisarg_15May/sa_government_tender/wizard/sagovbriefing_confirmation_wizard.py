# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BriefingConfirmationWizard(models.TransientModel):
    """Wizard to confirm whether briefing session is required before starting SCM processing"""
    _name = 'sagovtender.briefing.confirmation.wizard'
    _description = 'Briefing Session Confirmation Wizard'

    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        readonly=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    message = fields.Html(
        string='Message',
        compute='_compute_message',
        readonly=True
    )

    @api.depends('tender_id')
    def _compute_message(self):
        """Display confirmation message"""
        for wizard in self:
            if wizard.tender_id:
                wizard.message = _(
                    "<p><strong>Confirmation Required:</strong></p>"
                    "<p>The 'Briefing Session Required' checkbox is currently <strong>not checked</strong> "
                    "for tender <strong>%s</strong>.</p>"
                    "<p>Please confirm whether this tender requires a briefing session or not:</p>"
                    "<ul>"
                    "<li>Click <strong>'No Briefing Session Required'</strong> to proceed without a briefing session.</li>"
                    "<li>Click <strong>'Briefing Session Required'</strong> to mark this tender as requiring a briefing session.</li>"
                    "</ul>"
                ) % wizard.tender_id.name
            else:
                wizard.message = ""

    def action_no_briefing_required(self):
        """User confirms no briefing session is required - proceed with SCM processing"""
        self.ensure_one()
        # Proceed with the original action_start_scm_processing logic
        self.tender_id.write({
            'state': 'scm_processing',
            'scm_officer_id': self.env.user.id,
            'has_briefing_session': False  # Explicitly set to False
        })
        self.tender_id.message_post(
            body=_('Tender moved to SCM processing. No briefing session required.')
        )
        return {'type': 'ir.actions.act_window_close'}

    def action_briefing_required(self):
        """User confirms briefing session is required - set flag and close wizard"""
        self.ensure_one()
        # Set the briefing session required flag to True
        self.tender_id.write({
            'has_briefing_session': True
        })
        self.tender_id.message_post(
            body=_('Briefing session marked as required.')
        )
        return {'type': 'ir.actions.act_window_close'}
