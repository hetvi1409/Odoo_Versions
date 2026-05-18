from odoo import models, fields, api, _
from odoo.tools import date_utils, format_list
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, AccessError, UserError
from markupsafe import Markup
import re
import logging

_logger = logging.getLogger(__name__)


class AnnualProcurementPlan(models.Model):
    _name = "annual.procurement.plan"
    _description = "Annual Procurement Plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name desc"

    def _get_fiscal_year_selection(self):
        today = fields.Date.today()
        selection = []
        fiscal_start, fiscal_end = date_utils.get_fiscal_year(today, self.env.company.fiscalyear_last_day,
                                                              int(self.env.company.fiscalyear_last_month))

        for year in range(5):
            start = fiscal_start - date_utils.get_timedelta(year, "year")
            end = fiscal_end - date_utils.get_timedelta(year, "year")
            selection.append((fields.Date.to_string(start), f"{start.strftime('%Y')}/{end.strftime('%y')}"))
        return selection

    def _default_fiscal_year(self):
        return self._get_fiscal_year_selection()[0][0]

    def _default_currency(self):
        # try to find ZAR first, otherwise fall back to the company currency or any currency
        currency = self.env['res.currency'].search([('name', '=', 'ZAR')], limit=1)
        if not currency and self.env.company:
            currency = self.env.company.currency_id
        if not currency:
            currency = self.env['res.currency'].search([], limit=1)
        return currency.id if currency else False

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == _('New'):
            # Try to get a sequence from ir.sequence first
            sequence_number = self.env['ir.sequence'].next_by_code('annual.procurement.plan.seq')

            if not sequence_number:
                # Fallback: compute next number from the last record's name field
                last = self.search([('name', '!=', False)], order='id desc', limit=1)
                if last and last.name:
                    # Extract number from last name
                    match = re.search(r'(\d+)(?!.*\d)', last.name)
                    next_num = int(match.group(0)) + 1 if match else 1
                else:
                    next_num = 1

                # Get the current year from fiscal_year or use current year
                year = datetime.now().year
                if vals.get('fiscal_year'):
                    # fiscal_year is stored as date string, extract year from it
                    try:
                        year = int(vals['fiscal_year'].split('-')[0])
                    except (ValueError, IndexError, AttributeError):
                        year = datetime.now().year

                # Generate sequence number with APP prefix and actual year
                sequence_number = f"ANNUAL-APP-IMPORT-YEAR-{year}-{str(next_num).zfill(4)}"

            vals['name'] = sequence_number

        res = super(AnnualProcurementPlan, self).create(vals)
        res._set_procurement_config_defaults()
        return res

    def write(self, vals):
        res = super().write(vals)
        if 'total_app_budget' in vals or not vals.get('procurement_method_config_id'):
            self._set_procurement_config_defaults()
        return res

    # name = fields.Char(string="Reference", required=True, readonly=True, copy=False, default=lambda self: _('New'))
    # name = fields.Char(string="Reference", required=True)
    name = fields.Char(
        string="Plan Reference",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    sequence_number = fields.Char(string="Sequence Number", readonly=True, copy=False, index=True)
    entity_name = fields.Char(string="Procurement Entity Name")
    user_id = fields.Many2one("res.users", string="PMO / End User")
    # DEPRECATED: Legacy field - kept for backward compatibility, computed from procurement_method_config_id
    procurement_method = fields.Selection([
        ('Request for Proposal', 'Request for Proposal'),
        ('Request for Quotation', 'Request for Quotation'),
        ('Request For Quotations method', 'Request For Quotations method'),
        ('Pre Qualification', 'Pre Qualification'),
        ('Open Tender', 'Open Tender'),
        ('Restricted Tender', 'Restricted Tender'),
        ('Restricted Bidding Method', 'Restricted Bidding Method'),
        ('Direct Procurement', 'Direct Procurement / Benchmarking'),
        ('Direct Procurement Method', 'Direct Procurement Method / Benchmarking'),
        ('Framework Agreement', 'Framework Agreement'),
        ('Competitive Bidding Method', 'Competitive Bidding Method'),
        ('Single-source selection method', 'Single-source selection method'),
        ('Selection of Individual consultant method', 'Selection of Individual consultant method'),
        ('Selection Amongst Community Service Organizations', 'Selection Amongst Community Service Organizations'),
        ('Expression of Intrest', 'Expression of Intrest'),
        ('other', 'Other'),
    ], string='Procurement Method (Legacy)', compute='_compute_legacy_fields', store=True, readonly=True,
       help='DEPRECATED: Use procurement_method_config_id instead. This field is auto-computed for compatibility.')
    procurement_method_config_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method Configuration',
        help='Recommended procurement method based on total APP value'
    )
    preference_point_system_config_id = fields.Many2one(
        'sagovpreference.point.system',
        string='Preference Point System Configuration',
        help='Recommended preference point system based on total APP value'
    )
    indicative = fields.Selection([("Yes", "Yes"), ("No", "No"), ], string="Status", default="No")
    company_id = fields.Many2one("res.company", string="Company")
    fiscal_year = fields.Selection(selection="_get_fiscal_year_selection", string="Fiscal Year",
                                   default=_default_fiscal_year)
    department_id = fields.Many2one("hr.department", string="Department")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("reviewed", "Reviewed"),
        ("awaiting_approval", "Awaiting Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("published", "Published"),
    ], string="Status", default="draft", tracking=True)
    initiator_id = fields.Many2one("res.users", string="Initiator", default=lambda self: self.env.user,
                                   help="App Initiator / Creator", tracking=True)
    reviewer_ids = fields.One2many('app.reviewer', 'app_id', string="Reviewers", store=True)
    approver_id = fields.Many2one("res.users", string="Approver", help="Person who must approve the APP", tracking=True)
    approver_sign = fields.Binary("Approver Signature")
    approve_comment = fields.Text("Approver Comment")

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    approve_date = fields.Date(string="Approve Date")

    estimated_budget_total_from = fields.Float(string="Budget From")
    estimated_budget_total_to = fields.Float(string="Budget To")
    total_app_budget = fields.Float(string="Total APP Budget")
    total_unused_budget = fields.Float(string="Total Unused Budget")
    currency_id = fields.Many2one("res.currency", string="Currency", default=_default_currency)
    notes = fields.Text(string="Notes")

    org_structure = fields.Binary(string="Overall Organizational Structure of the Procuring Entity")
    pmu_structure = fields.Binary(string="Procurement Management Unit Structure")
    accounting_officer_identity = fields.Binary(string="Identity of Procuring Entity Accounting Officer")
    evaluation_committee_members = fields.Binary(string="Evaluation Committee Members")
    disposal_committee_members = fields.Binary(string="Disposal Committee Members")
    procuring_entities_facilities = fields.Binary(string="Procuring Entities Facilities for PMU")
    signed_copy_app = fields.Binary(string="Upload a Signed Copy of APP")
    asset_disposal_plan = fields.Binary(string="Asset Disposal Plan (.xlsx only)")
    asset_disposal_plan_filename = fields.Char(string="Asset Disposal Plan Filename")

    allowed_user_ids = fields.Many2many('res.users', 'app_allowed_user_rel', 'app_id', 'user_id',
                                        string='Turn-based Allowed Users', compute='_compute_allowed_user_ids',
                                        store=True, compute_sudo=True, )
    show_submit_button = fields.Boolean("Show Submit Button", compute="_compute_show_submit", default=False)
    show_reviewed = fields.Boolean("Show reviewed",
                                      compute="_compute_show_submit", default=False)
    can_delete_lines = fields.Boolean(compute="_compute_can_delete_lines", string="Can Delete QA/Recommender Lines")

    def _compute_can_delete_lines(self):
        for rec in self:
            if rec.state in ['draft','submitted'] and self.env.user.id in [rec.initiator_id.id, rec.create_uid.id]:
                rec.can_delete_lines = True
            else:
                rec.can_delete_lines = False

    def _check_xlsx_format(self):
        for rec in self:
            if rec.asset_disposal_plan and not rec.asset_disposal_plan_filename.lower().endswith('.xlsx'):
                raise ValidationError("Asset Disposal Plan must be an .xlsx file.")

    _constraints = [
        (_check_xlsx_format, "Invalid file type for Asset Disposal Plan", ['asset_disposal_plan'])
    ]

    line_ids = fields.One2many(
        "annual.procurement.plan.line",
        "plan_id",
        string="Procurement Lines"
    )

    @api.depends('procurement_method_config_id')
    def _compute_legacy_fields(self):
        """Compute legacy field from configuration field for backward compatibility"""
        for record in self:
            if record.procurement_method_config_id:
                # Map to closest matching selection value
                method_name = record.procurement_method_config_id.name
                # Try to match common patterns
                selection_map = {
                    'Request for Proposal': 'Request for Proposal',
                    'Request for Quotation': 'Request for Quotation',
                    'Open Tender': 'Open Tender',
                    'Competitive': 'Competitive Bidding Method',
                    'Single': 'Single-source selection method',
                    'Framework': 'Framework Agreement',
                }
                matched = False
                for key, value in selection_map.items():
                    if key in method_name:
                        record.procurement_method = value
                        matched = True
                        break
                if not matched:
                    record.procurement_method = 'other'
            else:
                record.procurement_method = False

    @api.onchange('total_app_budget')
    def _onchange_total_app_budget(self):
        """Suggest procurement method based on total APP budget"""
        if self.total_app_budget:
            method = self.env['sagovprocurement.method'].get_applicable_method(
                self.total_app_budget
            )
            if method:
                self.procurement_method_config_id = method
                if method.preference_point_system_ids:
                    self.preference_point_system_config_id = method.preference_point_system_ids[0]

    @api.onchange('procurement_method_config_id')
    def _onchange_procurement_method_config(self):
        """When procurement method changes, update related fields and trigger dependent calculations"""
        if self.procurement_method_config_id:
            if self.procurement_method_config_id.preference_point_system_ids:
                self.preference_point_system_config_id = (
                    self.procurement_method_config_id.preference_point_system_ids[0]
                )

    @api.onchange('preference_point_system_config_id')
    def _onchange_preference_point_system_config(self):
        """When preference point system changes, trigger dependent calculations"""
        # Ensure dependent fields are properly recalculated on form change
        pass

    def _set_procurement_config_defaults(self):
        for record in self:
            if not record.total_app_budget:
                continue
            if record.procurement_method_config_id:
                continue
            method = record.env['sagovprocurement.method'].get_applicable_method(
                record.total_app_budget
            )
            if method:
                record.procurement_method_config_id = method
                if method.preference_point_system_ids:
                    record.preference_point_system_config_id = method.preference_point_system_ids[0]

    def _compute_show_submit(self):
        for app in self:
            if self.env.user.id in [app.initiator_id.id, app.create_uid.id] and app.state == 'draft':
                app.show_submit_button = True
            else:
                app.show_submit_button = False
            if app.sudo().reviewer_ids:
                remaining_reviewers = app.sudo().reviewer_ids.filtered(
                    lambda l: l.required and (l.status != 'Completed' or not l.sign_initials))
                if not remaining_reviewers and self.env.user.id in app.reviewer_ids.mapped(
                        'user_id.id') and app.state in ['submitted']:
                    app.show_reviewed = True
                else:
                    app.show_reviewed = False
            else:
                app.show_reviewed = False

    @api.depends(
        'create_uid', 'initiator_id', 'state',
        'reviewer_ids.user_id', 'reviewer_ids.sign_initials', 'reviewer_ids.sequence',
        'approver_id', 'approver_sign',)
    def _compute_allowed_user_ids(self):
        for rec in self:
            allowed = set()

            # Always: creator + initiator
            if rec.create_uid:
                allowed.add(rec.create_uid.id)
            if rec.initiator_id:
                allowed.add(rec.initiator_id.id)

            # Reviewers: same logic
            rec_signed_users = rec.reviewer_ids.filtered(lambda r: r.sign_initials).mapped('user_id')
            allowed.update(u.id for u in rec_signed_users)
            if rec.state == 'submitted':
                pending_recs = rec.reviewer_ids.filtered(lambda r: not r.sign_initials).sorted('sequence')
                if pending_recs:
                    next_rec_user = pending_recs[0].user_id
                    if next_rec_user:
                        allowed.add(next_rec_user.id)

            # Approver logic
            if rec.approver_id:
                # Approver should always see app when approval is pending or done/rejected
                if rec.state in ['awaiting_approval', 'approved', 'rejected', 'published']:
                    allowed.add(rec.approver_id.id)
            if rec.approver_sign and rec.approver_id:
                allowed.add(rec.approver_id.id)
            # print("\n\n====allowed_user_ids==",rec.allowed_user_ids,allowed)
            rec.allowed_user_ids = [(6, 0, list(allowed))]

    def action_app_line_delete(self):
        # Immediately delete all APP lines for the plan with no UI notification or refresh.
        for plan in self:
            if plan.line_ids:
                plan.line_ids.sudo().unlink()
        return None

    def action_submit(self):
        if not self.reviewer_ids:
            raise ValidationError("Please add Reviewers before submit the APP.")
        if not self.approver_id:
            raise ValidationError("Please add Approver before submit the APP.")
        if self.create_uid != self.env.user and self.initiator_id.id != self.env.user.id:
            raise ValidationError(
                "Only app create user or Initiator user can submit for review.")
        if not self.line_ids:
            raise ValidationError("Please add procurement lines before submitting the app.")
        self.state = 'submitted'
        self._notify_next_reviewer()

    def _notify_next_reviewer(self):
        pending_reviewers = self.reviewer_ids.filtered(
            lambda r: not r.sign_initials and r.status not in ['Completed', 'Not-Completed'])
        if pending_reviewers:
            next_reviewer = pending_reviewers.sorted(key=lambda r: r.sequence)[0]
            next_reviewer.sudo().action_send_mail()
        else:
            # All reviewers are done — now notify the approver
            self.state = 'awaiting_approval'
            self._notify_next_approver()

    def action_reset_to_draft(self):
        self.state = 'draft'

    def action_review(self):
        if self.env.user.id not in self.reviewer_ids.mapped('user_id.id'):
            raise ValidationError("Only Reviewer can reviewed app.")
        if self.sudo().reviewer_ids:
            pending_reviewers = self.sudo().reviewer_ids.filtered(
                lambda l: getattr(l, 'required', True) and (
                        (l.status != 'Completed') or not l.sign_initials))
            if pending_reviewers:
                raise ValidationError("All Reviewers user must be signed and completed review app.")
        self.state = 'reviewed'

    def action_send_for_approval(self):
        if not self.approver_id:
            raise ValidationError("Please add approver before submit for approval.")
        self.state = 'awaiting_approval'
        template = self.env.ref('sa_government_tender.mail_template_app_submit')
        action = self.env['ir.actions.act_window']._for_xml_id('sa_government_tender.action_annual_procurement_plan')
        base_url = self.get_base_url()
        url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
        user = self.approver_id.name
        template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                       email_values={
                                                                                           'email_to': self.approver_id.partner_id.email})

    def _notify_next_approver(self):
        template = self.env.ref('sa_government_tender.mail_template_app_submit')
        action = self.env['ir.actions.act_window']._for_xml_id('sa_government_tender.action_annual_procurement_plan')
        base_url = self.get_base_url()
        url = base_url + '/odoo/' + action.get('path') + '/' + str(self.id)
        user = self.approver_id.name
        template.with_context(approve_user=user, request='approve', url=url).send_mail(self.id, force_send=True,
                                                                                       email_values={
                                                                                           'email_to': self.approver_id.partner_id.email})

    def action_sign_approver(self):
        if not self.approver_id:
            raise ValidationError("Please add Approver before sign the app.")
        if self.approver_id.id != self.env.user.id:
            raise ValidationError("Only approver can sign approve app.")
        if self.sudo().reviewer_ids:
            pending_reviewers = self.sudo().reviewer_ids.filtered(
                lambda l: getattr(l, 'required', True) and (
                        (l.status != 'Completed') or not l.sign_initials))
            if pending_reviewers:
                raise ValidationError("All Reviewers user must be signed and completed review app.")
        if self.approve_comment and not re.search(r'\w+', self.approve_comment):
            raise UserError("You must provide a valid comment before approving (not just spaces or symbols).")
        return {
            'name': 'Sign Approver',
            'type': 'ir.actions.act_window',
            'res_model': 'app.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_app_id': self.id,
                'default_field': 'approver_sign',
                'default_user_id': self.approver_id.id,
                'default_mode': 'approver',
            }
        }

    def action_reject(self):
        """Open wizard to capture rejection reason"""
        if self.approver_id.id != self.env.user.id:
            raise ValidationError("Only approver can reject app.")

        return {
            'name': 'Reject APP',
            'type': 'ir.actions.act_window',
            'res_model': 'app.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_app_id': self.id,
            }
        }

    def action_approve(self):
        """Approve APP and create sagovtender.annual.procurement.plan records for lines that don't have one yet.
        Ensures required sagov APP fields are filled with sensible defaults and writes back
        the sagov APP link to the APP line.
        """
        sagov_app_model = self.env['sagovtender.annual.procurement.plan']

        for plan in self:
            if plan.reviewer_ids:
                pending_reviewers = plan.sudo().reviewer_ids.filtered(
                    lambda l: getattr(l, 'required', True) and (
                            (l.status != 'Completed') or not l.sign_initials))
                if pending_reviewers:
                    raise ValidationError("Reviewers must be signed and reviewed.")
            if plan.create_uid == self.env.user or plan.initiator_id == self.env.user:
                raise ValidationError(
                    "You are not allowed to approve your own app. Please contact your approvers.")

            if plan.approver_id.id != self.env.user.id:
                raise ValidationError("Only approver can approve app.")
            if not plan.approver_sign:
                raise ValidationError("Please add approver signature before approve app.")
            plan.state = 'approved'
            for line in plan.line_ids:
                # skip if already linked
                if line.sagov_app_id:
                    continue

                # Build sagov APP name — include plan name + APP line name (+ requirements if present)
                app_line_label = line.name or f"Line {line.sequence or line.id}"
                parts = []
                if plan.name:
                    parts.append(plan.name)
                parts.append(app_line_label)
                if line.requirements:
                    parts.append(line.requirements)
                sagov_app_name = " - ".join(parts)

                # Determine fiscal year from plan dates (fallback to current year)
                fiscal_year = ""
                if plan.date_start:
                    start_date = plan.date_start if isinstance(plan.date_start, str) else plan.date_start.isoformat()
                    year = int(start_date.split('-')[0])
                    fiscal_year = f"{year}/{year + 1}"
                else:
                    current_year = datetime.now().year
                    fiscal_year = f"{current_year}/{current_year + 1}"

                # Map procurement method from line to sagov selection
                sagov_procurement_method = 'tender'  # default
                if line.procurement_method:
                    method_map = {
                        "Competitive Bidding Method": "tender",
                        "Restricted Bidding Method": "tender",
                        "Direct Procurement Method": "single_source",
                        "Request For Quotations method": "quotation",
                        "Single-source selection method": "single_source",
                        "Selection of Individual consultant method": "single_source",
                        "Selection Amongst Community Service Organizations": "quotation",
                        "Expression of Intrest": "tender",
                        "Request for Proposal": "tender",
                        "Pre Qualification": "tender",
                    }
                    sagov_procurement_method = method_map.get(line.procurement_method, 'tender')

                # Prepare sagov APP values
                vals = {
                    'name': sagov_app_name,
                    'fiscal_year': fiscal_year,
                    'item_description': line.requirements or sagov_app_name,
                    'estimated_value': line.total or 0,
                    'available_budget': plan.budget_amount if hasattr(plan, 'budget_amount') else line.total or 0,
                    'procurement_method': sagov_procurement_method,
                    'planned_date': line.tender_notice_date or plan.date_start or fields.Date.today(),
                    'company_id': plan.company_id.id or self.env.company.id,
                    'state': 'approved',
                    'source_app_line_id': line.id,
                    'source_app_id': plan.id,
                }

                # Add department if available
                if plan.department_id:
                    vals['department_id'] = plan.department_id.id
                else:
                    # Try to get department from line user or use current user's department
                    if line.user_id and line.user_id.employee_id and line.user_id.employee_id.department_id:
                        vals['department_id'] = line.user_id.employee_id.department_id.id
                    else:
                        # Find first department or create a default one
                        dept = self.env['hr.department'].search([], limit=1)
                        if dept:
                            vals['department_id'] = dept.id

                # Add optional fields if available
                if line.class_of_procurement:
                    vals['budget_line'] = line.class_of_procurement
                if line.source_of_funds:
                    vals['notes'] = line.source_of_funds

                # Create sagov APP record
                try:
                    sagov_app_rec = sagov_app_model.create(vals)
                except Exception as e:
                    _logger.exception("Failed creating sagov APP for APP line %s: %s", getattr(line, 'id', '?'), e)
                    continue

                # Write back sagov APP link
                try:
                    line.sudo().write({
                        'sagov_app_created': True,
                        'sagov_app_id': sagov_app_rec.id,
                    })
                except Exception as e:
                    _logger.exception("Failed writing sagov APP backlink to APP line %s: %s", getattr(line, 'id', '?'), e)
                    try:
                        line.sudo().write({'sagov_app_id': sagov_app_rec.id})
                    except Exception:
                        _logger.exception("Failed writing minimal sagov APP backlink for APP line %s",
                                          getattr(line, 'id', '?'))

        # After processing all plans/lines: show effect only if every APP line has a sagov APP
        all_created = True
        for plan in self:
            for ln in plan.line_ids:
                if not (ln.sagov_app_id or ln.sagov_app_created):
                    all_created = False
                    break
            if not all_created:
                break

        if all_created:
            return {
                "effect": {
                    "fadeout": "slow",
                    "message": "APP + APP Lines Approved and Sagov APPs Created Successfully!",
                    "type": "rainbow_man",
                }
            }
        return None


