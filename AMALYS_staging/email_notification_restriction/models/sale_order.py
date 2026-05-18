# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def remove_followers_except_customer(self):
        for order in self:
            customer_partner = order.partner_id
            followers_to_remove = order.message_follower_ids.filtered(
                lambda follower: follower.partner_id != customer_partner
            )
            followers_to_remove.sudo().unlink()

    def action_confirm(self):
        self.remove_followers_except_customer()
        res = super().action_confirm()
        return res

    def action_cancel(self):
        self.remove_followers_except_customer()
        res = super().action_cancel()
        return res

    def action_quotation_send(self):
        self.remove_followers_except_customer()
        res = super().action_quotation_send()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            record.remove_followers_except_customer()
        return res

    def get_portal_confirmation_action(self):
        pass

    def get_mail_url(self):
        pass
