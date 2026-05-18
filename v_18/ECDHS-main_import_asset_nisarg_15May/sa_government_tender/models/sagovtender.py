# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
import secrets


class TenderTender(models.Model):
    """Main Tender Model - Central to tender process (Steps 4-11)"""
    _name = 'sagovtender.tender'
    _description = 'Tender'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'create_date desc, name'

    name = fields.Char(
        string='Tender Number',
        required=False,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('sagovtender.tender')
    )
    access_token = fields.Char(
        string='Access Token',
        copy=False,
        readonly=True,
        index=True,
        help='Unique hex token for public tender URL access'
    )
    title = fields.Char(
        string='Tender Title',
        required=False,
        tracking=True,
        help='Brief title of the tender'
    )
    requisition_id = fields.Many2one(
        'sagovtender.purchase.requisition',
        string='Purchase Requisition',
        tracking=True,
        help='Select a requisition. If an APP is chosen, this list is filtered to that APP.'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    requisition_app_id = fields.Many2one(
        'sagovtender.annual.procurement.plan',
        string='Annual Procurement Plan',
        tracking=True,
        help='Optional. Choose an APP to filter requisitions; leave blank to see all approved requisitions.',
        default=lambda self: self.env.context.get('default_requisition_app_id')
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    specification_id = fields.Many2one(
        'sagovtender.specification',
        string='Specification',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    description = fields.Html(
        string='Tender Description',
        required=False,
        sanitize=True,
        sanitize_tags=True,
        sanitize_attributes=True,
        sanitize_style=True,
        strip_style=False,
        strip_classes=False,
        help='Full description of tender requirements'
    )

    @api.onchange('requisition_app_id')
    def _onchange_requisition_app_id(self):
        """Filter requisitions by APP when selected; otherwise show all approved."""
        domain = [('state', '=', 'approved')]
        if self.requisition_app_id:
            domain.append(('requisition_app_id', '=', self.requisition_app_id.id))
            if self.requisition_id and self.requisition_id.requisition_app_id != self.requisition_app_id:
                self.requisition_id = False
        return {'domain': {'requisition_id': domain}}

    # Tender Type & Method
    tender_type_id = fields.Many2one(
        'sagovtender.type',
        string='Tender Type',
        required=False,
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    # DEPRECATED: Legacy field - kept for backward compatibility, computed from procurement_method_config_id
    procurement_method = fields.Selection([
        ('rfq', 'Request for Quotation'),
        ('Request for Proposal', 'Request for Proposal'),
        ('Request for Quotation', 'Request for Quotation'),
        ('Request For Quotations method', 'Request For Quotations method'),
        ('tender', 'Competitive Tender'),
        ('Open Tender', 'Open Tender'),
        ('single_source', 'Single Source'),
        ('unsolicited', 'Unsolicited Proposal'),
        ('emergency', 'Emergency Procurement'),
        ('Pre Qualification', 'Pre Qualification'),
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

    # NEW: Configurable procurement method and preference system
    procurement_method_config_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method Configuration',
        help='Link to configurable procurement method per PFMA/MFMA/PPPFA',
        tracking=True
    )
    preference_point_system_config_id = fields.Many2one(
        'sagovpreference.point.system',
        string='Preference Point System Configuration',
        help='Link to configurable preference point system',
        tracking=True
    )
    workflow_stage_ids = fields.One2many(
        related='procurement_method_config_id.workflow_stage_ids',
        string='Workflow Stages',
        readonly=True
    )
    document_requirement_ids = fields.One2many(
        related='procurement_method_config_id.document_requirement_ids',
        string='Document Requirements',
        readonly=True
    )
    evaluation_criteria_ids = fields.One2many(
        related='procurement_method_config_id.evaluation_criteria_ids',
        string='Evaluation Criteria',
        readonly=True
    )

    # Workflow Stages
    current_workflow_stage_id = fields.Many2one(
        'sagovprocurement.workflow.stage',
        string='Current Workflow Stage',
        compute='_compute_current_workflow_stage',
        inverse='_inverse_current_workflow_stage',
        store=True,
        readonly=False,
        help='Current active workflow stage',
        domain="[('id', 'in', workflow_stage_ids)]"
    )
    current_workflow_stage_name = fields.Char(
        related='current_workflow_stage_id.name',
        string='Current Stage',
        store=True
    )
    stage_key = fields.Char(
        string='Stage Key',
        compute='_compute_stage_key',
        store=True,
        help='Normalized stage key derived from the current workflow stage'
    )
    show_tab_description = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_document_checklist = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_documents = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_advertisement = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_briefing_sessions = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_tender_opening = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_bids = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_compliance = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_declarations = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_evaluation = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_sagovbac_review = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_award = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_purchase_order = fields.Boolean(compute='_compute_visible_ui_sections')
    show_tab_downloads = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_start_scm_processing = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_publish_tender = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_start_briefing = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_schedule_briefing = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_complete_briefing = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_open_bid_submission = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_close_submission = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_conduct_opening = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_close_opening = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_start_compliance_check = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_end_compliance_check = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_request_declarations = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_start_evaluation = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_send_to_bac = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_bac_review = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_award_tender = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_view_award = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_cancel_tender = fields.Boolean(compute='_compute_visible_ui_sections')
    show_btn_next_stage = fields.Boolean(compute='_compute_next_stage_controls')

    # NEW: Document Checklist Automation
    document_checklist_ids = fields.One2many(
        'sagovtender.document.checklist',
        'tender_id',
        string='Document Checklist',
        help='Auto-generated document checklist from procurement method'
    )
    mandatory_documents_uploaded = fields.Boolean(
        string='All Mandatory Documents Uploaded',
        compute='_compute_document_status',
        store=True
    )
    documents_completion_rate = fields.Float(
        string='Document Completion (%)',
        compute='_compute_document_status',
        store=True
    )

    # Value & Budget
    estimated_value = fields.Monetary(
        string='Estimated Value',
        compute='_compute_estimated_value',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    approved_budget = fields.Monetary(
        string='Approved Budget',
        related='requisition_id.budget_confirmed_amount',
        currency_field='currency_id',
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=False,
        default=lambda self: self.env.company.currency_id
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    # DEPRECATED: Legacy field - kept for backward compatibility, computed from preference_point_system_config_id
    preference_system = fields.Selection([
        ('80_20', '80/20 System (R30,000 - R500,000)'),
        ('90_10', '90/10 System (Above R500,000)'),
        ('none', 'No Preference Points'),
        ('other', 'Other'),
    ], string='Preference Point System (Legacy)', compute='_compute_legacy_fields', store=True, readonly=True,
       help='DEPRECATED: Use preference_point_system_config_id instead. This field is auto-computed for compatibility.')

    @api.depends('procurement_method_config_id', 'preference_point_system_config_id')
    def _compute_legacy_fields(self):
        """Compute legacy fields from configuration fields for backward compatibility"""
        for record in self:
            # Map procurement method configuration to legacy Selection value
            if record.procurement_method_config_id:
                # Try to find matching selection value, default to 'other'
                method_name = record.procurement_method_config_id.name
                # Direct mapping for common values
                if 'RFQ' in method_name or 'Quotation' in method_name:
                    record.procurement_method = 'rfq'
                elif 'Competitive' in method_name or 'Tender' in method_name:
                    record.procurement_method = 'tender'
                elif 'Single' in method_name or 'Sole' in method_name:
                    record.procurement_method = 'single_source'
                elif 'Emergency' in method_name:
                    record.procurement_method = 'emergency'
                else:
                    record.procurement_method = 'other'
            else:
                record.procurement_method = False

            # Map preference system configuration to legacy Selection value
            if record.preference_point_system_config_id:
                system_type = record.preference_point_system_config_id.system_type
                record.preference_system = system_type if system_type in ['80_20', '90_10'] else 'other'
    def write(self, vals):
        if 'current_workflow_stage_id' in vals:
            for record in self:
                method_id = vals.get('procurement_method_config_id') or record.procurement_method_config_id.id
                workflow_stages = record._get_workflow_stages_for_method(method_id)
                target_stage = self.env['sagovprocurement.workflow.stage'].browse(
                    vals.get('current_workflow_stage_id')
                )
                record._validate_workflow_stage_transition(
                    target_stage,
                    record.current_workflow_stage_id,
                    workflow_stages=workflow_stages
                )
        old_method_map = {}
        if 'procurement_method_config_id' in vals:
            old_method_map = {record.id: record.procurement_method_config_id.id for record in self}

        res = super().write(vals)
        if 'requisition_id' in vals and not self.env.context.get('skip_requisition_app_sync'):
            for record in self:
                if record.requisition_id:
                    record.with_context(skip_requisition_app_sync=True).write({
                        'requisition_app_id': record.requisition_id.app_id.id
                    })
                elif 'requisition_app_id' not in vals:
                    record.with_context(skip_requisition_app_sync=True).write({
                        'requisition_app_id': False
                    })
        if 'requisition_app_id' in vals and not self.env.context.get('skip_requisition_app_sync'):
            for record in self:
                if record.requisition_id and record.requisition_app_id:
                    if record.requisition_id.app_id != record.requisition_app_id:
                        record.with_context(skip_requisition_app_sync=True).write({
                            'requisition_id': False
                        })
        if 'estimated_value' in vals or 'requisition_id' in vals or not vals.get('procurement_method_config_id'):
            self._set_procurement_config_defaults()
        if 'procurement_method_config_id' in vals:
            for record in self:
                if old_method_map.get(record.id) != record.procurement_method_config_id.id:
                    record._reset_workflow_for_method_change()
        return res

    def read(self, fields=None, load='_classic_read'):
        if fields is None or 'document_checklist_ids' in fields:
            for record in self:
                if record.procurement_method_config_id:
                    record._ensure_document_checklist()
        return super().read(fields=fields, load=load)

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        """Default procurement method from linked requisition/APP"""
        warning_lines = []
        if self.requisition_id:
            if self.specification_id and self.specification_id.requisition_id != self.requisition_id:
                self.specification_id = False
                warning_lines.append(
                    'The requisition changed, so the specification was cleared. Please reselect the correct specification.'
                )
            if self.requisition_app_id and self.requisition_id.app_id != self.requisition_app_id:
                warning_lines.append(
                    'The selected requisition belongs to a different APP. The APP was updated to match.'
                )
            self.requisition_app_id = self.requisition_id.app_id
            if self.requisition_id.app_id:
                method = self.requisition_id.app_id.procurement_method_config_id
                if method:
                    self.procurement_method_config_id = method
        else:
            self.requisition_app_id = False
            if self.specification_id:
                self.specification_id = False
                warning_lines.append(
                    'The requisition was cleared, so the specification was cleared.'
                )
        if warning_lines:
            return {
                'warning': {
                    'title': 'Tender updated',
                    'message': '\n'.join(warning_lines)
                }
            }

    @api.constrains('requisition_id', 'specification_id')
    def _check_specification_matches_requisition(self):
        for record in self:
            if record.specification_id and record.requisition_id:
                if record.specification_id.requisition_id != record.requisition_id:
                    raise ValidationError('Specification must match the selected requisition.')

    @api.onchange('requisition_app_id')
    def _onchange_requisition_app_id(self):
        warning = None
        if self.requisition_id and self.requisition_app_id:
            if self.requisition_id.app_id != self.requisition_app_id:
                self.requisition_id = False
                warning = {
                    'title': 'Requisition cleared',
                    'message': 'The selected requisition does not match this APP and was cleared.'
                }

        domain = [('state', '=', 'approved')]
        if self.requisition_app_id:
            domain.append(('app_id', '=', self.requisition_app_id.id))
        result = {'domain': {'requisition_id': domain}}
        if warning:
            result['warning'] = warning
        return result

    @api.onchange('estimated_value')
    def _onchange_estimated_value(self):
        """Suggest procurement method based on estimated value"""
        if self.estimated_value:
            method = self.env['sagovprocurement.method'].get_applicable_method(
                self.estimated_value
            )
            if method:
                self.procurement_method_config_id = method
                if method.preference_point_system_ids:
                    self.preference_point_system_config_id = method.preference_point_system_ids[0]

    @api.onchange('approved_budget')
    def _onchange_approved_budget(self):
        """Suggest procurement method based on approved budget"""
        if self.approved_budget:
            method = self.env['sagovprocurement.method'].get_applicable_method(
                self.approved_budget
            )
            if method:
                self.procurement_method_config_id = method
                if method.preference_point_system_ids:
                    self.preference_point_system_config_id = method.preference_point_system_ids[0]

    @api.onchange('procurement_method_config_id')
    def _onchange_procurement_method_config(self):
        """When procurement method changes, update related fields and trigger dependent calculations"""
        warning = None
        if self.procurement_method_config_id:
            if self.procurement_method_config_id.preference_point_system_ids:
                self.preference_point_system_config_id = (
                    self.procurement_method_config_id.preference_point_system_ids[0]
                )
            # Reset state to align stages with the new workflow configuration.
            self.state = 'draft'
            workflow_stages = self.workflow_stage_ids.sorted('sequence')
            if not self.current_workflow_stage_id or self.current_workflow_stage_id not in workflow_stages:
                self.current_workflow_stage_id = workflow_stages[0] if workflow_stages else False
            try:
                self.validate_document_requirements()
            except (UserError, ValidationError) as exc:
                warning = {
                    'title': 'Document validation',
                    'message': str(exc)
                }
        else:
            self.state = 'draft'
            self.current_workflow_stage_id = False
            warning = {
                'title': 'Procurement method required',
                'message': 'Please select a procurement method to initialize workflow stages and document checklist.'
            }
        if warning:
            return {'warning': warning}

    @api.onchange('preference_point_system_config_id')
    def _onchange_preference_point_system_config(self):
        """When preference point system changes, trigger dependent calculations"""
        # Ensure dependent fields are properly recalculated on form change
        pass

    def get_workflow_stages(self):
        """Get ordered workflow stages for this tender"""
        if self.procurement_method_config_id:
            return self.procurement_method_config_id.get_workflow_sequence()
        return []

    def get_required_documents(self):
        """Get all required documents for this tender"""
        if self.procurement_method_config_id:
            return self.procurement_method_config_id.get_document_requirements()
        return []

    def validate_procurement_method_compliance(self):
        """Validate that selected method meets compliance requirements"""
        if not self.procurement_method_config_id:
            raise ValidationError('Procurement method must be selected')

        method = self.procurement_method_config_id

        if self.estimated_value < method.min_value:
            raise ValidationError(
                f'Estimated value (R{self.estimated_value}) is below minimum '
                f'for {method.name} (R{method.min_value})'
            )

        if method.max_value > 0 and self.estimated_value > method.max_value:
            raise ValidationError(
                f'Estimated value (R{self.estimated_value}) exceeds maximum '
                f'for {method.name} (R{method.max_value})'
            )

        if method.preference_point_system_ids and self.preference_point_system_config_id:
            pref_system = self.preference_point_system_config_id
            if self.estimated_value < pref_system.minimum_applicable_value:
                raise ValidationError(
                    f'Estimated value (R{self.estimated_value}) is below minimum '
                    f'for {pref_system.name} (R{pref_system.minimum_applicable_value})'
                )

        return True

    def _set_procurement_config_defaults(self):
        for record in self:
            if record.procurement_method_config_id:
                continue
            method = False
            if record.requisition_id and record.requisition_id.app_id:
                method = record.requisition_id.app_id.procurement_method_config_id
            if not method and record.estimated_value:
                method = record.env['sagovprocurement.method'].get_applicable_method(
                    record.estimated_value
                )
            if method:
                record.procurement_method_config_id = method
                if method.preference_point_system_ids:
                    record.preference_point_system_config_id = method.preference_point_system_ids[0]
                record._reset_workflow_for_method_change()

    def _infer_stage_key_from_name(self, stage_name):
        """Infer a stable stage key from a workflow stage name."""
        name = (stage_name or '').lower()
        mappings = [
            ('draft', ['draft', 'init', 'start', 'registration', 'demand identification']),
            ('scm_processing', [
                'requisition', 'budget confirmation', 'specification', 'bsc approval',
                'treasury concurrence', 'feasibility', 'clarification', 'scm', 'processing'
            ]),
            ('advertised', ['advertise', 'advertisement', 'publish', 'rfq advertisement', 'tender advertisement']),
            ('briefing', ['briefing', 'compulsory briefing']),
            ('bid_submission', ['submission', 'submit', 'bidding', 'quotation submission', 'bid submission']),
            ('opening', ['opening', 'open bids', 'quotation opening', 'bid opening', 'bid opening register']),
            ('compliance', ['compliance', 'compliant', 'compliance verification']),
            ('declaration', ['declaration', 'interest']),
            ('evaluation', ['evaluation', 'scoring', 'bec evaluation', 'evaluation & scoring']),
            ('sagovbac_review', ['bac', 'adjudication', 'bac review', 'bac recommendation']),
            ('awarded', ['award', 'award approval', 'award notification', 'contract signing', 'purchase order']),
            ('cancelled', ['cancel']),
            ('rejected', ['reject']),
        ]
        for key, keywords in mappings:
            if any(keyword in name for keyword in keywords):
                return key
        return False

    def _find_stage_by_key(self, stage_key):
        """Find a workflow stage for the current method matching a stage key."""
        if not self.procurement_method_config_id or not stage_key:
            return False
        for stage in self.procurement_method_config_id.workflow_stage_ids.sorted('sequence'):
            if self._infer_stage_key_from_name(stage.name) == stage_key:
                return stage
        return False

    def _reset_workflow_for_method_change(self):
        """Reset workflow tracking when procurement method changes."""
        self.ensure_one()
        if 'workflow_stage_history_ids' in self._fields:
            self.workflow_stage_history_ids.unlink()

        if not self.procurement_method_config_id:
            self.document_checklist_ids.unlink()
            self.current_workflow_stage_id = False
            self.state = 'draft'
            return
        self.state = 'draft'
        self._ensure_document_checklist(post_message=True)

    def _set_state_and_stage(self, stage_key, vals=None, note=None):
        """Set legacy state and keep stage in sync with configuration."""
        self.ensure_one()
        write_vals = dict(vals or {})
        write_vals['state'] = stage_key
        self.write(write_vals)


    @api.depends('state')
    def _compute_stage_key(self):
        """Compute normalized stage key from the legacy state."""
        for record in self:
            record.stage_key = record.state or 'draft'

    @api.depends(
        'state',
        'procurement_method_config_id',
        'procurement_method_config_id.workflow_stage_ids',
        'procurement_method_config_id.workflow_stage_ids.sequence'
    )
    def _compute_current_workflow_stage(self):
        """Compute current workflow stage from the configured workflow."""
        for record in self:
            workflow_stages = record.procurement_method_config_id.workflow_stage_ids.sorted('sequence')
            if not record.procurement_method_config_id or not workflow_stages:
                record.current_workflow_stage_id = False
                continue
            stage_key = record.state or 'draft'
            target_stage = record._find_stage_by_key(stage_key)
            if not target_stage:
                target_stage = workflow_stages[0]

            if record.current_workflow_stage_id in workflow_stages:
                current_key = record._infer_stage_key_from_name(
                    record.current_workflow_stage_id.name
                )
                if current_key == stage_key:
                    continue

            record.current_workflow_stage_id = target_stage

    def _get_workflow_stages_for_method(self, method_id=None):
        method = self.env['sagovprocurement.method'].browse(method_id) if method_id else self.procurement_method_config_id
        if not method:
            return self.env['sagovprocurement.workflow.stage']
        return method.workflow_stage_ids.sorted('sequence')

    def _validate_workflow_stage_transition(self, target_stage, previous_stage, workflow_stages=None):
        self.ensure_one()
        stages = list(workflow_stages or self.workflow_stage_ids.sorted('sequence'))
        if not stages or not target_stage:
            return
        if target_stage not in stages:
            raise UserError('Selected stage is not part of the configured workflow.')

        target_index = stages.index(target_stage)
        if previous_stage and previous_stage in stages:
            previous_index = stages.index(previous_stage)
            if target_index > previous_index + 1:
                raise UserError('You can only move to the next stage without skipping.')
        else:
            if target_index != 0:
                raise UserError('Please start at the first stage before moving forward.')

    @api.constrains('current_workflow_stage_id', 'procurement_method_config_id')
    def _check_workflow_stage_transition(self):
        for record in self:
            workflow_stages = record.workflow_stage_ids.sorted('sequence')
            if not workflow_stages or not record.current_workflow_stage_id:
                continue
            previous_stage = record._origin.current_workflow_stage_id if record._origin else False
            record._validate_workflow_stage_transition(
                record.current_workflow_stage_id,
                previous_stage,
                workflow_stages=workflow_stages
            )

    def _inverse_current_workflow_stage(self):
        """Allow manual stage changes while enforcing sequential transitions."""
        for record in self:
            workflow_stages = record.workflow_stage_ids.sorted('sequence')
            target_stage = record.current_workflow_stage_id

            if not workflow_stages or not target_stage:
                continue

            previous_stage = record._origin.current_workflow_stage_id if record._origin else False
            record._validate_workflow_stage_transition(
                target_stage,
                previous_stage,
                workflow_stages=workflow_stages
            )

            stage_key = record._infer_stage_key_from_name(target_stage.name)
            if stage_key:
                record.state = stage_key

    @api.depends(
        'stage_key',
        'current_workflow_stage_id',
        'current_workflow_stage_id.visible_tabs',
        'current_workflow_stage_id.visible_header_buttons'
    )
    def _compute_visible_ui_sections(self):
        tab_fields = {
            'description': 'show_tab_description',
            'document_checklist': 'show_tab_document_checklist',
            'documents': 'show_tab_documents',
            'advertisement': 'show_tab_advertisement',
            'briefing_sessions': 'show_tab_briefing_sessions',
            'tender_opening': 'show_tab_tender_opening',
            'bids': 'show_tab_bids',
            'compliance': 'show_tab_compliance',
            'declarations': 'show_tab_declarations',
            'evaluation': 'show_tab_evaluation',
            'sagovbac_review': 'show_tab_sagovbac_review',
            'award': 'show_tab_award',
            'purchase_order': 'show_tab_purchase_order',
            'downloads': 'show_tab_downloads'
        }
        button_fields = {
            'start_scm_processing': 'show_btn_start_scm_processing',
            'publish_tender': 'show_btn_publish_tender',
            'start_briefing': 'show_btn_start_briefing',
            'schedule_briefing': 'show_btn_schedule_briefing',
            'complete_briefing': 'show_btn_complete_briefing',
            'open_bid_submission': 'show_btn_open_bid_submission',
            'close_submission': 'show_btn_close_submission',
            'conduct_opening': 'show_btn_conduct_opening',
            'close_opening': 'show_btn_close_opening',
            'start_compliance_check': 'show_btn_start_compliance_check',
            'end_compliance_check': 'show_btn_end_compliance_check',
            'request_declarations': 'show_btn_request_declarations',
            'start_evaluation': 'show_btn_start_evaluation',
            'send_to_bac': 'show_btn_send_to_bac',
            'bac_review': 'show_btn_bac_review',
            'award_tender': 'show_btn_award_tender',
            'view_award': 'show_btn_view_award',
            'cancel_tender': 'show_btn_cancel_tender'
        }
        for record in self:
            for field_name in tab_fields.values():
                setattr(record, field_name, False)
            for field_name in button_fields.values():
                setattr(record, field_name, False)

            tab_codes = set(record.current_workflow_stage_id.visible_tabs.mapped('code'))
            button_codes = set(record.current_workflow_stage_id.visible_header_buttons.mapped('code'))

            if tab_codes:
                for code, field_name in tab_fields.items():
                    setattr(record, field_name, code in tab_codes)
            else:
                stage_key = record.stage_key or 'draft'
                record.show_tab_description = True
                record.show_tab_document_checklist = True
                record.show_tab_documents = True
                record.show_tab_downloads = True
                record.show_tab_advertisement = stage_key != 'draft'
                record.show_tab_briefing_sessions = stage_key in [
                    'briefing', 'bid_submission', 'opening', 'compliance',
                    'declaration', 'evaluation', 'sagovbac_review', 'awarded'
                ]
                record.show_tab_tender_opening = stage_key in [
                    'opening', 'compliance', 'declaration', 'evaluation',
                    'sagovbac_review', 'awarded'
                ]
                record.show_tab_bids = stage_key in [
                    'advertised', 'briefing', 'bid_submission', 'opening',
                    'compliance', 'declaration', 'evaluation', 'sagovbac_review',
                    'awarded'
                ]
                record.show_tab_compliance = stage_key in [
                    'compliance', 'declaration', 'evaluation', 'sagovbac_review',
                    'awarded'
                ]
                record.show_tab_declarations = stage_key in [
                    'declaration', 'evaluation', 'sagovbac_review', 'awarded'
                ]
                record.show_tab_evaluation = stage_key in [
                    'evaluation', 'sagovbac_review', 'awarded'
                ]
                record.show_tab_sagovbac_review = stage_key in [
                    'sagovbac_review', 'awarded'
                ]
                record.show_tab_award = stage_key == 'awarded'
                record.show_tab_purchase_order = stage_key == 'awarded'

            if button_codes:
                for code, field_name in button_fields.items():
                    setattr(record, field_name, code in button_codes)
            else:
                stage_key = record.stage_key or 'draft'
                record.show_btn_start_scm_processing = stage_key == 'draft'
                record.show_btn_publish_tender = stage_key == 'scm_processing'
                record.show_btn_start_briefing = stage_key == 'advertised'
                record.show_btn_schedule_briefing = stage_key == 'briefing'
                record.show_btn_complete_briefing = stage_key == 'briefing'
                record.show_btn_open_bid_submission = stage_key == 'advertised'
                record.show_btn_close_submission = stage_key == 'bid_submission'
                record.show_btn_conduct_opening = stage_key == 'opening'
                record.show_btn_close_opening = stage_key == 'opening'
                record.show_btn_start_compliance_check = stage_key == 'compliance'
                record.show_btn_end_compliance_check = stage_key == 'compliance'
                record.show_btn_request_declarations = stage_key == 'declaration'
                record.show_btn_start_evaluation = stage_key == 'evaluation'
                record.show_btn_send_to_bac = stage_key == 'evaluation'
                record.show_btn_bac_review = stage_key == 'sagovbac_review'
                record.show_btn_award_tender = stage_key == 'sagovbac_review'
                record.show_btn_view_award = stage_key == 'awarded'
                record.show_btn_cancel_tender = True

    @api.depends('current_workflow_stage_id', 'workflow_stage_ids', 'workflow_stage_ids.sequence', 'is_locked')
    def _compute_next_stage_controls(self):
        for record in self:
            if record.is_locked:
                record.show_btn_next_stage = False
                continue
            workflow_stages = record.workflow_stage_ids.sorted('sequence')
            if not workflow_stages or not record.current_workflow_stage_id:
                record.show_btn_next_stage = False
                continue
            stages = list(workflow_stages)
            if record.current_workflow_stage_id not in stages:
                record.show_btn_next_stage = False
                continue
            current_index = stages.index(record.current_workflow_stage_id)
            record.show_btn_next_stage = current_index < len(stages) - 1

    @api.depends('document_checklist_ids.state', 'document_checklist_ids.mandatory')
    def _compute_document_status(self):
        """Calculate document completion status"""
        for record in self:
            checklist = record.document_checklist_ids
            if checklist:
                total = len(checklist)
                uploaded = len(checklist.filtered(lambda d: d.state in ['uploaded', 'verified']))
                record.documents_completion_rate = (uploaded / total * 100) if total > 0 else 0.0

                # Check mandatory documents
                mandatory = checklist.filtered(lambda d: d.mandatory)
                if mandatory:
                    record.mandatory_documents_uploaded = all(
                        d.state in ['uploaded', 'verified'] for d in mandatory
                    )
                else:
                    record.mandatory_documents_uploaded = True
            else:
                record.documents_completion_rate = 0.0
                record.mandatory_documents_uploaded = False

    # Functionality Evaluation
    has_functionality = fields.Boolean(
        string='Functionality Evaluation',
        default=True,
        help='Whether this tender includes functionality evaluation'
    )
    functionality_threshold = fields.Float(
        string='Functionality Threshold (%)',
        default=70.0,
        help='Minimum functionality score required (e.g., 70%)'
    )

    # Dates
    publication_date = fields.Date(
        string='Publication Date',
        tracking=True
    )
    closing_date = fields.Datetime(
        string='Closing Date/Time',
        required=False,
        tracking=True,
        help='Deadline for bid submissions'
    )
    opening_date = fields.Datetime(
        string='Opening Date/Time',
        tracking=True,
        help='Date and time of bid opening'
    )
    validity_period = fields.Integer(
        string='Validity Period (Days)',
        default=90,
        help='Number of days bids remain valid'
    )

    # Advertising
    advertisement_text = fields.Html(
        string='Advertisement Text',
        sanitize=True,
        sanitize_tags=True,
        sanitize_attributes=True,
        sanitize_style=True,
        help='Text of the tender advertisement'
    )
    advertisement_platform_ids = fields.Many2many(
        'sagovtender.advert.platform',
        string='Advertisement Platforms',
        help='Platforms where tender is advertised'
    )
    published_url = fields.Char(
        string='Published URL',
        help='URL where tender is published online'
    )

    # Documents
    sagovtender_document_ids = fields.One2many(
        'sagovtender.document',
        'tender_id',
        string='Tender Documents'
    )

    # Briefing Sessions
    briefing_session_ids = fields.One2many(
        'sagovtender.briefing.session',
        'tender_id',
        string='Briefing Sessions'
    )
    briefing_session_count = fields.Integer(
        string='Briefing Sessions',
        compute='_compute_briefing_session_count'
    )
    has_briefing_session = fields.Boolean(
        string='Briefing Session Required',
        default=False,
        tracking=True,
        help='Check if this tender requires a briefing session'
    )
    briefing_completed = fields.Boolean(
        string='Briefing Completed',
        compute='_compute_briefing_completed',
        store=True
    )

    # Bids
    bid_ids = fields.One2many(
        'sagovtender.bid',
        'tender_id',
        string='Bids Received'
    )
    bid_count = fields.Integer(
        string='Number of Bids',
        compute='_compute_bid_count'
    )

    # Opening Register
    opening_register_id = fields.Many2one(
        'sagovtender.bid.opening.register',
        string='Bid Opening Register',
        readonly=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    # Compliance
    sagovcompliance_check_ids = fields.One2many(
        'sagovtender.compliance.check',
        'tender_id',
        string='Compliance Checks',
        help='Links to compliance check records for each bid in this tender'
    )
    compliant_bid_count = fields.Integer(
        string='Compliant Bids',
        compute='_compute_compliant_bids'
    )

    # Declaration of Interest
    declaration_ids = fields.One2many(
        'sagovtender.declaration.interest',
        'tender_id',
        string='Declarations of Interest'
    )
    declarations_complete = fields.Boolean(
        string='All BEC Declarations Complete',
        store=True,
        compute='_compute_declarations_complete'
    )

    # Evaluation
    evaluation_ids = fields.One2many(
        'sagovtender.bid.evaluation',
        'tender_id',
        string='Bid Evaluations'
    )
    bec_committee_id = fields.Many2one(
        'sagovtender.committee',
        string='BEC Committee',
        domain=[('committee_type', '=', 'bec')],
        tracking=True,
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    bec_report_id = fields.Many2one(
        'ir.attachment',
        string='BEC Report',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    bec_completed = fields.Boolean(
        string='BEC Evaluation Complete',
        compute='_compute_bec_completed'
    )

    # BAC Review
    sagovbac_review_ids = fields.One2many(
        'sagovtender.bac.review',
        'tender_id',
        string='BAC Reviews'
    )
    bac_committee_id = fields.Many2one(
        'sagovtender.committee',
        string='BAC Committee',
        domain=[('committee_type', '=', 'bac')],
        tracking=True,
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    bac_report_id = fields.Many2one(
        'ir.attachment',
        string='BAC Report',
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    bac_recommendation = fields.Selection([
        ('approve', 'Approve BEC Recommendation'),
        ('reject', 'Reject'),
        ('refer_back', 'Refer Back to BEC'),
        ('cancel_tender', 'Cancel Tender'),
    ], string='BAC Recommendation', tracking=True)

    # Award
    award_id = fields.Many2one(
        'sagovtender.award',
        string='Tender Award',
        readonly=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    awarded_partner_id = fields.Many2one(
        'res.partner',
        string='Awarded To',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    award_value = fields.Monetary(
        string='Award Value',
        currency_field='currency_id',
        tracking=True
    )

    # Purchase Order Integration
    purchase_order_id = fields.Many2one(
    'purchase.order',
    string='Purchase Order',
    related='award_id.purchase_order_id',
    readonly=True,
    store=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scm_processing', 'SCM Processing'),
        ('advertised', 'Advertised'),
        ('briefing', 'Briefing Session'),
        ('bid_submission', 'Bid Submission Period'),
        ('opening', 'Bid Opening'),
        ('compliance', 'Compliance Check'),
        ('declaration', 'Declaration of Interest'),
        ('evaluation', 'BEC Evaluation'),
        ('sagovbac_review', 'BAC Review'),
        ('awarded', 'Awarded'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', required=False, tracking=True, copy=False)

    # Computed field for readonly state
    is_locked = fields.Boolean(
        string='Is Locked',
        compute='_compute_is_locked',
        help='True when tender is in Awarded, Rejected, or Cancelled state'
    )

    # Responsible Users
    scm_officer_id = fields.Many2one(
        'res.users',
        string='SCM Officer',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Tender Responsible',
        default=lambda self: self.env.user,
        tracking=True,
        help='SCM Officer or user responsible for this tender'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    # Department
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=False,
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=False,
        default=lambda self: self.env.company
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    # Audit Trail
    cancellation_reason = fields.Text(string='Cancellation Reason')
    notes = fields.Text(string='Internal Notes')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate access token and enforce security"""
        default_app_id = self.env.context.get('default_requisition_app_id')
        for vals in vals_list:
            if default_app_id and not vals.get('requisition_app_id'):
                vals['requisition_app_id'] = default_app_id
            if not vals.get('access_token'):
                # Generate cryptographically secure access token
                vals['access_token'] = secrets.token_hex(32)  # Increased to 64 chars for better security

            # Ensure token uniqueness
            if vals.get('access_token'):
                existing = self.search([('access_token', '=', vals['access_token'])], limit=1)
                if existing:
                    vals['access_token'] = secrets.token_hex(32)

        records = super(TenderTender, self).create(vals_list)
        records._set_procurement_config_defaults()
        for record in records:
            if record.requisition_id and not record.requisition_app_id:
                record.with_context(skip_requisition_app_sync=True).write({
                    'requisition_app_id': record.requisition_id.app_id.id
                })
            if record.requisition_id and record.requisition_app_id:
                if record.requisition_id.app_id != record.requisition_app_id:
                    record.with_context(skip_requisition_app_sync=True).write({
                        'requisition_id': False
                    })
            record._reset_workflow_for_method_change()
        return records

    @api.constrains('estimated_value', 'approved_budget')
    def _check_monetary_values(self):
        """Validate monetary values to prevent overflow and negative amounts"""
        for record in self:
            if record.estimated_value and record.estimated_value < 0:
                raise ValidationError(_("Estimated value cannot be negative"))
            if record.approved_budget and record.approved_budget < 0:
                raise ValidationError(_("Approved budget cannot be negative"))
            if record.estimated_value and record.estimated_value > 999999999999.99:
                raise ValidationError(_("Estimated value exceeds maximum allowed amount"))

    @api.constrains('closing_date', 'opening_date', 'publication_date')
    def _check_dates(self):
        """Validate tender dates for logical consistency"""
        for record in self:
            if record.closing_date and record.opening_date:
                if record.opening_date <= record.closing_date:
                    raise ValidationError(_("Opening date must be after closing date"))
            if record.publication_date and record.closing_date:
                if fields.Datetime.from_string(str(record.publication_date)) >= record.closing_date:
                    raise ValidationError(_("Closing date must be after publication date"))

    @api.depends('bid_ids')
    def _compute_bid_count(self):
        """Count submitted bids"""
        for record in self:
            record.bid_count = len(record.bid_ids.filtered(lambda b: b.state != 'cancelled'))

    @api.depends('stage_key')
    def _compute_is_locked(self):
        """Compute if tender is in a locked state (Awarded, Rejected, or Cancelled)"""
        for record in self:
            record.is_locked = record.stage_key in ['awarded', 'rejected', 'cancelled']

    @api.depends('briefing_session_ids')
    def _compute_briefing_session_count(self):
        """Count briefing sessions"""
        for record in self:
            record.briefing_session_count = len(record.briefing_session_ids)

    @api.depends('briefing_session_ids.state', 'has_briefing_session')
    def _compute_briefing_completed(self):
        """Check if briefing session is completed"""
        for record in self:
            if not record.has_briefing_session:
                record.briefing_completed = True
            else:
                completed_sessions = record.briefing_session_ids.filtered(lambda s: s.state == 'completed')
                record.briefing_completed = len(completed_sessions) > 0

    @api.depends('bid_ids.is_compliant')
    def _compute_compliant_bids(self):
        """Count compliant bids"""
        for record in self:
            record.compliant_bid_count = len(
                record.bid_ids.filtered(lambda b: b.is_compliant and b.state != 'cancelled')
            )

    @api.depends('declaration_ids.state', 'bec_committee_id', 'bec_committee_id.member_ids')
    def _compute_declarations_complete(self):
        """Check if all BEC members have declared"""
        for record in self:
            if record.bec_committee_id and record.bec_committee_id.member_ids:
                required_declarations = len(record.bec_committee_id.member_ids)
                completed = len(record.declaration_ids.filtered(lambda d: d.state == 'cleared'))
                record.declarations_complete = completed >= required_declarations
            else:
                record.declarations_complete = False

    @api.depends('evaluation_ids')
    def _compute_bec_completed(self):
        """Check if BEC evaluation is complete"""
        for record in self:
            if record.evaluation_ids:
                record.bec_completed = all(eval.state == 'approved' for eval in record.evaluation_ids)

            else:
                record.bec_completed = False

    @api.depends('requisition_id.commodity_line_ids.subtotal')
    def _compute_estimated_value(self):
        """Compute tender estimated value from requisition commodity lines."""
        for record in self:
            if record.requisition_id:
                record.estimated_value = sum(record.requisition_id.commodity_line_ids.mapped('subtotal'))
            else:
                record.estimated_value = 0.0

    @api.constrains('closing_date', 'opening_date')
    def _check_dates(self):
        """Validate dates"""
        for record in self:
            if record.closing_date and record.closing_date < fields.Datetime.now():
                if record.stage_key == 'draft':
                    raise ValidationError('Closing date must be in the future.')
            if record.opening_date and record.closing_date:
                if record.opening_date <= record.closing_date:
                    raise ValidationError('Opening date must be after closing date.')

    @api.onchange('estimated_value')
    def _onchange_estimated_value(self):
        """Auto-set preference system based on value"""
        if self.estimated_value:
            if self.estimated_value <= 500000:
                self.preference_system = '80_20'
            else:
                self.preference_system = '90_10'

    # ===== DOCUMENT CHECKLIST =====
    def _create_document_checklist(self):
        """Create document checklist from procurement method requirements"""
        self.ensure_one()
        if not self.procurement_method_config_id or not self.id:
            return

        # Clear existing checklist
        self.document_checklist_ids.unlink()

        # Create checklist items for each document requirement
        doc_reqs = self.procurement_method_config_id.document_requirement_ids.sorted('sequence')
        for doc_req in doc_reqs:
            self.env['sagovtender.document.checklist'].create({
                'tender_id': self.id,
                'document_requirement_id': doc_req.id,
                'state': 'pending'
            })

        mandatory_count = len(doc_reqs.filtered(lambda d: d.mandatory))
        self.message_post(
            body=f'✓ Document checklist created: {len(doc_reqs)} documents required ({mandatory_count} mandatory)'
        )

    def _ensure_document_checklist(self, post_message=False):
        """Ensure checklist exists and includes all configured requirements."""
        self.ensure_one()
        if not self.procurement_method_config_id or not self.id:
            return 0, 0

        doc_reqs = self.procurement_method_config_id.document_requirement_ids.sorted('sequence')
        obsolete_items = self.document_checklist_ids.filtered(
            lambda item: item.document_requirement_id and item.document_requirement_id not in doc_reqs
        )
        removed_count = len(obsolete_items)
        if obsolete_items:
            obsolete_items.unlink()
        existing_req_ids = set(self.document_checklist_ids.mapped('document_requirement_id').ids)

        if not self.document_checklist_ids:
            missing_reqs = doc_reqs
        else:
            missing_reqs = doc_reqs.filtered(lambda req: req.id not in existing_req_ids)

        if not missing_reqs:
            if post_message and removed_count:
                total_count = len(self.document_checklist_ids)
                self.message_post(
                    body=(
                        f'Document checklist refreshed: removed {removed_count} obsolete document(s) '
                        f'(total {total_count}) for {self.procurement_method_config_id.name}'
                    )
                )
            return 0, removed_count

        for doc_req in missing_reqs:
            self.env['sagovtender.document.checklist'].create({
                'tender_id': self.id,
                'document_requirement_id': doc_req.id,
                'state': 'pending'
            })

        added_count = len(missing_reqs)
        if post_message and (added_count or removed_count):
            total_count = len(self.document_checklist_ids)
            self.message_post(
                body=(
                    f'Document checklist refreshed: added {added_count} document(s) and '
                    f'removed {removed_count} obsolete document(s) (total {total_count}) '
                    f'for {self.procurement_method_config_id.name}'
                )
            )
        return added_count, removed_count

    def validate_document_requirements(self):
        """Validate all mandatory documents are uploaded"""
        self.ensure_one()

        if not self.id:
            return True

        if not self.procurement_method_config_id:
            raise UserError('Please select a procurement method before validating documents.')

        self._ensure_document_checklist(post_message=True)

        mandatory_docs = self.document_checklist_ids.filtered(lambda d: d.mandatory)
        missing_docs = mandatory_docs.filtered(lambda d: d.state not in ['uploaded', 'verified'])

        if missing_docs:
            doc_names = '\n'.join([f'• {doc.name}' for doc in missing_docs])
            raise ValidationError(
                f'Missing {len(missing_docs)} mandatory document(s):\n{doc_names}\n\n'
                f'Required by: {self.procurement_method_config_id.name}'
            )

        return True

    def validate_quotation_requirements(self):
        """Validate minimum quotations received per procurement method"""
        self.ensure_one()

        if not self.procurement_method_config_id:
            return True

        method = self.procurement_method_config_id
        required_count = method.quotations_required

        if required_count > 0:
            # Count compliant bids/quotations
            compliant_bids = self.bid_ids.filtered(lambda b: b.is_compliant and b.state != 'cancelled')

            if len(compliant_bids) < required_count:
                raise ValidationError(
                    f'{method.name} requires at least {required_count} valid quotation(s)/bid(s).\n'
                    f'Currently received: {len(compliant_bids)} compliant bid(s).\n\n'
                    f'Compliance: PFMA Section 76, MFMA Section 111, National Treasury Regulations'
                )

        return True

    def validate_committee_requirements(self):
        """Validate required committee approvals are complete"""
        self.ensure_one()

        if not self.procurement_method_config_id:
            return True

        method = self.procurement_method_config_id
        errors = []

        # Check BSC Approval
        if method.requires_bsc_approval:
            # Add BSC validation logic here
            if not hasattr(self, 'bsc_approved') or not self.bsc_approved:
                errors.append(
                    f'• BSC (Bid Specification Committee) Approval required\n'
                    f'  Delegation: {method.bsc_delegation or "As per method"}'
                )

        # Check BEC Evaluation
        if method.requires_bec_evaluation:
            if not self.evaluation_ids:
                errors.append('• BEC (Bid Evaluation Committee) Evaluation required')
            elif not all(e.state == 'approved' for e in self.evaluation_ids):
                errors.append('• All BEC evaluations must be in "Approved" state')

        # Check BAC Review
        if method.requires_bac_review:
            if not self.bac_review_ids:
                errors.append(
                    f'• BAC (Bid Adjudication Committee) Review required\n'
                    f'  Delegation: {method.bac_delegation or "As per method"}'
                )
            elif not all(b.state == 'approved' for b in self.bac_review_ids):
                errors.append('• All BAC reviews must be in "Approved" state')

        if errors:
            error_msg = (
                f'Committee approval requirements not met for {method.name}:\n\n' +
                '\n'.join(errors) +
                '\n\nCompliance: Constitution Section 217, PFMA, MFMA, National Treasury SCM Regulations'
            )
            raise ValidationError(error_msg)

        return True

    def validate_advertising_period(self):
        """Validate advertising period meets procurement method requirements"""
        self.ensure_one()

        if not self.procurement_method_config_id or not self.publication_date:
            return True

        method = self.procurement_method_config_id
        required_days = getattr(method, 'advertising_period_days', method.advertising_days_minimum)

        if required_days > 0 and self.closing_date:
            pub_date = fields.Datetime.from_string(str(self.publication_date))
            close_date = self.closing_date

            actual_days = (close_date - pub_date).days

            if actual_days < required_days:
                raise ValidationError(
                    f'{method.name} requires minimum {required_days} days advertising period.\n'
                    f'Current period: {actual_days} days\n\n'
                    f'Please adjust closing date to comply with National Treasury regulations.'
                )

        return True

    # ===== WORKFLOW ACTIONS =====

    def action_next_workflow_stage(self):
        self.ensure_one()
        if self.is_locked:
            raise UserError('This tender is locked and cannot be moved forward.')
        workflow_stages = self.workflow_stage_ids.sorted('sequence')
        if not workflow_stages:
            raise UserError('No workflow stages are configured for this tender.')
        if not self.current_workflow_stage_id:
            self.write({'current_workflow_stage_id': workflow_stages[0].id})
            return True
        stages = list(workflow_stages)
        if self.current_workflow_stage_id not in stages:
            raise UserError('Current stage is not part of the configured workflow.')
        current_index = stages.index(self.current_workflow_stage_id)
        if current_index >= len(stages) - 1:
            raise UserError('This tender is already at the final workflow stage.')
        next_stage = stages[current_index + 1]
        self.write({'current_workflow_stage_id': next_stage.id})
        return True

    def action_start_scm_processing(self):
        """Start SCM processing - check if briefing session confirmation is needed"""
        self.ensure_one()

        # Validate required fields
        if not self.sagovtender_document_ids:
            raise UserError('Please attach tender documents before publishing.')

        if not self.closing_date:
            raise UserError('Please set a closing date before starting SCM processing.')

        if self.closing_date < fields.Datetime.now():
            raise UserError('Closing date must be in the future.')

        # If briefing session IS required, show confirmation wizard
        if self.has_briefing_session:
            return {
                'name': _('Confirm Briefing Session'),
                'type': 'ir.actions.act_window',
                'res_model': 'sagovtender.briefing.confirmation.wizard',
                'view_mode': 'form',
                'context': {
                    'default_tender_id': self.id,
                },
                'target': 'new'
            }

        # If briefing session is not required, proceed directly to SCM processing
        self._set_state_and_stage(
            'scm_processing',
            vals={'scm_officer_id': self.env.user.id},
            note='Tender moved to SCM processing.'
        )
        self.message_post(body='Tender moved to SCM processing.')

    def action_publish_tender(self):
        """Publish/Advertise tender with full validation"""
        for record in self:
            # NEW: Validate document requirements
            record.validate_document_requirements()

            # NEW: Validate advertising period
            record.validate_advertising_period()

            if not record.sagovtender_document_ids:
                raise UserError('Please attach tender documents before publishing.')
            if not record.advertisement_text:
                raise UserError('Please prepare advertisement text before publishing.')

            record._set_state_and_stage(
                'advertised',
                vals={'publication_date': fields.Date.today()},
                note='Tender published/advertised.'
            )
            record.message_post(body='Tender published/advertised - All compliance checks passed.')
            # TODO: Send notifications, publish to platforms

    def action_schedule_briefing(self):
        """Schedule briefing session"""
        self.ensure_one()
        if not self.has_briefing_session:
            raise UserError('This tender does not require a briefing session.')

        return {
            'name': _('Schedule Briefing Session'),
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.briefing.session',
            'view_mode': 'form',
            'context': {
                'default_tender_id': self.id,
                'default_responsible_user_id': self.env.user.id
            },
            'target': 'new'
        }

    def action_start_briefing(self):
        """Move to briefing session state"""
        self._set_state_and_stage('briefing', note='Tender moved to briefing session stage.')
        self.message_post(body='Tender moved to briefing session stage.')

    def action_complete_briefing(self):
        """Complete briefing and move to bid submission"""
        self.ensure_one()
        if self.has_briefing_session and not self.briefing_completed:
            raise UserError('Please complete at least one briefing session before proceeding.')
        self._set_state_and_stage('bid_submission', note='Briefing completed. Bid submission opened.')
        self.message_post(body='Briefing session completed. Tender opened for bid submissions.')

    def action_open_bid_submission(self):
        """Open for bid submission"""
        self._set_state_and_stage('bid_submission', note='Tender opened for bid submissions.')
        self.message_post(body='Tender opened for bid submissions.')

    def action_close_submission(self):
        """Close bid submission"""
        self._set_state_and_stage('opening', note='Bid submission closed. Ready for opening.')
        self.message_post(body='Bid submission closed. Ready for opening.')

    def action_conduct_opening(self):
        """Conduct bid opening"""
        self.ensure_one()
        if not self.opening_register_id:
            # Create opening register
            register = self.env['sagovtender.bid.opening.register'].create({
                'tender_id': self.id,
                'opening_date': fields.Datetime.now(),
            })
            self.opening_register_id = register.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.bid.opening.register',
            'res_id': self.opening_register_id.id,
            'view_mode': 'form',
            'target': 'new',
            'flags': {
                'mode': 'readonly',
            },
            'context': {
                'form_view_initial_mode': 'readonly',
            }
        }

    def action_close_opening(self):
        """Close bid opening"""
        self._set_state_and_stage('compliance', note='Bid opening closed. Compliance check ready.')
        self.message_post(body='Bid opening closed. Ready for compliance check.')

    def action_start_sagovcompliance_check(self):
        """Start compliance checking"""
        self._set_state_and_stage('compliance', note='Compliance checking started.')
        # Create compliance check records for each bid
        # for bid in self.bid_ids.filtered(lambda b: b.state == 'opened'):
        #     if not bid.sagovcompliance_check_id:
        #         self.env['sagovtender.compliance.check'].create({
        #             'tender_id': self.id,
        #             'bid_id': bid.id,
        #             'partner_id': bid.partner_id.id,
        #         })
        # self.message_post(body='Compliance checking started.')

        # Open a wizard to select bid then open compliance check in modal
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Compliance Check',
            'res_model': 'sagovtender.compliance.check.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tender_id': self.id,
            }
        }

    def action_end_sagovcompliance_check(self):
        """Close compliance check"""
        self._set_state_and_stage('declaration', note='Compliance check completed. Declarations requested.')
        self.message_post(body='Compliance check completed. Ready for declarations of interest.')

    def action_request_declarations(self):
        """Request declarations of interest"""
        self.ensure_one()
        if not self.bec_committee_id:
            raise UserError('Please assign BEC Committee before requesting declarations.')

        self._set_state_and_stage('declaration', note='Declarations of interest requested.')

        # Create declaration records for BEC members
        for member in self.bec_committee_id.member_ids:
            existing = self.declaration_ids.filtered(lambda d: d.user_id == member.user_id)
            if not existing:
                self.env['sagovtender.declaration.interest'].create({
                    'tender_id': self.id,
                    'user_id': member.user_id.id,
                    'committee_id': self.bec_committee_id.id,
                })

        self.message_post(body='Declarations of interest requested from BEC members.')

    def action_start_evaluation(self):
        """Start BEC evaluation"""
        self.ensure_one()
        if not self.declarations_complete:
            raise UserError('All BEC members must complete their declarations before evaluation.')
        if self.compliant_bid_count == 0:
            raise UserError('No compliant bids to evaluate.')

        self._set_state_and_stage('evaluation', note='BEC evaluation started.')

        # Create evaluation records
        compliant_bids = self.bid_ids.filtered(lambda b: b.is_compliant)
        for bid in compliant_bids:
            if not self.evaluation_ids.filtered(lambda e: e.bid_id == bid):
                self.env['sagovtender.bid.evaluation'].create({
                    'tender_id': self.id,
                    'bid_id': bid.id,
                })

        self.message_post(body='BEC evaluation started.')

    def action_send_to_bac(self):
        """Send to BAC for review"""
        self.ensure_one()
        if not self.bec_completed:
            raise UserError('BEC evaluation must be completed first.')
        if not self.bac_committee_id:
            raise UserError('Please assign BAC Committee.')

        self._set_state_and_stage('sagovbac_review', note='Tender sent to BAC for review.')

        # Create BAC review record
        if not self.sagovbac_review_ids:
            self.env['sagovtender.bac.review'].create({
                'tender_id': self.id,
                'committee_id': self.bac_committee_id.id,
            })

        self.message_post(body='Tender sent to BAC for review.')

    def action_award_tender(self):
        """Award tender"""
        self.ensure_one()
        if not self.bac_recommendation:
            raise UserError('BAC recommendation is required.')
        if self.bac_recommendation != 'approve':
            raise UserError('BAC must approve before awarding.')
        # Check BAC review records
        if not self.sagovbac_review_ids:
            raise UserError('No BAC review record found.')
        if self.sagovbac_review_ids:
            completed_reviews = self.sagovbac_review_ids.filtered(
                lambda r: r.state in ('refered_back', 'completed')
            )
            if not completed_reviews:
                raise UserError('BAC review records are not completed.')
        # Open award wizard
        return {
            'type': 'ir.actions.act_window',
            'name': 'Award Tender',
            'res_model': 'sagovtender.award.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_tender_id': self.id}
        }

    def action_cancel_tender(self):
        """Cancel tender"""
        self._set_state_and_stage('cancelled', note='Tender cancelled.')
        self.message_post(body=f'Tender cancelled. Reason: {self.cancellation_reason or "Not specified"}')

    def action_view_bids(self):
        """View tender bids"""
        self.ensure_one()
        return {
            'name': 'Tender Bids',
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.bid',
            # 'view_mode': 'list,form',
            'view_mode': 'form',
            'target': 'new',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id}
        }

    def action_view_award(self):
        """View tender award"""
        self.ensure_one()
        if not self.award_id:
            raise UserError('This tender has not been awarded yet.')
        return {
            'name': 'Tender Award',
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.award',
            'view_mode': 'form',
            'res_id': self.award_id.id,
        }

    def action_view_briefing_sessions(self):
        """View briefing sessions"""
        self.ensure_one()
        return {
            'name': 'Briefing Sessions',
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.briefing.session',
            'view_mode': 'list,form',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id}
        }

    def action_bac_review(self):
        """View BAC review records"""
        self.ensure_one()
        # Get existing BAC review or create context for new one
        bac_review = self.sagovbac_review_ids[:1] if self.sagovbac_review_ids else None

        action = {
            'name': 'BAC Review',
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.bac.review',
            'view_mode': 'form',
            'context': {'default_tender_id': self.id, 'default_committee_id': self.bac_committee_id.id},
            'target': 'new'
        }

        if bac_review:
            action['res_id'] = bac_review.id

        return action


class TenderType(models.Model):
    """Tender Types"""
    _name = 'sagovtender.type'
    _description = 'Tender Type'
    _order = 'name'

    name = fields.Char(string='Type Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)


class TenderAdvertisementPlatform(models.Model):
    """Advertisement Platforms"""
    _name = 'sagovtender.advert.platform'
    _description = 'Advertisement Platform'
    _order = 'name'

    name = fields.Char(string='Platform Name', required=True)
    platform_type = fields.Selection([
        ('etender', 'eTender Portal'),
        ('website', 'Department Website'),
        ('newspaper', 'Newspaper'),
        ('bulletin', 'Government Bulletin'),
        ('other', 'Other'),
    ], string='Type', required=True)
    url = fields.Char(string='URL')
    active = fields.Boolean(string='Active', default=True)
