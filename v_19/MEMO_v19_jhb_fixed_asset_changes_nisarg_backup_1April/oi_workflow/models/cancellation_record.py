from odoo import models, fields, api, _


class CancellationRecord(models.Model):
    _name = 'cancellation.record'
    _description = 'Cancellation Record Workflow Log'
    _inherit = ['approval.record', 'mail.thread', 'mail.activity.mixin']
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.model
    def _create_approval_settings(self):
        return
        # model_id = self.env['ir.model']._get_id('approval.record')
        # record = self.env['approval.settings'].search([('model_id', '=', model_id)])
        # if model_id and not record:
        #     record = self.env['approval.settings'].create({
        #         'model_id': model_id,
        #     })
        # if record:
        #     record.with_context(is_approval_setting=False)._create_external_id()

    name = fields.Char(string='Number', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    requester_id = fields.Many2one('res.users', string='Requester')
    model_id = fields.Many2one('ir.model', string='Object', required=True, ondelete='cascade')
    record_id = fields.Integer(required=True, string='Record ID')
    model_name = fields.Char(string='Model Name')
    rec_ref = fields.Char(compute='_calc_rec_ref', string='Record Reference')
    reason = fields.Text(string='Reason')

    def _calc_rec_ref(self):
        for record in self:
            ref = ''
            if record.record_id and record.model_id:
                rec = record.get_record()
                if rec.exists():
                    ref = "%s,%s" % (record.model_id.model, record.record_id)
            record.rec_ref = ref

    def get_record(self):
        return self.env[self.model_id.model].browse(self.record_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or not vals['name']:
                vals['name'] = self.env['ir.sequence'].next_by_code(self._name)
            # Auto-set model_id if not provided (example: from context)
            if 'model_id' not in vals and 'model_name' in vals:
                model = self.env['ir.model'].search([('model', '=', vals['model_name'])], limit=1)
                if model:
                    vals['model_id'] = model.id
        return super().create(vals_list)

    def _on_approve(self):
        rec = self.get_record()
        cancel_state = rec._on_cancel()
        if cancel_state:
            rec.write({'state': cancel_state})
        super()._on_approve()
