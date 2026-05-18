from odoo import api, fields, models


class PropertyZoning(models.Model):
    _name = 'property.zoning'
    _description = "Property Zoning"

    name = fields.Char(string='Name', required=True)


class UserDepartment(models.Model):
    _name = 'property.department'
    _description = "Property Department"

    name = fields.Char(string='Name', required=True)


class PropertyCategory(models.Model):
    _name = 'property.category'
    _description = "Property Category"

    name = fields.Char(string='Name', required=True)


class PropertyCategoryAMP(models.Model):
    _name = 'property.category.amp'
    _description = "Property Category AMP"

    name = fields.Char(string='Name')
    category_name = fields.Char(string='Category AMP', required=True)
    category_id = fields.Many2one('property.category', required=True)

    @api.onchange('category_id', 'category_name')
    def onchange_category(self):
        name = ""
        if self.category_id:
            name = self.category_id.name
        if self.category_name:
            name = name + ' - ' + self.category_name
        self.name = name
