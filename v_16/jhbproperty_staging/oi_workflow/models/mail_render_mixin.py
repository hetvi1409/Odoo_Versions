
from odoo import models, api

class MailRenderMixin(models.AbstractModel):
    _inherit = 'mail.render.mixin'
    
    @api.model
    def _render_template(self, template_src, model, res_ids, engine='inline_template',
                         add_context=None, options=None, post_process=False):
        if model=='approval.record':
            model = self._context.get('active_model')                               
                   
        return super(MailRenderMixin, self)._render_template(template_src, model, res_ids, engine = engine, add_context =add_context, options = options, post_process = post_process)
                    