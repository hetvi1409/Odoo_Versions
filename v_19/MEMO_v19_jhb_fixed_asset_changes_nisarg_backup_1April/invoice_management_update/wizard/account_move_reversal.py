from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, adding binary field fo add attachments.
    """
    _inherit = 'account.move.reversal'

    attachment_ids = fields.Many2many('ir.attachment')

    @api.model
    def default_get(self, fields):
        """Super this method for changing the refund_method:
        It used to change the state of reversal, in case of we're creating
        reverse for multiple invoices """
        res = super(AccountMoveReversal, self).default_get(fields)
        move_ids = self.env['account.move'].browse(
            self.env.context['active_ids']) if self.env.context.get(
            'active_model') == 'account.move' else self.env['account.move']
        if 'refund_method' in fields:
            res['refund_method'] = (len(move_ids) > 1 or move_ids.move_type == 'entry') and 'refund' or 'refund'
        return res

    def reverse_moves(self):
        res = super(AccountMoveReversal, self).reverse_moves()
        for rec in self.attachment_ids:
            for new_move in self.new_move_ids:
                new_move_attach = rec.copy()
                new_move_attach.res_model = new_move._name
                new_move_attach.res_id = new_move.id
            for move in self.move_ids:
                move_attach = rec.copy()
                move_attach.res_model = move._name
                move_attach.res_id = move.id
        return res
