from werkzeug import urls

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    department_id = fields.Many2one('helpdesk.department')
    category_id = fields.Many2one('helpdesk.category',
                                  domain="[('department_id', '=', department_id)]")
    sub_category_id = fields.Many2one('helpdesk.sub.category',
                                      domain="[('category_id', '=', category_id)]")
    operation_area = fields.Char(string="Operation Area")
    date_attended = fields.Date(string="Date Attended")
    date_completed = fields.Date(string="Date Completed")
    location = fields.Char(string="Location")
    comments = fields.Text(string="Comments")
    town = fields.Char(string="Town/Area")
    # assignee_id = fields.Many2one('res.partner', string="Technician")

    is_internal_resolve = fields.Boolean(
        string="Issue will be internal resolve?")
    is_reviewed = fields.Boolean(string="Is reviewed")
    inventory_required = fields.Boolean(string="Inventory is Required?")
    product_id = fields.Many2one('product.template', string="Products")
    qty_available = fields.Boolean(string="Quantity is available")

    stock_request_ids = fields.Many2many('helpdesk.request.stock',
                                         string="Stock Requests")
    stock_request = fields.Boolean(string="Stock Request",
                                   compute='_compute_stock_request')
    stock_request_count = fields.Integer(string="Stock Requests count",
                                         compute="compute_stock_request_count")

    @api.onchange('department_id', 'category_id', 'sub_category_id', 'name')
    def _onchange_department_id(self):
        """Change department, category and sub_category
            autopopulate the name field"""
        name = ""
        if self.department_id:
            name = name + self.department_id.name
        if self.category_id:
            name = name + ':' + self.category_id.name
        if self.sub_category_id:
            name = name + ':' + self.sub_category_id.name
        if self.description:
            name = name + ':' + self.description
        self.name = name

    def action_review_incidents(self):
        """Method for review the incident"""
        return {
            'name': _('Helpdesk review'),
            'view_mode': 'form',
            'res_model': 'helpdesk.review',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_ticket_id': self.id
            }
        }

    def action_inventory_available(self):
        """Method for review the inventory available"""
        if self.product_id:
            if self.product_id.qty_available == 0.0:
                mail_content = _('Hi %s,<br>'
                                 'Quantity not available for your product %s'
                                 ) % \
                               (self.user_id.name, self.product_id.name)
                recipient_ids = self.env.ref('stock.group_stock_manager').users.ids
                main_content = {
                    'subject': _(
                        'Incidents: %s - Quantity not Available' % self.product_id.name),
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    # 'email_to': ticket.user_id.email
                    'recipient_ids': [(6, 0, recipient_ids)]
                }
                mail_id = self.env['mail.mail'].sudo().create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.sudo().send()
                print(mail_id)
                msg = (_('Quantity is not available for the product %s') % self.product_id.name)
                self.message_post(body=msg)
                # raise ValidationError(
                #     _('Quantity is not available for the product %s') % self.product_id.name)
            else:
                self.qty_available = True
        else:
            raise UserError(_("Please add a product"))

    def action_quantity_available_notification(self):
        """Method for review the quantity available and send a notification"""
        tickets = self.env['helpdesk.ticket'].search(
            [('qty_available', '=', False), ('is_reviewed', '=', True)])
        print(tickets, "quantity available")
        for ticket in tickets:
            if ticket.product_id.qty_available != 0.0:
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                Urls = urls.url_join(base_url,
                                     'web#id=%s&model=helpdesk.ticket&view_type=form' % ticket.id)
                mail_content = _('Hi %s,<br>'
                                 'Quantity available for your product %s'
                                 '<div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                                 'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                                 'border-color:#875A7B;text-decoration: none; display: inline-block; '
                                 'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                                 'cursor: pointer; white-space: nowrap; background-image: none; '
                                 'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                                 'View %s</a></div>'
                                 ) % \
                               (self.user_id.name, self.product_id.name, Urls,
                                tickets.name)
                main_content = {
                    'subject': _(
                        'Incidents: %s - Quantity Available' % ticket.name),
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': ticket.user_id.email
                }
                mail_id = self.env['mail.mail'].sudo().create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.sudo().send()

    def action_request_stock(self):
        """Method for requesting the stock"""
        return {
            'name': _('Helpdesk Stock Request'),
            'view_mode': 'form',
            'res_model': 'helpdesk.request.stock',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_ticket_id': self.id
            }
        }

    @api.depends('stock_request_ids')
    def compute_stock_request_count(self):
        """Calculating the request count"""
        for rec in self:
            rec.stock_request_count = len(self.stock_request_ids)

    @api.depends('stock_request_ids', 'qty_available')
    def _compute_stock_request(self):
        for rec in self:
            rec.stock_request = False
            if rec.qty_available:
                if rec.stock_request_ids:
                    state = rec.stock_request_ids.mapped('state')
                    if 'confirm' in state:
                        rec.stock_request = False
                    else:
                        rec.stock_request = True
                else:
                    rec.stock_request = True

    def action_stock_request(self):
        """Open stock requests"""
        if len(self.stock_request_ids) == 1:
            return {
                'name': _('Helpdesk Stock Request'),
                'view_mode': 'form',
                'res_model': 'helpdesk.request.stock',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.stock_request_ids.id
            }
        else:
            return {
                'name': _('Helpdesk Stock Request'),
                'view_mode': 'tree,form',
                'res_model': 'helpdesk.request.stock',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', self.stock_request_ids.ids)]
            }
