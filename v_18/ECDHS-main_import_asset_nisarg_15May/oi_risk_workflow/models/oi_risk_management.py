from odoo import models, fields, api, _
from werkzeug import urls


class Risk(models.Model):
    _inherit = 'oi_risk_management.risk'

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
    # Fraud Risk Register
    link_to_outcome = fields.Text(string='Link to Outcome')
    chief_directorate_id = fields.Many2one('hr.department', string="Chief Directorate", copy=False)
    directorate_id = fields.Many2one('hr.department', string="Sub-Directorate",
                                     domain="[('parent_id', '=', chief_directorate_id)]", copy=False)
    impact_value = fields.Integer(string='Impact Value')
    likelihood_value = fields.Integer(string='Likelihood Value')
    inherent_risk_value = fields.Integer(string='Inherent Risk Value', compute='_compute_inherent_risk_value',
                                         readonly=True)
    current_controls = fields.Text(string='Current Controls')
    control_effectiveness = fields.Char(string='Control Effectiveness')
    effectiveness_rating = fields.Float(string='Effectiveness')
    residual_risk_value = fields.Float(string='Residual Risk Value', compute='_compute_inherent_risk_value',
                                       readonly=True)
    risk_appetite = fields.Text(string='Risk Appetite')
    risk_tolerance = fields.Char(string='Risk Tolerance')
    risk_response_treatment = fields.Char(string='Risk Response Treatment')
    improve_management_of_risk = fields.Text(string='Action to Improve Management of the Risk')
    action_owner = fields.Many2one('hr.department', string='Action Owner')
    timeline = fields.Char(string='Timeline')
    # Emerging Risk Register
    unit = fields.Many2one('hr.department', string="Unit", copy=False)

    def _compute_inherent_risk_value(self):
        for risk in self:
            risk.inherent_risk_value = 0
            risk.residual_risk_value = 0
            if risk.impact_value and risk.likelihood_value:
                risk.inherent_risk_value = risk.impact_value * risk.likelihood_value
            if risk.inherent_risk_value and risk.effectiveness_rating:
                risk.residual_risk_value = risk.inherent_risk_value * risk.effectiveness_rating

    def _compute_can_edit(self):
        current_user = self.env.user.id

        for record in self:
            record.can_edit = False

            # -------------------------------
            # RISK FLOW
            # -------------------------------
            if record.risk_state not in ['approved', 'rejected']:
                continue

            if record.risk_state == 'draft' and current_user == record.preparer_id.id:
                record.can_edit = True

            elif record.risk_state == 'prepared' and current_user == record.reviewer_id.id:
                record.can_edit = True

            elif record.risk_state == 'reviewed' and current_user == record.approver_id.id:
                record.can_edit = True

            # -------------------------------
            # ASSESSMENT FLOW
            # -------------------------------
            if record.risk_assessment_state not in ['approved', 'rejected']:
                continue
            if record.risk_assessment_state == 'draft' and current_user == record.preparer_id.id:
                record.can_edit = True

            elif record.risk_assessment_state == 'prepared' and current_user == record.reviewer_id.id:
                record.can_edit = True

            elif record.risk_assessment_state == 'reviewed' and current_user == record.approver_id.id:
                record.can_edit = True

            # -------------------------------
            # TREATMENT FLOW
            # -------------------------------
            if record.risk_treatment_state not in ['approved', 'rejected']:
                continue
            if record.risk_treatment_state == 'draft' and current_user == record.preparer_id.id:
                record.can_edit = True

            elif record.risk_treatment_state == 'prepared' and current_user == record.reviewer_id.id:
                record.can_edit = True

            elif record.risk_treatment_state == 'reviewed' and current_user == record.approver_id.id:
                record.can_edit = True

    def action_risk_revert(self):
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'risk.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_risk_details': self.id,
                'default_oi_risk_management_risk': self.name,
                'default_risk_type': 'risk',
            },
        }

    def action_assessment_revert(self):
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'risk.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_risk_details': self.id,
                'default_oi_risk_management_risk': self.name,
                'default_risk_type': 'assessment',
            },
        }

    def action_treatment_revert(self):
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'risk.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_risk_details': self.id,
                'default_oi_risk_management_risk': self.name,
                'default_risk_type': 'treatment',
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
                             'web#id=%s&model=oi_risk_management.risk&view_type=form' % self.id)

        return Urls