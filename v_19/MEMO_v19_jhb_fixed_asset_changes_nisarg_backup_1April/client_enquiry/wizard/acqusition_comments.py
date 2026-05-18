from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PropertyAcquisition(models.TransientModel):
    """Client transaction"""
    _name = 'acquisition.comments'

    acquisition_id = fields.Many2one('property.acquisition', string="Acquisition")
    comments = fields.Char(string="Comment")
    attachment_ids = fields.Many2many('ir.attachment', string="Documents")
    type = fields.Selection([('negotiation', 'Negotiation'),
                             ('agreed', 'Agreed'),
                             ('agreement_signed', 'Agreement signed'),
                             ('conveyancing', 'Conveyancing'),
                             ])

    def action_submit(self):
        """Submit"""
        if self.type == 'negotiation':
            self.acquisition_id.negotiation_comment = self.comments
            self.acquisition_id.negotiation_attachment_ids = self.attachment_ids
            self.acquisition_id.state = 'negotiation'
        if self.type == 'agreed':
            self.acquisition_id.agreement_comment = self.comments
            self.acquisition_id.agreement_attachment_ids = self.attachment_ids
            self.acquisition_id.state = 'agreement_draft'
        if self.type == 'agreement_signed':
            self.acquisition_id.sign_agreement_comment = self.comments
            self.acquisition_id.sign_agreement_attachment_ids = self.attachment_ids
            self.acquisition_id.state = 'agreement_signed'
        if self.type == 'conveyancing':
            self.acquisition_id.conveyancing_comment = self.comments
            self.acquisition_id.conveyancing_attachment_ids = self.attachment_ids
            self.acquisition_id.state = 'conveyance'