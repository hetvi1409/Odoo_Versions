from odoo import api, fields, models, _


class ContractProcurementRequest(models.Model):
    _name = 'contract.procurement.request'
    _description = 'Contract Procurement Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        default=lambda self: _('New'),
        readonly=True
    )
    contract_id = fields.Many2one(
        'xf.partner.contract',
        required=True,
        ondelete='cascade'
    )
    request_date = fields.Date(default=fields.Date.today())
    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user
    )
    end_user_id = fields.Many2one(
        'res.users',
        string='End User',
    )
    reason = fields.Selection([
        ('contract_expiry', 'Contract Expiry'),
        ('termination', 'Early Termination'),
        ('other', 'Other')],
        required=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')],
        default='draft',
        tracking=True
    )
    notes = fields.Text()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'contract.procurement.request') or _('New')
        return super().create(vals)

    def action_submit(self):
        self.write({'state': 'submitted'})
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary='Procurement Process Required',
            note='Please initiate the procurement process',
            user_id=self.end_user_id.id
        )
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract_procurement_submitted')
        template.send_mail(self.contract_id.id, force_send=True,)
        self.contract_id.message_post(
            body="Procurement was submitted: %s" % (self.name))
        self.message_post(
            body="Procurement was submitted: %s" % (self.name))

    def action_mark_completed(self):
        self.write({'state': 'completed'})
        self.contract_id.write({'procurement_required': False})
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract_procurement_approved')
        template.send_mail(self.contract_id.id, force_send=True,)
        self.message_post(
            body="Procurement was completed: %s" % (self.name))
        self.contract_id.message_post(
            body="Procurement was completed: %s" % (self.name))