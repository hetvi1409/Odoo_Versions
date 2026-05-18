from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InspectionDetails(models.Model):
    _name = 'inspection.details'
    _description = 'Inspection Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name of Incident")
    jmc_number = fields.Char(string="JMC Number")
    property_name = fields.Many2one('building', string='Property Name')
    region_id = fields.Many2one('regions', string="Region")
    # inspected details
    inspected_detail = fields.Text(string='Inspection Results')
    inspected_document_ids = fields.Many2many('ir.attachment',
                                                     string='Inspected Documents')
    task_id = fields.Many2one('project.task', string='Task')

    image_1 = fields.Binary(string='Photo 1', help="Select image here")
    image_2 = fields.Binary(string='Photo 2', help="Select image here")
    image_3 = fields.Binary(string='Photo 3', help="Select image here")
    image_4 = fields.Binary(string='Photo 4', help="Select image here")
    image_5 = fields.Binary(string='Photo 5', help="Select image here")
    image_6 = fields.Binary(string='Photo 6', help="Select image here")

    def action_close_inspection(self):
        inspection = self.task_id
        inspection.inspection_finish()
        action = {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'view_id': self.env.ref('project.view_task_form2').id,
            # Replace with the actual view ID
            'target': 'current',
            'res_id': inspection.id,  # Set to False to create a new record
        }
        return action
