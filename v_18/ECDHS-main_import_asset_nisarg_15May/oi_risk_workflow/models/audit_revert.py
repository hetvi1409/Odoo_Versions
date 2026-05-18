from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AuditFinding(models.Model):
    _inherit = "audit.revert"

    reference_type = fields.Selection(selection_add=[('oi_risk_management_risk', 'Risk Management'),
                                                     ('oi_risk_management_activity', 'Risk Activity'),
                                                     ('oi_risk_management_register','Risk Register')])
    reference = fields.Selection(selection_add=[('oi_risk_management.risk', 'Risk Management'),
                                                ('oi_risk_management.activity', 'Risk Activity'),
                                                ('risk.register','Risk Register')])
    record_state = fields.Selection(
        selection_add=[('draft', 'Draft'), ('prepared', 'Prepared'), ('reviewed', 'Reviewed')])
    risk_type = fields.Selection(
        [('risk', 'Risk'), ('assessment', 'Assessment'), ('treatment', 'Treatment'), ('activity', 'Activity'),('register','Register')],
        string="Risk Type")

    @api.depends('res_id', 'res_model', 'reference_type')
    def _compute_name(self):
        """Compute the name"""
        type = {
            'internal_audit_plan': 'Internal Audit Rolling Plan: 3 year',
            'audit_method': 'Internal Audit Methodology',
            'rolling_plan': 'Internal Audit Rolling Plan: 1 year',
            'operational_plan': 'Internal Audit Operational Plan',
            'audit_universe': 'Audit Universe',
            'pestel_analysis': 'Pestel Analysis',
            'swot_analysis': 'Swot Analysis',
            'audit_action_plan': 'Audit Action Plan',
            'quality_control_peer': 'Quality Control Peer',
            'quality_control_outsourced_peer': 'Quality Control Outsourced Peer',
            'internal_quality_control': 'Internal Quality Control',
            'financial_statement': 'Council Resolution',
            'internal_audit_charter': 'Internal Audit Charter',
            'audit_committee_charter': 'Audit Committee Charter',
            'project_checklist': 'Project Checklist',
            'quality_assurance': 'Quality Assurance',
            'client_survey': 'Client Survey',
            'audit_finding': 'Audit Finding',
            'audit_strategy': 'Audit Strategy',
            'audit_followup': 'Audit Followup',
            'professional_development': 'Professional Development',
            'audit_standards': 'Audit Standards',
            'other_documents': 'Other Documents',
            'minutes_meeting': 'Minutes Of Meeting',
            'project_project': 'Project',
            'project_task': 'Task',
            'complaince_assessment': 'Complain Assessment',
            'complaince_evaluation': 'Complain Evaluation',
            'complaince_treatment': 'Complain Treatment',
            'oi_risk_management_risk': 'Risk Management',
            'oi_risk_management_activity': 'Risk Activity',
            'oi_risk_management_register' : 'Risk Register',
        }
        for rec in self:
            name = ""
            record = ""
            if rec.res_model and rec.res_id:
                record = rec.env[rec.res_model].browse(rec.res_id)
            if rec.reference_type:
                name = type[rec.reference_type]
            if record:
                if rec.reference_type == 'audit_action_plan':
                    name = name + ': ' + record.requirements
                elif rec.reference_type == 'project_checklist':
                    name = name + ': ' + record.project_title
                elif rec.reference_type == 'quality_assurance':
                    name = name + ': ' + record.assurance_number
                elif rec.reference_type == 'client_survey':
                    name = name + ': ' + record.subject
                elif rec.reference_type == 'audit_finding':
                    name = name + ': ' + record.finding_name
                elif rec.reference_type == 'audit_followup':
                    name = name + ': ' + record.followup_name
                elif rec.reference_type == 'professional_development':
                    name = name + ': ' + record.subject
                elif rec.reference_type == 'project_project':
                    name = name + ': ' + record.name
                elif rec.reference_type == 'project_task':
                    name = name + ': ' + record.name
                else:
                    name = name + ': ' + record.name
            rec.name = name

    def action_review(self):
        """Review the actions"""
        if not self.audit_findings:
            raise UserError(_('Please add the revert proposal'))
        for rec in self:
            record = rec.env[rec.res_model].browse(rec.res_id)
            # record.action_update()
            record.feedback = rec.comments or ''
            rec.state = 'reviewed'
            if rec.res_model in ['audit.finding', 'audit.action.plan', 'audit.committee.charter', 'audit.universe',
                                 'internal.audit.charter', 'operational.plan', 'pestel.analysis', 'rolling.plan',
                                 'swot.analysis']:
                if rec.record_state == 'preparer':
                    record.sudo().write({'stages': 'draft'})
                if rec.record_state == 'second_reviewer':
                    record.sudo().write({'stages': 'preparer'})
                if rec.record_state == 'approved':
                    record.sudo().write({'stages': 'second_reviewer'})
            if rec.res_model in ['audit.standards', 'audit.strategy', 'financial.statement', 'internal.audit.method',
                                 'internal.quality.control', 'minutes.meeting',
                                 'other.documents', 'professional.development', 'quality.control.outsourced.peer',
                                 'quality.control.peer']:
                if rec.record_state == 'preparer':
                    record.sudo().write({'state': 'draft'})
                if rec.record_state == 'second_reviewer':
                    record.sudo().write({'state': 'preparer'})
                if rec.record_state == 'approved':
                    record.sudo().write({'state': 'second_reviewer'})
            if rec.res_model in ['internal.audit.plan']:
                if rec.record_state == 'second_reviewer':
                    record.sudo().write({'state': 'new'})
                if rec.record_state == 'approved':
                    record.sudo().write({'state': 'second_reviewer'})
            if rec.res_model in ['compliance.assessment']:
                if rec.record_state == 'prepared':
                    record.sudo().write({'state': 'draft'})
                if rec.record_state == 'reviewed':
                    record.sudo().write({'state': 'prepared'})
                if rec.record_state == 'approved':
                    record.sudo().write({'state': 'reviewed'})
            if rec.res_model in ['complaince.treatment']:
                if rec.record_state == 'prepared':
                    record.sudo().write({'status': 'draft'})
                if rec.record_state == 'reviewed':
                    record.sudo().write({'status': 'prepared'})
                if rec.record_state == 'approved':
                    record.sudo().write({'status': 'reviewed'})
            if rec.res_model in ['oi_risk_management.risk']:
                if rec.risk_type == 'risk':
                    if rec.record_state == 'prepared':
                        record.sudo().write({'risk_state': 'draft'})
                    if rec.record_state == 'reviewed':
                        record.sudo().write({'risk_state': 'prepared'})
                    if rec.record_state == 'approved':
                        record.sudo().write({'risk_state': 'reviewed'})
                if rec.risk_type == 'assessment':
                    if rec.record_state == 'prepared':
                        record.sudo().write({'risk_assessment_state': 'draft'})
                    if rec.record_state == 'reviewed':
                        record.sudo().write({'risk_assessment_state': 'prepared'})
                    if rec.record_state == 'approved':
                        record.sudo().write({'risk_assessment_state': 'reviewed'})
                if rec.risk_type == 'treatment':
                    if rec.record_state == 'prepared':
                        record.sudo().write({'risk_treatment_state': 'draft'})
                    if rec.record_state == 'reviewed':
                        record.sudo().write({'risk_treatment_state': 'prepared'})
                    if rec.record_state == 'approved':
                        record.sudo().write({'risk_treatment_state': 'reviewed'})
            if rec.res_model in ['oi_risk_management.activity']:
                if rec.record_state == 'prepared':
                    record.sudo().write({'factor_state': 'draft'})
                if rec.record_state == 'reviewed':
                    record.sudo().write({'factor_state': 'prepared'})
                if rec.record_state == 'approved':
                    record.sudo().write({'factor_state': 'reviewed'})
            if rec.res_model in ['risk.register']:
                if rec.record_state == 'prepared':
                    record.sudo().write({'risk_register_state': 'draft'})
                if rec.record_state == 'reviewed':
                    record.sudo().write({'risk_register_state': 'prepared'})
                if rec.record_state == 'approved':
                    record.sudo().write({'risk_register_state': 'reviewed'})
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_revert_review')
            email_values = {
                'recipient_ids': [(6, 0, rec.res_user_id.partner_id.ids)]
            }
            mail_template.send_mail(rec.id, force_send=True, email_values=email_values)
