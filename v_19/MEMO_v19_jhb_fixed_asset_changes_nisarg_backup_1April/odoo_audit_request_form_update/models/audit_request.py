from odoo import fields, models


class AuditRequest(models.Model):
    _inherit = 'custom.audit.request'

    def get_audit_details(self):
        """return audit details"""
        all_audit_count = self.env[self._name].search_count([])
        my_audit_count = self.env[self._name].search_count([('responsible_user_id', '=', self.env.user.id)])
        to_approve_count = self.env[self._name].search_count([('state', '=', 'b_confirm')])
        to_complete_count = self.env[self._name].search_count([('state', '=', 'c_approve')])
        return {
            'all_audit_count': all_audit_count,
            'my_audit_count': my_audit_count,
            'to_approve_count': to_approve_count,
            'to_complete_count':to_complete_count
        }

    def get_audit_category_details(self):
        name = self.env['custom.audit.category'].search([]).mapped('name')
        count = []
        for rec in name:
            category = self.env['custom.audit.category'].search([('name', '=', rec)])
            audit = self.env[self._name].search_count([('audit_category_id', '=', category.id)])
            count.append(audit)

        return{
            'name': name,
            'audit': count,
        }