# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    email_to_partners = fields.Many2many('res.partner', string="Email To Partner", compute="_set_email_to_partners")

    @api.depends('partner_id')
    def _set_email_to_partners(self):
        # Fetch invoice partner's invoice address. if not, send mail to invoice partner.
        for rec in self:
            rec.email_to_partners = rec.partner_id.child_ids.filtered(lambda child: child.type == 'invoice') or rec.partner_id

    def remove_followers_except_customer(self):
        for order in self:
            customer_partner = order.partner_id
            followers_to_remove = order.message_follower_ids.filtered(
                lambda follower: follower.partner_id != customer_partner
            )
            followers_to_remove.unlink()

    def action_invoice_sent(self):
        self.remove_followers_except_customer()
        res = super().action_invoice_sent()
        return res

    def action_post(self):
        self.remove_followers_except_customer()
        res = super().action_post()
        return res