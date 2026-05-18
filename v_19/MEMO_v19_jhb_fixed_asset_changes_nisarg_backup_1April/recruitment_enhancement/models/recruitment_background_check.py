from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import timedelta
from markupsafe import Markup

class RecruitmentBackgroundCheck(models.Model):
    _name = 'recruitment.background.check'
    _description = 'Recruitment Background Check'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', copy=False)
    requisition_id = fields.Many2one('recruitment.requisition', required=True)
    applicant_id = fields.Many2one('hr.applicant', required=True)
    interview_session_id = fields.Many2one('recruitment.interview', string="Interview Evaluation")
    check_type = fields.Selection([
        ('credit', 'Credit Record Check'),
        ('cv', 'CV Validation'),
        ('employment', 'Employment Record Verification'),
        ('criminal', 'Criminal Check'),
        ('identity', 'Identity Validation'),
    ], required=True, tracking=True)

    requested_date = fields.Date(default=fields.Date.today)
    completed_date = fields.Date()
    vendor_name = fields.Char()

    status = fields.Selection([
        ('pending', 'Pending'),
        ('clear', 'Clear'),
        ('approval_in_process', 'Approval In Process'),
        ('concern', 'Concern'),
        ('failed', 'Failed'),
    ], default='pending', tracking=True)

    result_notes = fields.Text()
    reviewed_by = fields.Many2one('res.users')


    approval_line_ids = fields.One2many("approval.team.line", "background_check_id", string="Approval Lines")

    approval_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('partially_approved', 'Partially Approved'),
        ('fully_approved', 'Fully Approved'),
        ('rejected', 'Rejected'),
    ], default='not_started', tracking=True)

    state = fields.Selection([
        ("draft", "Draft"),
        ("in_process", "In Process"),
        ("approval_in_process", "Approval In Process"),
        ("approved", "Approved"),
        ("done", "Completed"),
        ("rejected", "Rejected"),
        ('cancelled', 'Cancelled'),
    ], default="draft", tracking=True)

    current_approver_id = fields.Many2one('res.users', string="Current Approver", compute="_compute_current_approver",
                                          store=True)
    is_current_approver = fields.Boolean(string="Is Current Approver", compute="_compute_is_current_approver")
    is_approval_line = fields.Boolean(string="Is Approval Line", compute="_compute_is_approval_line")

    def _compute_is_approval_line(self):
        for rec in self:
            rec.is_approval_line = bool(rec.approval_line_ids)

    @api.depends('current_approver_id')
    def _compute_is_current_approver(self):
        for rec in self:
            if rec.current_approver_id == self.env.user:
                rec.is_current_approver = True
            else:
                rec.is_current_approver = False

    @api.depends('approval_line_ids.status', 'approval_line_ids.sequence')
    def _compute_current_approver(self):
        for rec in self:
            pending_lines = rec.approval_line_ids.filtered(lambda l: l.status == 'pending').sorted('sequence')
            rec.current_approver_id = pending_lines[0].user_id if pending_lines else False


    # def action_start_approval_process(self):
    #     if not self.approval_line_ids:
    #         raise ValidationError(_("Please add at least one approval line before starting the approval process."))

    #     for line in self.approval_line_ids:
    #         if not line.user_id or not line.approver_role_id:
    #             raise ValidationError(
    #                 _("Please select an approver role and a user for all approval lines before starting the approval process."))

    #     self.state = "approval_in_process"
    #     self.status = "approval_in_process"
    #     self.approval_status = 'partially_approved'

    def action_start_approval_process(self):
        if not self.approval_line_ids:
            raise ValidationError(_("Please add at least one approval line before starting the approval process."))

        missing_info = []
        for line in self.approval_line_ids:
            if not line.user_id and not line.approver_role_id:
                missing_info.append(_("Line %s: Missing both approver role and user") % line.sequence)
            elif not line.user_id:
                missing_info.append(_("Line %s: User is missing for approval role ['%s']") % (line.sequence, line.approver_role_id.name))
        if missing_info:
            raise ValidationError(_("Please complete the following approval lines:\n%s") % "\n".join(missing_info))

        self.state = "approval_in_process"
        self.status = "approval_in_process"
        self.approval_status = 'partially_approved'

    def action_approve_applicant(self):
        self.ensure_one()
        login_user = self.env.user

        if login_user != self.current_approver_id:
            raise AccessError(_("You are not authorized to approve this applicant. Current approver is %s.") % (
                    self.current_approver_id.name or _("Unknown")))

        approval_line = self.approval_line_ids.filtered(
            lambda line: line.user_id == login_user and line.status == 'pending')[:1]

        if not approval_line:
            raise AccessError(_("No pending approval line found for you or you have already approved it."))

        if approval_line:
            approval_line.approved = True
            approval_line.status = 'approved'
            approval_line.approval_date = fields.Datetime.now()
            self._update_approval_status()

        approval_signed_required = False
        rejected_signed_required = False
        if approval_line.approval_signed:
            approval_signed_required = True

        if approval_line.rejected_signed:
            rejected_signed_required = True

        # Open wizard for signature
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sign Approval'),
            'res_model': 'approval.team.line',
            'view_mode': 'form',
            'view_id': self.env.ref('recruitment_enhancement.approval_team_line_approved_view_form').id,
            'res_id': approval_line.id,
            'target': 'new',
            'context': {
                'default_requisition_id': self.id,
                'default_approval_line_id': approval_line.id,
                'default_user_id': login_user.id,
                'default_contract_id': self.id,
                'form_view_initial_mode': 'edit',
                'default_approval_signed': approval_signed_required,
                'default_rejected_signed': rejected_signed_required,
            },
        }

    def action_reject_applicant(self):
        self.ensure_one()
        login_user = self.env.user

        if login_user != self.current_approver_id:
            raise AccessError(_("You are not authorized to reject this applicant. Current approver is %s.") % (
                    self.current_approver_id.name or _("Unknown")))

        line = self.approval_line_ids.filtered(lambda l: l.user_id == login_user and l.status == 'pending')[:1]
        if not line:
            raise AccessError(_("No pending approval line found for you."))

        # Mark the line as rejected; user will enter the reason in the popup form
        line.write({
            'status': 'rejected',
            'approval_date': fields.Datetime.now(),
            'approved': False,
        })

        other_lines = self.approval_line_ids.filtered(lambda l: l.status == 'pending')
        other_lines.write({'status': 'rejected'})

        # Mark requisition as rejected
        self.write({
            'state': 'rejected',
        })
        self._update_approval_status()


        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Requisition'),
            'res_model': 'approval.team.line',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'recruitment_enhancement.approval_team_line_reject_view_form'
            ).id,
            'res_id': line.id,
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
                'default_user_id': login_user.id,
                'form_view_initial_mode': 'edit',
            },
        }

    def _update_approval_status(self):
        total_lines = len(self.approval_line_ids)
        approved_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'approved'))
        rejected_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'rejected'))
        pending_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'pending'))

        if pending_count > 0:
            self.approval_status = 'partially_approved'
        elif rejected_count > 0:
            self.state = "rejected"
            self.approval_status = 'rejected'
            self._set_status('failed')
        else:
            self.state = "approved"
            self.approval_status = 'fully_approved'
            self._set_status('clear')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.background.check') or 'New'
        return super().create(vals_list)

    def _set_status(self, status):
        self.write({
            'status': status,
            'completed_date': fields.Date.today(),
            'reviewed_by': self.env.user.id,
        })

    def action_mark_pending(self):
        self._set_status('pending')
        if self.approval_line_ids:
            self.approval_line_ids.unlink()

    def action_mark_concern(self):
        self._set_status('concern')

    def action_mark_failed(self):
        self._set_status('failed')

    @classmethod
    def _mandatory_types(cls):
        return {'credit', 'cv', 'employment', 'criminal', 'identity'}
