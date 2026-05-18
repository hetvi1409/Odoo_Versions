from odoo import fields, models, _
from odoo.exceptions import UserError


class MemoDocuments(models.Model):
    """EDC Evaluation"""
    _name = 'memo.evaluation'
    _description = 'Memo Evaluation'

    memo_id = fields.Many2one('contract.memo', string="Memo")
    status = fields.Selection([('yes', 'Yes'), ('no', 'No')],
            string='All Supporting Document Are Attached',
            help='All Supporting Document Are Attached',
            required=True)
    reason = fields.Char(string="Reason", required=True)
    supplier_ids = fields.Many2many('res.partner', string="Supplier")

    def action_submit(self):
        """Method for submit the form"""
        if self.status == 'no':
            self.memo_id.sudo().message_post(body="Document is not supported. Reason: %s" %(self.reason))
            self.memo_id.state = 'draft'
        if self.status == 'yes':
            self.memo_id.sudo().message_post(body="Document is supported. Reason: %s" %(self.reason))
            if not self.supplier_ids:
                raise UserError(_('Please Add the Supplier'))
            contract = self.env['xf.partner.contract'].create({
                'name': self.memo_id.sudo().description,
                'partner_id': self.memo_id.sudo().partner_id.id,
                'type': self.memo_id.sudo().type,
                'contract_amount_type': self.memo_id.sudo().contract_amount_type,
                'amount': self.memo_id.sudo().total_amount,
                'date_start': self.memo_id.sudo().date_start,
                'date_end': self.memo_id.sudo().date_end,
                'supplier_ids': self.supplier_ids,
            })
            self.memo_id.contract_id = contract.id
            self.memo_id.state = 'approved'