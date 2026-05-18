from odoo import models, fields


class ResConfSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sign_template_id = fields.Many2one(
        'sign.template',
        string="Sign Template",
        config_parameter="real_estate_management.sign_template_id",
    )
    otl_sign_template_id = fields.Many2one(
        'sign.template',
        string="OTL Sign Template",
        config_parameter="real_estate_management.otl_sign_template_id",
    )
    tenant_application_form_id = fields.Many2one(
        'ir.attachment',
        string="Tenant Application Form",
        config_parameter="real_estate_management.tenant_application_form_id",
    )

    property_terms_condition_id = fields.Many2one(
        'property.terms.condition',
        string="Terms and Conditions Template",
        config_parameter="real_estate_management.property_terms_condition_id",
    )


class PropertyTermsCondition(models.Model):
    _name = 'property.terms.condition'
    _description = 'Property Terms and Conditions'

    name = fields.Char(string="Name", required=True, default="Default Terms")
    content = fields.Html(string="Terms and Conditions")
