from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HelpdeskTickets(models.Model):
    """Helpdesk Tickets"""
    _inherit = "helpdesk.ticket"

    category_id = fields.Many2one('helpdesk.category', string="Category", domain="[('team_id', '=', team_id)]")
    sub_category_id = fields.Many2one('helpdesk.sub.category', string="Sub Category",
                                      domain="[('category_id', '=', category_id)]")

    # Helpdesk Ticket web form validation code
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            team_id = vals.get('team_id')
            email = vals.get('partner_email', '')

            if team_id:
                team = self.env['helpdesk.team'].browse(team_id)

                if team.name == 'I.T Support':
                    if not email or not email.endswith('@jhbproperty.co.za'):
                        raise ValidationError(
                            _("Only company emails ending with '@jhbproperty.co.za' can submit I.T Support tickets.")
                        )

                    employee = self.env['hr.employee'].search(
                        [('work_email', '=', email)],
                        limit=1
                    )
                    if not employee:
                        raise ValidationError(
                            _("No employee found with this email address.")
                        )

        return super().create(vals_list)


class HelpdeskTeam(models.Model):
    """Helpdesk Tickets"""
    _inherit = "helpdesk.team"

    def action_open_category(self):
        """Open Category"""
        return {
            'name': _('Category'),
            'view_mode': 'list,form',
            'res_model': 'helpdesk.category',
            'type': 'ir.actions.act_window',
            'domain': [('team_id', '=', self.id)],
            'target': 'self',
            'context': {
                'default_team_id': self.id
            },
        }

    def action_open_sub_category(self):
        """Open Category"""
        return {
            'name': _('Sub-Category'),
            'view_mode': 'list,form',
            'res_model': 'helpdesk.sub.category',
            'type': 'ir.actions.act_window',
            'domain': [('team_id', '=', self.id)],
            'target': 'self',
            'context': {
                'default_team_id': self.id
            },
        }

    category_count = fields.Integer(string="Category Count", compute="_compute_category_count")
    sub_category_count = fields.Integer(string="Sub Category Count", compute="_compute_category_count")

    def _compute_category_count(self):
        """Compute Category Count"""
        for rec in self:
            rec.category_count = self.env['helpdesk.category'].search_count([('team_id', '=', rec.id)])
            rec.sub_category_count = self.env['helpdesk.sub.category'].search_count([('team_id', '=', rec.id)])

    # def _ensure_submit_form_view(self):
    #     teams = self.filtered('use_website_helpdesk_form')
    #     if not teams:
    #         return
    #
    #     default_form = self.env.ref('helpdesk_customer_care.ticket_submit_form').sudo().arch
    #     for team in teams:
    #         if not team.website_form_view_id:
    #             xmlid = 'website_helpdesk.team_form_' + str(team.id)
    #             form_template = self.env['ir.ui.view'].sudo().create({
    #                 'type': 'qweb',
    #                 'arch': default_form,
    #                 'name': xmlid,
    #                 'key': xmlid
    #             })
    #             self.env['ir.model.data'].sudo().create({
    #                 'module': 'website_helpdesk',
    #                 'name': xmlid.split('.')[1],
    #                 'model': 'ir.ui.view',
    #                 'res_id': form_template.id,
    #                 'noupdate': True
    #             })
    #             team.website_form_view_id = form_template.id
    #         else:
    #             xmlid = 'website_helpdesk.team_form_' + str(team.id)
    #             view = self.env['ir.ui.view'].sudo().search([('name', '=', xmlid)])
    #
    #             view.sudo().write({'arch': default_form,})
