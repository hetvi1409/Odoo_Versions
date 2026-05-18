from odoo import fields, models, _
from odoo.exceptions import UserError


class crmLlead2opportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    property_enquiry = fields.Selection([('completed', 'Completed'), ('not_completed', 'Not Completed')], string="Is Enquiry Completed")

    def action_apply(self):
        print(self.property_enquiry)
        if not self.property_enquiry:
            raise UserError('Is Enquiry completed?')
        else:
            if self.property_enquiry == 'not_completed':
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "crm.lead.comments",
                    "views": [[False, "form"]],
                    "target": 'new',
                    "context": {
                        'default_crm_lead_id': self.lead_id.id,
                    },
                }
        res = super().action_apply()
        return res

class CRMComments(models.TransientModel):
    _name ="crm.lead.comments"

    crm_lead_id = fields.Many2one('crm.lead')
    comments = fields.Text(string="Comments", required=True)

    def action_submit(self):
        self.ensure_one()
        if self.crm_lead_id:
            self.crm_lead_id.message_post(body=f"Comments: {self.comments}")
        return {'type': 'ir.actions.act_window_close'}
