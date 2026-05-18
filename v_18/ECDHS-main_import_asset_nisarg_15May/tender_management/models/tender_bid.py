import base64
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class TenderBid(models.Model):
    """
    Model representing a bid submitted for a tender.
    """
    _name = 'tender.bid'
    _description = 'Tender Bid'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Ref No', required=True, copy=False,
                       readonly=True, index=True, tracking=True,
                       default='New')
    bid_name = fields.Char(string='Bid Name')
    bid_type = fields.Selection([('rfi', 'RFI'), ('rfp', 'RFP'),
                                 ('rfq', 'RFQ')],
                                string='Bid Type', tracking=True,
                                default='rfi',
                                help='The status of the bid Type')
    tender_id = fields.Many2one('tender.tender', string='Tender',
                                help='The tender for which the bid is submitted')
    vendor_id = fields.Many2one('res.partner', string='Vendor',
                                help='The vendor submitting the bid')
    # bid_amount = fields.Float(string='Bid Amount',
    #                           help='The amount quoted in the bid')
    document_ids = fields.One2many('tender.document', 'bid_id',
                                   string='Documents',
                                   help='Documents related to the Bid')
    # submission_deadline Date <- submission_date Datetime
    submission_deadline = fields.Date(string='Submission Deadline',
                                      default=fields.Date.context_today,
                                      help='The date and time when the bid was'
                                           ' submitted')
    # compliance_status = fields.Many2one('res.compliance',
    #                                     string='Compliance Status',)
    evaluation_score = fields.Float(string='Evaluation Score',
                                    help='Score for bid evaluation')
    evaluation_progress = fields.Float(string='Evaluation Progress',
                                       compute='_compute_evaluation_progress',
                                       store=True,
                                       help='Evaluation Progress in percentage')
    comments = fields.Text(string='Comments',
                           help='Additional comments or notes')
    state = fields.Selection([('draft', 'Draft'),
                              ('submitted', 'Submitted'),
                              ('compliance_review_pending',
                               'Compliance Review Pending'),
                              ('compliance_review_approved',
                               'Compliance Review Approved'),
                              ('compliance_review_rejected',
                               'Compliance Review Rejected'),
                              ('evaluation_started', 'Evaluation Started'),
                              ('evaluation_completed', 'Evaluation Completed'),
                              ('adjudication_pending', 'Adjudication Pending'),
                              (
                                  'adjudication_approved',
                                  'Adjudication Approved'),
                              (
                                  'adjudication_rejected',
                                  'Adjudication Rejected'),
                              ('done', 'Done'),
                              ('award_letter_sent', 'Award Letter Sent'),
                              ('purchase', 'Purchase'),
                              ('cancel', 'Rejected'),
                              ],
                             string='Status', tracking=True,
                             default='draft',
                             help='The status of the bid (draft or submitted)')
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 help="Company Name",
                                 default=lambda self: self.env.company)
    is_bid_published = fields.Boolean(string='Is Bid Published')
    # start_compliance_review = fields.Boolean(string='start Compliance Review')
    start_evaluation = fields.Boolean(string='start Evaluation')
    is_rfq_created = fields.Boolean(string='RFQ Created')
    award_letter_id = fields.Many2one('bid.award', string="Award Letter",
                                      readonly=True)
    file = fields.Binary(string="File")

    # set_adjudication_status = fields.Boolean(string='Set Adjudication Status')


    def action_view_documents(self):
        """view documents"""
        self.ensure_one()
        return {
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'name': _("%(name)s's Documents", name=self.name),
            'domain': [
                ('res_model', '=', 'tender.bid'),
                ('res_id', '=', self.id),
            ],
            'view_mode': 'kanban,list,form',
            'context': {'default_res_model': 'tender.bid',
                        'default_res_id': self.id,
                        'create': False},
        }

    @api.model_create_multi
    def create(self, vals):
        for rec in vals:
            if rec.get('name', 'New') == 'New':
                rec['name'] = self.env['ir.sequence'].next_by_code(
                    'tender.bid') or 'New'
        return super(TenderBid, self).create(vals)

    def action_bid_publish(self):
        self.is_bid_published = True

    def action_submit(self):
        """
        Action to Submit the tender.
        """
        self.state = 'submitted'

    @api.depends('evaluation_score')
    def _compute_evaluation_progress(self):
        for record in self:
            # Assuming the maximum score is 100
            max_score = 100
            if record.evaluation_score > max_score:
                record.evaluation_score = max_score
            record.evaluation_progress = (
                                                     record.evaluation_score / max_score) * 100

    def action_start_compliance_review(self):
        self.state = 'compliance_review_pending'

    def action_approve_compliance_review(self):
        self.state = 'compliance_review_approved'

    def action_reject_compliance_review(self):
        self.state = 'compliance_review_rejected'

    def action_start_evaluation(self):
        self.start_evaluation = True
        self.state = 'evaluation_started'

    def action_completed_evaluation(self):
        self.state = 'evaluation_completed'

    def action_adjudication_pending(self):
        self.state = 'adjudication_pending'

    def action_adjudication_approve(self):
        self.state = 'adjudication_approved'

    def action_adjudication_reject(self):
        self.state = 'adjudication_rejected'

    def action_done(self):
        for rec in self:
            if rec.state == 'adjudication_approved':
                rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            # if rec.state == 'adjudication_approved':
            rec.state = 'cancel'

    def action_done_tender(self):
        self.state = 'done'

    def action_cancel_tender(self):
        self.state = 'cancel'

    def action_create_award_letter(self):

        if not self.award_letter_id:
            self._prepare_award_letter()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Award Letter',
            'res_model': 'bid.award',
            'view_mode': 'form',
            'res_id': self.award_letter_id.id,
            'target': 'new',
        }

    def _prepare_award_letter(self):
        award_letter = self.env['bid.award'].create({
            'bid_id': self.id,
            'vendor_id': self.vendor_id.id,
            'subject': f"Award Letter for {self.name}",
            'body': f"Dear {self.vendor_id.name},\n\nWe are pleased to inform you that your bid has been awarded. Please review the attached document for further details.\n\nBest Regards,\nYour Company",
        })
        self.award_letter_id = award_letter.id

    def action_view_award_letter(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Award Letter',
            'res_model': 'bid.award',
            'view_mode': 'form',
            'res_id': self.award_letter_id.id,
            'target': 'current',
        }

    def create_rfq(self):
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.vendor_id.id,
            'tender_bid_id': self.id,  # Pass the current tender bid record
        })
        # Update tender.bid fields
        self.write({
            'is_rfq_created': True,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': purchase_order.id,
            'target': 'current',
        }

    def action_create_rfqs(self):
        for bid in self:
            if bid.state not in ['done', 'award_letter_sent']:
                raise UserError(
                    "RFQ can only be created if the status is 'Done' or the award letter has been sent.")
            else:
                bid.create_rfq()
        return True

    def action_view_tender(self):
        tender_id = self.tender_id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tender',
            'res_model': 'tender.tender',
            'view_mode': 'form',
            'res_id': tender_id.id,
            'target': 'current',
        }

    def action_view_rfq(self):
        self.ensure_one()  # Ensure this method is called on a single record
        purchase_order = self.env['purchase.order'].search(
            [('tender_bid_id', '=', self.id)], limit=1)
        if purchase_order:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Purchase Order',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': purchase_order.id,
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window_close',
            }


class ComplianceStatus(models.Model):
    """
    Model representing a class of compliance.
    """
    _name = 'res.compliance'
    _description = 'Compliance Status'

    name = fields.Char(string='Compliance Status',
                       help='The name of the Compliance Status')
