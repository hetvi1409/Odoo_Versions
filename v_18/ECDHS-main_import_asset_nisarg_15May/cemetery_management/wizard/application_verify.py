from odoo import fields, models, _


class ApplicationVerify(models.Model):
    """Verify the record"""
    _name = 'application.verify'
    _description = "Application Verify"

    application_id = fields.Many2one('cemetery.application', string="Application")
    is_completed_accurate = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                             string="Is the application "
                                                    "complete and accurate",
                                             required=True)
    comments = fields.Char(string="Comment", required=True)

    def action_submit(self):
        """Submit the application"""
        if self.is_completed_accurate == 'yes':
            self.state = 'verified'
            self.application_id.message_post(body=_("The Application was verified "))
            self.application_id.message_post(body=_("Verified Comments: " + self.comments))
        else:
            self.state = 'draft'
            self.application_id.message_post(body=_("The Application was not verified, Please recheck the application."))
            self.application_id.message_post(body=_("Verified Comments: " + self.comments))
