from odoo import fields, models, _


class InternalAuditRevert(models.TransientModel):
    """Project Task revert"""
    _name = 'internal.audit.revert.wizard'

    comments = fields.Text(string="Comments", required=True)
    audit_method_id = fields.Many2one('internal.audit.method', string="Audit Methodology")
    internal_audit_plan_id = fields.Many2one('internal.audit.plan', string="Internal Audit Plan")
    audit_action_plan_id = fields.Many2one('audit.action.plan', string="Audit Action Plan")
    quality_control_peer_id = fields.Many2one('quality.control.peer')
    quality_control_outsourced_peer_id = fields.Many2one('quality.control.outsourced.peer')
    internal_quality_control_id = fields.Many2one('internal.quality.control')
    project_checklist_id = fields.Many2one('project.checklist')
    quality_assurance_id = fields.Many2one('quality.assurance')
    financial_statement_id = fields.Many2one('financial.statement')
    client_survey_id = fields.Many2one('client.survey')
    audit_committee_charter_id = fields.Many2one('audit.committee.charter')
    audit_followup_id = fields.Many2one('audit.followup')
    professional_development_id = fields.Many2one('professional.development')
    audit_standards_id = fields.Many2one('audit.standards')
    other_documents_id = fields.Many2one('other.documents')
    minutes_meeting_id = fields.Many2one('minutes.meeting')
    project_project_id = fields.Many2one('project.project')

    def action_submit(self):
        """Submit the revert records"""
        record = ''
        reference_type = ''
        if self.audit_method_id:
            record = self.audit_method_id
            reference_type = 'audit_method'
            mail_template = record.env.ref(
                'internal_audit_management.email_template_methodology_review')
            mail_template.send_mail(record.id, force_send=True)
            previous_state = record.state
            self.env['methodology.tracking'].create({
                'methodology_tracking_id': record.id,
                'user_id': record.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'comment': 'Reverted',
                'date': fields.Datetime.now(),
            })
            record.previous_state = previous_state
            record.state = 'reverted'
        if self.internal_audit_plan_id:
            record = self.internal_audit_plan_id
            reference_type = 'internal_audit_plan'
            mail_template = self.env.ref(
                'internal_audit_management.email_template_internal_audit_plan_reviewed')
            mail_template.send_mail(record.id, force_send=True)
            previous_state = record.state
            record.previous_state = previous_state
            record.env['internal.audit.plan.tracking'].create({
                'internal_audit_plan_tracking_id': record.id,
                'user_id': record.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': record.state,
                'date': fields.Datetime.now(),
            })
            record.state = 'reverted'
        if self.audit_action_plan_id:
            record = self.audit_action_plan_id
            reference_type = 'audit_action_plan'
            previous_state = record.stages
            record.previous_state = previous_state
            record.stages = 'reverted'
        if self.quality_control_peer_id:
            record = self.quality_control_peer_id
            reference_type = 'quality_control_peer'
            previous_state = record.state
            record.previous_state = previous_state
        if self.quality_control_outsourced_peer_id:
            record = self.quality_control_outsourced_peer_id
            reference_type = 'quality_control_outsourced_peer'
            previous_state = record.state
            record.previous_state = previous_state
            self.env['quality.control.outsourced.peer.tracking'].create({
                'quality_control_outsourced_peer_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'reverted',
                'comment': 'Reverted',
                'date': fields.Datetime.now(),
            })
            mail_template = self.env.ref(
                'internal_audit_management.email_template_quality_control_outsourced_peer_reviewed')
            mail_template.send_mail(record.id, force_send=True)
        if self.internal_quality_control_id:
            record = self.internal_quality_control_id
            reference_type = 'internal_quality_control'
            previous_state = record.state
            record.previous_state = previous_state
            self.env['internal.quality.control.tracking'].create({
                'internal_quality_control_tracking_id': record.id,
                'user_id': self.env.user.id,
                'previous_stage_id': previous_state,
                'new_stage_id': 'reverted',
                'comment': 'Reverted',
                'date': fields.Datetime.now(),
            })
            mail_template = self.env.ref(
                'internal_audit_management.email_template_internal_quality_control_reviewed')
            mail_template.send_mail(record.id, force_send=True)
        if self.project_checklist_id:
            record = self.project_checklist_id
            reference_type = 'project_checklist'
            mail_template = self.env.ref(
                'internal_audit_management.email_template_project_checklist_revert')
            mail_template.send_mail(record.id, force_send=True)
            previous_state = record.state
            record.previous_state = previous_state
        if self.quality_assurance_id:
            record = self.quality_assurance_id
            reference_type = 'quality_assurance'
            mail_template = self.env.ref(
                'internal_audit_management.email_template_quality_assurance_revert')
            mail_template.send_mail(record.id, force_send=True)
            previous_state = record.state
            record.previous_state = record.state
        if self.financial_statement_id:
            record = self.financial_statement_id
            reference_type = 'financial_statement'
            mail_template = self.env.ref(
                'internal_audit_management.email_template_financial_statement_reviewed')
            mail_template.send_mail(record.id, force_send=True)
            previous_state = record.state
            record.previous_state = previous_state
        if self.client_survey_id:
            record = self.client_survey_id
            reference_type = 'client_survey'
        if self.audit_followup_id:
            record = self.audit_followup_id
            reference_type = 'audit_followup'
            previous_state = record.stage
            record.previous_state = previous_state
            record.feedback = self.comments
        if self.professional_development_id:
            record = self.professional_development_id
            reference_type = 'professional_development'
            previous_state = record.state
            record.previous_state = previous_state
            record.feedback = self.comments
        if self.audit_standards_id:
            record = self.audit_standards_id
            reference_type = 'audit_standards'
            previous_state = record.state
            record.previous_state = previous_state
            record.state = 'reverted'
            record.feedback = self.comments
        if self.other_documents_id:
            record = self.other_documents_id
            reference_type = 'other_documents'
            previous_state = record.state
            record.previous_state = previous_state
            record.state = 'reverted'
            record.feedback = self.comments
        if self.minutes_meeting_id:
            record = self.minutes_meeting_id
            reference_type = 'minutes_meeting'
            previous_state = record.state
            record.previous_state = previous_state
            record.state = 'reverted'
            record.feedback = self.comments
        if self.project_project_id:
            record = self.project_project_id
            reference_type = 'project_project'
            record.feedback = self.comments
        if record:
            if self.audit_action_plan_id:
                res_user_id = ""
                if record.stages == 'first_reviewer':
                    res_user_id = record.user_reviewer_1_ids
                if record.stages == 'second_reviewer':
                    res_user_id = record.user_reviewer_2_ids
                state = record.stages
            elif self.audit_followup_id:
                res_user_id = ""
                if record.stage == 'first_reviewer':
                    res_user_id = record.user_reviewer_1_ids
                if record.stage == 'second_reviewer':
                    res_user_id = record.user_reviewer_2_ids
                state = record.stage
                record.stage = 'reverted'
            elif self.project_project_id:
                record.env['audit.revert'].create({
                    'res_id': record.id,
                    'res_model': record._name,
                    'comments': self.comments,
                    'user_id': record.env.uid,
                    'reference_type': reference_type,
                })
                record.feedback = self.comments
                return
            else:
                res_user_id = ""
                if record.state == 'first_reviewer':
                    if len(record.user_reviewer_1_ids) == 1:
                        res_user_id = record.user_reviewer_1_ids
                    elif len(record.user_reviewer_1_ids) == 0:
                        res_user_id = ""
                    else:
                        res_user_id = record.user_reviewer_1_ids[0]
                if record.state == 'second_reviewer':
                    if len(record.user_reviewer_2_ids) == 1:
                        res_user_id = record.user_reviewer_2_ids
                    elif len(record.user_reviewer_2_ids) == 0:
                        res_user_id = ""
                    else:
                        res_user_id = record.user_reviewer_2_ids[0]
                state = record.state
                record.state = 'reverted'

        if self.audit_committee_charter_id:
            rec = self.audit_committee_charter_id
            rec.feedback = self.comments
            rec.action_revert()
        if record:
            record.env['audit.revert'].create({
                'res_id': record.id,
                'res_model': record._name,
                'comments': self.comments,
                'user_id': record.env.uid,
                'record_state': state,
                'reference_type': reference_type,
                'res_user_id': res_user_id.id if res_user_id else None,
            })
            record.feedback = self.comments