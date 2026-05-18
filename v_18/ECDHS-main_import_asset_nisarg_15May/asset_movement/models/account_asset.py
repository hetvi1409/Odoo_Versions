from odoo import models, fields

class AccountAsset(models.Model):
    _inherit = "account.asset"

    location_history_ids = fields.One2many(
        "asset.location.history",
        "asset_id",
        string="Location History"
    )

    def write(self, vals):
        for asset in self:
            if "job_location_id" in vals:
                old_location = asset.job_location_id
                new_location = vals.get("job_location_id")

                if old_location.id != new_location:
                    self.env["asset.location.history"].create({
                        "asset_id": asset.id,
                        "old_location_id": old_location.id,
                        "new_location_id": new_location,
                    })

        return super().write(vals)
