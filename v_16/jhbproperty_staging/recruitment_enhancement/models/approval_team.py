# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields,api
from odoo.exceptions import ValidationError


class PerformanceContractApprovalTeam(models.Model):
    _name = "approval.team"
    _description = "Approval Team"
    _rec_name = "name"

    sequence = fields.Integer("Sequence", default=1)
    name = fields.Char("Team Name", required=True)
    line_ids = fields.One2many("approval.team.line", "team_id", string="Approval Lines")
    model = fields.Char(index=True)
    model_id = fields.Many2one("ir.model", string="Model", compute='_compute_model_id', inverse='_inverse_compute_model_id')
    department_id = fields.Many2one('hr.department', string="Department")


    @api.constrains('department_id')
    def _check_unique_department(self):
        for record in self:
            if not record.department_id:
                continue
            duplicate = self.env['approval.team'].search([
                ('department_id', '=', record.department_id.id),
                ('id', '!=', record.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(
                    "Department '%s' is already assigned to approval team '%s'. "
                    % (record.department_id.name, duplicate.name)
                )

    @api.depends('model')
    def _compute_model_id(self):
        for record in self:
            record.model_id = self.env['ir.model']._get(record.model)

    def _inverse_compute_model_id(self):
        for record in self:
            record.model = record.model_id.model



class PerformanceContractApprovalTeamLine(models.Model):
    _name = "approval.team.line"
    _description = "Approval Team Line"
    _rec_name = "user_id"

    contract_id = fields.Many2one("recruitment.requisition", ondelete="cascade")
    applicant_id = fields.Many2one("hr.applicant", string="Applicant")
    background_check_id = fields.Many2one("recruitment.background.check", string="Background Check")
    sequence = fields.Integer("Sequence",default=1)
    user_id = fields.Many2one("res.users")
    approver_role_id = fields.Many2one("approver.role", string="Approver Role")
    department_id = fields.Many2one("hr.department", string="Department", related="user_id.employee_id.department_id", store=True)
    signature = fields.Binary('Signature')
    team_id = fields.Many2one("approval.team", string="Approval Team")
    status = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                              default='pending', string="Status")
    approved = fields.Boolean(default=False)
    approval_date = fields.Datetime(string="Date")
    reject_reason = fields.Text(string="Reject Reason")
    approval_signed = fields.Boolean(string="Approval Signed")
    rejected_signed = fields.Boolean(string="Rejected Signed")
    has_role = fields.Boolean(string="Has Group")
    is_editable_line = fields.Boolean(
        string="Editable Line",
        compute="_compute_is_editable_line",
        store=False
    )
    group_ids = fields.Many2many("res.groups", string="Groups")
    job_id = fields.Many2one('hr.job',string="Job Position",related="user_id.employee_id.job_id", store=True)

    group_user_domain_ids = fields.Many2many(
        'res.users',
        'approval_line_group_domain_rel',
        'line_id',
        'user_id',
        string="Group Users",
        compute='_compute_group_user_domain_ids',
        store=True,
    )

    @api.depends('group_ids')
    def _compute_is_editable_line(self):
        for rec in self:
            rec.is_editable_line = len(rec.group_ids) > 0

    @api.depends('group_ids', 'has_role')
    def _compute_group_user_domain_ids(self):
        for rec in self:
            if rec.has_role and rec.group_ids:
                group_idss = rec.group_ids.ids
                if group_idss:
                    self.env.cr.execute("""
                        SELECT DISTINCT uid
                        FROM res_groups_users_rel
                        WHERE gid = ANY(%s)
                    """, (group_idss,))
                    user_ids = [row[0] for row in self.env.cr.fetchall()]
                    rec.group_user_domain_ids = [(6, 0, user_ids)]
                else:
                    rec.group_user_domain_ids = [(5, 0, 0)]
            else:
                rec.group_user_domain_ids = [(5, 0, 0)]

    @api.onchange('has_role')
    def _onchange_has_role(self):
        if self.has_role:
            self.user_id = False
        else:
            self.group_ids = [(5, 0, 0)]

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id and not self.has_role:
            self.group_ids = [(5, 0, 0)]

    def write(self, vals):
        res = super().write(vals)

        signature_fields = {'approval_signed', 'rejected_signed', 'signature'}
        if signature_fields.intersection(vals.keys()):
            for line in self:
                requisition = line.contract_id
                if not requisition:
                    continue
                if requisition.state not in ('approved', 'rejected'):
                    continue
                has_pending = bool(requisition.approval_line_ids.filtered(lambda l: l.status == 'pending'))
                if has_pending:
                    continue
                if not (line.approval_signed or line.rejected_signed or line.signature):
                    continue
                requisition._send_final_approval_notification()

        return res
