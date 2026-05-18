from odoo import api, fields, models, _


class ServitudeRegister(models.Model):
    _name = 'servitude.register'
    _description = "Servitude Register"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char('Sequence', copy=False)
    servitude_type = fields.Selection([('right', 'Right of Way'),
                                       ('easement', 'Easement')], required=True, string="Type")
    description = fields.Text(string='Purpose of the servitude', required=True)
    property_ids = fields.Many2many('building', string="Properties", required=True)
    holder_id = fields.Many2one('res.partner',
                                string="Entity benefiting from servitude", required=True)
    # grantor_id = fields.Many2one('res.partner',
    #                              string="Property owner granting servitude", required=True)
    grantor_ids = fields.Many2many('res.partner',
                                 string="Property owner granting servitude", required=True)
    deed_number = fields.Char(string="Legal document reference")
    registration_date = fields.Date(string="Date of registration", default=fields.Date.today())
    expiry_date = fields.Date(string="Expiry date", required=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('submit', 'Submitted'),
        ('pending', 'Pending'), ('approve', 'Approved'),
        ('active', 'Active'), ('expired', 'Expired'),
        ('revoked', 'Revoked'),], default="draft")
    payment_amount = fields.Float(string="Amount", required=True)
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),], string="Payment Status",
        related="invoice_id.payment_state")
    attachment_ids = fields.Many2many('ir.attachment', string="Legal Documents")
    invoice_id = fields.Many2one('account.move', string="Invoice")

    def action_submit(self):
        """Action Submit"""
        self.state = 'submit'

    @api.onchange('property_ids')
    def action_property(self):
        """Updating owner grating in the """
        property = self.env['building'].browse(self.property_ids.ids)
        owner = property.mapped('partner_id')
        self.grantor_ids = owner.ids

    def action_approve(self):
        """Method to approbe the """
        self.state = 'approve'
        self.message_post(
            body=_('The Servitude %s was approved by %s') % (
                     self.name, self.env.user.name))

        mail_template = self.env.ref('servitude_register.email_template_servitude_register_approve')
        email_values = {
            'recipient_ids': [(6, 0, self.holder_id.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_reject(self):
        """Method to reject the """
        self.state = 'revoked'
        self.message_post(
            body=_('The Servitude %s was rejected by %s') % (
                     self.name, self.env.user.name))

        mail_template = self.env.ref('servitude_register.email_template_servitude_register_refuse')
        email_values = {
            'recipient_ids': [(6, 0, self.holder_id.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_create_invoices(self):
        """Create invoices"""
        move = self.env['account.move'].create({
            'partner_id': self.holder_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today()
        })
        self.env['account.move.line'].create({
            'move_id': move.id,
            'name': 'Servitude Register',
            'price_unit': self.payment_amount
        })
        self.invoice_id = move.id
        self.state = 'active'

        self.message_post(
            body=_('The Invoice %s was created by %s') % (
                     self.name, self.env.user.name))

        mail_template = self.env.ref('servitude_register.email_template_servitude_register_invoice')
        email_values = {
            'recipient_ids': [(6, 0, self.holder_id.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)

    def action_view_property(self):
        """Property view"""
        property = self.property_ids
        action = {
            'name': _('Property'),
            'type': 'ir.actions.act_window',
            'res_model': property._name,
            'context': {'create': False},
        }
        if len(property) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': property.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', property.ids)],
            })
        return action

    def action_expired_date(self):
        """Expired Date"""
        servitude = self.env['servitude.register'].sudo().search([
            ('state', '=', 'active'), ('expiry_date', '=', fields.Date.today())])
        for rec in servitude:
            rec.state = 'expired'