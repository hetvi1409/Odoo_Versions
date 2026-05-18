# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PropertyIntelligence(models.Model):
    _name = 'property.intelligence'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = 'Property Intelligence (Illegal Occupied and Fraud)'
    _rec_name = 'query_details'

    query_details = fields.Char(string='Query Details', required=True,
                                tracking=True)
    date = fields.Date(string='Date', tracking=True, copy=False,
                       default=lambda self: fields.Date.context_today(self))
    requester_id = fields.Many2one('res.partner',
                                   string='Requester Information',
                                   required=True,
                                   tracking=True, copy=False)
    property_id = fields.Many2one('building', string='Property Information',
                                  tracking=True, required=True, copy=False)
    address = fields.Char(string='Address', tracking=True,
                          related='property_id.address', copy=False)
    erf_number = fields.Char(string='Erf Number', tracking=True,
                             related='property_id.erf_number', copy=False)
    jmc_number = fields.Char(string='Jmc Number', tracking=True,
                             related='property_id.jmc_number', copy=False)
    owner_id_number = fields.Char(string='Owner ID', tracking=True,
                                  related='property_id.owner_id_number',
                                  copy=False)
    owner_id = fields.Many2one('res.partner', string='Owner', related='property_id.partner_id', copy=False)
    supporting_document_ids = fields.Many2many('ir.attachment',
                                               'supporting_document_rel',
                                               string='Supporting Documents')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'),
         ('send', 'Investigation'), ('completed', 'Investigation Completed'),
         ('block', 'Block Property'), ('memo', 'Create Memo'), ('feedback', 'Feedback Received'), ('refuse','Refused')], default='draft',
        string='State')
    capture_document_ids = fields.Many2many('ir.attachment',
                                            'capture_document_rel',
                                            string='Investigation Document')
    team_id = fields.Many2one(
        'crm.team',
        string='Investigation Team',
        ondelete='set null'
    )
    member_ids = fields.Many2many(
        'res.users',
        string='Team Members'
    )
    image_ids = fields.Many2many('ir.attachment', 'image_rel', string='Photos')
    detailed_report = fields.Text(string='Detailed Report')
    approval_request_id = fields.Many2one(
        'approval.request',
        string='Approval Request', readonly=True)
    approval_request_count = fields.Integer(
        string='Approval Request Count',
        compute='_compute_approval_request_count'
    )
    # last_stage_updated = fields.Datetime('Last Stage Updated', readonly=True)
    user_id = fields.Many2one('res.users', string='Assignees')
    feedback_document_ids = fields.Many2many('ir.attachment',
                                            'feedback_document_rel',
                                            string='Feedback Document')

    last_stage_updated = fields.Datetime('Last Stage Updated', readonly=True)

    @api.model
    def create(self, values):
        res = super(PropertyIntelligence, self).create(values)
        res.last_stage_updated = fields.Datetime.now()
        return res
    # @api.model
    # def create(self, values):
    #     res = super(PropertyIntelligence, self).create(values)
    #     res.last_stage_updated = fields.Datetime.now()
    #     return res

    @api.depends('approval_request_id')
    def _compute_approval_request_count(self):
        for record in self:
            record.approval_request_count = 1 if record.approval_request_id else 0

    def action_open_approval_request(self):
        self.ensure_one()
        if not self.approval_request_id:
            raise ValidationError("No approval request linked to this record.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Request',
            'res_model': 'approval.request',
            'view_mode': 'form',
            'res_id': self.approval_request_id.id,
            'target': 'current',
        }

    def action_draft(self):
        self.state = 'draft'

    def action_submit(self):
        for record in self:
            if not record.supporting_document_ids:
                raise ValidationError(
                    "You must add supporting documents before confirming.")
            record.state = 'confirm'

    def action_send(self):
        for record in self:
            if not record.team_id and not record.member_ids:
                raise ValidationError(
                    "You must add investigation Team and members.")
            record.state = 'send'

    def action_completed(self):
        for record in self:
            if not record.capture_document_ids:
                raise ValidationError(
                    "You must add Capture Documents after investigation."
                )
            record.state = 'completed'

    def action_create_memo(self):
        for record in self:
            if record.approval_request_id:
                raise ValidationError(
                    "A memo has already been created for this record."
                )
            if not record.supporting_document_ids:
                raise ValidationError(
                    "You must add supporting documents for verification."
                )
            approval_type = self.env['approval.category'].search(
                [('name', '=', 'Memo')], limit=1
            )
            if not approval_type:
                raise ValidationError(
                    "Approval type 'Memo' not found. Please create it in the Approvals module."
                )
            approval_request = self.env['approval.request'].create({
                'name': f'Memo for {record.query_details}',
                'request_owner_id': self.env.user.id,
                'category_id': approval_type.id,
                'date': fields.Date.context_today(self),
                'location': record.address,
                'reason': f'Approval request for property intelligence record {record.query_details}.',
                'investigation_report_ids': [(6, 0, record.capture_document_ids.ids)],
                'image_ids': [(6, 0, record.image_ids.ids)],
                'property_intelligence_id': self.id
            })
            record.approval_request_id = approval_request.id
            record.state = 'memo'

    def action_block(self):
        for record in self:
            if not record.supporting_document_ids:
                raise ValidationError(
                    "You must add supporting documents for verification."
                )
            record.state = 'block'
            record.property_id.state = 'blocked'
