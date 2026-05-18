from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LegalMissing(models.TransientModel):
    """Legal Missing"""
    _name = 'legal.missing'

    legal_id = fields.Many2one('project.project', string="Legal")
    comments = fields.Char(string="Comment")
    conveyancing = fields.Selection([('yes', 'Yes'), ('no', 'No')], )
    is_missing = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Missing Document ?")
    type = fields.Selection([('missing', 'Missing'),
                             ('conveyancing', 'Conveyancing')])

    def action_submit(self):
        """Submit"""
        if self.type == 'missing':
            self.legal_id.missing_document = self.comments
        if self.type == 'conveyancing':
            self.legal_id.conveyancing_comment = self.comments
        if self.is_missing == 'yes':
            self.legal_id.state = 'prepare_task'
        elif self.is_missing == 'no':
            self.legal_id.state = 'draft'

