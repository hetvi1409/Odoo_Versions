from odoo import fields, models, _
from odoo.exceptions import UserError


class BidEvaluation(models.Model):
    """Bid Evaluation"""
    _name = "bid.evaluation"
    _description = "Bid Evaluation"

    purchase_requisition_id = fields.Many2one('purchase.requisition',
                                              string="Purchase requisition",
                                              help="Purchase Requisition")
    review_status = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                     string="Review Status", help="Was process fair?")
    reason = fields.Char(string="Reason", help="Reason for not approving")
    attachment_ids = fields.Many2many('ir.attachment', string="Documents", help="Documents Details")

    def action_submit(self):
        """Method to submit bid evaluation"""
        if not self.review_status:
            raise UserError(_('Please select a review status'))
        if self.review_status == 'no':
            if not self.reason:
                raise UserError(_('Please add a reason'))
        if self.review_status == 'yes':
            if not self.attachment_ids:
                raise UserError(_('Please add documents'))
            for rec in self.attachment_ids:
                rec.res_model = self.purchase_requisition_id._name
                rec.res_id = self.purchase_requisition_id.id
            self.purchase_requisition_id.attachment_ids = self.attachment_ids
            self.purchase_requisition_id.state = 'bid_evaluated'
