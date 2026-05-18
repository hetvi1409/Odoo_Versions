from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AuditFinding(models.Model):
    _name = "audit.revert"
    _description = "Audit Reverts"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", compute="_compute_name")
    audit_findings = fields.Char(string="Audit Proposal", readonly=False, tracking=True)
    comments = fields.Text(string="Review Comments", required=True, tracking=True)
    reference_type = fields.Selection(string="Type", tracking=True,
                                      selection=[('internal_audit_plan', 'Internal Audit Rolling Plan: 3 year'),
                                                 ('audit_method', 'Internal Audit Methodology'),
                                                 ('rolling_plan', 'Internal Audit Rolling Plan: 1 year'),
                                                 ('operational_plan', 'Internal Audit Operational Plan'),
                                                 ('audit_universe', 'Audit Universe'),
                                                 ('pestel_analysis', 'Pestel Analysis'),
                                                 ('swot_analysis', 'Swot Analysis'),
                                                 ('audit_action_plan', 'Audit Action Plan'),
                                                 ('quality_control_peer', 'Quality Control Peer'),
                                                 ('quality_control_outsourced_peer', 'Quality Control Outsourced Peer'),
                                                 ('internal_quality_control', 'Internal Quality Control'),
                                                 ('financial_statement', 'Council Resolution'),
                                                 ('internal_audit_charter', 'Internal Audit Charter'),
                                                 ('audit_committee_charter', 'Audit Committee Charter'),
                                                 ('project_checklist', 'Project Checklist'),
                                                 ('quality_assurance', 'Quality Assurance'),
                                                 ('client_survey', 'Client Survey'),
                                                 ('audit_finding', 'Audit Finding'),
                                                 ('audit_followup', 'Audit Followup'),
                                                 ('professional_development', 'Professional Development'),
                                                 ('audit_standards', 'Audit Standards'),
                                                 ('audit_strategy', 'Audit Strategy'),
                                                 ('other_documents', 'Other Documents'),
                                                 ('minutes_meeting', 'Minutes Meeting'),
                                                 ('project_project', 'Project'),
                                                 ('project_task', 'Task'),
                                                 ])
    res_id = fields.Integer(string="Resource ID", required=True)
    res_model = fields.Char(string="Resource Model", required=True)
    user_id = fields.Many2one('res.users', string="Created User", tracking=True)
    res_user_id = fields.Many2one('res.users', string="Responsible User", tracking=True)
    state = fields.Selection([('ongoing', 'Ongoing'), ('reviewed', 'Approved'), ('rejected', 'Rejected')],
                             default='ongoing')
    reference = fields.Reference(selection=[('internal.audit.plan', 'ARP 3 Year'),
                                            ('internal.audit.method', 'Audit Methodology'),
                                            ('rolling.plan', 'ARP 1 Year'),
                                            ('operational.plan', 'Internal Audit Operational Plan'),
                                            ('audit.universe', 'Audit Universe'),
                                            ('pestel.analysis', 'Pestel Analysis'),
                                            ('swot.analysis', 'Swot Analysis'),
                                            ('audit.action.plan', 'Audit Action Plan'),
                                            ('quality.control.peer', 'Quality Control Peer'),
                                            ('quality.control.outsourced.peer', 'Quality Control Outsourced Peer'),
                                            ('internal.quality.control', 'Internal Quality Control'),
                                            ('financial.statement', 'Council Resolution'),
                                            ('internal.audit.charter', 'Internal Audit Charter'),
                                            ('audit.committee.charter', 'Audit Committee Charter'),
                                            ('project.checklist', 'Project Checklist'),
                                            ('quality.assurance', 'Quality Assurance'),
                                            ('client.survey', 'Client Survey'),
                                            ('audit.finding', 'Audit Finding'),
                                            ('audit.followup', 'Audit Followup'),
                                            ('professional.development', 'Professional Development'),
                                            ('audit.standards', 'Audit Standards'),
                                            ('other.documents', 'Other Documents'),
                                            ('minutes.meeting', 'Minutes Meeting'),
                                            ('project.project', 'Project'),
                                            ('project.task', 'Task'),
                                            ], compute="_compute_reference", store=True)

    record_state = fields.Selection([
        ('new', 'Preparer'),
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('in_progress', "In Progress"),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'), ],
        default="new", string="Current State")
    date = fields.Datetime(string="Created Date", default=fields.Datetime.now())

    @api.depends('res_id', 'res_model')
    def _compute_reference(self):
        for record in self:
            if record.res_model and record.res_id:
                target_model = record.res_model
                target_record = self.env[target_model].browse(record.res_id)
                if target_record:
                    record.reference = f'{target_model},{target_record.id}'
                else:
                    record.reference = False
            else:
                record.reference = False

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
            'project_task': 'Task'
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

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AuditFinding, self).create(vals_list)
        return records

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
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_revert_review')
            email_values = {
                'recipient_ids': [(6, 0, rec.res_user_id.partner_id.ids)]
            }
            mail_template.send_mail(rec.id, force_send=True, email_values=email_values)

    def action_rejected(self):
        """Review the actions"""
        if not self.audit_findings:
            raise UserError(_('Please add the revert proposal'))
        for rec in self:
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_revert_rejected')
            email_values = {
                'recipient_ids': [(6, 0, rec.res_user_id.partner_id.ids)]
            }
            mail_template.send_mail(rec.id, force_send=True,
                                    email_values=email_values)
            rec.state = 'rejected'

    def action_move_to_new(self):
        """Review the actions"""
        for rec in self:
            rec.audit_findings = ''
            mail_template = self.env.ref(
                'internal_audit_management.email_template_audit_revert_ongoing')
            email_values = {
                'recipient_ids': [(6, 0, rec.res_user_id.partner_id.ids)]
            }
            mail_template.send_mail(rec.id, force_send=True,
                                    email_values=email_values)
            rec.state = 'ongoing'

    def send_follow_up_mail(self):
        """Send the follow up mail"""

        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_revert_to_review')
        email_values = {
            'recipient_ids': [(6, 0, self.res_user_id.partner_id.ids)]
        }
        mail_template.send_mail(self.id, force_send=True, email_values=email_values)

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=audit.revert&view_type=list' % self.id)
        return Urls

    def action_view_records(self):
        """Method for view records"""
        return {
            'name': 'Record',
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }
