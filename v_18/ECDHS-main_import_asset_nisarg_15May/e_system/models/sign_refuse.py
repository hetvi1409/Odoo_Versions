# -*- coding: utf-8 -*-
import re
from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import UserError

# Matches at least one sequence of two or more alphabetic characters,
# ensuring the reason is not just a single character or punctuation.
_WORD_RE = re.compile(r'[a-zA-Z]{2,}')


class SignLog(models.Model):
    _inherit = 'sign.log'

    refusal_reason = fields.Text(string="Refuse Reason", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Inject refusal_reason from context into 'refuse' log entries."""
        refusal_reason = self.env.context.get('refuse_reason')
        if refusal_reason:
            for vals in vals_list:
                if vals.get('action') == 'refuse' and not vals.get('refusal_reason'):
                    vals['refusal_reason'] = refusal_reason
        return super().create(vals_list)


class SignRequestItem(models.Model):
    _inherit = 'sign.request.item'

    def _refuse(self, refusal_reason):
        """Refuse request item and post a clearly labeled refusal reason in chatter."""
        self.ensure_one()
        if not self.env.su:
            raise UserError(_("This function can only be called with sudo."))
        if self.state != 'sent' or self.sign_request_id.state != 'sent':
            raise UserError(_("This sign request item cannot be refused"))

        stripped = (refusal_reason or '').strip()
        if not stripped or not _WORD_RE.search(stripped):
            raise UserError(_(
                "A refusal reason is required and must contain at least one real word. "
                "A single character or punctuation alone is not accepted."
            ))

        normalized = refusal_reason

        self.env['sign.log'].create({
            'sign_request_item_id': self.id,
            'action': 'refuse',
            'refusal_reason': normalized,
        })
        self.write({'signing_date': fields.Date.context_today(self), 'state': 'canceled'})

        refuse_user = self.partner_id.user_ids[:1]
        if refuse_user and refuse_user.has_group('sign.group_sign_user'):
            self.sign_request_id.activity_feedback(['mail.mail_activity_data_todo'], user_id=refuse_user.id)

        message_post = _(
            "The signature has been refused by %(partner)s(%(role)s)",
            partner=self.partner_id.name,
            role=self.role_id.name,
        )
        message_post = Markup(
            '{}<p><strong class="o_refuse_reason_label">{}</strong></p><p class="o_refuse_reason_value" style="white-space: pre">{}</p>'
        ).format(message_post, _("Refuse Reason:"), normalized)
        self.sign_request_id.message_post(body=message_post)
        self.sign_request_id._refuse(self.partner_id, normalized)
