# python
from odoo import models, api

class Message(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        # safe check: use mapping lookup instead of calling the frozendict
        if self.env.context.get('default_parent_id'):
            return super(Message, self.with_context(default_parent_id=None)).create(vals_list)
        return super(Message, self).create(vals_list)
