from odoo import api, fields, models, _


class AuditCategory(models.Model):
    _inherit = "custom.audit.category"

    request_count = fields.Integer(compute="_compute_request_count")
    request_approved = fields.Integer(compute="_compute_request_approved")
    request_completed = fields.Integer(compute="_compute_request_completed")
    request_reviewed = fields.Integer(compute="_compute_request_reviewed")

    def action_view_category(self):
        """Action to view category"""
        return {
            'name': _('Request'),
            'view_mode': 'list,form',
            'res_model': 'custom.audit.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('audit_category_id', '=', self.id)]
        }

    def action_view_request_approved(self):
        """Action to view category"""
        return {
            'name': _('Request'),
            'view_mode': 'list,form',
            'res_model': 'custom.audit.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('audit_category_id', '=', self.id), ('state', '=', 'd_done')]
        }

    def action_view_completed(self):
        """Action to view category"""
        return {
            'name': _('Request'),
            'view_mode': 'list,form',
            'res_model': 'custom.audit.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('audit_category_id', '=', self.id), ('state', '=', 'c_approve')]
        }

    def action_view_request_reviewed(self):
        """Action to view category"""
        return {
            'name': _('Request'),
            'view_mode': 'list,form',
            'res_model': 'custom.audit.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('audit_category_id', '=', self.id), ('state', '=', 'b_confirm')]
        }

    @api.depends()
    def _compute_request_count(self):
        for rec in self:
            rec.request_count = rec.env['custom.audit.request'].search_count([('audit_category_id', '=', rec.id)])

    @api.depends()
    def _compute_request_approved(self):
        for rec in self:
            rec.request_approved = rec.env['custom.audit.request'].search_count([('audit_category_id', '=', rec.id), ('state', '=', 'c_approve')])

    @api.depends()
    def _compute_request_completed(self):
        for rec in self:
            rec.request_completed = rec.env['custom.audit.request'].search_count([('audit_category_id', '=', rec.id), ('state', '=', 'd_done')])

    @api.depends()
    def _compute_request_reviewed(self):
        for rec in self:
            rec.request_reviewed = rec.env['custom.audit.request'].search_count([('audit_category_id', '=', rec.id), ('state', '=', 'b_confirm')])
