from odoo import fields, models


class PurchaseOrder(models.Model):
    """Inherited this method for approving the purchase order"""
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('first_approve', 'First Approve'),
                                            ('approve', 'Approve'), ('sent',)],
                             ondelete={'first_approve': 'cascade',
                                       'approve': 'cascade'})

    def action_first_approve(self):
        """Method for approve the purchase order"""
        self.write({'state': 'first_approve'})
