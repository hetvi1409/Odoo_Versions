# -*- coding: utf-8 -*-
from odoo import fields, models


class OmniClassFunction(models.Model):
    _name = "omniclass.function"
    _description = "OmniClass Table 11 - Function"
    name = fields.Char(required=True)
    code = fields.Char(index=True)
    description = fields.Text()


class OmniClassSpace(models.Model):
    _name = "omniclass.space"
    _description = "OmniClass Table 21 - Space"
    name = fields.Char(required=True)
    code = fields.Char(index=True)
    description = fields.Text()


class OmniClassElement(models.Model):
    _name = "omniclass.element"
    _description = "OmniClass Table 22 - Element"
    name = fields.Char(required=True)
    code = fields.Char(index=True)
    description = fields.Text()


class OmniClassProduct(models.Model):
    _name = "omniclass.product"
    _description = "OmniClass Table 31 - Product"
    name = fields.Char(required=True)
    code = fields.Char(index=True)
    description = fields.Text()


class OmniClassMaterial(models.Model):
    _name = "omniclass.material"
    _description = "OmniClass Table 33 - Material"
    name = fields.Char(required=True)
    code = fields.Char(index=True)
    description = fields.Text()


class OmniClassProperties(models.Model):
    _name = "omniclass.properties"
    _description = "OmniClass Table 91 - Properties"
    name = fields.Char(required=True)
    code = fields.Char(index=True)
    description = fields.Text()
