from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    is_enquiry = fields.Boolean(string="Enquiry")
    enquiry_count = fields.Integer(string="Enquiry Count", compute="_compute_enquiry_count")
    assessment_count = fields.Integer(string="Assessment Count", compute="_compute_enquiry_count")
    assessment_started = fields.Integer(string="Assessment started",
                                        compute='_compute_assessment_started')
    assessment_completed = fields.Integer(string="Assessment completed",
                                        compute='_compute_assessment_completed')
    assessment_cancelled = fields.Integer(string="Assessment cancelled",
                                        compute='_compute_assessment_cancelled')
    open_enquiry_count = fields.Integer(string="Open Enquiry count",
                                        compute='_compute_open_enquiry')
    unassigned_enquiry = fields.Integer(string="Unassigned Enquiry",
                                        compute='_compute_unassigned_enquiry')
    urgent_enquiry = fields.Integer(string="Urgent Enquiry", compute='_compute_urgent_enquiry')

    def action_view_enquiry(self):
        """Open enquiry from the team"""
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'client.enquiry',
            'view_mode': 'list,kanban,form',
            "view_type": "list",
            'domain': [('team_id', '=', self.id)],
        }
        return action

    def _compute_enquiry_count(self):
        """Compute the enquiry count and assessment count"""
        for rec in self:
            enquiry = self.env['client.enquiry'].search_count(
                [('team_id', '=', rec.id)])
            rec.enquiry_count = enquiry
            enquiry = self.env['client.enquiry'].search(
                [('team_id', '=', rec.id)])
            assessment = self.env['enquiry.assessment'].search_count([
                ('enquiry_id', 'in', enquiry.ids)])
            rec.assessment_count = assessment

    def _compute_assessment_started(self):
        """Compute assessment started"""
        for rec in self:
            enquiry = self.env['client.enquiry'].search_count(
                [('team_id', '=', rec.id), ('state', '=', 'assessment')])
            rec.assessment_started = enquiry

    def _compute_assessment_completed(self):
        """Compute the assessment completed"""
        enquiry = 0
        for rec in self:
            enquiry = rec.env['client.enquiry'].search_count(
                [('team_id', '=', rec.id), ('state', '=', 'completed')])
            rec.assessment_completed = enquiry

    def _compute_assessment_cancelled(self):
        """Calculate cancelled enquiry count"""
        for rec in self:
            enquiry = rec.env['client.enquiry'].search_count(
                [('team_id', '=', rec.id), ('state', '=', 'cancelled')])
            rec.assessment_cancelled = enquiry

    def _compute_open_enquiry(self):
        """Count of draft enquiries"""
        for rec in self:
            enquiry_count = rec.env['client.enquiry'].search_count(
                [('team_id', '=', rec.id), ('state', '=', 'draft')])
            rec.open_enquiry_count = enquiry_count

    def _compute_unassigned_enquiry(self):
        """Compute the unassigned queries"""
        for rec in self:
            enquiry = rec.env['client.enquiry'].search_count(
                [('team_id', '=', rec.id), ('user_id', '=', False)])
            rec.unassigned_enquiry = enquiry

    def _compute_urgent_enquiry(self):
        """Compute Urgent Enquiry"""
        for rec in self:
            enquiry = rec.env['client.enquiry'].search_count(
                [('team_id', '=', rec.id), ('priority', '=', '3')])
            rec.urgent_enquiry = enquiry

    def action_view_urgent_enquiry(self):
        """View urgent enquiry"""
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'client.enquiry',
            'view_mode': 'list,kanban,form',
            'domain': [('team_id', '=', self.id), ('priority', '=', '3')]
        }
        return action

    def action_view_assessment_started(self):
        """Open the assessment started enquiry"""
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'client.enquiry',
            'view_mode': 'list,kanban,form',
            'domain': [('team_id', '=', self.id), ('state', '=', 'assessment')]
        }
        return action

    def action_view_assessment_completed(self):
        """View the completed assessment"""
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'client.enquiry',
            'view_mode': 'list,kanban,form',
            'domain': [('team_id', '=', self.id), ('state', '=', 'completed')]
        }
        return action

    def action_view_assessment_cancelled(self):
        """View the assessment cancelled details"""
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'client.enquiry',
            'view_mode': 'list,kanban,form',
            'domain': [('team_id', '=', self.id), ('state', '=', 'cancelled')]
        }
        return action

    def action_view_open_enquiry(self):
        """view the drafted enquiries"""
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'client.enquiry',
            'view_mode': 'list,kanban,form',
            'domain': [('team_id', '=', self.id), ('state', '=', 'draft')]
        }
        return action

    def action_view_unassigned_enquiry(self):
        """View the unassigned enquiry"""
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'client.enquiry',
            'view_mode': 'list,kanban,form',
            'domain': [('team_id', '=', self.id), ('user_id', '=', False)]
        }
        return action

    def action_view_enquiry_team(self):
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.team',
            'view_mode': 'form',
            'res_id': self.id
        }
        return action

    def action_view_enquiry_assessment(self):
        """To open the assessment"""
        enquiry = self.env['client.enquiry'].search([('team_id', '=', self.id)])
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'enquiry.assessment',
            'view_mode': 'list,kanban,form',
            'domain': [('enquiry_id', 'in', enquiry.ids)]
        }
        return action


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'


    def _default_team_id(self):
        team_id = self.env['helpdesk.team'].search([('member_ids', 'in', self.env.uid), ('is_enquiry', '=', False)], limit=1).id
        if not team_id:
            team_id = self.env['helpdesk.team'].search([('is_enquiry', '=', False)], limit=1).id
        return team_id

    # team_id = fields.Many2one('helpdesk.team', string='Team', default=_default_team_id, index=True, tracking=True, domain="[('is_enquiry', '=', False)]")
    # enquiry_id = fields.Many2one('client.enquiry')