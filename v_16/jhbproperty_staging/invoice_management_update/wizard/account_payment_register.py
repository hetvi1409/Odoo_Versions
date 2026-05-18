from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    """Replaced some methods based on the payments states.
    Added new state in the payments, so need to change the _post_payments button"""

    _inherit = 'account.payment.register'

    def _post_payments(self, to_process, edit_mode=False):
        """ Replaced the functionality for approving the payments"""
        payments = self.env['account.payment']
        for vals in to_process:
            payments |= vals['payment']
            payment = vals['payment']
            if payments.payment_type == 'inbound':
                payment.to_reconcile_ids = [(4, to_reconcile.id) for to_reconcile in vals['to_reconcile']]
            else:
                """Added this conditions for post the payments of the bill"""
                payments.action_post()
        # payments.action_post()

    def action_create_payments(self):
        """Override the default action_create_payments methode for
        to check the payments if they already exist or not"""
        if self._context.get('active_model') == 'account.move':
            move = self.env['account.move'].browse(
                self._context.get('active_ids'))
        elif self._context.get('active_model') == 'account.move.line':
            move = self.env['account.move.line'].browse(
                self._context.get('active_ids', [])).move_id
        payment = self.env['account.payment'].search([('invoice_id', '=', move.id)])
        if payment:
            raise UserError(_('This invoice already have a payment in %s'
                              ' state. Check the payment: %s') %(payment.state,
                                                                 payment.name))
        res = super(AccountPaymentRegister, self).action_create_payments()
        return res

