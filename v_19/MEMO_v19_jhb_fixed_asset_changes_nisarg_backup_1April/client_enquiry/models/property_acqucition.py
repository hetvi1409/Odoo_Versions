from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PropertyAcquisition(models.Model):
    """Client transaction"""
    _name = 'property.acquisition'
    _description = "Property Acquisition"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", copy=False)
    property_id = fields.Many2one('building', string="Property", required=True, tracking=True)
    address = fields.Char(string="Address")
    jmc_number = fields.Char(string="JMC Number", tracking=True)
    stand_number = fields.Char(string="Stand Number")
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'),
                              ('valuation', 'Valuation'),
                              ('transaction_created', 'Transaction'),
                              ('negotiation', 'Negotiation Ongoing'),
                              ('agreed', 'Approve'),
                              ('agreement_draft', 'Drafting Sale Agreement'),
                              ('agreement_signed', 'Agreement Signed'),
                              ('conveyancing', 'Conveyancing in Progress'),
                              ('conveyance', 'Conveyance'),
                              ('hand_over', 'Hand Over'),
                              ('rejected', 'Rejected'),
                              ('terminate', 'Terminated'),], default="draft", tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', store=True,
                                      string="Documents", required=True)
    comments = fields.Html(string="Comments",help="Add the Comments")
    valuation_id = fields.Many2one('assessment.valuation', string="Valuation", copy=False, tracking=True)
    valuation_state = fields.Selection(related="valuation_id.state")
    transaction_id = fields.Many2one('client.transaction', string="Transaction", copy=False, tracking=True)
    price = fields.Float(string="Price",)
    owner_id = fields.Many2one("res.partner", string="Property Owner",
                               required=True, tracking=True)
    buyer_id = fields.Many2one("res.partner", string="Potential Buyer",
                               required=True, tracking=True)
    negotiation_comment = fields.Char(string="Negotiation Comment")
    negotiation_attachment_ids = fields.Many2many("ir.attachment", 'negotiation_attachment_rel')
    agreement_comment = fields.Char(string="Agreement Comment")
    agreement_attachment_ids = fields.Many2many("ir.attachment", 'agreement_attachment_rel')
    sign_agreement_comment = fields.Char(string="Sign Agreement Comment")
    sign_agreement_attachment_ids = fields.Many2many("ir.attachment", 'sign_agreement_attachment_rel')
    conveyancing_comment = fields.Char(string="Conveyancing Comment")
    conveyancing_attachment_ids = fields.Many2many("ir.attachment", 'conveyancing_attachment_rel')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'property.acquisition'
            vals['name'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        return super(PropertyAcquisition, self).create(vals_list)

    @api.onchange('property_id')
    def onchange_property(self):
        """Onchange property Details"""
        self.address = self.property_id.address
        self.jmc_number = self.property_id.jmc_number
        self.stand_number = self.property_id.stand_number
        self.price = self.property_id.pricing
        self.owner_id = self.property_id.partner_id.id

    def check_ownership(self):
        """Check ownership of an existing property"""
        return {
            'name': _('Assessment report'),
            'view_mode': 'form',
            'res_model': 'check.ownership',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('client_enquiry.check_ownership_acquisition_view_form').id,
            'target': 'new',
            'context': {
                'default_property_id': self.property_id.id,
                'default_acquisition_id': self.id,
                'default_jmc_number': self.jmc_number
            }
        }

    def action_create_valuation(self):
        """Create Valuation"""
        valuation = self.env['assessment.valuation'].create({
            'property_id': self.property_id.id,
            # 'assessment_id': self.assessment_id.id,
            # 'enquiry_id': self.enquiry_id.id,
            'acquisition_id': self.id,
            'property_number': self.property_id.code,
            'size': self.property_id.building_area,
            'jmc_number': self.property_id.jmc_number,
            'address': self.property_id.address,
            'attachment_ids': self.attachment_ids
        })
        self.state = 'valuation'
        self.valuation_id = valuation.id

    def action_create_transaction(self):
        """Create a new assessment"""
        if self.valuation_state != 'transaction':
            raise UserError(_('Please update the valuation'))
        transaction = self.valuation_id.action_create_transaction()

    def action_start_negotiation(self):
        return {
            'name': _('Negotiation'),
            'view_mode': 'form',
            'res_model': 'acquisition.comments',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_acquisition_id': self.id,
                'default_type': 'negotiation'
            }
        }
        self.write({'state': 'negotiation'})

    def action_handover(self):
        """Handover property"""

    def action_agreement(self):
        self.write({'state': 'agreed'})

    def action_draft_agreement(self):
        return {
            'name': _('Approve'),
            'view_mode': 'form',
            'res_model': 'acquisition.comments',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_acquisition_id': self.id,
                'default_type': 'agreed'
            }
        }
        self.write({'state': 'agreement_draft'})

    def action_sign_agreement(self):
        return {
            'name': _('Sign Agreement'),
            'view_mode': 'form',
            'res_model': 'acquisition.comments',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_acquisition_id': self.id,
                'default_type': 'agreement_signed'
            }
        }
        self.write({'state': 'agreement_signed'})

    def action_start_conveyancing(self):
        self.write({'state': 'conveyancing'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_conveyance(self):
        return {
            'name': _('Conveyancing'),
            'view_mode': 'form',
            'res_model': 'acquisition.comments',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_acquisition_id': self.id,
                'default_type': 'conveyancing'
            }
        }

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

    def action_view_valuation(self):
        """View assessment valuation"""
        valuation = self.valuation_id
        action = {
            'name': _('Valuation'),
            'type': 'ir.actions.act_window',
            'res_model': 'assessment.valuation',
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

    def action_view_transaction(self):
        """View assessment valuation"""
        valuation = self.transaction_id
        action = {
            'name': _('Transaction'),
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
