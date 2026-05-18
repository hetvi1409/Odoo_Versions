from odoo import api, fields, models,_


class AuditUniverseRevert(models.Model):

    _name = "audit.universe.tracking"

    audit_universe_revert_id = fields.Many2one(comodel_name="audit.universe", help="Add the audit universe")

    period = fields.Char(string="Period", readonly=True)
    comments = fields.Text(string="Comments")
    stage = fields.Char(string="Status",help="stage of the audit universe")