class APPReviewer(models.Model):
    _name = 'app.reviewer'
    _description = 'APP Reviewer'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence', default=1)
    required = fields.Boolean(string="Required", default=True)
    user_id = fields.Many2one('res.users', string="User", required=True,
                              domain="['|', ('id', 'not in', existing_request_user_ids), ('id', '=', user_id)]")
    display_name = fields.Char(related='user_id.name', readonly=True, store=True)
    existing_request_user_ids = fields.Many2many('res.users', compute='_compute_existing_request_user_ids')
    status = fields.Selection(
        [('Completed', 'Completed'), ('Not-Completed', 'Not-Completed')], string="Status", default='')
    app_id = fields.Many2one('annual.procurement.plan', string="APP", ondelete='cascade')
    sign_initials = fields.Binary(string="Digital Initials", copy=False)
    comment = fields.Text("Comment")
    date = fields.Datetime(string="Date")
    is_editable = fields.Boolean(compute='_compute_is_editable', string="Can Edit")

    @api.depends('user_id', 'comment', 'status')
    def _compute_is_editable(self):
        current_user = self.env.user
        for rec in self:
            rec.is_editable = (
                    current_user.id in [
                rec.app_id.create_uid.id if rec.app_id.create_uid else False,
                rec.app_id.initiator_id.id if rec.app_id.initiator_id else False,
                rec.user_id.id if rec.user_id else False,
            ])

    def _create_activity(self):
        for reviewer in self:
            reviewer.app_id.activity_schedule(
                'sa_government_tender.mail_activity_app_review',
                user_id=reviewer.user_id.id)

    @api.depends('app_id.reviewer_ids.user_id')
    def _compute_existing_request_user_ids(self):
        for approver in self:
            approver.existing_request_user_ids = self.mapped('app_id.reviewer_ids.user_id')._origin or False

    def write(self, vals):
        # Skip validations when resetting APP to draft
        if self.env.context.get('reset_to_draft'):
            return super(APPReviewer, self).write(vals)
        trigger_next = False
        for record in self:
            if 'sign_initials' in vals and record.sudo().user_id.id != self.env.uid:
                raise ValidationError("You cannot sign on behalf of another user.")
            if 'sign_initials' in vals and ('comment' in vals and not record.comment) and (
                    'status' not in vals and (record.status == '' or record.status is False)):
                raise ValidationError("Please add Review Status.")
            if 'sign_initials' in vals:
                vals['date'] = fields.Datetime.now()
                trigger_next = True  # Flag to notify next reviewer
        result = super(APPReviewer, self).write(vals)
        for record in self:
            if record.status == 'Not-Completed' and record.sign_initials:
                trigger_next = False
                if record.app_id:
                    template = self.env.ref('sa_government_tender.mail_template_app_submit')
                    action = self.env['ir.actions.act_window']._for_xml_id(
                        'sa_government_tender.action_annual_procurement_plan')
                    base_url = self.get_base_url()
                    url = base_url + '/odoo/' + action.get('path') + '/' + str(record.app_id.id)
                    user = record.app_id.create_uid.name
                    template.with_context(approve_user=user, request=record.status, url=url).sudo().send_mail(
                        record.app_id.id, force_send=True,
                        email_values={
                            'email_to': record.app_id.create_uid.partner_id.email})
                record.app_id.state = 'draft'
            if trigger_next:
                # record.app_id.state = 'reviewed'
                record.app_id.sudo()._notify_next_reviewer()
        return result

    def action_send_mail(self):
        template = self.env.ref('sa_government_tender.mail_template_app_submit')
        action = self.env['ir.actions.act_window']._for_xml_id('sa_government_tender.action_annual_procurement_plan')
        base_url = self.get_base_url()
        url = base_url + '/odoo/' + action.get('path') + '/' + str(self.app_id.id)
        user = self.user_id.name
        template.with_context(approve_user=user, request='review', url=url).sudo().send_mail(
            self.app_id.id, force_send=True,
            email_values={
                'email_to': self.user_id.partner_id.email})

    def action_sign_line(self):
        reviewers = self.app_id.reviewer_ids.sorted(key=lambda r: r.sequence)
        pending_reviewers = reviewers.filtered(lambda r: not r.sign_initials)
        if pending_reviewers and self in pending_reviewers:
            first_pending = pending_reviewers[0]
            if self != first_pending:
                raise ValidationError("You cannot sign before the previous reviewer has signed.")
        if not self.status:
            raise ValidationError("Please add Review Status.")
        if not self.comment or not re.search(r'\w+', self.comment):
            raise UserError("You must provide a valid comment before sign (not just spaces or symbols).")
        return {
            'name': 'Sign',
            'type': 'ir.actions.act_window',
            'res_model': 'app.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_app_id': self.app_id.id,
                'default_user_id': self.user_id.id,
                'default_mode': 'review',
            }
        }

    def unlink(self):
        for rec in self:
            if rec.app_id.state not in ('draft'):
                allowed = False
                if self.env.user in (rec.app_id.create_uid, rec.app_id.initiator_id):
                    allowed = True
                if not allowed:
                    raise AccessError(_("You do not have permission to delete this Reviewer line."))

        return super(APPReviewer, self).unlink()
