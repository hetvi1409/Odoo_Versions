from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    replace_powered_by_odoo = fields.Boolean(
        string="Replace Powered by Odoo",
        config_parameter="powered_by_odoo_remove.replace_powered_by_odoo",
    )
    powered_by_text = fields.Char(
        string="Replacement Text",
        config_parameter="powered_by_odoo_remove.powered_by_text",
    )
    login_background_image = fields.Binary(
        string="Login Background Image",
    )
    app_background_image = fields.Binary(
        string="App Screen Background Image",
    )

    def set_values(self):
        super().set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        config_parameters.set_param(
            "powered_by_odoo_remove.login_background_image",
            self.login_background_image or False,
        )
        config_parameters.set_param(
            "powered_by_odoo_remove.app_background_image",
            self.app_background_image or False,
        )

    def get_values(self):
        values = super().get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        values.update(
            login_background_image=config_parameters.get_param(
                "powered_by_odoo_remove.login_background_image"
            ),
            app_background_image=config_parameters.get_param(
                "powered_by_odoo_remove.app_background_image"
            ),
        )
        return values
