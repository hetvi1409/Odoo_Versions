from odoo import fields, models


class AssetTransferDepartment(models.Model):
    """Model for asset transfer department"""
    _name = 'asset.transfer.department'
    _description = """Asset transfer department"""

    name = fields.Char('Name', help="Name of the transfer department",
                       required=True, copy=False)


class AssetTransferDivision(models.Model):
    """Model for asset transfer division"""
    _name = 'asset.transfer.division'
    _description = """Asset transfer Division"""

    name = fields.Char('Name', help="Name of the transfer division",
                       required=True, copy=False)


class AssetTransferOwnership(models.Model):
    """Model for asset transfer ownership"""
    _name = 'asset.transfer.ownership'
    _description = """Asset transfer Ownership"""

    name = fields.Char('Name', help="Name of the transfer ownership",
                       required=True, copy=False)
