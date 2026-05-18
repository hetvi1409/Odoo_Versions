
from odoo import models, fields, api
from odoo.exceptions import UserError

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # Enquiry Details
    region = fields.Many2one('res.municipality',string='Municipality')
    # subject = fields.Text('Subject')
    category = fields.Selection([
        ('Individual Subsidy', 'Individual Subsidy'),
        ('Destitute', 'Destitute'),
        ('Fraud and Corruption', 'Fraud and Corruption'),
        ('Eviction', 'Eviction'),
        ('First Home Finance', 'First Home Finance'),
        ('Disaster', 'Disaster'),
        ('Illegal Occupation', 'Illegal Occupation'),
        ('Title Deed', 'Title Deed'),
        ('Rental Tribunal', 'Rental Tribunal'),
        ('Estate', 'Estate'),
        ('Family Dispute', 'Family Dispute'),
        ('Change of Financial Dependant', 'Change of Financial Dependant'),
        ('Selling of House', 'Selling of House')
    ], string='Directorate')
    department_id = fields.Many2one('hr.department', string='Department')

    # Enquirer Details
    enquirer_name = fields.Char(string='Enquirer Name')
    enquirer_surname = fields.Char(string='Enquirer Surname')
    id_number = fields.Char(string='ID Number')
    contact_number = fields.Char(string='Contact Number')
    email = fields.Char(string='Email Address')

    # Source Tracking
    channel = fields.Selection([
        ('facebook', 'FaceBook'),
        ('whatsapp', 'Whatsapp'),
        ('tiktok', 'Tiktok'),
        ('email', 'Email'),
        ('walk_in', 'Walk-in'),
        ('phone_call', 'Phone Call'),
        ('hotline', 'Presidential Hotline'),
        ('correspondence', 'Correspondence'),
        ('website', 'Website')
    ], string='Nature of Logging')

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    facebook_message_id = fields.Char(string="Facebook Message ID")
    facebook_sender_id = fields.Char(string="Facebook Sender ID")
    facebook_page_id = fields.Char(string="Facebook Page ID")

    show_channel = fields.Boolean(compute="_compute_show_channel", store=False)

    @api.depends("team_id")
    def _compute_show_channel(self):
        """Show channel field only if team is 'Customer Care Support'"""
        customer_care_team = self.env.ref("customer_care.customer_carehelpdesk_team")  # Get team record
        for record in self:
            record.show_channel = record.team_id == customer_care_team


    def write(self, vals):
        if 'stage_id' in vals:
            for ticket in self:
                new_stage = self.env['helpdesk.stage'].browse(vals['stage_id'])

                if new_stage.name == self.env.ref('customer_care.helpdesk_stage_new').name:
                    if not self.env.user.has_group('customer_care.group_customer_care_qa') and not self.env.user.has_group('base.group_system'):
                        raise UserError("Only QA can move a ticket to closed stage.")
                    else:
                        if ticket.partner_id:
                            template = self.env.ref('customer_care.email_template_ticket_closing')
                            self.env['mail.template'].browse(template.id).send_mail(ticket.id, force_send=True)

        return super().write(vals)


    def action_assign_partner(self):
        for rec in self:
            existing_partner = self.env['res.partner'].sudo().search([
                ('email', '=', rec.email),
            ])

            if not existing_partner:
                existing_partner = self.env['res.partner'].sudo().create({
                    'name': rec.name or '',
                    'phone': rec.contact_number or '',
                    'email': rec.email or '',
                })
                rec.partner_id = existing_partner.id

            elif len(existing_partner) == 1:
                rec.partner_id = existing_partner.id

            else:
                pass



