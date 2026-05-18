# -*- coding: utf-8 -*-
# Eastern Cape Department of Human Settlements
# Email Template Preview – singleton settings-style page

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EcdhsMailTemplatePreview(models.Model):
    _name = 'ecdhs.mail.template.preview'
    _description = 'Email Template Preview'

    # Singleton: there is always exactly one record.
    name = fields.Char(default='Email Template Preview', readonly=True)

    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'ecdhs.contract')],
        help='Select an email template defined for the ecdhs.contract model.',
    )
    service_provider_id = fields.Many2one(
        'res.partner',
        string='Service Provider',
        help='Optionally filter the contract list to a specific service provider.',
    )
    contract_id = fields.Many2one(
        'ecdhs.contract',
        string='Test Contract',
        help='Contract record used to render dynamic template variables.',
    )
    preview_subject = fields.Char(
        string='Rendered Subject',
        readonly=True,
    )
    preview_body_html = fields.Html(
        string='Rendered Email Body',
        readonly=True,
        sanitize=False,
    )

    # -------------------------------------------------------------------------
    # Onchange helpers
    # -------------------------------------------------------------------------

    @api.onchange('service_provider_id')
    def _onchange_service_provider_id(self):
        """Clear downstream fields when provider changes."""
        self.contract_id = False
        self.preview_subject = False
        self.preview_body_html = False

    @api.onchange('mail_template_id', 'contract_id')
    def _onchange_clear_preview(self):
        """Clear rendered output when selection changes."""
        self.preview_subject = False
        self.preview_body_html = False

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def action_load_preview(self):
        """Render the selected template against the chosen contract and write
        the output into the preview fields so the form refreshes in place."""
        self.ensure_one()
        if not self.mail_template_id:
            raise UserError(_('Please select an email template.'))
        if not self.contract_id:
            raise UserError(_('Please select a test contract to render the template against.'))

        rendered_subject = self.mail_template_id._render_field(
            'subject', self.contract_id.ids,
        )
        rendered_body = self.mail_template_id._render_field(
            'body_html', self.contract_id.ids,
        )

        self.write({
            'preview_subject': rendered_subject.get(self.contract_id.id) or False,
            'preview_body_html': rendered_body.get(self.contract_id.id) or False,
        })
        # Reload the same form so rendered values are visible immediately
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
