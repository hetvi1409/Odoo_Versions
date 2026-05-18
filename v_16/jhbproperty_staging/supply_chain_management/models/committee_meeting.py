from odoo import fields, models


class CommitteeMeeting(models.Model):
    """Inheriting the models for create meeting from the Purchase requisition"""
    _inherit = 'committee.meeting'

    purchase_requisition_id = fields.Many2one('purchase.requisition',
                                              string='Purchase Requisition')
    eac = fields.Boolean(string="Eac", readonly=True)
