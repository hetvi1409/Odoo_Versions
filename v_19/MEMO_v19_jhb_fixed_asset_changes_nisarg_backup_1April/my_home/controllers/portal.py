# -*- coding: utf-8 -*-
import werkzeug.utils
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal


class ProjectCustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'project_count' in counters:
            values['project_count'] = request.env['project.project'].search_count(
                ['|', '|', '|', '|', '|', '|', ('activity_user_id', '=', request.env.user.id),
                 ('favorite_user_ids', 'in', request.env.user.ids),
                 ('alias_user_id', '=', request.env.user.id), ('create_uid', '=', request.env.user.id),
                 ('legal_manager_id', '=', request.env.user.id), ('user_id', '=', request.env.user.id),
                 ('write_uid', '=', request.env.user.id)]) \
                if request.env['project.project'].check_access_rights('read', raise_exception=False) else 0
        if 'task_count' in counters:
            values['task_count'] = request.env['project.task'].search_count(
                [('project_id', '!=', False), ('user_ids', 'in', request.env.user.ids)]) \
                if request.env['project.task'].check_access_rights('read', raise_exception=False) else 0
        return values


class PortalAccount(portal.CustomerPortal):

    def _get_invoices_domain(self):
        return [('state', 'not in', ('cancel', 'draft')), ('move_type', 'in',
                                                           ('out_invoice', 'out_refund', 'in_invoice', 'in_refund',
                                                            'out_receipt', 'in_receipt')), '|', '|', '|','|',
                ('activity_user_id', '=', request.env.user.id), ('create_uid', '=', request.env.user.id),
                ('write_uid', '=', request.env.user.id), ('invoice_user_id', '=', request.env.user.id),
                ('user_id', '=', request.env.user.id)]
