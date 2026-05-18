from odoo import fields, models, api, _
from collections import defaultdict, deque
from odoo.tools import OrderedSet
from odoo.exceptions import UserError
import re

import logging

_logger = logging.getLogger(__name__)

_logger.critical("🚨 mrp.batch.produce override FILE LOADED")

class MrpBatchProduct(models.TransientModel):
    _inherit = 'mrp.batch.produce'

    @api.depends('production_id')
    def _compute_lot_name(self):
        for wizard in self:
            if wizard.lot_name:
                continue
            wizard.lot_name = self.production_id.lot_producing_id.name
            if not wizard.lot_name:
                company = self.production_id.company_id
                product = self.production_id.product_id
                last_serial = self.env['stock.lot'].search(
                    ['|', ('company_id', '=', company.id),
                     ('company_id', '=', False),
                     ('product_id', '=', product.id)],
                    limit=1, order='id DESC')
                # if last_serial:
                #     wizard.lot_name = self.env['stock.lot']._get_next_serial(self.production_id.company_id, self.production_id.product_id)
                # else:
                date = fields.Datetime.now()
                year = f"{date.year % 100:02d}"
                month = f"{date.month:02d}"
                if year != wizard.production_id.bom_id.year_sequence:
                    wizard.production_id.bom_id.year_sequence = year
                if month != wizard.production_id.bom_id.month_sequence:
                    wizard.production_id.bom_id.month_sequence = month
                    wizard.production_id.bom_id.last_sequence = "00"

                code = wizard.production_id.product_id.default_code or "XXXX"

                code = code.split('-', 1)[1] if '-' in code else code
                sequence_code = str(int(wizard.production_id.bom_id.last_sequence) + 1)

                wizard.lot_name = f"{wizard.production_id.bom_id.year_sequence}{wizard.production_id.bom_id.month_sequence}{code}{sequence_code}"

    def _production_text_to_object(self, mark_done=False):
        self.ensure_one()

        if not self.production_text:
            raise UserError(_("Please specify the serial number you would like to use."))

        production = self.production_id
        product = production.product_id

        serials = []
        for line in self.production_text.splitlines():
            line = line.strip()
            if not line:
                continue
            serial = line.split(self.component_separator)[0]
            serials.append(serial)

        duplicates = [s for s in serials if serials.count(s) > 1]
        if duplicates:
            raise UserError(_("Duplicate serials in input:\n%s") % "\n".join(set(duplicates)))

        result = super()._production_text_to_object(mark_done=mark_done)

        last_line = [line for line in self.production_text.splitlines() if line][-1]

        product_code = product.default_code or "XXXX"
        product_code = product_code.split('-', 1)[1] if '-' in product_code else product_code

        year = last_line[:2]
        month = last_line[2:4]
        code_len = len(product_code)
        sequence = last_line[4 + code_len:]

        production.bom_id.write({
            'year_sequence': year,
            'month_sequence': month,
            'last_sequence': sequence
        })

        return result

    @api.model
    def default_get(self, fields_list):
        _logger.info('DEFAULT GET CALLED')
        res = super().default_get(fields_list)

        production_id = self.env.context.get('default_production_id')
        if not production_id:
            return res

        production = self.env['mrp.production'].browse(production_id)

        if production.product_tracking == 'serial':
            if production.lot_producing_id:
                res['lot_name'] = production.lot_producing_id.name
                return res

            next_serial = self._get_next_serial_for_product(production.product_id)

            if not next_serial:
                raise UserError(_("Unable to generate serial number for product %s") % production.product_id.display_name)

            res['lot_name'] = next_serial

        return res

    def _get_next_serial_for_product(self, product):
        StockLot = self.env['stock.lot']

        last_lot = StockLot.search(
            [('product_id', '=', product.id)],
            order='id desc',
            limit=1
        )

        if not last_lot:
            return product.default_code and f"{product.default_code}0001" or "SN0001"

        base = last_lot.name

        match = re.search(r'(\d+)$', base)
        if not match:
            return base + "1"

        number = match.group(1)
        prefix = base[:-len(number)]
        next_number = int(number)

        while True:
            next_number += 1
            new_serial = f"{prefix}{str(next_number).zfill(len(number))}"

            exists = StockLot.search_count([
                ('name', '=', new_serial),
                ('product_id', '=', product.id),
                ('company_id', 'in', [self.env.company.id, False])
            ])

            if not exists:
                return new_serial