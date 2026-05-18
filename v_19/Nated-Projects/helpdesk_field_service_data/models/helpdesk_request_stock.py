from odoo import api, fields, models, _


class HelpdeskRequestStock(models.Model):
    """Helpdesk request stock"""
    _name = "helpdesk.request.stock"
    _description = "Helpdesk Request Stock"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name of the request stock", default="New")
    ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket",
                                required=True)
    partner_id = fields.Many2one('res.partner', string="Contact")
    picking_type_id = fields.Many2one('stock.picking.type', required=True,
                                      domain="[('code', '=', 'internal')]",
                                      string="Picking Type")
    location_id = fields.Many2one('stock.location', string="Source Location",
                                  required=True,
                                  domain="[('company_id', 'in', [company_id, False])]")
    destination_id = fields.Many2one('stock.location',
                                     string="Destination Location",
                                     required=True,
                                     domain="[('company_id', 'in', [company_id, False])]")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'),
                              ('confirm', 'Confirm'), ('cancel', 'Cancel')],
                             default='draft', tracking=True)
    picking_id = fields.Many2one('stock.picking')

    @api.model
    def create(self, vals):
        """generate request stock sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'helpdesk.request.stock') or 'New'
        result = super(HelpdeskRequestStock, self).create(vals)
        ticket = self.env['helpdesk.ticket'].browse(int(vals['ticket_id']))
        ticket.stock_request_ids = [(4, result.id)]
        return result

    def action_submit(self):
        """Method For submitting the stock request"""
        self.state = 'submit'
        msg = _('%s: Stock request for the ticket %s is submitted') % (
            self.name, self.ticket_id.name)
        self.ticket_id.message_post(body=msg)

    def action_ticket(self):
        """Open stock requests"""
        return {
            'name': _('Helpdesk Tickets'),
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.ticket_id.id
        }

    def action_picking(self):
        """Open stock requests"""
        return {
            'name': _('Helpdesk Tickets'),
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.picking_id.id
        }

    def action_confirm(self):
        """Method For Conforming the stock request"""
        self.state = 'confirm'
        msg = _('%s: Stock request for the ticket %s is Confirmed') % (
            self.name, self.ticket_id.name)
        self.ticket_id.message_post(body=msg)
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.destination_id.id,
            'origin': self.ticket_id.name
        })
        self.picking_id = picking.id

    def action_cancel(self):
        """Method For Conforming the stock request"""
        self.state = 'cancel'
        msg = _('%s: Stock request for the ticket %s is Cancel') % (
            self.name, self.ticket_id.name)
        self.ticket_id.message_post(body=msg)
