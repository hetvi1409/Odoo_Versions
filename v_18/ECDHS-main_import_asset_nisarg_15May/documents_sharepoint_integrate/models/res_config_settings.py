from email.policy import default

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sharepoint_client_id = fields.Char(string="SharePoint Client ID")
    sharepoint_client_secret = fields.Char(string="SharePoint Client Secret")
    sharepoint_tenant_id = fields.Char(string="SharePoint Tenant ID",default='common')
    # sharepoint_site_url = fields.Char(string="SharePoint Site URL")

    def set_values(self):
        """Save values in system parameters."""
        super().set_values()
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("sharepoint.client_id", self.sharepoint_client_id)
        params.set_param("sharepoint.client_secret", self.sharepoint_client_secret)
        params.set_param("sharepoint.tenant_id", self.sharepoint_tenant_id)
        # params.set_param("sharepoint.site_url", self.sharepoint_site_url)

    @api.model
    def get_values(self):
        """Retrieve values from system parameters."""
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            sharepoint_client_id=params.get_param("sharepoint.client_id"),
            sharepoint_client_secret=params.get_param("sharepoint.client_secret"),
            sharepoint_tenant_id=params.get_param("sharepoint.tenant_id"),
            # sharepoint_site_url=params.get_param("sharepoint.site_url"),
        )
        return res
