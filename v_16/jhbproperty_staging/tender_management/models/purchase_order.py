from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    tender_bid_id = fields.Many2one('tender.bid', string='Related Tender Bid')

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.state == 'purchase' and order.tender_bid_id:
                order.tender_bid_id.state = 'purchase'
        return res
