from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class AssetCategory(models.Model):
    _name = 'asset.category'

    name = fields.Char('Name', help="Name of the asset category", required=True, copy=False)
    description = fields.Char('Description',
                              help="Description of the asset category")
    is_movable = fields.Boolean('Is Movable')
    is_immovable = fields.Boolean('Is Immovable')
    is_intangible = fields.Boolean('Is Intangible')


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
