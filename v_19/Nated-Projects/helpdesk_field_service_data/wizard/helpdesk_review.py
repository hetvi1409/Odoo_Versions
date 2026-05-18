from odoo import fields, models


class HelpdeskReview(models.TransientModel):
    """Helpdesk Review"""
    _name = 'helpdesk.review'
    _description = 'Helpdesk Review'

    is_internal_resolve = fields.Boolean(
        string="Issue will be internal resolve?")
    ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket details",
                                readonly=True)
    assignee_id = fields.Many2one('res.users', string="Technician")

    def action_submit(self):
        """Submit the review"""
        self.ticket_id.is_reviewed = True
        self.ticket_id.user_id = self.assignee_id
        self.ticket_id.is_internal_resolve = self.is_internal_resolve
