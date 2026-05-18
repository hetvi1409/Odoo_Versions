from odoo import models, fields, api, _
from werkzeug import urls


class Activity(models.Model):
    _inherit = 'oi_risk_management.activity'

    def _get_preparer_id(self):
        """Get the ID"""
        return int(self.env['ir.config_parameter'].sudo().get_param('oi_risk_workflow.preparer_id')) if self.env[
            'ir.config_parameter'].sudo().get_param('oi_risk_workflow.preparer_id') else False

    def _get_reviewer_id(self):
        """Get the ID of the currently logged-in employee"""
        return int(self.env['ir.config_parameter'].sudo().get_param('oi_risk_workflow.reviewer_id')) if self.env[
            'ir.config_parameter'].sudo().get_param('oi_risk_workflow.reviewer_id') else False

    def _get_approver_id(self):
        """Get the ID of the currently logged-in employee"""
        return int(self.env['ir.config_parameter'].sudo().get_param('oi_risk_workflow.approver_id')) if self.env[
            'ir.config_parameter'].sudo().get_param('oi_risk_workflow.approver_id') else False

    preparer_id = fields.Many2one('res.users', string="Preparer", default=_get_preparer_id)
    reviewer_id = fields.Many2one('res.users', string="Reviewer", default=_get_reviewer_id)
    approver_id = fields.Many2one('res.users', string="Approver", default=_get_approver_id)
    feedback = fields.Char(string="Complaince Reverts/ Review Notes", tracking=True)
    can_edit = fields.Boolean(
        string="Can Edit",
        compute="_compute_can_edit", default=True
    )

    def _compute_can_edit(self):
        current_user = self.env.user
        for record in self:
            # Default → cannot edit
            record.can_edit = False

            # Approved → nobody can edit
            if record.factor_state in ['approved', 'rejected']:
                continue

            # Draft → only Preparer
            if record.factor_state == 'draft' and current_user == record.preparer_id:
                record.can_edit = True

            # Preparer Stage → Reviewer 1
            elif record.factor_state == 'prepared'and current_user == record.reviewer_id:
                record.can_edit = True

            # Second Reviewer Stage → Approver
            elif record.factor_state == 'reviewed' and current_user == record.approver_id:
                record.can_edit = True

    def action_activity_revert(self):
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'risk.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_activity_details': self.id,
                'default_oi_risk_management_activity': self.name,
                'default_risk_type': 'activity',
            },
        }

    def action_view_records(self):
        """Method for view records"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.revert',
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=oi_risk_management.activity&view_type=form' % self.id)

        return Urls