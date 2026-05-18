import base64

from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseRequisition(models.Model):
    """ Model for storing purchase requisition """
    _name = 'purchase.requisition'
    _description = 'Purchase Requisition'
    _inherit = "mail.thread", "mail.activity.mixin"

    name = fields.Char(string="Reference No", readonly=True, Tracking=True,
                       copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_ids = fields.Many2many('res.partner', string="Vendor",
                                   required=True, Tracking=True)
    selected_partner_id = fields.Many2one('res.partner',
                                          string="Selected supplier")
    requisition_date = fields.Date(string="Requisition Date",
                                   default=lambda self: fields.Date.today(),
                                   help='Date of Requisition')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company,
                                 help='Company')
    line_ids = fields.One2many(
        'purchase.requisition.line', 'requisition_id',
        string="Products",
        help='Requisition product')
    quote_line_ids = fields.One2many(
        'requisition.quote', 'requisition_id',
        string="Quote details",
        help='Quote product details')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('first_approve', 'First Approval'),
         ('second_approve', 'Second Approval'),
         ('approve', 'approved'),
         ('created_po', 'PO Created'),
         ('advertisement', 'Send Advertisement'),
         ('bid_evaluated', 'Bid Evaluation Completed'),
         ('agreement', 'Agreement'),
         ('cancelled', 'Cancelled')],
        default='draft', copy=False, tracking=True)

    budget_count = fields.Integer(string="Budget",
                                  compute='_compute_budget_count')

    type = fields.Selection([('competitive_bid', 'Competitive Bid'),
                             ('not_competitive', 'Not Competitive Bid')],
                            string='Type', help='Type of purchase Requisition')
    amount_total = fields.Monetary(string="Total Amount", help="Total Amount",
                                   compute='_compute_amount_total')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related='company_id.currency_id',
                                  help='Currency')
    memo_id = fields.Many2one('bsc.memo', string='Memo',
                              help='Memo details')
    meeting_count = fields.Integer(string="Meeting Count", help="Meeting Count",
                                   compute='_compute_meeting_count')

    recommendation_report = fields.Text(string="Recommendation Report",
                                        help="Recommendation Report")
    independent_advisor_id = fields.Many2one('res.partner',
                                             string='Independent Advisor',
                                             help='Independent Advisor will check '
                                                  'the recommendations')
    report_send = fields.Boolean(string="Report", help="Is report send or not", copy=False)
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Bid documents",
                                      help="Bid evaluation documents")
    msc_meeting_id = fields.Many2one('calendar.event', string="BSC Meeting")
    eac_meeting_id = fields.Many2one('calendar.event', string="BSC Meeting")

    @api.model
    def create(self, vals):
        """generate purchase requisition sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'purchase.requisition') or 'New'
        result = super(PurchaseRequisition, self).create(vals)
        return result

    @api.constrains('partner_ids')
    def _check_partner_ids(self):
        """Check the partner ids of the purchase requisition"""
        for rec in self:
            if len(rec.partner_ids) <= 2:
                raise UserError(_('Please add the at least 3 vendors'))

    @api.constrains('type')
    def _check_type(self):
        """Check the type of the purchase requisition"""
        for rec in self:
            if not rec.type:
                raise UserError(_('Please select the type'))

    @api.constrains('line_ids')
    def _check_line_ids(self):
        """Check Lines IDs"""
        for rec in self:
            if len(rec.line_ids) <= 0:
                raise UserError(_('Please add the lines'))

    @api.constrains('amount_total', 'type')
    def _check_amount_total(self):
        """Check the amount"""
        for rec in self:
            if rec.line_ids:
                if rec.type == 'not_competitive':
                    if rec.amount_total > 20000:
                        raise UserError(_('For the RFQ the total amount will'
                                          ' be less than 20000. Otherwise '
                                          'check the type.'))
                if rec.type == 'competitive_bid':
                    if rec.amount_total < 20000:
                        raise UserError(
                            _('For the Competitive the total amount will'
                              ' be grater than 20000. Otherwise '
                              'check the type.'))

    def action_first_approve(self):
        """Method for the first approval"""
        for rec in self:
            rec.state = 'first_approve'
            rec.message_post(
                body=_('The Requisition %s first approval done by %s '
                       'is successfully completed.') % (rec.name,
                                                        rec.env.user.name))

    def action_first_review(self):
        """Method for the first review"""
        for rec in self:
            rec.state = 'cancelled'
            rec.message_post(
                body=_('The Requisition %s first approval done by %s '
                       'is refused.') % (rec.name, rec.env.user.name))

    def reset_drafts(self):
        """Method for reset the state into draft"""
        for rec in self:
            rec.state = 'draft'
            rec.report_send = ''
            rec.selected_partner_id = ''
            self.quote_line_ids.unlink()

    def action_budget_approve(self):
        """Method for the budget approval"""
        for rec in self:
            rec.state = 'second_approve'
            rec.message_post(
                body=_('The Requisition %s second approval done by %s '
                       'is successfully completed.') % (
                         rec.name, rec.env.user.name))
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            Urls = urls.url_join(base_url,
                                 'web#id=%s&model=purchase.requisition&view_type=form' % rec.id)
            mail_content = _('Hi,<br>'
                             'This are the Quotes from the particular suppliers. Please check the %s.'
                             '<div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                             'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                             'border-color:#875A7B;text-decoration: none; display: inline-block; '
                             'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                             'cursor: pointer; white-space: nowrap; background-image: none; '
                             'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                             'View %s</a></div>'
                             ) % \
                           (rec.name,
                            Urls, rec.name)
            recipient_ids = rec.env.ref(
                'supply_chain_management.purchase_requisition_scm').users
            partner = recipient_ids.mapped('partner_id')
            main_content = {
                'subject': _(
                    'Quote for: %s' % rec.name),
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'recipient_ids': [(6, 0, partner.ids)]
            }
            mail_id = rec.env['mail.mail'].sudo().create(main_content)
            mail_id.mail_message_id.body = mail_content
            mail_id.sudo().send()

    def action_budget_refuse(self):
        """Method for the budget approval"""
        for rec in self:
            rec.state = 'cancelled'
            rec.message_post(
                body=_('The Requisition %s second approval done by %s '
                       'is refused.') % (rec.name, rec.env.user.name))

    def _compute_budget_count(self):
        """Compute the number of budget"""
        for rec in self:
            rec.budget_count = self.env['budget.analytic'].search_count([
                ('date_from', '<=', rec.requisition_date),
                ('date_to', '>=', rec.requisition_date)])

    def get_budget_details(self):
        """To get the budget details"""
        for rec in self:
            budget = self.env['budget.analytic'].search([
                ('date_from', '<=', rec.requisition_date),
                ('date_to', '>=', rec.requisition_date)])
            action = {
                'name': _('Budget'),
                'type': 'ir.actions.act_window',
                'res_model': 'budget.analytic',
                'context': {'create': False},
            }
            if len(budget) == 1:
                action.update({
                    'view_mode': 'form',
                    'res_id': budget.id,
                })
            else:
                action.update({
                    'view_mode': 'list,form',
                    'domain': [('id', 'in', budget.ids)],
                })
            return action

    def action_create_meeting(self):
        """Create a new meeting"""
        meeting = self.env['calendar.event'].create({
            'name': 'BSC Meetings',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.msc_meeting_id = meeting.id
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Committee Meeting',
        #     'res_model': 'committee.meeting',
        #     'view_mode': 'form',
        #     'context': {
        #         'default_purchase_requisition_id': self.id,
        #         'default_committee_id': self.env.ref(
        #             'supply_chain_management.committee_purchase_requisition').id,
        #         'default_subject': 'BSC meeting & system'
        #     }
        # }

    def action_approve(self):
        """Method for final approve"""
        for rec in self:
            if rec.type == 'competitive_bid':
                meeting = self.eac_meeting_id
                meeting_state = meeting.mapped('state')
                if 'approved' not in meeting_state:
                    raise UserError(_('Meeting is not approved'))
            if rec.selected_partner_id:
                rec.state = 'approve'
                rec.message_post(
                    body=_('The Requisition %s final approval done by %s '
                           'is successfully completed.') % (rec.name,
                                                            rec.env.user.name))
            else:
                raise UserError(_("Please select a supplier"))

    def action_refuse(self):
        """Method for final refuse"""
        for rec in self:
            rec.message_post(
                body=_('The Requisition %s final approval done by %s '
                       'is refused.') % (rec.name, rec.env.user.name))
            rec.message_post(
                body=_('Evaluate the quotes and select lowest one')
            )

    def action_create_po(self):
        """Method for Create Purchase Order"""
        purchase = self.env['purchase.order'].create({
            'partner_id': self.selected_partner_id.id,
        })

        for line in self.line_ids:
            self.env['purchase.order.line'].create({
                'product_id': line.product_id.id,
                'order_id': purchase.id
            })
        self.state = 'created_po'

    @api.depends('line_ids')
    def _compute_amount_total(self):
        """Calculate the total amount"""
        for rec in self:
            rec.amount_total = 0
            rec.amount_total = sum(self.line_ids.mapped('sub_total'))

    def get_memo_details(self):
        """To get the memo details."""
        action = {
            'name': _('Memo'),
            'type': 'ir.actions.act_window',
            'res_model': 'bsc.memo',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.memo_id.id,
        }
        return action

    @api.depends()
    def _compute_meeting_count(self):
        for rec in self:
            rec.meeting_count = self.env['committee.meeting'].search_count(
                [('purchase_requisition_id', '=', rec.id)])

    def get_committee_meeting_details(self):
        """Get all committee meeting details"""
        meeting = self.env['calendar.event'].search(
            [('res_id', '=', self.id),
             ('res_model', '=', self._name)])
        action = {
            'name': _('Meeting'),
            'type': 'ir.actions.act_window',
            'res_model': meeting._name,
            'context': {'create': False},
        }
        if len(meeting) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': meeting.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', meeting.ids)],
            })
        return action

    def action_approve_spec(self):
        """Only for the competitive bid.
        Methode for approving the spec"""
        # meeting = self.env['committee.meeting'].search(
        #     [('purchase_requisition_id', '=', self.id)])
        meeting = self.msc_meeting_id
        if not meeting:
            raise UserError(_('There is no meeting scheduled for the BSC '
                              'meeting.'))
        for rec in self:
            if rec.selected_partner_id:
                rec.state = 'approve'
                rec.message_post(
                    body=_('The Requisition %s final approval done by %s '
                           'is successfully completed.') % (rec.name,
                                                            rec.env.user.name))
            else:
                raise UserError(_("Please select a supplier"))

    def action_refuse_spec(self):
        """Only for the competitive bid.
        Methode for approving the spec"""
        for rec in self:
            rec.state = 'cancelled'
            rec.message_post(
                body=_('The Requisition %s final approval done by %s '
                       'is Cancelled.') % (rec.name, rec.env.user.name))

    def action_tender_advertisement(self):
        """Methode for tender advertisement"""
        report = self.env.ref(
            'supply_chain_management.action_report_purchase_requisition')
        data_record = base64.b64encode(
            self.env['ir.actions.report'].sudo()._render_qweb_pdf(
                report, [self.id], data=None)[0])
        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'name': _('Tender Advertisement'),
            'view_mode': 'form',
            'res_model': 'tender.advertisement',
            'context': {'default_purchase_requisition_id': self.id,
                        'default_datas': data_record
                        },
        }

    def action_send_audit_report(self):
        """Method for sending an audit report"""
        if not self.quote_line_ids:
            raise UserError(_('Please Add a quote line'))
        if len(self.partner_ids) > len(self.quote_line_ids):
            raise UserError(_('Add a quote line'))
        if not self.recommendation_report:
            raise UserError(_('Please Add a recommendation report'))
        if not self.independent_advisor_id:
            raise UserError(_('Please Add an independent advisor'))

        report = self.env.ref(
            'supply_chain_management.action_report_independent_auditor')
        data_record = base64.b64encode(
            self.env['ir.actions.report'].sudo()._render_qweb_pdf(report,
                                                                  [self.id],
                                                                  data=None)[0])
        ir_values = {
            'name': 'Audit Report',
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'purchase.requisition',
            'res_id': self.id
        }
        report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
        mail_content = _('Hi, %s<br>'
                         'This is the independent report of the %s. Please check and verify this.'
                         ) % \
                       (self.independent_advisor_id.name,
                        self.name)
        partner = self.independent_advisor_id
        main_content = {
            'subject': _(
                'Independent Audit Report for: %s' % self.name),
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_id = self.env['mail.mail'].sudo().create(main_content)
        mail_id.attachment_ids = [(4, report_attachment.id)]
        mail_id.mail_message_id.body = mail_content
        mail_id.sudo().send()
        self.report_send = True

    def action_bid_evaluation(self):
        """Method for evaluating bid"""
        if not self.report_send:
            raise ValidationError(_("Please send the report to the"
                                    " independent advisor"))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bid Evaluation',
            'res_model': 'bid.evaluation',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_requisition_id': self.id
            }
        }

    def unlink(self):
        """Added an condition for deleting the record"""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Can't delete the purchase requisition "
                                  "in this state."))
        res = super().unlink()
        return res

    def action_edc_meeting(self):
        """Method for creating meeting"""

        meeting = self.env['calendar.event'].create({
            'name': 'Executive Adjudication Committee Meetings',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.eac_meeting_id = meeting.id
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Committee Meeting',
        #     'res_model': 'committee.meeting',
        #     'view_mode': 'form',
        #     'context': {
        #         'default_purchase_requisition_id': self.id,
        #         'default_committee_id': self.env.ref(
        #             'supply_chain_management.committee_purchase_requisition').id,
        #         'default_subject': 'Executive Adjudication Committee',
        #         'default_eac': True
        #     }
        # }

    def action_edc(self):
        """Method for edc meeting and approval"""
        meeting = self.env['committee.meeting'].search(
            [('purchase_requisition_id', '=', self.id),
             ('eac', '=', True)])
        meeting_state = meeting.mapped('state')
        # if 'approved' not in meeting_state:
        #     raise UserError(_('Meeting is not approved'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'EDC Evaluation',
            'res_model': 'edc.evaluation',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_requisition_id': self.id,
                'default_partner_ids': self.partner_ids.ids
            }
        }

    def supply_document_upload(self):
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


class RequisitionProducts(models.Model):
    _name = 'purchase.requisition.line'
    _description = 'Purchase Requisition Line'

    requisition_id = fields.Many2one(
        'purchase.requisition', help='Requisition product')
    product_id = fields.Many2one('product.product', required=True,
                                 help='Product',
                                 domain="[('purchase_ok', '=', True)]")
    description = fields.Text(
        string="Description", help='Product Description')
    quantity = fields.Integer(string='Quantity', help='Quantity', default=1)
    uom = fields.Char(related='product_id.uom_id.name',
                      string='Unit of Measure', help='Product Uom')
    amount = fields.Monetary(string='Amount', help='Cost price')
    sub_total = fields.Monetary(string='Subtotal', help='Subtotal amount',
                                compute='_compute_sub_total')
    company_id = fields.Many2one('res.company', string='Company',
                                 related='requisition_id.company_id',
                                 help='Company')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related='company_id.currency_id',
                                  help='Currency')

    @api.onchange('product_id')
    def onchange_product_id(self):
        """Calculate the products price"""
        for rec in self:
            if rec.product_id:
                rec.amount = rec.product_id.lst_price
                if rec.product_id.default_code and rec.product_id.name:
                    rec.description = '[' + rec.product_id.default_code + '] ' + rec.product_id.name
                else:
                    rec.description = rec.product_id.name

    @api.depends('amount', 'quantity')
    def _compute_sub_total(self):
        """Calculate the sub total"""
        for rec in self:
            rec.sub_total = rec.amount * rec.quantity


class RequisitionQuote(models.Model):
    _name = 'requisition.quote'
    _description = 'Requisition Quote'

    requisition_id = fields.Many2one(
        'purchase.requisition', help='Requisition product')

    partner_id = fields.Many2one('res.partner', required=True,
                                 help='Partner')
    description = fields.Char(string="Description", help="Description")
    amount = fields.Float(string='amount', help='Amount')
