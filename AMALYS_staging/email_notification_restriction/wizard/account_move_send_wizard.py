from odoo import api, models

class AccountMoveSendWizard(models.TransientModel):
    _inherit = 'account.move.send.wizard'

    @api.depends('mail_template_id', 'mail_lang')
    def _compute_mail_subject_body_partners(self):
        # Call the base compute first
        super()._compute_mail_subject_body_partners()

        for wizard in self:
            move = wizard.move_id
            commercial_partner = move.commercial_partner_id

            if commercial_partner:
                extra_partners = self.env['res.partner']
                if commercial_partner.email:
                    extra_partners |= commercial_partner
                extra_partners |= commercial_partner.child_ids.filtered( lambda c: c.type == 'invoice' and c.email)

                # Add extra recipients (union so no duplicates)
                wizard.mail_partner_ids |= extra_partners
