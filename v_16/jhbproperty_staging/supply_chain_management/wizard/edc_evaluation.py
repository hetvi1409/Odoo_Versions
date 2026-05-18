from odoo import fields, models, _
from odoo.exceptions import UserError


class EDCEvaluation(models.Model):
    """EDC Evaluation"""
    _name = 'edc.evaluation'
    _description = 'Edc Evaluation'


    purchase_requisition_id = fields.Many2one('purchase.requisition',
                                              string="Purchase Requisition")
    review_status = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                     string='Review Status',
                                     help='Review Status')
    reason = fields.Char(string="Reason")
    partner_ids = fields.Many2many('res.partner', string="Vendor")
    selected_partner_id = fields.Many2one('res.partner',
                                          string="Selected supplier")

    def action_submit(self):
        """Method for submit the form"""
        if not self.review_status:
            raise UserError(_('Please select the review status'))
        if self.review_status == 'no':
            if not self.reason:
                raise UserError(_('Please Add the reason'))
            self.purchase_requisition_id.state = 'advertisement'
        if self.review_status == 'yes':
            if not self.selected_partner_id:
                raise UserError(_('Please Add the Customer'))
            self.purchase_requisition_id.selected_partner_id = self.selected_partner_id.id
            self.purchase_requisition_id.state = 'agreement'
