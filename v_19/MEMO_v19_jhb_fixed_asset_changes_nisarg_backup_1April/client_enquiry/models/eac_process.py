from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EACProcess(models.Model):
    """EAC Process 2"""
    _name = 'eac.process'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'


    name = fields.Char(string="Name", copy=False)
    enquiry_id = fields.Many2one('client.enquiry', string="Enquiry")
    assessment_id = fields.Many2one('enquiry.assessment', string="Assessment")
    property_id = fields.Many2one('building', string="Property", required=True)
    valuation_id = fields.Many2one('assessment.valuation', string="Valuation")
    address = fields.Char(string="Address")
    jmc_number = fields.Char(string="JMC Number")
    stand_number = fields.Char(string="Stand Number")
    circulation_id = fields.Many2one('circulation.comments', string="Circulation Comments")
    transaction_id = fields.Many2one('client.transaction',)
    user_id = fields.Many2one('res.users', string='Assignee')

    state = fields.Selection([('draft', 'Draft'),
                              ('eac_meeting', 'EAC Committee'),
                              ('eac_approve', 'EAC Approve'),
                              ('approve', 'Approve'),
                              ], default='draft')
    last_stage_updated = fields.Datetime('Last Stage Updated', readonly=True)

    transaction_attachment_ids = fields.Many2many('ir.attachment',
                                                  string="Transaction Documents")
    eac_committee_id = fields.Many2one("calendar.event", string="JPC EAC Committee")
    eac_attachment_ids = fields.Many2many('ir.attachment', 'eac_attachment_rel',
                                                  string="EAC Documents")
    eac_comments = fields.Char(string="EAC Comments")
    review_comments = fields.Char(string="Review Comments")


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'eac.process'
            vals['name'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
            vals['last_stage_updated'] = fields.Datetime.now()
        res = super(EACProcess, self).create(vals_list)
        res.last_stage_updated = fields.Datetime.now()
        return res


    @api.onchange('transaction_id')
    def _onchange_valuation(self):
        """Change of valuation"""
        self.valuation_id = self.transaction_id.valuation_id.id
        self.property_id = self.transaction_id.property_id.id
        self.enquiry_id = self.transaction_id.enquiry_id.id
        self.assessment_id = self.transaction_id.assessment_id.id
        self.circulation_id = self.transaction_id.circulation_id.id
        self.address = self.transaction_id.address
        self.jmc_number = self.transaction_id.jmc_number
        self.stand_number = self.transaction_id.stand_number
        self.transaction_attachment_ids = self.transaction_id.transaction_attachment_ids

    def create_eac_meeting(self):
        """Create a new eac_meeting"""
        eac_committee_id = self.env['calendar.event'].create({
            'name': 'JPC EAC',
            'res_model': self._name,
            'res_id': self.id,
        })
        self.eac_committee_id = eac_committee_id.id

    def action_approve_eac_meeting(self):
        """Approve a new eac_meeting"""
        return {
            'name': _('Approve'),
            'view_mode': 'form',
            'res_model': 'eac.review',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_eac_id': self.id,
                'default_type': 'approve'
            }
        }

    def action_refuse_eac_meeting(self):
        """Approve a new eac_meeting"""
        return {
            'name': _('Refuse'),
            'view_mode': 'form',
            'res_model': 'eac.review',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_eac_id': self.id,
                'default_type': 'refuse'
            }
        }
    def action_approve(self):
        """Approve a new eac_meeting"""
        return {
            'name': _('Approve'),
            'view_mode': 'form',
            'res_model': 'eac.review',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_eac_id': self.id,
                'default_types': 'approve'
            }
        }

    def action_refuse(self):
        """Approve a new eac_meeting"""
        return {
            'name': _('Refuse'),
            'view_mode': 'form',
            'res_model': 'eac.review',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_eac_id': self.id,
                'default_types': 'refuse'
            }
        }

    def action_create_eac_meeting(self):
        """Create EAC Meeting"""
        self.state = 'eac_meeting'
        self.create_eac_meeting()

    def action_view_eac_meeting(self):
        """View assessment valuation"""
        meeting = self.eac_committee_id
        action = {
            'name': _('Meeting'),
            'type': 'ir.actions.act_window',
            'res_model': meeting._name,
            'context': {'create': False},
            'view_mode': 'form',
            'target' : 'new',
            'res_id': meeting.id,
            }
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

