from odoo import api, fields, models, _


class HrReferralSendMail(models.TransientModel):
    _inherit = 'hr.referral.send.mail'

    @api.depends('job_id', 'url')
    def _compute_body_html(self):
        for wizard in self:
            wizard.body_html = _('Hello,<br><br>Kindly visit the CEF intranet and/or the website for the currently advertised job opportunities within the Company.<br><br>If interested, please click here to apply.<br><br>Best wishes to those interested in the opportunities.<br><br><a href="%s">See Job Offers</a>', wizard.url)
