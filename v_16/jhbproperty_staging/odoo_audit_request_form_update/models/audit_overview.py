from odoo import api, fields, models, _
from random import randint


class AuditOverview(models.Model):
    """Audit Overview"""
    _name = 'audit.overview'
    _description = "Audit Overview"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(string='Color', default=_get_default_color)
    name = fields.Char(string="Name")
    request_count = fields.Integer(string="Audit Count",
                                   compute="_compute_request_count")
    request_reviewed = fields.Integer(string="Audit Request Count",
                                      compute="_compute_request_viewed")
    request_approved = fields.Integer(string="Audit Approved Count",
                                      compute="_compute_request_approved")
    request_completed = fields.Integer(string="Audit Completed Count",
                                       compute="_compute_request_completed")
    internal_review_count = fields.Integer(string="Audit Internal Review Count", default=7)
    internal_peer_review_count = fields.Integer(string="Audit Internal Peer Review Count", default=3)
    outsourced_peer_review = fields.Integer(string="Outsourced Peer Review Count", default=4)
    user_id = fields.Many2one('res.users')
    committee_user_id = fields.Many2one('res.users')
    compliance_count = fields.Integer(string="Compliance Count", compute="_compute_compliance_count")
    communicate_auditee_count = fields.Integer(string="Communicate with auditee management", default=3)
    communicate_audit_team_count = fields.Integer(string="Communicate with audite Team", default=5)
    prior_impact_count = fields.Integer(string="Prior Impact Count", default=3)
    final_analytic_procedure_count = fields.Integer(string="Final Analysis Procedure Count", default=4)
    evaluate_going_concern_count = fields.Integer(string="Evaluate going Concern Count", default=3)
    evaluate_subsequent_events = fields.Integer(string="Evaluate subsequent events", default=5)

    def action_view_audit(self):
        """View Audit"""
        return {
            'name': _('Overall Internal Audit Methodology'),
            'view_mode': 'kanban,tree,form',
            'res_model': 'custom.audit.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_request_reviewed(self):
        """View Audit"""
        return {
            'name': _('Overall Internal Audit Methodology'),
            'view_mode': 'kanban,tree,form',
            'res_model': 'custom.audit.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('state', '=', 'b_confirm')]
        }

    def action_view_request_approved(self):
        """View Audit"""
        return {
            'name': _('Overall Internal Audit Methodology'),
            'view_mode': 'kanban,tree,form',
            'res_model': 'custom.audit.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('state', '=', 'd_done')]
        }

    def action_view_completed(self):
        """View Audit"""
        return {
            'name': _('Overall Internal Audit Methodology'),
            'view_mode': 'kanban,tree,form',
            'res_model': 'custom.audit.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('state', '=', 'c_approve')]
        }

    @api.depends()
    def _compute_request_count(self):
        for rec in self:
            rec.request_count = self.env['custom.audit.request'].search_count([])

    @api.depends()
    def _compute_request_viewed(self):
        for rec in self:
            rec.request_reviewed = self.env['custom.audit.request'].search_count([('state', '=', 'b_confirm')])

    @api.depends()
    def _compute_request_approved(self):
        for rec in self:
            rec.request_approved = self.env['custom.audit.request'].search_count([('state', '=', 'd_done')])

    @api.depends()
    def _compute_request_completed(self):
        for rec in self:
            rec.request_completed = self.env['custom.audit.request'].search_count([('state', '=', 'c_approve')])

    def action_view_quality_control(self):
        """View quality control"""
        print('Quality Control')

    def action_view_internal_review(self):
        """View internal review framework"""
        print('Internal Review Framework')

    def action_view_internal_peer_review(self):
        """View internal peer review framework"""
        print('Internal Peer Review Framework')

    def action_view_outsourced_peer_review(self):
        """View outsourced peer review framework"""
        print('Outsourced Peer Review Framework')

    def action_view_user(self):
        """View user"""
        return {
            'name': _('Internal audit Charter'),
            'view_mode': 'form',
            'res_model': self.user_id._name,
            'res_id': self.user_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_committee_user(self):
        """View user"""
        return {
            'name': _('AuditCommittee Charter'),
            'view_mode': 'form',
            'res_model': self.committee_user_id._name,
            'res_id': self.committee_user_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_internal_audit(self):
        """View internal audit"""

    def action_view_business(self):
        """View Understanding of business"""

    def action_view_compliance(self):
        """View Understanding of business"""
        return {
            'name': _('AuditCommittee Charter'),
            'view_mode': 'tree,form',
            'res_model': 'business.challenges',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.depends()
    def _compute_compliance_count(self):
        """Compute compliance count"""
        for rec in self:
            rec.compliance_count = self.env['business.challenges'].search_count([])

    def action_view_communication_correspondence(self):
        """View communication correspondence"""

    def action_view_communicate_auditee(self):
        """View communication communicate with auditee"""

    def action_view_communicate_audit_team(self):
        """View communication communicate with audit team"""

    def action_view_information_ui(self):
        """View information UI"""

    def action_view_oversight(self):
        """View Oversight"""

    def action_view_management_representation(self):
        """View Management Representation"""

    def action_view_entity_environment(self):
        """View entity environment"""

    def action_view_audit_strategy(self):
        """View Audit Strategy"""
        return {
            'name': _('Develop audit strategy'),
            'view_mode': 'tree,form',
            'res_model': 'strategic.planning',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_revise_materiality(self):
        """View Revision materiality"""

    def action_view_multiple_location(self):
        """View Multiple location"""

    def action_view_entity_internal_control(self):
        """View Entity internal control"""

    def action_view_entity_business_processes(self):
        """View Entity internal control"""

    def action_view_plan_response_risk(self):
        """View Assess and plan response to risks of material misstatement"""

    def action_view_use_work(self):
        """View use of work"""

    def action_view_allegation(self):
        """View allegation"""

    def action_view_audit_transactions(self):
        """View audit transactions"""

    def action_view_audit_disclosures(self):
        """View audit disclosure"""

    def action_view_material_irregularities(self):
        """View audit disclosure"""

    def action_view_evaluate_audit_evidence(self):
        """View audit evidence"""

    def action_view_prior_impact(self):
        """Evaluate impact of prior year uncorrected misstatements"""

    def action_view_final_analytic_procedure(self):
        """View final analytics procedure"""

    def action_view_evaluate_going_concern(self):
        """View evaluations"""

    def action_view_evaluate_subsequent_events(self):
        """View evaluations subsequent events"""

    def action_view_uncorrected_misstatements(self):
        """View incorrect misstatements"""

    def action_view_deficiencies_internal_control(self):
        """View deficiencies of internal control"""

    def action_view_key_audit_matters(self):
        """View key audit matters"""

    def action_view_prepare_management_reports(self):
        """View prepare management reports"""

    def action_view_prepare_auditor_report(self):
        """View prepare auditor report"""

    def action_view_prepare_dashboard_reports(self):
        """View prepare dashboard reports"""

    def action_view_prepare_general_report(self):
        """View prepare general report"""

    def action_view_overall_conclusion(self):
        """View overall conclusion"""

    def action_view_internal_audit_action_plan(self):
        """View internal audit action plan"""

    def action_view_external_audit_action_plan(self):
        """View external audit action plan"""
