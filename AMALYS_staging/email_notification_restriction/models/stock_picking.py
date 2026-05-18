# -*- coding: utf-8 -*-
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def remove_followers_except_customer(self):
        for order in self:
            customer_partner = order.partner_id
            followers_to_remove = order.message_follower_ids.filtered(
                lambda follower: follower.partner_id != customer_partner
            )
            followers_to_remove.unlink()

    def button_validate(self):
        self.remove_followers_except_customer()
        res = super().button_validate()
        return res