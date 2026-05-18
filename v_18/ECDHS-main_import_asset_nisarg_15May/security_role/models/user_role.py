# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models
from odoo.tools import partition
import itertools
from itertools import repeat


def is_boolean_group(name):
    return name.startswith('in_group_')

def is_selection_groups(name):
    return name.startswith('sel_groups_')

def is_reified_group(name):
    return is_boolean_group(name) or is_selection_groups(name)

def get_selection_groups(name):
    return [int(v) for v in name[11:].split('_')]

def get_boolean_group(name):
    return int(name[9:])

def parse_m2m(commands):
    "return a list of ids corresponding to a many2many value"
    ids = []
    for command in commands:
        if isinstance(command, (tuple, list)):
            if command[0] in (Command.UPDATE, Command.LINK):
                ids.append(command[1])
            elif command[0] == Command.CLEAR:
                ids = []
            elif command[0] == Command.SET:
                ids = list(command[2])
        else:
            ids.append(command)
    return ids


class AccessRole(models.Model):
    _name = 'user.role'
    _description = 'Access Role'

    name = fields.Char(string='Name', required=True)
    user_ids = fields.Many2many('res.users')
    groups_id = fields.Many2many('res.groups',
                                 string='Groups')
    accesses_count = fields.Integer('# Access Rights',
                                    compute='_compute_accesses_count', compute_sudo=True)
    rules_count = fields.Integer('# Record Rules',
                                 compute='_compute_accesses_count', compute_sudo=True)
    groups_count = fields.Integer('# Groups',
                                  compute='_compute_accesses_count', compute_sudo=True)



    @property
    def SELF_READABLE_FIELDS(self):
        """ The list of fields a user can read on their own user record.
        In order to add fields, please override this property on model extensions.
        """
        return [
            'signature', 'company_id', 'login', 'email', 'name', 'image_1920',
            'image_1024', 'image_512', 'image_256', 'image_128', 'lang', 'tz',
            'tz_offset', 'groups_id', 'partner_id', 'write_date', 'action_id',
            'avatar_1920', 'avatar_1024', 'avatar_512', 'avatar_256', 'avatar_128',
            'share', 'device_ids',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """ The list of fields a user can write on their own user record.
        In order to add fields, please override this property on model extensions.
        """
        return ['signature', 'action_id', 'company_id', 'email', 'name', 'image_1920',
                'lang', 'tz']

    @api.depends('groups_id')
    def _compute_accesses_count(self):
        for user in self:
            groups = user.groups_id
            user.accesses_count = len(groups.model_access)
            user.rules_count = len(groups.rule_groups)
            user.groups_count = len(groups)

    def action_get_groups(self):
        self.ensure_one()
        return {
            'name': 'Groups',
            'view_mode': 'tree,form',
            'res_model': 'res.groups',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('id', 'in', self.groups_id.ids)],
            'target': 'current',
        }

    def action_get_accesses(self):
        self.ensure_one()
        return {
            'name': 'Access Rights',
            'view_mode': 'tree,form',
            'res_model': 'ir.model.access',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('id', 'in', self.groups_id.model_access.ids)],
            'target': 'current',
        }

    def action_get_rules(self):
        self.ensure_one()
        return {
            'name': 'Record Rules',
            'view_mode': 'tree,form',
            'res_model': 'ir.rule',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('id', 'in', self.groups_id.rule_groups.ids)],
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for values in vals_list:
            new_vals_list.append(self._remove_reified_groups(values))
        users = super(AccessRole, self).create(new_vals_list)
        return users

    def write(self, values):
        values = self._remove_reified_groups(values)
        res = super(AccessRole, self).write(values)
        return res

    def _remove_reified_groups(self, values):
        """ return `values` without reified group fields """
        add, rem = [], []
        values1 = {}

        for key, val in values.items():
            if is_boolean_group(key):
                (add if val else rem).append(get_boolean_group(key))
            elif is_selection_groups(key):
                rem += get_selection_groups(key)
                if val:
                    add.append(val)
            else:
                values1[key] = val

        if 'groups_id' not in values and (add or rem):
            added = self.env['res.groups'].sudo().browse(add)
            added |= added.mapped('trans_implied_ids')
            added_ids = added._ids
            # remove group ids in `rem` and add group ids in `add`
            # do not remove groups that are added by implied
            values1['groups_id'] = list(itertools.chain(
                zip(repeat(3), [gid for gid in rem if gid not in added_ids]),
                zip(repeat(4), add)
            ))
        return values1

    @api.model
    def default_get(self, fields):
        group_fields, fields = partition(is_reified_group, fields)
        fields1 = (fields + ['groups_id']) if group_fields else fields
        values = super(AccessRole, self).default_get(fields1)
        self._add_reified_groups(group_fields, values)
        return values

    def _determine_fields_to_fetch(self, field_names, ignore_when_in_cache=False):
        valid_fields = partition(is_reified_group, field_names)[1]
        return super()._determine_fields_to_fetch(valid_fields, ignore_when_in_cache)

    def _read_format(self, fnames, load='_classic_read'):
        valid_fields = partition(is_reified_group, fnames)[1]
        return super()._read_format(valid_fields, load)

    def onchange(self, values, field_names, fields_spec):
        reified_fnames = [fname for fname in fields_spec if is_reified_group(fname)]
        if reified_fnames:
            values = {key: val for key, val in values.items() if key != 'groups_id'}
            values = self._remove_reified_groups(values)

            if any(is_reified_group(fname) for fname in field_names):
                field_names = [fname for fname in field_names if
                               not is_reified_group(fname)]
                field_names.append('groups_id')

            fields_spec = {
                field_name: field_spec
                for field_name, field_spec in fields_spec.items()
                if not is_reified_group(field_name)
            }
            fields_spec['groups_id'] = {}
        result = super().onchange(values, field_names, fields_spec)
        if reified_fnames and 'groups_id' in result.get('value', {}):
            self._add_reified_groups(reified_fnames, result['value'])
            result['value'].pop('groups_id', None)
        return result

    def read(self, fields=None, load='_classic_read'):
        # determine whether reified groups fields are required, and which ones
        fields1 = fields or list(self.fields_get())
        group_fields, other_fields = partition(is_reified_group, fields1)
        drop_groups_id = False
        if group_fields and fields:
            if 'groups_id' not in other_fields:
                other_fields.append('groups_id')
                drop_groups_id = True
        else:
            other_fields = fields
        res = super(AccessRole, self).read(other_fields, load=load)
        # post-process result to add reified group fields
        if group_fields:
            for values in res:
                self._add_reified_groups(group_fields, values)
                if drop_groups_id:
                    values.pop('groups_id', None)
        return res

    def _add_reified_groups(self, fields, values):
        """ add the given reified group fields into `values` """
        gids = set(parse_m2m(values.get('groups_id') or []))
        for f in fields:
            if is_boolean_group(f):
                values[f] = get_boolean_group(f) in gids
            elif is_selection_groups(f):
                # determine selection groups, in order
                sel_groups = self.env['res.groups'].sudo().browse(get_selection_groups(f))
                sel_order = {g: len(g.trans_implied_ids & sel_groups) for g in sel_groups}
                sel_groups = sel_groups.sorted(key=sel_order.get)
                # determine which ones are in gids
                selected = [gid for gid in sel_groups.ids if gid in gids]
                # if 'Internal User' is in the group, this is the "User Type" group
                # and we need to show 'Internal User' selected, not Public/Portal.
                if self.env.ref('base.group_user').id in selected:
                    values[f] = self.env.ref('base.group_user').id
                else:
                    values[f] = selected and selected[-1] or False

    def fields_get(self, allfields=None, attributes=None):
        self.env['res.groups']._update_role_groups_view()
        res = super(AccessRole, self).fields_get(allfields, attributes=attributes)
        # Add reified groups fields
        for app, kind, gs, category_name in self.env[
            'res.groups'].sudo().get_groups_by_application():
            if kind == 'selection':
                # 'User Type' should not be 'False'. A user is either 'employee',
                # 'portal' or 'public' (required).
                selection_vals = [(False, '')]
                if app.xml_id == 'base.module_category_user_type':
                    selection_vals = [(1, 'Internal User')]
                field_name = self.env['res.groups'].name_selection_groups(gs.ids)
                if allfields and field_name not in allfields:
                    continue
                # Selection group field
                tips = []
                if app.description:
                    tips.append(app.description + '\n')
                tips.extend('%s: %s' % (g.name, g.comment) for g in gs if g.comment)
                if field_name == 'sel_groups_1_10_11':
                    res[field_name] = {
                        'type': 'selection',
                        'string': app.name or 'Other',
                        'selection': selection_vals,
                        'help': '\n'.join(tips),
                        'value':1,
                        'default':1,
                        'exportable': False,
                        'selectable': False,
                        'required': True
                    }
                else:
                    res[field_name] = {
                        'type': 'selection',
                        'string': app.name or 'Other',
                        'selection': selection_vals + [(g.id, g.name) for g in gs],
                        'help': '\n'.join(tips),
                        'exportable': False,
                        'selectable': False,
                    }
            else:
                # Boolean group fields
                for g in gs:
                    field_name = self.env['res.groups'].name_boolean_group(g.id)
                    if allfields and field_name not in allfields:
                        continue
                    res[field_name] = {
                        'type': 'boolean',
                        'string': g.name,
                        'help': g.comment,
                        'exportable': False,
                        'selectable': False,
                    }
        # Add self-readable/writable fields
        missing = set(self.SELF_WRITEABLE_FIELDS).union(
            self.SELF_READABLE_FIELDS).difference(res.keys())
        if allfields:
            missing = missing.intersection(allfields)
        if missing:
            res.update({
                key: dict(values, readonly=key not in self.SELF_WRITEABLE_FIELDS,
                          searchable=False)
                for key, values in
                super(AccessRole, self.sudo()).fields_get(missing, attributes).items()
            })
        return res


class IrModuleCategoryView(models.Model):
    _inherit = "ir.module.category"

    def write(self, values):
        res = super().write(values)
        if "name" in values:
            self.env["res.groups"]._update_role_groups_view()
        return res

    def unlink(self):
        res = super().unlink()
        self.env["res.groups"]._update_role_groups_view()
        return res
