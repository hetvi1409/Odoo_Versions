from odoo import models, fields, api
from odoo import Command


class RiskTreatmentAttachment(models.Model):
    _name = 'risk.treatment.attachment'
    _description = 'Risk Treatment Attachments'

    treatment_id = fields.Many2one(
        'oi_risk_management.risk_treatment',
        string="Risk Treatment",
        ondelete='cascade'
    )
    datas = fields.Binary("File", required=True)
    name = fields.Char("File Name", required=True)
    description = fields.Text("Description")
    attachment_id = fields.Many2one('ir.attachment')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list):
            treatment_id = vals.get('treatment_id')
            if not treatment_id:
                continue
            if isinstance(treatment_id, (list, tuple)):
                treatment_id = treatment_id[0]
            try:
                treatment = self.env['oi_risk_management.risk_treatment'].browse(int(treatment_id))
            except (TypeError, ValueError):
                treatment = self.env['oi_risk_management.risk_treatment'].browse(treatment_id)
            if vals.get("datas"):
                attachment = self.env["ir.attachment"].create({
                    "name": vals.get("name") or "Attachment",
                    "datas": vals["datas"],
                    "res_model": "oi_risk_management.risk_treatment",
                    "res_id": treatment.id,
                    "description": vals.get("description"),
                })
                rec.attachment_id = attachment.id
                treatment.write({'attachment_ids': [Command.link(attachment.id)]})
        return records

    def unlink(self):
        """Delete the current record."""
        for rec in self:
            rec.attachment_id.unlink()
        return super().unlink()