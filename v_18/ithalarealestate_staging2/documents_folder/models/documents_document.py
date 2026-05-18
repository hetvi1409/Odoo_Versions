# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from collections import OrderedDict
from odoo.osv import expression
from odoo.exceptions import ValidationError, UserError
from markupsafe import Markup
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import clean_context
from dateutil.relativedelta import relativedelta
import re


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    document_verified = fields.Boolean(string='Is Verified?', default=False)

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        if field_name == 'folder_id':
            enable_counters = kwargs.get('enable_counters', False)
            search_panel_fields = ['access_token', 'company_id', 'description', 'display_name', 'folder_id',
                                   'is_favorited', 'is_pinned_folder', 'owner_id', 'shortcut_document_id',
                                   'user_permission', 'active']
            if not self.env.user.share:
                search_panel_fields += ['alias_name', 'alias_domain_id', 'alias_tag_ids', 'partner_id',
                                        'create_activity_type_id', 'create_activity_user_id']
            domain = [('type', '=', 'folder')]

            if unique_folder_id := self.env.context.get('documents_unique_folder_id'):
                values = self.env['documents.document'].search_read(
                    expression.AND([domain, [('folder_id', 'child_of', unique_folder_id)]]),
                    search_panel_fields,
                    order='id asc',
                )
                accessible_folder_ids = {rec['id'] for rec in values}
                for record in values:
                    if record['folder_id'] not in accessible_folder_ids:
                        record['folder_id'] = False  # consider them as roots
                return {
                    'parent_field': 'folder_id',
                    'values': values,
                }

            records = self.env['documents.document'].search_read(domain, search_panel_fields, order='id asc')
            accessible_folder_ids = {rec['id'] for rec in records}
            alias_tag_data = {}
            if not self.env.user.share:
                alias_tag_ids = {alias_tag_id for rec in records for alias_tag_id in rec['alias_tag_ids']}
                alias_tag_data = {
                    alias_tag['id']: {
                        'id': alias_tag.id,
                        'color': alias_tag.color,
                        'display_name': alias_tag.display_name
                    } for alias_tag in self.env['documents.tag'].browse(alias_tag_ids)
                }
            domain_image = {}
            if enable_counters:
                model_domain = expression.AND([
                    kwargs.get('search_domain', []),
                    kwargs.get('category_domain', []),
                    kwargs.get('filter_domain', []),
                    [(field_name, '!=', False)]
                ])
                domain_image = self._search_panel_domain_image(field_name, model_domain, enable_counters)

            values_range = OrderedDict()
            shared_root_id = "SHARED" if not self.env.user.share else False
            for record in records:
                record_id = record['id']
                if not self.env.user.share:
                    record['alias_tag_ids'] = [alias_tag_data[tag_id] for tag_id in record['alias_tag_ids']]
                if enable_counters:
                    image_element = domain_image.get(record_id)
                    record['__count'] = image_element['__count'] if image_element else 0
                folder_id = record['folder_id']
                if folder_id:
                    folder_id = folder_id[0]
                    if folder_id not in accessible_folder_ids:
                        if record['shortcut_document_id']:
                            continue
                        folder_id = shared_root_id
                elif record['owner_id'][0] == self.env.user.id:
                    folder_id = "MY"
                elif record['owner_id'][0] != self.env.ref('base.user_root').id or self.env.user.share:
                    if record['shortcut_document_id']:
                        continue
                    folder_id = shared_root_id
                else:
                    folder_id = "COMPANY"

                record['folder_id'] = folder_id
                values_range[record_id] = record

            if enable_counters:
                self._search_panel_global_counters(values_range, 'folder_id')

            special_roots = []
            if not self.env.user.share:
                special_roots = [
                    {'bold': True, 'childrenIds': [], 'parentId': False, 'user_permission': 'edit'} | values
                    for values in [
                        {
                            'display_name': _("Ithala File Plan"),
                            'id': 'COMPANY',
                            'description': _("Common roots for all company users."),
                            'user_permission': 'view',
                        }, {
                            'display_name': _("My Drive"),
                            'id': 'MY',
                            'user_permission': 'edit',
                            'description': _("Your individual space."),
                        }, {
                            'display_name': _("Shared with me"),
                            'id': 'SHARED',
                            'description': _("Additional documents you have access to."),
                        }, {
                            'display_name': _("Recent"),
                            'id': 'RECENT',
                            'description': _("Recently accessed documents."),
                        }, {
                            'display_name': _("Trash"),
                            'id': 'TRASH',
                            'description': _("Items in trash will be deleted forever after %s days.",
                                             self.get_deletion_delay()),
                        }]
                ]

            return {
                'parent_field': 'folder_id',
                'values': list(values_range.values()) + special_roots,
            }

        return super().search_panel_select_range(field_name)

