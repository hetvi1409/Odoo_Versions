from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Project(models.Model):
    _inherit = 'project.project'

    property_id = fields.Many2one('building', string="Property", required=True, tracking=True)
    address = fields.Char(string="Address")
    jmc_number = fields.Char(string="JMC Number", tracking=True)
    # jmc_numbers = fields.Many2one('building',string="JMC Number", tracking=True)
    stand_number = fields.Char(string="Stand Number")
    owner_id = fields.Many2one("res.partner", string="Property Owner",
                               required=True, tracking=True)
    price = fields.Float(string="Price",)
    legal_manager_id = fields.Many2one("res.users", string="Legal Manager")
    state = fields.Selection([('draft', 'Draft'),
                              ('assigned', 'Assigned'),
                              ('prepare_task', 'Prepare Task'),
                              ('task', 'Task Created'),
                              ], default='draft')
    ref = fields.Char(string="Ref", copy=False)
    internal_reference_no = fields.Char(string="Internal Reference No")
    date_created = fields.Date(string="Date Created")
    date_estimated = fields.Date(string="Date Estimated")
    total_expense = fields.Float(string="Total Expense")
    attachment_ids = fields.Many2many('ir.attachment','missing_documents_rel',
                                      string="Upload Document")
    # missing_document = fields.Char(string="Missing Document Comments")
    missing_document = fields.Char(string="Missing Document Comments")
    conveyancing_comment = fields.Char(string="Conveyancing Comment")

    def action_assign(self):
        if not self.legal_manager_id:
            raise UserError(_('Please Add Legal Manager'))
        self.write({'state': 'assigned'})

    def action_view_documents(self):
        self.ensure_one()
        return {
            'res_model': 'documents.request_wizard',
            'type': 'ir.actions.act_window',
            'name': "Request Document",
            # 'domain': [
            #     ('res_model', '=', self._name), ('res_id', '=', self.id),
            # ],
            'target': 'new',
            'view_mode': 'form',
            'context': {'default_res_model': self._name,
                        'default_res_id': self.id,
                         'default_folder_id': self.env['documents.document'].search([('name', '=', 'Legal')], limit=1).id}
        }




    def action_missing_documents(self):
        """Missing Documents"""
        return {
            'name': _('Legal Missing Documents'),
            'view_mode': 'form',
            'res_model': 'legal.missing',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_legal_id': self.id,
                'default_type': 'missing',
            }
        }

    def action_create_default_tasks(self):
        """Action Create Tasks"""
        if self.task_template_id:
            self.create_default_tasks()
        self.state = 'task'

    @api.onchange('property_id')
    def onchange_property(self):
        """Onchange property Details"""
        self.address = self.property_id.address
        self.jmc_number = self.property_id.jmc_number
        self.stand_number = self.property_id.stand_number
        self.price = self.property_id.pricing
        self.owner_id = self.property_id.partner_id.id

    def action_view_property(self):
        """View assessment valuation"""
        valuation = self.property_id
        action = {
            'name': _('Property'),
            'type': 'ir.actions.act_window',
            'res_model': valuation._name,
            'context': {'create': False},
        }
        if len(valuation) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': valuation.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', valuation.ids)],
            })
        return action
