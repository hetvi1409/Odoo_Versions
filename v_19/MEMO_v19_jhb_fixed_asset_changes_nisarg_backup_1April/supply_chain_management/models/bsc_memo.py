from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class BSCMemo(models.Model):
    """Model for BSC Memo"""
    _name = 'bsc.memo'
    _description = "BSC Memo"
    _inherit = "mail.thread", "mail.activity.mixin"

    name = fields.Char(string="Reference No", readonly=True, Tracking=True)
    description = fields.Char(string="Description", required=True, Tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer',
                                 help="Customer Details", required=True)
    total_amount = fields.Monetary(string="Total Amount", help="Total amount",
                                   required=True)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  string='Currency', readonly=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company,
                                 required=True)
    date = fields.Date(string="Date", help="Memo date",
                       readonly=True, Tracking=True, default=fields.Date.today())
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'),
                              ('cancelled', 'Cancelled')], default='draft',
                             string="State", help="State")
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Documents", help="Documents")
    transaction_id = fields.Many2one('client.transaction', copy=False)
    enquiry_id = fields.Many2one('client.enquiry', string="Enquiry", copy=False)
    assessment_id = fields.Many2one('enquiry.assessment', string="Assessment", copy=False)
    property_id = fields.Many2one('building', string="Property", required=True, copy=False)
    valuation_id = fields.Many2one('assessment.valuation', copy=False,
                                   string="Assessment Valuation")
    circulation_id = fields.Many2one('circulation.comments', copy=False,  string="Circulation Comments")


    @api.model
    def create(self, vals):
        """generate purchase requisition sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'bsc.memo') or 'New'
        result = super().create(vals)
        return result

    def action_approve(self):
        """Method to approve the memo"""
        if not self.total_amount > 20000:
            raise ValidationError(_('Total amount must be grater than 20000'))
        if not self.attachment_ids:
            raise ValidationError(_('Please attach documents'))
        self.state = 'approve'
        self.message_post(body=_('The Memo %s was approved by %s.') %
                               (self.name, self.env.user.name))
        mail_content = _('Hi,<br> %s'
                         'Your memo %s was approved.'
                         ) % (self.partner_id.name, self.name)
        partner = self.partner_id
        main_content = {
            'subject': _(
                'Memo Approved: %s' % self.name),
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_id = self.env['mail.mail'].sudo().create(main_content)
        mail_id.mail_message_id.body = mail_content
        mail_id.sudo().send()

    def action_refuse(self):
        """Method to approve the memo"""
        self.state = 'cancelled'
        self.message_post(body=_('The Memo %s was approved by %s.') %
                               (self.name, self.env.user.name))
        mail_content = _('Hi,<br> %s'
                         'Your memo %s was refused.'
                         ) % (self.partner_id.name, self.name)
        partner = self.partner_id
        main_content = {
            'subject': _(
                'Memo Refused: %s' % self.name),
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_id = self.env['mail.mail'].sudo().create(main_content)
        mail_id.mail_message_id.body = mail_content
        mail_id.sudo().send()

    def reset_drafts(self):
        """Method for reset the state into draft"""
        for rec in self:
            rec.state = 'draft'

    def action_create_purchase_requisition(self):
        """Methode to create the purchase requisition"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Requisition',
            'res_model': 'purchase.requisition',
            'view_mode': 'form',
            'context': {
                'default_memo_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_type': 'competitive_bid'
            }
        }

    def get_purchase_requisition_details(self):
        """Method to show purchase requisition details"""
        requisition = self.env['purchase.requisition'].search([('memo_id', '=', self.id)])
        action = {
            'name': _('Requisition'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition',
            'context': {'create': False},
        }
        if len(requisition) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': requisition.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', requisition.ids)],
            })
        return action

    def unlink(self):
        """Method to unlink bsc memo"""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("We can't only delete memo in "
                                  "the draft state."))

    def action_supply_attachment(self):
        return {
            'name': 'Documents',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'supply.chain.document',
            # Pass the ID of the created record
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
        }


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

    def action_view_circulation(self):
        """View assessment valuation"""
        valuation = self.circulation_id
        action = {
            'name': _('Circulation'),
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

    def action_view_assessment(self):
        """View assessment"""
        assessment = self.assessment_id
        action = {
            'name': _('Assessment'),
            'type': 'ir.actions.act_window',
            'res_model': 'enquiry.assessment',
            'context': {'create': False},
        }
        if len(assessment) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': assessment.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', assessment.ids)],
            })
        return action

    def action_view_enquiry(self):
        """View assessment"""
        assessment = self.enquiry_id
        action = {
            'name': _('Enquiry'),
            'type': 'ir.actions.act_window',
            'res_model': 'client.enquiry',
            'context': {'create': False},
        }
        if len(assessment) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': assessment.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', assessment.ids)],
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