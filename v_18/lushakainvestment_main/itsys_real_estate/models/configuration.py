# -*- coding: utf-8 -*-
from odoo import api, fields, models

class real_estate_setings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    reservation_hours= fields.Integer(string='Hours to release units reservation',
                                              config_parameter='itsys_real_estate.reservation_hours')

    penalty_percent= fields.Integer ('Penalty Percentage')
    penalty_account= fields.Many2one('account.account',
                                             'Late Payments Penalty Account',
                                             config_parameter='itsys_real_estate.penalty_account')
    discount_account= fields.Many2one('account.account',
                                              'Discount Account',
                                              config_parameter='itsys_real_estate.discount_account')
    income_account= fields.Many2one('account.account',
                                            'Income Account',
                                            config_parameter='itsys_real_estate.income_account')
    me_account= fields.Many2one('account.account',
                                        'Managerial Expenses Account',
                                        config_parameter='itsys_real_estate.me_account')
    analytic_account= fields.Many2one('account.analytic.account',
                                              'Analytic Account',
                                              config_parameter='itsys_real_estate.analytic_account')
    security_deposit_account= fields.Many2one('account.account',
                                                      'Security Deposit Account',
                                                      config_parameter='itsys_real_estate.security_deposit_account')

    revenue_account= fields.Many2one('account.account',
                                                      'Revenue Account',
                                                      config_parameter='itsys_real_estate.revenue_account')

class Config(models.TransientModel):
    _name = 'gmap.config'

    @api.model
    def get_key_api(self):
        return self.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')
    
    
# -----------------------------------------------
# NEW MODELS (M2O Lookups)
# -----------------------------------------------

class PropertyProjectStage(models.Model):
    _name = "property.project.stage"
    _description = "Project Development Stage"
    _order = "sequence asc"

    name = fields.Char("Stage Name", required=True)
    sequence = fields.Integer("Sequence", default=1)
    description = fields.Text("Description")
    active = fields.Boolean(default=True)
    color = fields.Integer("Color Index")


class PropertyProjectType(models.Model):
    _name = "property.project.type"
    _description = "Project Type"

    name = fields.Char("Project Type", required=True)
    description = fields.Text("Description")
    active = fields.Boolean(default=True)


class PropertyPowerSupplier(models.Model):
    _name = "property.power.supplier"
    _description = "Power Supplier"

    name = fields.Char("Supplier Name", required=True)
    supplier_ref = fields.Char("Reference Code")
    active = fields.Boolean(default=True)


class ResMunicipality(models.Model):
    _name = "res.municipality"
    _description = "Municipality"

    name = fields.Char("Municipality", required=True)
    province_id = fields.Many2one('res.country.state', string="Province")
    active = fields.Boolean(default=True)

class PropertyProfessional(models.Model):
    _name = "property.professional"
    _description = "Property Professional"

    name = fields.Char(required=True, string="Name")
    mobile = fields.Char("Mobile")
    email = fields.Char("Email")
    specialization = fields.Char("Specialisation")
    note = fields.Text("Notes")

    region_id = fields.Many2one(
        "regions",
        string="Project",
        ondelete="cascade"
    )
