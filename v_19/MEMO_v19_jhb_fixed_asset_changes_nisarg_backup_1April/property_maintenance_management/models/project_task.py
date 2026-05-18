from datetime import date, datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError



class ProjectTask(models.Model):
    _inherit = 'project.task'

    jmc_number = fields.Char(
        string="JMC Number")
    check_inspection_start = fields.Boolean(string="Inspection Start")
    check_inspection_finish = fields.Boolean(string="Inspection Finish")
    is_job_card_created = fields.Boolean(string="Is Job Card Created")
    check_work_start = fields.Boolean(string="Check work start")
    check_work_done = fields.Boolean(string="Check work done", compute="_compute_check_work_done")
    is_save = fields.Boolean(string="Is Save")
    manager_id = fields.Many2one('res.users', string='Project Manager',
                                 related='project_id.user_id', readonly=True)

    def action_save(self):
        """Save the task"""
        self.is_save = True
        pass


    def inspection_start(self):
        self.check_inspection_start = True
        start = self.env['project.task.type'].search([('name', '=', 'Inspection Started')])
        self.stage_id = start.id
        property = self.helpdesk_ticket_id

        inspection_values = {
            'name': f"Inspection for {self.name}",
            'jmc_number': self.jmc_number,
            'property_name': property.property_name.id,
            'region_id': property.region_id.id,
            'task_id': self.id
        }
        inspection_record = self.env['inspection.details'].create(
            inspection_values)

    def action_inspection(self):
        inspection = self.env['inspection.details'].search([
            ('task_id', '=', self.id)
        ])
        action = {
            'name': _('Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'inspection.details',
            'context': {'create': False},
        }
        if len(inspection) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': inspection.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', inspection.ids)],
            })
        return action

    def inspection_finish(self):
        finish = self.env['project.task.type'].search(
            [('name', '=', 'Inspection Completed')])
        self.stage_id = finish.id
        inspection_details_helpdesk = self.helpdesk_ticket_id
        inspection_details_inspection = self.env['inspection.details'].search(
            [('jmc_number', '=', self.jmc_number), ('task_id', '=', self.id)])
        if inspection_details_inspection.inspected_detail:
            inspection_details_helpdesk.inspected_detail = inspection_details_inspection.inspected_detail
        if inspection_details_inspection.inspected_document_ids:
            inspection_details_helpdesk.inspected_document_ids = inspection_details_inspection.inspected_document_ids
        if inspection_details_inspection.image_1:
            inspection_details_helpdesk.image_1 = inspection_details_inspection.image_1
        if inspection_details_inspection.image_2:
            inspection_details_helpdesk.image_2 = inspection_details_inspection.image_2
        if inspection_details_inspection.image_3:
            inspection_details_helpdesk.image_3 = inspection_details_inspection.image_3
        if inspection_details_inspection.image_4:
            inspection_details_helpdesk.image_4 = inspection_details_inspection.image_4
        if inspection_details_inspection.image_5:
            inspection_details_helpdesk.image_5 = inspection_details_inspection.image_5
        if inspection_details_inspection.image_6:
            inspection_details_helpdesk.image_6 = inspection_details_inspection.image_6
        # Set the 'check_inspection_finish' flag in both models
        self.check_inspection_finish = True
        if inspection_details_helpdesk.check_inspection_finish == False and self.check_inspection_finish:
            inspection_details_helpdesk.check_inspection_finish = True

    # @api.depends('jmc_number')
    # def _compute_is_job_card_created(self):
    #     for ticket in self:
    #         ticket.is_job_card_created = False
    #         job_card = self.env['helpdesk.ticket'].search(
    #             [('jmc_number', '=', ticket.jmc_number)], limit=1)
    #         if job_card.is_job_card_created:
    #             ticket.is_job_card_created = True

    def action_job_card_show(self):
        job_card_id = self.env['job.card'].search(
            [('helpdesk_job_card_id', '=', self.helpdesk_ticket_id.id)],)

        if job_card_id:
            action = {
                'name': 'Job Card',
                'type': 'ir.actions.act_window',
                'res_model': 'job.card',
                'view_mode': 'list,form',
                'domain': [('id', 'in', job_card_id.ids)],
                'target': 'current',
            }
            return action
        raise UserError("No Job Card linked to this ticket.")

    def action_work_start(self):
        # work_start = self.env['project.task.type'].search(
        #     [('name', '=', 'In Progress')])
        # self.stage_id = work_start.id
        self.check_work_start = True

    def _compute_check_work_done(self):
        for rec in self:
            rec.check_work_done = False
            work_start = self.env['project.task.type'].search(
                [('name', '=', 'Done')])
            if rec.stage_id == work_start:
                rec.check_work_done = True
