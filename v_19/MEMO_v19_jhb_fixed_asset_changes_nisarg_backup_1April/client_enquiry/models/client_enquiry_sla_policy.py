from odoo import api, fields, models


class ClientEnquirySlaPolicy(models.Model):
    """"Client Enquiry SLA Policy"""
    _inherit = 'client.enquiry.sla.policy'

    process_status = fields.Selection([
        ('assessment', 'Assessment'),
        ('sent_for_comments', 'Sent for Comments'),
        ('ptob', 'PTOB'),
        ('valuation', 'Valuation'),
        ('transaction', 'Transaction'),
        ('eac', 'EAC'),
        ('legal', 'Legal'),
        ('property_intelligence', 'Property Intelligence'),
        ('land_regularization', 'Land Regularization'),
        ('enquiry', 'Enquiry')
    ], string='Select Process', copy=False,required=True)

    reached_state_assessment = fields.Selection([('draft', 'In Progress'),
                              ('ownership', 'Assessment Completed'),
                              ('compile', 'Compile Assessment review'),
                              ('objection', 'Objection'),
                              ('negotiation', 'Negotiation'),
                              ('PTOB', 'PTOB'),
                              ('valuation', 'Waiting for Valuation Result'),
                              ('valuation_completed', 'Valuation Completed'),
                              ('terminate', 'Assessment Not Supported'),
                              ('transition', 'Transaction'),
                              ('send_transition', 'Send Transaction'),
                              ('approve', 'Approved'),
                              ('internal_meeting', 'Internal Meeting'),
                              ('internal_meeting_approved', "Board Approved"),
                              ('mayoral_approved', "Mayoral Approved"),
                              ('council_approved', 'Council Approved'),
                              ('technical_growth',
                               'Technical Growth Cluster Approved'),
                              ('sub_mayoral', 'Sub-Mayoral Approved'),
                              ('executive', 'Executive Management Team'),
                              ('council_79_approved', "Council 79 Approved"),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')],
                             default='draft', tracking=True,string='State')

    reached_state_comments = fields.Selection([('draft', 'Draft'), ('send', 'Send for Comments'),
                              ('objection', 'Objection'),
                              ('create_ptob', 'Create PTOB'),
                              ('valuation', 'Valuation'),
                              ('terminate', 'Terminated'), ],
                             default="draft",string='State')

    reached_state_valuations = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'),
                              ('scm', 'SCM'), ('transaction', 'create Transaction'),
                              ('terminate', 'Terminated'),
                              ('transaction_created', 'Transaction'),
                              ],string='State')

    reached_state_transaction = fields.Selection([('draft', 'Enquiry'),
                              ('submit', 'Submitted'),
                              ('assessment', 'Assessment'),
                              ('land_regularisation', 'Land Regularisation'),
                              ('circulation_comments', 'Circulation for Comments'),
                              ('valuation', 'Valuation'),
                              ('transaction', 'Transaction'),
                              ('public_participation', 'Committees'),
                              ('section_advert', 'Section 79 Advert'),
                              ('bide_specification', 'Bid Specification'), ('scm_process', 'SCM Process'),
                              ('legal_agreement', 'Legal Agreements'), ('Take_on', 'Take-On')],string='State')

    reached_state_eac = fields.Selection([('draft', 'Draft'),
                              ('eac_meeting', 'EAC Committee'),
                              ('eac_approve', 'EAC Approve'),
                              ('approve', 'Approve'),
                              ],string='State')

    reached_state_legal = fields.Selection([('draft', 'Draft'),
                              ('assigned', 'Assigned'),
                              ('prepare_task', 'Prepare Task'),
                              ('task', 'Task Created'),
                              ],string='State')

    reached_state_property_intelligence =fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'),
         ('send', 'Investigation'), ('completed', 'Investigation Completed'),
         ('block', 'Block Property'), ('memo', 'Create Memo'), ('feedback', 'Feedback Received'), ('refuse','Refused')], default='draft',
        string='State')

    reached_state_land_regularization = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'),
         ('send', 'Investigation'), ('completed', 'Investigation Completed'),
         ('block', 'Block Property'), ('memo', 'Create Memo'), ('feedback', 'Feedback Received'), ('refuse','Refused')], default='draft',
        string='State')

    reached_state_enquiry = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'),
         ('send', 'Investigation'), ('completed', 'Investigation Completed'),
         ('block', 'Block Property'), ('memo', 'Create Memo'), ('feedback', 'Feedback Received'),
         ('refuse', 'Refused')], default='draft',
        string='State')








