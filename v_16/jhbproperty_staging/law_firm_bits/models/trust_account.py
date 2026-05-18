from odoo import models, fields, _


class TrustAccount(models.Model):
    _name = 'trust.account'
    _description = 'Trust Account'

    name = fields.Char("Trust Account")
    partner_id = fields.Many2one("res.partner", "Customer")

    case_id = fields.Many2one("project.project", domain=[('is_case', '=', True)])
    matter_id = fields.Many2one("project.project", domain=[('is_matter', '=', True)])

    amount = fields.Float("Amount")
    amount_due = fields.Float(compute='_compute_amount_due')
    doc_attachment_ids = fields.Many2many("ir.attachment", 'trust_account_ir_attachments_rel')

    move_line_ids = fields.One2many("account.move.line", 'trust_account_id')

    def _compute_amount_due(self):
        for rec in self:
            rec.amount_due = rec.amount - sum(rec.move_line_ids.mapped('price_subtotal'))
