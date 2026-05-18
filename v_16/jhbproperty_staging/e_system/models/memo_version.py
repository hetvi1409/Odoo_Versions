from odoo import models, fields, api
from datetime import datetime


class MemoVersion(models.Model):
    _name = 'memo.version'
    _description = 'Memo Version'
    _order = 'version_number desc'

    memo_id = fields.Many2one('memo.memo', string="Memo", required=True, ondelete='cascade')
    version_number = fields.Char(string="Version", required=True)
    memo_name = fields.Char("Title")
    # body_snapshot = fields.Html(string="Snapshot")
    comment = fields.Text("Comment")
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user)
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    subject = fields.Text("Subject")
    purpose_body = fields.Html("Purpose")
    background_body = fields.Html("Background")
    motivation_body = fields.Html("Motivation")
    project_status = fields.Html("Project Status")

    def action_revert_version(self):
        if self.memo_id and self.memo_id.state not in ['approved','published','rejected']:
            self.memo_id.sudo().write({'subject': self.subject,
                                       'name': self.memo_name,
                                       'purpose_body': self.purpose_body,
                                       'background_body': self.background_body,
                                       'motivation_body': self.motivation_body,
                                       'project_status': self.project_status})
