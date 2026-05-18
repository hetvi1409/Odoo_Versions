from random import randint
from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class AssetCategory(models.Model):
    _name = 'asset.category'

    name = fields.Char('Name', help="Name of the asset category", required=True, copy=False)
    description = fields.Char('Description',
                              help="Description of the asset category")
    draft_asset_count = fields.Integer(string="Draft Asset Count",
                                       help="Draft Asset Count",
                                       compute="compute_asset_count")
    running_asset_count = fields.Integer(string="Running Asset Count",
                                         help="Running Asset Count",
                                         compute="compute_asset_count")
    cancelled_asset_count = fields.Integer(string="Cancelled Asset Count",
                                           help="Cancelled Asset Count",
                                           compute="compute_asset_count")
    asset_count = fields.Integer(string="Asset Count", help="Asset Count",
                                 compute="compute_asset_count")
    impaired_asset_count = fields.Integer(string="Impaired Asset Count",
                                          help="Impaired Asset Count",
                                          compute="compute_asset_count")

    is_movable = fields.Boolean('Is Movable')
    is_immovable = fields.Boolean('Is Immovable')
    is_intangible = fields.Boolean('Is Intangible')

    def action_open_asset(self):
        """Open the assets"""
        return {
            'name': _('Assets'),
            'view_mode': 'list,kanban,form',
            'res_model': 'account.asset',
            'domain': [('asset_category_id', '=', self.id)],
            'context': {
                'default_asset_category_id': self.id,
            },
            'type': 'ir.actions.act_window',
        }

    def compute_asset_count(self):
        """Compute the asset count"""
        for rec in self:
            rec.draft_asset_count = self.env['account.asset'].search_count(
                [('asset_category_id', '=', rec.id), ('state', '=', 'draft')])
            rec.running_asset_count = self.env['account.asset'].search_count(
                [('asset_category_id', '=', rec.id), ('state', '=', 'open')])
            rec.cancelled_asset_count = self.env['account.asset'].search_count(
                [('asset_category_id', '=', rec.id),
                 ('state', '=', 'cancelled')])
            rec.asset_count = self.env['account.asset'].search_count(
                [('asset_category_id', '=', rec.id)])
            rec.impaired_asset_count = self.env['account.asset'].search_count(
                [('asset_category_id', '=', rec.id),
                 ('state', '=', 'impaired')])

    def action_draft_asset(self):
        """Open draft asset"""
        return {
            'name': _('Assets'),
            'view_mode': 'list,kanban,form',
            'res_model': 'account.asset',
            'domain': [('asset_category_id', '=', self.id),
                       ('state', '=', 'draft')],
            'context': {
                'default_asset_category_id': self.id,
            },
            'type': 'ir.actions.act_window',
        }

    def action_running_asset(self):
        """Open running asset"""
        return {
            'name': _('Assets'),
            'view_mode': 'list,kanban,form',
            'res_model': 'account.asset',
            'domain': [('asset_category_id', '=', self.id),
                       ('state', '=', 'open')],
            'type': 'ir.actions.act_window',
        }

    def action_cancelled_asset(self):
        """Cancelled asset"""
        return {
            'name': _('Assets'),
            'view_mode': 'list,kanban,form',
            'res_model': 'account.asset',
            'domain': [('asset_category_id', '=', self.id),
                       ('state', '=', 'cancelled')],
            'context': {
                'default_asset_category_id': self.id,
            },
            'type': 'ir.actions.act_window',
        }

    def action_impaired_asset(self):
        return {
            'name': _('Assets'),
            'view_mode': 'list,kanban,form',
            'res_model': 'account.asset',
            'domain': [('asset_category_id', '=', self.id),
                       ('state', '=', 'impaired')],
            'context': {
                'default_asset_category_id': self.id,
            },
            'type': 'ir.actions.act_window',
        }


    def get_classification_type(self):
        self.ensure_one()
        if self.is_movable:
            return 'movables'
        elif self.is_immovable:
            return 'immovable'
        elif self.is_intangible:
            return 'intangible'
        return False

    @api.constrains('is_movable', 'is_immovable', 'is_intangible')
    def _check_category_type(self):
        for rec in self:
            # Check that at least one category type is selected
            if not (rec.is_movable or rec.is_immovable or rec.is_intangible):
                raise ValidationError(
                    _("At least one category type must be selected "
                      "for the asset category '%s'.") % rec.name
                )

            # Check that only one category type is selected
            selected_count = sum([rec.is_movable, rec.is_immovable, rec.is_intangible])
            if selected_count > 1:
                raise ValidationError(
                    _("Only one category type can be selected "
                      "for the asset category '%s'.") % rec.name
                )

class AssetType(models.Model):
    """Model for asset type"""
    _name = 'asset.type'
    _description = 'Asset type'

    name = fields.Char('Name', help="Name of the asset category", required=True,
                       copy=False)
    category_id = fields.Many2one('asset.category')