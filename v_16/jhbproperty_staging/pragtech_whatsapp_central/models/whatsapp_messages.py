import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class WhatsappMessagesHistory(models.Model):
    _name = 'whatsapp.messages.history'
    _description = "Whatsapp Messages History"
    _order = "id desc"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)


class WhatsappHelpdeskMessages(models.Model):
    _name = 'whatsapp.helpdesk.messages'
    _description = "Whatsapp Help Messages"

    # @api.model
    # def default_get(self, fields):
    #     Param = self.env['res.config.settings'].sudo().get_values()
    #     setting_integrators = Param.get('whatsapp_integrators')
    #     res = super(WhatsappHelpdeskMessages, self).default_get(fields)
    #     res['integrators'] = setting_integrators
    #     return res

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    image_1024 = fields.Image("Image 1024")
    parent_id = fields.Many2one('whatsapp.helpdesk.messages', 'Parent')
    action_type_ids = fields.One2many('helpdesk.action.type', 'wht_helpdesk_id')
    child_ids = fields.One2many('whatsapp.helpdesk.messages', 'parent_id', string='Child')
    attachment_ids = fields.Many2many('ir.attachment', 'whatsapp_helpdesk_msg_ir_attachments_rel', 'wizard_id',
                                      'attachment_id', 'Attachments')
    integrators = fields.Selection([
        ('apichat', 'API Chat'),
        ('chatapi', 'Chat API'),
        ('gupshup', 'GupShup API'),
        ('meta', 'Meta'),
    ], string="Integrators")

    _sql_constraints = [
        ('code_parent_uniq', 'unique (code)', 'The code must be unique')]

    def get_formview_action(self, access_uid=None):
        """ Override this method in order to redirect many2one towards the right model depending on access_uid """
        res = super(WhatsappHelpdeskMessages, self).get_formview_action(access_uid=access_uid)
        if access_uid:
            self_sudo = self.with_user(access_uid)
        else:
            self_sudo = self

        if not self_sudo.check_access_rights('read', raise_exception=False):
            res['res_model'] = 'whatsapp.helpdesk.messages'
        return res

    child_all_count = fields.Integer(
        'Indirect Subordinates Count',
        compute='_compute_subordinates', store=False,
        compute_sudo=True)
    subordinate_ids = fields.One2many('whatsapp.helpdesk.messages', string='Subordinates',
                                      compute='_compute_subordinates',
                                      help="Direct and indirect subordinates",
                                      compute_sudo=True)


    def _get_subordinates(self, parents=None):
        """
        Helper function to compute subordinates_ids.
        Get all subordinates (direct and indirect) of an employee.
        An employee can be a manager of his own manager (recursive hierarchy; e.g. the CEO is manager of everyone but is also
        member of the RD department, managed by the CTO itself managed by the CEO).
        In that case, the manager in not counted as a subordinate if it's in the 'parents' set.
        """
        if not parents:
            parents = self.env[self._name]

        indirect_subordinates = self.env[self._name]
        parents |= self
        direct_subordinates = self.child_ids - parents
        child_subordinates = direct_subordinates._get_subordinates(parents=parents) if direct_subordinates else self.browse()
        indirect_subordinates |= child_subordinates
        return indirect_subordinates | direct_subordinates


    @api.depends('child_ids', 'child_ids.child_all_count')
    def _compute_subordinates(self):
        for employee in self:
            employee.subordinate_ids = employee._get_subordinates()
            employee.child_all_count = len(employee.subordinate_ids)


class WhatsappActionType(models.Model):
    _name = 'helpdesk.action.type'
    _description = "Whatsapp Action Type"

    action_type = fields.Selection([
        ('url', 'Send Text'),
        ('send_image', 'Send Image'),
        ('send_video', 'Send Video'),
        ('send_audio', 'Send Audio'),
        ('send_file', 'Send File'),
    ], 'Type', default='url')
    file_data = fields.Binary('File')
    url = fields.Char('URL')
    name = fields.Char('Name', required=True)
    wht_helpdesk_id = fields.Many2one('whatsapp.helpdesk.messages', 'Whatsapp Helpdesk Messages')
