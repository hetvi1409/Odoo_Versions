from odoo import models, fields, api
from odoo.exceptions import ValidationError


class UtilityTariff(models.Model):
    _name = "utility.tariff"
    _description = "Utility Tariff Plan"
    _order = "name"

    name = fields.Char(required=True)
    utility_type = fields.Selection(
        [("water", "Water"), ("electricity", "Electricity")],
        required=True, default="water"
    )
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", store=True,
        readonly=True
    )

    fixed_product_id = fields.Many2one(
        "product.product",
        required=True,
        help="Product for the fixed monthly charge/levy (VAT as configured on product)."
    )
    block_ids = fields.One2many(
        "utility.tariff.block", "tariff_id", string="Tariff Blocks", copy=True
    )

    price_includes_tax = fields.Selection(
        [
            ("exclusive", "Tax Excluded"),
            ("inclusive", "Tax Included"),
        ],
        string="Price Includes Tax",
        default="exclusive",
        required=True,
        help="Define whether block prices include VAT or are tax exclusive.",
    )

    # Optional: default tax (for convenience, often 15% in South Africa)
    tax_id = fields.Many2one(
        "account.tax",
        string="Default Tax",
        domain=[("type_tax_use", "=", "sale")],
        help="Default tax to apply to consumption charges if not specified on product.",
    )

    @api.constrains("block_ids")
    def _check_blocks(self):
        """Ensure tariff blocks are ordered and non-overlapping."""
        for plan in self:
            blocks = plan.block_ids.sorted(key=lambda b: b.from_qty)
            last_to = 0.0
            for b in blocks:
                if b.to_qty and b.to_qty <= b.from_qty:
                    raise ValidationError(
                        "In plan '%s': Each block 'To Qty' must be greater than 'From Qty'." % plan.name
                    )
                if b.from_qty < last_to:
                    raise ValidationError(
                        "In plan '%s': Blocks must not overlap and must be in ascending order." % plan.name
                    )
                last_to = b.to_qty or last_to


class UtilityTariffBlock(models.Model):
    _name = "utility.tariff.block"
    _description = "Utility Tariff Block"
    _order = "from_qty asc"

    tariff_id = fields.Many2one("utility.tariff", required=True, ondelete="cascade")
    from_qty = fields.Float(required=True, help="Lower limit (inclusive). Example: 0 for first block.")
    to_qty = fields.Float(help="Upper limit (exclusive). Leave empty for unlimited upper range.")
    price_per_unit = fields.Monetary(required=True, help="Price per kL or kWh in this block.")
    currency_id = fields.Many2one(related="tariff_id.currency_id", store=True, readonly=True)
