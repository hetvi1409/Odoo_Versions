# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self,vals):
        record = super(SaleOrder,self).create(vals)
        if record.partner_id:
            if record.partner_id.credit_limit:
                credit_limit = record.partner_id.credit_limit
                total_amount = record.amount_total
                total_due = record.partner_id.get_total_due()
                if total_due + total_amount > credit_limit:
                    raise UserError(
                        f"Credit limit exceeded!\n"
                        f"Limit: {credit_limit}\n"
                        f"Due: {total_due}\n"
                        f"Current Order: {total_amount}"
                    )
                else:
                    pass
            else:
                pass
        return record

    def write(self,vals):
        for res in self:
            if res.state != 'sale':
                if res.partner_id.credit_limit:
                    credit_limit = res.partner_id.credit_limit
                    total_amount = res.amount_total
                    total_due = res.partner_id.get_total_due()
                    if total_due + total_amount > credit_limit:
                        if self.env.user.has_group('credit_limit_control.group_sales_manager'):
                            pass
                        else:
                            raise UserError(
                                f"Credit limit exceeded!\n"
                                f"Limit: {credit_limit}\n"
                                f"Due: {total_due}\n"
                                f"Current Order: {total_amount}"
                            )
                    else:
                        pass
                else:
                    pass

        return super(SaleOrder,self).write(vals)