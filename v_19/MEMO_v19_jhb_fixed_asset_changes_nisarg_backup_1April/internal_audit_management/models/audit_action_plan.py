from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AuditActionPlan(models.Model):
    """Audit Action Plan"""
    _name = "audit.action.plan"
    _description = "Audit Action Plan"
    _rec_name = "requirements"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    type = fields.Selection([('internal', 'Internal'),
                             ('external', 'External')], string="Type")

    stages = fields.Selection([('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),], copy=False,
                             default="preparer", string="State")
    requirements = fields.Char(string="Requirements", required=True,
                               help="Requirements")
    record_work_done = fields.Char(string="Work done", required=True,
                                   help="Record of work done")
    conclusion = fields.Char(string="Conclusion", required=True,
                             help="Conclusion")
    finding = fields.Char(string="Audit Finding", required=True)
    rating = fields.Selection([
        ("auditors_report", "Matters affecting the auditor’s report"),
        ("important", "Other important matters"),
        ("administrative", "Administrative matters")],
        string="Auditor's Rating", required=True)
    impact = fields.Char(string="Auditor's Impact")
    deficiency = fields.Char(string="Auditor's Internal Control Deficiency")
    recommendation = fields.Char(string="Auditor's Recommendation")
    department_id = fields.Many2one('hr.department', string="Department")
    section = fields.Selection([("asset", 'Asset Management'),
                                ("expenditure", 'Expenditure Management')], string="Section")
    # head_department_id = fields.Many2one('audit.head.department', string="Head of Department")
    reviewer = fields.Selection([("manager", 'Manager Assets'),
                                 ("grants", 'Manager Grants')], string="Reviewer")
    preparer = fields.Selection([("assets", 'Senior Accountant: Assets'),
                                 ("grants", 'Senior Accountant: Grants')],
                                string="Preparer")
    start_date = fields.Date(string="Start Date", required=True)
    completion_date = fields.Date(string="Targeted Completion Date", required=True)
    undertaken_date = fields.Char(string="Activities undertaken to date")
    resolved = fields.Selection([("in_progress", 'In-Progress'),
                                 ('yes', "yes"), ('no', "No")],
                                string="Resolved", required=True)
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Audit Evidence")
    blockages = fields.Char(string="Blockages", required=True)
    proposed_completion_date = fields.Date(string="Proposed Revised "
                                                  "Completion Date", required=True)
    auditor_conclusion = fields.Date(string="Auditors' Conclusion", required=True)
    user_id = fields.Many2one('res.users', Tracking=True,
                              string="Responsible User")
    # audit_id = fields.Many2one('audit.request', string="Audit", tracking=True)
    feedback = fields.Char(string="Feedback", tracking=True)
    team_id = fields.Many2one('hr.department', string="Team", required=True)
    # role_id = fields.Many2one('audit.role', string="Roles")
    attachment_doc_ids = fields.Many2many('ir.attachment', 'attachment_doc_rel', string="Attachment")

    # risk_ids = fields.Many2many('business.risk', string="Risk")
    # complaince_ids = fields.Many2many('compliance.assessment', string="Complaince")
    active = fields.Boolean(string="Active", default=True)
    record_of_work_ids = fields.One2many('record.works','record_work_id',string='Record of Work')
    manager_id = fields.Many2one('res.users', string="Manager")
    user_preparer_ids = fields.Many2one('res.users',string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2one('res.users',string="First Reviewer",
                                           tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',string="Second Reviewer ",
                                           tracking=True)
    user_approver_ids = fields.Many2one('res.users',string="Approver", tracking=True)
    project_id = fields.Many2one('project.project',string="Project")
    project_task = fields.Many2one('project.task',string="Project Task")
    audit_type = fields.Selection([('internal', 'Internal'),('external', 'External')],string="Audit Type")
    audit_details = fields.Html(string="Audit Details")
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])
    is_current_user_approver = fields.Boolean(compute='_compute_is_reviewer',
                                              store=False)
    is_current_user_reviewer = fields.Boolean(compute='_compute_is_reviewer',
                                              store=False)
    is_current_user_reviewer2 = fields.Boolean(compute='_compute_is_reviewer',
                                               store=False)

    @api.depends('user_approver_ids', 'user_reviewer_1_ids',
                 'user_reviewer_2_ids')
    def _compute_is_reviewer(self):
        current_user = self.env.uid
        for rec in self:
            rec.is_current_user_approver = rec.user_approver_ids.id == current_user
            rec.is_current_user_reviewer = rec.user_reviewer_1_ids.id == current_user
            rec.is_current_user_reviewer2 = rec.user_reviewer_2_ids.id == current_user

    def action_review(self):
        """First Review"""
        self.stages = 'first_reviewer'

    def action_2nd_review(self):
        """Second Review"""
        self.stages = 'second_reviewer'

    def action_approve(self):
        """First Review"""
        self.stages = 'approved'

    def action_reject(self):
        """First Review"""
        self.stages = 'rejected'


    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=audit.action.plan&view_type=list' % self.id)
        return Urls

    def action_archive(self):
        res = super().action_archive()
        for rec in self:
            if rec.stages != 'approve':
                raise UserError(_('Only in the approve state can archive'))
        return res

    def action_revert(self):
        """Action SEND BACK TO REVIEW"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_audit_action_plan_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
        }
        if not self.feedback:
            raise UserError(_('Please add the Audit Reverts/ Review Notes'))
        previous_state = self.stages
        self.previous_state = previous_state
        # Concatenate all comments into a single string
        res_user_id = ""
        if self.stages == 'first_reviewer':
            res_user_id = self.user_reviewer_1_ids
        if self.stages == 'second_reviewer':
            res_user_id = self.user_reviewer_2_ids
        self.env['audit.revert'].create({
            'res_id': self.id,
            'res_model': self._name,
            'comments': self.feedback,
            'user_id': self.env.uid,
            'record_state': self.stages,
            'reference_type': 'audit_action_plan',
            'res_user_id': res_user_id.id if res_user_id else None,
        })
        self.stages = 'reverted'

    def action_update(self):
        self.feedback = ""
        self.stages = self.previous_state

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

class RecordWorks(models.Model):
    _name = "record.works"
    _description = "Record Works"

    record_work_id = fields.Many2one('audit.action.plan',string='Record Work')
    audit_area = fields.Html(string='Audit Area')
    title_of_finding = fields.Html(string='Title of finding')
    recommendation = fields.Html(string='Recommendation')
    mgmt_action_plan = fields.Html(string='Managements Action Plan')
    action_date = fields.Date(string='Action Date')
    implemented_not = fields.Selection([('implemented', 'Implemented'),('not_implemented', 'Not Implemented')], string="Implemented/ Not Implemented")
    follow_up = fields.Html(string='Follow Up')
