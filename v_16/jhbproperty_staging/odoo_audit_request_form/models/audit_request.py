# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import UserError


class CustomAuditRequest(models.Model):
    _name = "custom.audit.request"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Audit Request'
    
    name = fields.Char(
        string='Audit Request Name', 
        copy=True,
        required=True
    )
    sequence_name = fields.Char(
        string='Audit Request Number', 
        copy=False, 
    )
    audit_date = fields.Date(
        string='Audit Date', 
        copy=True,
        required=True
    )
    deadline_date = fields.Date(
        string='Deadline Date', 
        copy=True,
        required=True
    )
    create_date = fields.Date(
        string='Created Date', 
        copy=True,
        required=True,
        default=fields.Date.context_today
    )
    responsible_user_id = fields.Many2one(
        'res.users', 
        string='Created by',
        copy=True,
        required=True,
        default=lambda self: self.env.user.id
    )
    audit_user_id = fields.Many2one(
        'res.users', 
        string='Audit Responsible',
        copy=True,
        required=True
    )
    approve_user_id = fields.Many2one(
        'res.users', 
        string='Approved by',
        copy=False,
        readonly=True
    )
    audit_reason = fields.Html(
        string='Audit Request Details', 
        copy=True,
    )
    refuse_reason = fields.Text(
        string='Reason', 
        copy=False,
        readonly=True
    )
    state = fields.Selection(selection=[
        ('a_draft', 'Draft'),
        ('b_confirm', 'Confirmed'),
        ('c_approve', 'Approved'),
        ('d_done', 'Audit Completed'),
        ('e_cancel', 'Cancelled'),
        ('f_refuse', 'Refused')],
        string='State', 
        copy=False,
        default='a_draft')
    
    refuse_user_id = fields.Many2one(
        'res.users', 
        string='Refused by',
        copy=False,
        readonly=True
    )
    date_approve = fields.Date(
        string='Approved Date', 
        copy=False,
        readonly=True
    )
    date_refuse = fields.Date(
        string='Refused Date', 
        copy=False,
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company',
        copy=True,
        readonly=True,
        default=lambda self: self.env.user.company_id
    )
    confirm_user_id = fields.Many2one(
        'res.users', 
        string='Confirmed by',
        copy=False,
        readonly=True
    )
    date_confirm = fields.Date(
        string='Confirmed Date', 
        copy=False,
        readonly=True
    )
    date_done = fields.Date(
        string='Audit Completed Date', 
        copy=False,
        readonly=True
    )
    done_user_id = fields.Many2one(
        'res.users', 
        string='Audit Completed by',
        copy=False,
        readonly=True
    )
    audit_category_id = fields.Many2one(
        'custom.audit.category', 
        string='Audit Category',
        copy=True,
        required=True
    )
    audit_tag_ids = fields.Many2many(
        'custom.audit.tag', 
        string='Audit Tags',
        copy=True,
        required=True
    )
    expected_result = fields.Html(
        string='Audit Expected Result', 
        copy=True,
    )
    request_for = fields.Html(
        string='Audit Result', 
        copy=False,
    )
    type = fields.Selection(selection=[
        ('internal', 'Internal'),
        ('external', 'External')],
        string='Audit Method', 
        copy=True,
        required=True,
        default='internal')
    partner_id = fields.Many2one(
        'res.partner', 
        string='External Audit Partner',
        copy=True,
    )
    
    @api.model
    def create(self, vals):
        vals.update({
            'sequence_name': self.env['ir.sequence'].next_by_code('custom.audit.request')
            })
        return super(CustomAuditRequest, self).create(vals)
    
    def unlink(self):
        if any(self.filtered(lambda request: request.state not in ('a_draft', 'e_cancel'))):
            raise UserError(_('You cannot delete a audit request which is not draft or cancelled!'))
        return super(CustomAuditRequest, self).unlink()
            
    def custom_audit_action_reset_draft(self):
        self.state = 'a_draft'
        
    def custom_audit_action_confirm(self):
        self.state = 'b_confirm'
        self.confirm_user_id = self.env.user.id        
        self.date_confirm = fields.Date.today()
        template = self.env.ref('odoo_audit_request_form.custom_email_template_audit_request_confirm_probc', False)
        template.send_mail(self.id)
        
    def custom_audit_action_approve(self):
        self.state = 'c_approve'
        self.approve_user_id = self.env.user.id        
        self.date_approve = fields.Date.today()
        
    def custom_audit_action_done(self):
        self.state = 'd_done'
        self.done_user_id = self.env.user.id        
        self.date_done = fields.Date.today()
        template = self.env.ref('odoo_audit_request_form.custom_email_template_audit_request_done_probc', False)
        template.send_mail(self.id)
        
    def custom_audit_action_cancel(self):
        self.state = 'e_cancel'
        
    def custom_action_audit_send_mail(self):
       self.ensure_one()
       ir_model_data = self.env['ir.model.data']
       try:
           #template_id = ir_model_data.get_object_reference('odoo_audit_request_form', 'custom_email_send_template_all_audit_request_state_probc')[1]
           template_id = self.env['ir.model.data']._xmlid_to_res_id('odoo_audit_request_form.custom_email_send_template_all_audit_request_state_probc', raise_if_not_found=False)
       except ValueError:
           template_id = False
       ctx = dict()
       ctx.update({
           'default_model': 'custom.audit.request',
           'default_res_id': self.ids[0],
           'default_use_template': bool(template_id),
           'default_template_id': template_id,
           'default_composition_mode': 'comment',
       })
       return {
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'mail.compose.message',
           'target': 'new',
           'context': ctx,
       }
