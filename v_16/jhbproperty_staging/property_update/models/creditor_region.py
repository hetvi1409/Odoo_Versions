from odoo import fields, models


class CreditorRegion(models.Model):
    """Creditor Region"""
    _name = 'creditor.region'
    _description = 'Creditor region'

    name = fields.Char(string="Name", required=True)


class ArrStatus(models.Model):
    """Arr status"""
    _name = 'arr.status'
    _description = 'Arr Status'

    name = fields.Char(string="Name", required=True)


class LeaseType(models.Model):
    """Lease Type"""
    _name = 'lease.type'
    _description = 'Lease type'

    name = fields.Char(string="Name", required=True)


class PortfolioCategory(models.Model):
    """Portfolio Category"""
    _name = 'portfolio.category'
    _description = 'Portfolio Category'

    name = fields.Char(string="Name", required=True)


class UnitType(models.Model):
    """Unit Type"""
    _name = 'property.unit.type'
    _description = 'Unit Type'

    name = fields.Char(string="Name", required=True)


class TownshipTownship(models.Model):
    """Unit Type"""
    _name = 'township.township'
    _description = 'township'

    name = fields.Char(string="Name", required=True)
