# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.account.controllers.portal import CustomerPortal as AccountCustomerPortal


class ProjectCustomerPortal(CustomerPortal):

    def _can_read_model(self, model_name):
        """Guard search_count calls to avoid access-related crashes in portal home."""
        try:
            request.env[model_name].check_access_rights('read')
            return True
        except AccessError:
            return False

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'project_count' in counters:
            values['project_count'] = request.env['project.project'].search_count(
                ['|', '|', '|', '|', ('activity_user_id', '=', request.env.user.id),
                 ('favorite_user_ids', 'in', request.env.user.ids), ('create_uid', '=', request.env.user.id),
                 ('user_id', '=', request.env.user.id),
                 ('write_uid', '=', request.env.user.id)]) \
                if self._can_read_model('project.project') else 0
        if 'task_count' in counters:
            values['task_count'] = request.env['project.task'].search_count(
                ['|', '|', '|', ('project_id', '!=', False), ('project_privacy_visibility', '=', 'portal'),
                 ('message_partner_ids', 'in', request.env.user.partner_id.ids),
                 ('user_ids', 'in', request.env.user.ids)]) \
                if self._can_read_model('project.task') else 0
        return values


class PortalAccount(AccountCustomerPortal):

    def _get_invoices_domain(self, m_type=None):
        if m_type in ['in', 'out']:
            move_type = [m_type + move for move in ('_invoice', '_refund', '_receipt')]
        else:
            move_type = ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
        return [
            ('state', 'not in', ('cancel', 'draft')),
            ('move_type', 'in', move_type),
            '|', '|', '|', '|', '|',
            ('activity_user_id', '=', request.env.user.id),
            ('create_uid', '=', request.env.user.id),
            ('write_uid', '=', request.env.user.id),
            ('invoice_user_id', '=', request.env.user.id),
            ('message_partner_ids', 'in', request.env.user.partner_id.ids),
            ('partner_id', 'child_of', request.env.user.partner_id.commercial_partner_id.id),
        ]
