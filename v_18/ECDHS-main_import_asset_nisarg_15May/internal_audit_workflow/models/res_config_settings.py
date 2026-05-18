from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _group_preparer_reviewer_approver(self):
        group = self.env.ref('base.group_user', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []

    audit_preparer_id = fields.Many2one('res.users', string="Preparer", config_parameter="internal_audit_workflow.preparer_id", domain=_group_preparer_reviewer_approver)
    audit_reviewer_id = fields.Many2one('res.users', string="Reviewer", config_parameter="internal_audit_workflow.reviewer_id", domain=_group_preparer_reviewer_approver)
    audit_approver_id = fields.Many2one('res.users', string="Approver", config_parameter="internal_audit_workflow.approver_id", domain=_group_preparer_reviewer_approver)
