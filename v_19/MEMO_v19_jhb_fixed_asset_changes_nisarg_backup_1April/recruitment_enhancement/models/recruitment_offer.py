from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RecruitmentOffer(models.Model):
    _name = 'recruitment.offer'
    _description = 'Recruitment Final Offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', copy=False)
    requisition_id = fields.Many2one('recruitment.requisition', required=True)
    interview_session_id = fields.Many2one('recruitment.interview.session')
    applicant_id = fields.Many2one('hr.applicant', required=True, domain="[('job_id', '=', requisition_id.job_id)]")

    offer_date = fields.Date(default=fields.Date.today)
    proposed_start_date = fields.Date()
    contract_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('fixed_term', 'Fixed Term'),
    ], required=True, default='permanent')
    salary_offered = fields.Float(digits=(16, 2))

    requires_ceo_cfo_approval = fields.Boolean()
    final_approver_id = fields.Many2one('res.users')

    offer_letter_file = fields.Binary(attachment=True)
    offer_letter_filename = fields.Char()
    contract_file = fields.Binary(attachment=True)
    contract_filename = fields.Char()

    onboarding_it_account = fields.Boolean()
    onboarding_access_card = fields.Boolean()
    onboarding_workstation = fields.Boolean()
    onboarding_induction = fields.Boolean()
    policy_acknowledgement_signed = fields.Boolean()
    confidentiality_signed = fields.Boolean()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('sent', 'Sent to Candidate'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    ], default='draft', tracking=True)

    background_check_ok = fields.Boolean(compute='_compute_background_check_ok')

    @api.depends('applicant_id', 'requisition_id')
    def _compute_background_check_ok(self):
        mandatory = self.env['recruitment.background.check']._mandatory_types()
        for rec in self:
            if not rec.applicant_id or not rec.requisition_id:
                rec.background_check_ok = False
                continue
            checks = self.env['recruitment.background.check'].search([
                ('requisition_id', '=', rec.requisition_id.id),
                ('applicant_id', '=', rec.applicant_id.id),
            ])
            found_types = set(checks.mapped('check_type'))
            clear_types = set(checks.filtered(lambda c: c.status == 'clear').mapped('check_type'))
            rec.background_check_ok = mandatory.issubset(found_types) and mandatory.issubset(clear_types)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.offer') or 'New'
        return super().create(vals_list)

    def action_submit_for_approval(self):
        for rec in self:
            if not rec.background_check_ok:
                raise ValidationError(_('All mandatory background checks must be clear before sending for approval.'))
            rec.state = 'to_approve'

    def action_approve(self):
        self.write({'state': 'approved', 'final_approver_id': self.env.user.id})

    def action_send_offer(self):
        for rec in self:
            if rec.state != 'approved':
                raise ValidationError(_('Only approved offers can be sent.'))
            rec.state = 'sent'

    def action_mark_accepted(self):
        hired_stage = self.env['hr.recruitment.stage'].search([('hired_stage', '=', True)], limit=1)
        for rec in self:
            rec.state = 'accepted'
            if hired_stage:
                rec.applicant_id.stage_id = hired_stage.id
            rec.applicant_id.date_closed = fields.Datetime.now()

    def action_mark_rejected(self):
        self.write({'state': 'rejected'})

    def action_close(self):
        self.write({'state': 'closed'})
