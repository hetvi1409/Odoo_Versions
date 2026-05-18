from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    code = fields.Char(string="Code")


class product_template(models.Model):
    _inherit = 'product.template'

    saoa_code_id = fields.Many2one('saoa.codes', string="SAOA Code")
    saoa_code_only = fields.Char(related="saoa_code_id.code")
    ppn1_code_id = fields.Many2one('ppn1.codes', string="PPN1 Code")
    common_icd_id = fields.Many2one('icd.codes', string="Common ICD")
    nappi_code_id = fields.Many2one('nappi.codes', string="NAPPI Code")
    lens_material_id = fields.Many2one('lens.material', string="Lens Material")
    lens_type_id = fields.Many2one('lens.type', string="Lens Type")
    old_code_id = fields.Many2one('old.codes', string="Old Code")

    @api.constrains('name')
    def _check_name(self):
        if '|' in self.name:
            raise ValidationError(_("You cannot create product with vertical line('|')"))

        return True

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if self._context.get('frame_model'):
            categ_id = self.env['product.category'].search([('name', '=', 'Frames')])
            child_categ_id = self.env['product.category'].search([('id', 'child_of', categ_id.ids)])
            args = ['|', ('categ_id', 'in', child_categ_id.ids), ('categ_id.name', '=', 'Sunglasses')]
            return super(product_template, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                              name_get_uid=name_get_uid)
        else:
            return super(product_template, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                              name_get_uid=name_get_uid)


class lens_material(models.Model):
    _name = 'lens.material'
    _description = 'Lense Material'

    name = fields.Char(string="Lens Material")


class lens_type(models.Model):
    _name = 'lens.type'
    _description = 'Lense Type'

    name = fields.Char(string="Lens Type")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
