from odoo import models, fields, _
from odoo.exceptions import UserError


class BidAward(models.Model):
    _name = 'bid.award'
    _description = 'Bid Award'
    _rec_name = 'bid_id'

    bid_id = fields.Many2one('tender.bid', string='Bid')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    subject = fields.Char(string='Subject')
    body = fields.Text(string='Body')
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Attachment")
    #function
    def action_send_award_letter(self):
        if not self.vendor_id.email:
            raise UserError("The vendor does not have an email address.")
        template = self.env.ref('tender_management.email_template_bid_award')
        template.send_mail(self.id, force_send=True)
        self.bid_id.state = 'award_letter_sent'
