from odoo import fields, models


class AmendmentsBill(models.TransientModel):
    """Model for Amendments bill"""
    _name = 'amendments.bill'
    _description = 'Amendments Bill'

    move_id = fields.Many2one('account.move')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    any_amendments = fields.Boolean(string="Any amendments")
    attachment_ids = fields.Many2many('ir.attachment',
                                     string="Documents")

    def action_submit(self):
        """this methode for submitting the amendments"""
        self.move_id.any_amendments = True
        if self.any_amendments:
            for attach in self.attachment_ids:
                attachment = attach.copy()
                attachment.write({'res_model': 'account.move',
                                  'res_id': self.move_id.id})
