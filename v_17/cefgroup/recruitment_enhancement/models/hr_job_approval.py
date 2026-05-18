from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError


class HrJobApproval(models.Model):
    _inherit = 'hr.job'

    approval_team_id = fields.Many2one('approval.team', string='Approval Team', domain="[('model','=','hr.job')]")
    # approval_line_ids is already defined in hr.job by the user

    approval_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('partially_approved', 'Partially Approved'),
        ('fully_approved', 'Fully Approved'),
        ('rejected', 'Rejected'),
    ], default='not_started', tracking=True)

    current_approver_id = fields.Many2one('res.users', string="Current Approver", compute="_compute_current_approver", store=True)
    is_current_approver = fields.Boolean(string="Is Current Approver", compute="_compute_is_current_approver")

    @api.depends('current_approver_id')
    def _compute_is_current_approver(self):
        for rec in self:
            if rec.current_approver_id == self.env.user:
                rec.is_current_approver = True
            else:
                rec.is_current_approver = False

    @api.depends('approval_line_ids.status', 'approval_line_ids.sequence','approval_team_id')
    def _compute_current_approver(self):
        for rec in self:
            pending_lines = rec.approval_line_ids.filtered(lambda l: l.status == 'pending').sorted('sequence')
            rec.current_approver_id = pending_lines[0].user_id if pending_lines else False


    def action_start_approval_process(self):
        if not self.approval_line_ids:
            raise ValidationError(_("Please add at least one approval line before starting the approval process."))

        for line in self.approval_line_ids:
            if not line.user_id or not line.approver_role_id:
                raise ValidationError(_("Please select an approver role and a user for all approval lines before starting the approval process."))

        self.requisition_state = "submitted" # Mapping slightly to what v17 uses
        self.approval_status = 'partially_approved'

    def action_approve_requisition_flow(self):
        self.ensure_one()
        login_user = self.env.user

        if login_user != self.current_approver_id:
            raise AccessError(_("You are not authorized to approve this document. Current approver is %s.") % (self.current_approver_id.name or _("Unknown")))

        approval_line = self.approval_line_ids.filtered(lambda line: line.user_id == login_user and line.status == 'pending')[:1]

        if not approval_line:
            raise AccessError(_("No pending approval line found for you or you have already approved it."))

        if approval_line:
            approval_line.approved = True
            approval_line.status = 'approved'
            approval_line.approval_date = fields.Datetime.now()
            self._update_approval_status()
            self._notify_approval_line_users('Approved', login_user)

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
                'default_contract_id': self.id,
                'default_approval_line_id': approval_line.id,
                'default_user_id': login_user.id,
                'form_view_initial_mode': 'edit',
                'default_approval_signed': approval_signed_required,
                'default_rejected_signed': rejected_signed_required,
            },
        }

    def action_reject_requisition_flow(self):
        self.ensure_one()
        login_user = self.env.user

        if login_user != self.current_approver_id:
            raise AccessError(_("You are not authorized to reject this document. Current approver is %s.") % (self.current_approver_id.name or _("Unknown")))

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
            'requisition_state': 'rejected',
        })

        self._notify_approval_line_users('Rejected', login_user, reason=line.reject_reason)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Requisition'),
            'res_model': 'approval.team.line',
            'view_mode': 'form',
            'view_id': self.env.ref('recruitment_enhancement.approval_team_line_reject_view_form').id,
            'res_id': line.id,
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
                'default_user_id': login_user.id,
                'form_view_initial_mode': 'edit',
            },
        }

    def _update_approval_status(self):
        pending_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'pending'))
        rejected_count = len(self.approval_line_ids.filtered(lambda l: l.status == 'rejected'))

        if pending_count > 0:
            self.approval_status = 'partially_approved'
        elif rejected_count > 0:
            self.requisition_state = "rejected"
            self.approval_status = 'rejected'
        else:
            self.requisition_state = "approved"
            self.approval_status = 'fully_approved'

    def _notify_approval_line_users(self, status, action_user, reason=False):
        self.ensure_one()
        partners = self.approval_line_ids.mapped('user_id.partner_id')
        if not partners:
            return

        # We gracefully handle missing mail_template if v_19 email_template isn't needed fully, 
        # or we just log a message if it's missing.
        try:
            template = self.env.ref('recruitment_enhancement.mail_template_requisition_line_update', raise_if_not_found=False)
            if template:
                url = "%s/web#id=%s&model=%s&view_type=form" % (self.get_base_url(), self.id, self._name)
                template.with_context(
                    status=status,
                    action_user=action_user.name,
                    reason=reason,
                    url=url,
                ).sudo().send_mail(
                    self.id,
                    force_send=True,
                    email_values={'recipient_ids': [(6, 0, partners.ids)]}
                )
        except Exception:
            pass
