from odoo import fields, models,_


class ContractMonitoringChecklist(models.Model):
    _name = 'contract.monitoring.checklist'
    _description = 'Contract Monitoring Checklist'

    contract_id = fields.Many2one('xf.partner.contract')
    item = fields.Char('Checklist Item', required=True)
    compliance_status = fields.Selection([
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('na', 'N/A')],
        string='Status')
    comments = fields.Text('Comments')



class ContractMonitoringReport(models.Model):
    _name = 'contract.monitoring.report'
    _description = 'Contract Monitoring Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'contract_id'

    contract_id = fields.Many2one('xf.partner.contract', required=True)
    company_id = fields.Many2one(
        'res.company',
        related='contract_id.company_id',
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='contract_id.partner_id',
        store=True,
        readonly=True,
    )
    date = fields.Date('Report Date', default=fields.Date.today())
    user_id = fields.Many2one('res.users', 'Responsible',
                              default=lambda self: self.env.user)
    findings = fields.Text('Findings')
    actions_taken = fields.Text('Actions Taken')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request_terminated', 'Request for Termination'),
        ('approve', 'Approved'), ('rejected', 'Rejected'),
    ],
        default='draft')

    def process_non_compliance(self):
        self.ensure_one()
        if self.contract_id:
            template = self.env.ref('xf_partner_contract_management.email_template_non_compliance')
            # self.contract_id.message_post_with_template(template.id)
            template.send_mail(self.id, force_send=True,
                                    )
            self.contract_id.message_post(body="Non-Complaince was created: %s" % (self.contract_id.name))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {

                'title': 'Non-Compliance Processed',
                'message': 'The service provider has been notified.',
                'sticky': False,
                'type': 'success',
            }
        }

    def action_approval_termination(self):
        """Request for termination approval"""
        self.state = 'request_terminated'
        self.contract_id.message_post(body="Termination approval request was created: %s" % (self.contract_id.name))
        self.message_post(body="Termination approval request was created: %s" % (self.contract_id.name))
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract_approval_termination')
        template.send_mail(self.contract_id.id, force_send=True,)

    def action_approve(self):
        """Action approve"""
        self.state = 'approve'
        self.contract_id.message_post(body="Approved the terminated requested: %s" % (self.contract_id.name))
        self.message_post(body="Approved the terminated requested: %s" % (self.contract_id.name))
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract_approval_termination')
        template.send_mail(self.contract_id.id, force_send=True, )

    def action_refuse(self):
        """Action approve"""
        self.state = 'rejected'
        self.contract_id.message_post(body="Refused the terminated requested: %s" % (self.contract_id.name))
        self.message_post(body="Refused the terminated requested: %s" % (self.contract_id.name))
        template = self.env.ref(
            'xf_partner_contract_management.email_template_send_contract_refused_termination')
        template.send_mail(self.contract_id.id, force_send=True, )

    def action_view_contract(self):
        contract = self.contract_id
        action = {
            'name': _('Contract Monitoring'),
            'type': 'ir.actions.act_window',
            'res_model': contract._name,
            'context': {'create': False},
        }
        if len(contract) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': contract.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', contract.ids)],
            })
        return action

    def action_send_terminated_mail(self):
        """Share Meeting of minutes"""

        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup(
                'xf_partner_contract_management.email_template_send_contract_approval_termination')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                'mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': self.contract_id._name,
            'default_res_ids': self.contract_id.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        action = {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        return action
