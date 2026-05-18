from odoo import api, fields, models


class AccountMove(models.Model):
    """Adding project details into it"""
    _inherit = 'account.move'

    project_id = fields.Many2one('project.task', domain="[('is_completed', '=', True)]")
    attachment_ids = fields.Many2many("ir.attachment", required=True, )

    @api.onchange('project_id')
    def onchange_project_id(self):
        """Change the project"""
        if self.project_id:
            self.project_id.invoice_id = self.id

    def write(self, vals):
        for rec in self:
            rec.project_id.invoice_id = rec.id
        return super(AccountMove, self).write(vals)