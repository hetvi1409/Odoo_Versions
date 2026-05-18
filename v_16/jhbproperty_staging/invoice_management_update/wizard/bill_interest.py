from odoo import fields, models, _


class BillInterest(models.TransientModel):
    _name = 'bill.interest'
    _description = 'Bill interest'

    bill_ids = fields.Many2many('account.move',
                               domain="[('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]")
    # partner_id = fields.Many2one(related='bill_id.partner_id')
    # payment_state = fields.Selection(related='bill_id.payment_state')

    def action_submit(self):
        """Method for submit the interest"""
        bills_ = []
        for bill in self.bill_ids:
            product = self.env.ref(
                'invoice_management_update.product_product_invoice_interest')
            amount = bill.amount_total * 10/ 100
            bill_id = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': bill.partner_id.id,
                'invoice_date': fields.Date.today(),
                'date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'product_id': product.id,
                    'price_unit': amount,
                    'tax_ids': [(6, 0, [])],
                    'ref': 'Interest: ' + bill.name
                })]
            })
            template = self.env.ref('portal.portal_share_template', False)
            share_link = bill_id.get_base_url() + bill_id._get_share_url(
                redirect=True, pid=bill_id.partner_id.id)
            bill_id.message_post_with_view(template,
                                                     values={'partner': bill_id.partner_id,
                                                             'note': False,
                                                             'record': bill_id,
                                                             'share_link': share_link},
                                                     subject=_(
                                                         "You are invited to access %s",
                                                         bill_id.display_name),
                                                     email_layout_xmlid='mail.mail_notification_light',
                                                     partner_ids=[
                                                         (6, 0, bill_id.partner_id.ids)])
            bills_ = bills_ + [bill_id.id]
        account_move = self.env['account.move'].browse(bills_)

        action = {
            'name': _('Bill'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
        }
        if len(account_move) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': account_move.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', account_move.ids)],
            })
        return action

