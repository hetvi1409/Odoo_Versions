from datetime import date, datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Maintenance(models.Model):
    _inherit = 'helpdesk.ticket'

    # Customer Details
    partner_street = fields.Char(string='Street')
    partner_street2 = fields.Char(string='Street2')
    partner_city = fields.Char(string='City')
    partner_state_id = fields.Many2one("res.country.state", string='State',
                                       ondelete='restrict')
    partner_country_id = fields.Many2one('res.country', string='Country',
                                         ondelete='restrict')
    partner_zip = fields.Char(string="Zip", help="Zip code for the customer")
    partner_mobile = fields.Char(string='Mobile')

    ticket_job_card_id = fields.Many2one('job.card', string='Job Card')

    is_maintenance_request = fields.Boolean(string="Is Maintenance Request",
                                            compute="_compute_is_maintenance_request")
    property_name = fields.Many2one('building', string='Property Name')
    jmc_number = fields.Char(string='JMC Number')
    description = fields.Text(string='Description')
    request = fields.Many2one('building', 'Maintenance', copy=False)
    type = fields.Selection(
        [('emergency', 'Emergency'), ('minor', 'Minor'), ('major', 'Major')],
        string='Type')
    location = fields.Char(string='Location')
    # job_card_id = fields.Integer(string='Job Cart ID')
    region_id = fields.Many2one('regions', string="Region")
    supervisor_id = fields.Many2one('res.users', string="Supervisor")
    user_check = fields.Boolean(string="User check", compute="_compute_user_check")
    submit_check = fields.Boolean(string="Submit check")
    assign_for_inspection_check = fields.Boolean(string="Assign For Inspection check", compute="_compute_assign_for_inspection_check")
    department = fields.Char(string='Department')
    assignee_for_inspection = fields.Many2one('res.users',string='Assignee  For Inspection')
    # assignee_for_inspection_2 = fields.Many2one('res.users',string='Assignee  For Inspection')
    # inspected details tab
    inspected_detail = fields.Text(string='Inspection Results', readonly=True)
    inspected_document_ids = fields.Many2many('ir.attachment',
                                              string='Inspected Documents', readonly=True)

    image_1 = fields.Binary(string='Photo 1', help="Select image here", readonly=True)
    image_2 = fields.Binary(string='Photo 2', help="Select image here", readonly=True)
    image_3 = fields.Binary(string='Photo 3', help="Select image here", readonly=True)
    image_4 = fields.Binary(string='Photo 4', help="Select image here", readonly=True)
    image_5 = fields.Binary(string='Photo 5', help="Select image here", readonly=True)
    image_6 = fields.Binary(string='Photo 6', help="Select image here", readonly=True)
    check_inspection_finish = fields.Boolean(string="Inspection Finish")

    is_inventory_required = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Is Inventory Required')
    # required_inventory_ids = fields.One2many('inventory.required', "required_inventory", string="Required Inventory Items")
    check_inventory_approve = fields.Boolean(string="Approve Check")
    check_approved = fields.Boolean(string="Approved")
    is_job_card_created = fields.Boolean(string="Is Job Card Created", compute="_compute_is_job_card_created")
    check_work_done = fields.Boolean(string="Check work done", compute="_compute_check_work_done")
    is_job_card_create = fields.Boolean(string="Is Job Card Created")
    is_in_progress_stage = fields.Boolean(string="Is In Progress")
    is_card_decline = fields.Boolean(string="Is Card Decline")
    is_card_approved = fields.Boolean(string="Is Card Approved")
    is_job_assigned = fields.Boolean(string="Is Job Assigned")
    is_task_solved = fields.Boolean(string="Is Task Solved", compute="_compute_is_task_solved")
    task_solved = fields.Boolean(string="Task Solved")
    # access_for_job_card_creation = fields.Boolean(string="Is Job Card Created")
    # sla_status_id = fields.Many2one('res.users',string='Assignee  For Inspection')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            partner = self.partner_id
            self.partner_street = partner.street
            self.partner_street2 = partner.street2
            self.partner_city = partner.city
            self.partner_state_id = partner.state_id
            self.partner_country_id = partner.country_id
            self.partner_zip = partner.zip
            self.partner_mobile = partner.mobile


    # def action_inventory_approval_request(self):
    #     # Check if there are any required_inventory_ids
    #     if not self.required_inventory_ids:
    #         raise ValidationError(
    #             "No products have been added. Please add products to request inventory.")
    # #
    #     # Check stock availability for selected products
    #     for item in self.required_inventory_ids:
    #         if item.product_id.qty_available <= 0:
    #             raise ValidationError(
    #                 f"The product {item.product_id.display_name} is not available in stock.")
    #
    #     # If all checks pass, proceed with your business logic
    #     stage = self.env['helpdesk.stage'].search(
    #         [('name', '=', 'Waiting Inventory Approval')])
    #     self.stage_id = stage
    #     self.check_inventory_approve = True
    #
    def action_job_card_creation(self):
        self.is_job_card_create = True

        # Create a new record for the job card
        job_card_model = self.env['job.card']
        job_card = job_card_model.create({
            'helpdesk_job_card_id': self.id,
            'property_name': self.property_name.name,
            'jmc_number': self.jmc_number,
            'partner_street': self.partner_street,
            'partner_street2': self.partner_street2,
            'partner_city': self.partner_city,
            'partner_state_id': self.partner_state_id.id,
            'partner_zip': self.partner_zip,
            'partner_country_id': self.partner_country_id.id,
            'location': self.location,
            'partner_id': self.partner_id.id,
            'partner_email': self.partner_email,
            'partner_phone': self.partner_phone,
            'name': self.name,
            'technician': self.assignee_for_inspection.id,
            'ticket_ref': self.ticket_ref,

            # Add other fields as needed
        })

        # Update the helpdesk ticket with the job card reference
        self.write({'ticket_job_card_id': job_card.id})

        # Open a new window with the form view of the job card
        return {
            'name': 'Add Job Cards',
            'type': 'ir.actions.act_window',
            'res_model': 'job.card',
            'view_mode': 'form',
            'view_id': self.env.ref('property_maintenance_management.job_card_view_form').id,
            'res_id': job_card.id,
        }
    def action_approve_inventory(self):
        stage_approve = self.env['helpdesk.stage'].search(
                [('name', '=', 'Approved')])
        self.stage_id = stage_approve
        self.check_approved = True

    #     receipt = self.env['stock.picking'].create({
    #         'picking_type_id': 1,
    #         'partner_id': self.partner_id.id,
    #         'location_id': 1,
    #         'location_dest_id': 1,
    #         'move_ids': [(0, 0, {
    #             'name': self.required_inventory_ids.product_id.name,
    #             'product_id': self.required_inventory_ids.product_id.id,
    #             'product_uom_qty': 1,
    #             # 'product_uom': product.uom_id.id,
    #             'location_id': 2,
    #             'location_dest_id': 2,
    #         })]
    #     })
    #     receipt.action_confirm()
    #
    #     # receipt.move_line_ids.qty_done = 1
    #     # receipt.move_line_ids = [(0, 0, {
    #     #     'product_id': kit.id,
    #     #     'qty_done': 1,
    #     #     'product_uom_id': kit.uom_id.id,
    #     #     'location_id': customer_location.id,
    #     #     'location_dest_id': stock_location.id,
    #     # })]
    #
    #     # receipt.button_validate()
    #     stage_progress = self.env['helpdesk.stage'].search(
    #         [('name', '=', 'In Progress')])
    #
    #     self.stage_id = stage_progress

    def action_submit(self):
        self.submit_check = True

        # Iterate through each team associated with the ticket
        for team in self.team_id:
            # Find the SLA for the current team and issue type
            issue_type = self.env['helpdesk.sla'].search([
                ('issue_type', '=', self.type),
                ('team_id', '=', team.id),
            ])

            # If an SLA is found, update the sla_status_ids field
            if issue_type:
                # Unlink all existing records in sla_status_ids
                self.sla_status_ids.unlink()

                # Add the filtered SLA to the one2many field
                existing_sla = self.sla_status_ids.filtered(
                    lambda sla: sla.sla_id.id == issue_type.id)

                try:
                    self.sudo().sla_status_ids = [(0, 0, {
                        'sla_id': issue_type.id,
                        'status': existing_sla.status,
                        'deadline': existing_sla.deadline,
                    })]
                except Exception as e:
                    print(f"Error: {e}")
        return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'A new ticket created',
                               'type': 'rainbow_man',
            }
            }

    def action_assign_job(self):
        assigned_card = self.env['project.task'].search(
            [('jmc_number', '=', self.jmc_number)])
        assigned_card.is_job_card_created = True
        self.is_job_assigned = True

    def get_job_card_details(self):
        # Ensure that there is a linked job card
        card = self.env['job.card'].search([('helpdesk_job_card_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Card Details',
            'view_mode': 'list,form',
            'res_model': 'job.card',
            'domain': [('id', 'in', card.ids)],
            'target': 'current',
        }

    @api.onchange('property_name')
    def _onchange_property_name(self):
        if self.property_name:
            self.jmc_number = self.property_name.jmc_number
            self.region_id = self.property_name.region_id.id

    @api.depends('team_id')
    def _compute_is_maintenance_request(self):
        maintenance_team_names = ['Facilities']

        for rec in self:
            rec.is_maintenance_request = False
            team = self.env['helpdesk.team'].search(
                [('name', 'in', maintenance_team_names)])

            if rec.team_id and rec.team_id in team:
                rec.is_maintenance_request = True

    @api.depends('is_maintenance_request', 'supervisor_id')
    def _compute_user_check(self):
        current_user = self.env.user
        for ticket in self:
            ticket.user_check = False
            if ticket.is_maintenance_request and ticket.supervisor_id == current_user:
                ticket.user_check = True
            elif not ticket.is_maintenance_request:
                ticket.user_check = True

    @api.depends('is_maintenance_request', 'user_check', 'user_id')
    def _compute_assign_for_inspection_check(self):
        for rec in self:
            rec.assign_for_inspection_check = False
            if rec.is_maintenance_request and rec.user_check:
                # if rec.user_id:
                if rec.stage_id.name == 'New':
                    rec.assign_for_inspection_check = True

    def action_assigned_for_inspection(self):
        stage_progress = self.env['helpdesk.stage'].search(
            [('name', '=', 'In Progress')])
        if not self.assignee_for_inspection:
            raise ValidationError(
                "Please add Assignee  For Inspection.")
        self.stage_id = stage_progress
        if self.stage_id == stage_progress:
            self.is_in_progress_stage = True
        project_id = self.env['project.project'].search([
            ('name', '=', 'Field Service'), ('company_id', '=', self.env.company.id)])

        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'view_id': self.env.ref('project.view_task_form2').id,
            # Replace with the actual view ID
            'target': 'current',
            'res_id': False,  # Set to False to create a new record
            'context': {
                'default_project_id': project_id.id,
                'default_helpdesk_ticket_id': self.id,
                'default_name': self.name,
                'default_jmc_number': self.jmc_number,
                'default_partner_id': self.partner_id.id,
                'default_user_ids': [(6, 0, self.assignee_for_inspection.ids)],
            },
        }
        return action

    def action_add_job_cards(self):
        # Assuming you have a 'job.card' model
        # job_card_model = self.env['job.card']

        # Create a new record for the job card
        # job_card = job_card_model.create({
        #     'property_name': self.property_name.name,
        #     'jmc_number': self.jmc_number,
        #     'location': self.location,
        #     'partner_id': self.partner_id.id,
        #     'partner_email': self.partner_email,
        #     'partner_phone': self.partner_phone,
        #     # Link the job card to the helpdesk ticket
        #     # Add other fields as needed
        # })

        # Open a new window with the form view of the job card
        return {
            'name': 'Add Job Cards',
            'type': 'ir.actions.act_window',
            'res_model': 'job.card',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'property_maintenance_management.job_card_view_form').id,
            # 'res_id': job_card.id,
            'target': 'new',
        }

    def _compute_is_job_card_created(self):
        for ticket in self:
            ticket.is_job_card_created = False
            job_card = self.env['job.card'].search(
                [('jmc_number', '=', ticket.jmc_number)], limit=1)
            if job_card:
                ticket.is_job_card_created = True

    def _compute_check_work_done(self):
        for ticket in self:
            ticket.check_work_done = False
            job_card = self.env['project.task'].search(
                [('jmc_number', '=', ticket.jmc_number)], limit=1)
            if job_card.check_work_done:
                ticket.check_work_done = True

    def _compute_is_task_solved(self):
        for rec in self:
            rec.is_task_solved = False
            done_work = self.env['project.task'].search(
                [('jmc_number', '=', rec.jmc_number), ('helpdesk_ticket_id', '=', rec.id)], limit=1)
            if done_work.stage_id.name == 'Done':
                rec.is_task_solved = True

    def action_solved_task(self):
        for rec in self:
            stage = self.env['helpdesk.stage'].search(
                [('name', '=', 'Solved')])
            rec.stage_id = stage.id
            rec.task_solved = True

    inspection_count = fields.Integer(compute="_compute_inspection")

    @api.model
    def _compute_inspection(self):
        for rec in self:
            inspection_count = 0
            task = self.env['project.task'].search(
                [('helpdesk_ticket_id', '=', self.id)], limit=1)
            if task:
                inspection_count = self.env['inspection.details'].search_count([
                    ('task_id', '=', task.id)
                ])
            rec.inspection_count = inspection_count

    def action_inspection(self):
        task = self.env['project.task'].search([('helpdesk_ticket_id', '=', self.id)])
        inspection = []
        if task:
            inspection = self.env['inspection.details'].search([
                ('task_id', '=', task.id)
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

