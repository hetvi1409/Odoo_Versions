from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super().session_info()
        config = self.env["ir.config_parameter"].sudo()
        result["powered_by_text"] = config.get_param(
            "powered_by_odoo_remove.powered_by_text", ""
        )
        result["replace_powered_by_odoo"] = bool(
            config.get_param("powered_by_odoo_remove.replace_powered_by_odoo")
        )
        return result
