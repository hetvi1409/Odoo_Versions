from odoo import models, fields, api, _


class QualityControlPeer(models.Model):
    _inherit = 'quality.control.peer'

    def _get_preparer_id(self):
        """Get the ID"""
        return int(self.env['ir.config_parameter'].sudo().get_param('internal_audit_workflow.preparer_id')) if self.env['ir.config_parameter'].sudo().get_param('internal_audit_workflow.preparer_id') else False

    def _get_reviewer_id(self):
        """Get the ID of the currently logged-in employee"""
        return int(self.env['ir.config_parameter'].sudo().get_param('internal_audit_workflow.reviewer_id')) if self.env['ir.config_parameter'].sudo().get_param('internal_audit_workflow.reviewer_id') else False

    def _get_approver_id(self):
        """Get the ID of the currently logged-in employee"""
        return int(self.env['ir.config_parameter'].sudo().get_param('internal_audit_workflow.approver_id')) if self.env['ir.config_parameter'].sudo().get_param('internal_audit_workflow.approver_id') else False

    preparer_id = fields.Many2one('res.users', string="Preparer", default=_get_preparer_id)
    reviewer_id = fields.Many2one('res.users', string="Reviewer", default=_get_reviewer_id)
    approver_id = fields.Many2one('res.users', string="Approver", default=_get_approver_id)
    can_edit = fields.Boolean(
        string="Can Edit",
        compute="_compute_can_edit", default=True
    )

    # @api.depends('state','preparer_id','reviewer_id','approver_id')
    def _compute_can_edit(self):
        current_user = self.env.user
        for record in self:
            # Default -> cannot edit
            record.can_edit = False

            # Approved/rejected -> nobody can edit
            if record.state in ['approved', 'rejected']:
                continue

            # Preparer → only Preparer
            if record.state == 'preparer' and current_user == record.preparer_id:
                record.can_edit = True

            # Reviewer Stage → Reviewer 1
            elif record.state == 'second_reviewer' and current_user == record.reviewer_id:
                record.can_edit = True
