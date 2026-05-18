from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    x_studio_case = fields.Char('Case')

    def _prepare_stock_lot_values(self):
        self.ensure_one()
        name = self.env['ir.sequence'].next_by_code('stock.lot.serial')
        exist_lot = not name or self.env['stock.lot'].search([
            ('product_id', '=', self.product_id.id),
            '|', ('company_id', '=', False), ('company_id', '=', self.company_id.id),
        ], limit=1)
        date = fields.Datetime.now()
        year = f"{date.year % 100:02d}"
        month = f"{date.month:02d}"
        if year != self.bom_id.year_sequence:
            self.bom_id.year_sequence = year
        if month != self.bom_id.month_sequence:
            self.bom_id.month_sequence = month
            self.bom_id.last_sequence = "00"

        code = self.product_id.default_code or "XXXX"

        code = code.split('-', 1)[1] if '-' in code else code
        sequence_code = str(int(self.bom_id.last_sequence) + 1)

        name = f"{self.bom_id.year_sequence}{self.bom_id.month_sequence}{code}{sequence_code}"
        exist_lot = not name or self.env['stock.lot'].search([
            ('product_id', '=', self.product_id.id), ('name', '=', name),
            '|', ('company_id', '=', False),
            ('company_id', '=', self.company_id.id),
        ], limit=1)
        self.bom_id.last_sequence = sequence_code

        if exist_lot:
            sequence_code = str(int(self.bom_id.last_sequence) + 1)

            name = f"{self.bom_id.year_sequence}{self.bom_id.month_sequence}{code}{sequence_code}"

        # if exist_lot:
        #     name = self.env['stock.lot']._get_next_serial(self.company_id, self.product_id)
        # else:
        #     date = self.date_start
        #     year = f"{date.year % 100:02d}"
        #     month = f"{date.month:02d}"
        #
        #     code = self.product_id.default_code or "XXXX"
        #
        #     code = code.split('-', 1)[1] if '-' in code else code
        #
        #     name = f"{year}{month}{code}01"
        if not name:
            raise UserError(_("Please set the first Serial Number or a default sequence"))
        return {
            'product_id': self.product_id.id,
            'name': name,
        }

    def action_mark_as_done(self):
        records = self.env['mrp.production'].browse(self._context.get('active_ids', []))
        if records:
            res = records.filtered(lambda mo: mo.state in {'confirmed', 'to_close', 'progress'}).button_mark_done()
            if res is not True:
                action = res
