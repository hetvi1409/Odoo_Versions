# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SagovProcurementWorkflowStage(models.Model):
    """Workflow stage/step for a procurement method"""
    _name = 'sagovprocurement.workflow.stage'
    _description = 'Procurement Method Workflow Stage'
    _order = 'sequence'

    method_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        string='Stage Name',
        required=True,
        help='E.g., Demand Identification, Requisition Capture, Evaluation, etc.'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of execution in workflow'
    )
    description = fields.Html(
        string='Description',
        help='Detailed description of this stage'
    )
    responsible_group = fields.Selection([
        ('end_user', 'End User'),
        ('scm', 'SCM Team'),
        ('bsc', 'BSC - Bid Specification Committee'),
        ('bec', 'BEC - Bid Evaluation Committee'),
        ('bac', 'BAC - Bid Adjudication Committee'),
        ('delegated_authority', 'Delegated Authority'),
        ('supplier', 'Supplier/Vendor'),
        ('other', 'Other')
    ], string='Responsible Group', required=True)
    stage_type = fields.Selection([
        ('information', 'Information Gathering'),
        ('approval', 'Approval'),
        ('evaluation', 'Evaluation'),
        ('administrative', 'Administrative'),
        ('decision', 'Decision Making'),
        ('notification', 'Notification'),
        ('other', 'Other')
    ], string='Stage Type', default='administrative')
    duration_days = fields.Integer(
        string='Duration (Days)',
        help='Expected number of days for this stage'
    )
    required = fields.Boolean(
        string='Required',
        default=True,
        help='Is this stage mandatory or optional?'
    )
    visible_tabs = fields.Many2many(
        'sagovtender.ui.section',
        'sagovprocurement_workflow_stage_visible_tab_rel',
        'stage_id',
        'section_id',
        string='Visible Tabs',
        domain=[('section_type', '=', 'tab')],
        help='Tabs that should be visible when this stage is active.'
    )
    visible_header_buttons = fields.Many2many(
        'sagovtender.ui.section',
        'sagovprocurement_workflow_stage_visible_btn_rel',
        'stage_id',
        'section_id',
        string='Visible Header Buttons',
        domain=[('section_type', '=', 'header_button')],
        help='Header buttons that should be visible when this stage is active.'
    )
