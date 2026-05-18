from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class MachineryComponent(models.Model):
    _name = 'machinery.component'
    _description = 'Machinery Component'
    _rec_name = 'name'

    product_cost_split_ids = fields.One2many('product.cost.split', 'machine', string='Cost Splits')
    split_count = fields.Integer(string="Cost Split Count", compute="_compute_split_count", store=True)

    name = fields.Char(string='Component Name', required=True)
    default_code = fields.Char(string='Code', required=True, copy=False)
    serial_number = fields.Char(string='Serial Number')
    component_type = fields.Selection([
        ('electrical', 'Electrical'),
        ('mechanical', 'Mechanical'),
        ('hydraulic', 'Hydraulic'),
        ('pneumatic', 'Pneumatic'),
        ('software', 'Software'),
        ('other', 'Other'),
    ], string='Type', required=True)

    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer', domain=[('is_company', '=', True)])
    product_ids = fields.Many2many('product.product', string='Produced Products')
    cos_account_ids = fields.Many2many(
        'account.account',
        'machinery_component_cos_account_rel',
        'component_id',
        'account_id',
        string='COS Accounts',
        domain=[('account_type', '=', 'expense_direct_cost')]
    )

    income_account_ids = fields.Many2many(
        'account.account',
        'machinery_component_income_account_rel',
        'component_id',
        'account_id',
        string='Income Accounts',
        domain=[('account_type', '=', 'income')]
    )
    purchase_date = fields.Date(string='Purchase Date')
    warranty_expiry = fields.Date(string='Warranty Expiry')
    status = fields.Selection([
        ('new', 'New'),
        ('in_use', 'In Use'),
        ('faulty', 'Faulty'),
        ('replaced', 'Replaced'),
        ('disposed', 'Disposed'),
    ], string='Status', default='new')

    location = fields.Char(string='Current Location')
    notes = fields.Text(string='Notes')

    @api.constrains('default_code')
    def _check_unique_component_code(self):
        for rec in self:
            if self.search_count([('default_code', '=', rec.default_code)]) > 1:
                raise ValidationError("Component Code must be unique!")

    @api.depends('product_cost_split_ids')
    def _compute_split_count(self):
        for record in self:
            record.split_count = len(record.product_cost_split_ids)

    def action_view_product_cost_splits(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Cost Splits',
            'res_model': 'product.cost.split',
            'view_mode': 'list',
            'domain': [('machine', '=', self.id)],
            'context': {'default_machine': self.id},
        }

    def create_product_cost_splits(self):
        """
        Create product.cost.split records for each product in product_ids.
        Then create corresponding product.cost.split.line for each account in cos_account_ids.
        Avoid creating duplicates for existing products.
        """
        # Retrieve the mapping from ir.config_parameter
        mapping = self._get_product_cos_account_mapping()
    
        if not mapping:
            raise ValidationError("Account to product mapping is not configured.")
    
        # Loop through all products associated with the machinery component
        for product in self.product_ids:
            # Check if a product.cost.split already exists for this product and machinery component
            existing_split = self.env['product.cost.split'].search([
                ('main_product_id', '=', product.id),
                ('machine', '=', self.id)
            ], limit=1)
    
            if existing_split:
                _logger.info(f"Skipping creation of product.cost.split for {product.name} as it already exists.")
                continue  # Skip creating a new split if it already exists
    
            # Create the product.cost.split record since it does not exist
            product_cost_split = self.env['product.cost.split'].create({
                'main_product_id': product.id,
                'machine': self.id,
                'line_ids': []  # Will be populated with lines later
            })
    
            # Collect all the accounts based on the mapping for this product
            account_ids = {}
    
            # Now create product.cost.split.line records for each account in cos_account_ids
            for account in self.cos_account_ids:
                # Get the account code
                account_code = account.account_code
    
                if account_code in mapping:
                    # Find the corresponding component_product_id
                    component_product_id = mapping[account_code]
    
                    # If we have not added this line yet for the component_product_id, initialize it
                    if component_product_id not in account_ids:
                        account_ids[component_product_id] = {
                            'component_product_id': component_product_id,
                            'account_ids': [],
                        }
    
                    # Add the current account to the list of accounts for this component_product_id
                    account_ids[component_product_id]['account_ids'].append(account.id)
    
            # Create the product.cost.split.line for each component_product_id
            for component_product_id, data in account_ids.items():
                self.env['product.cost.split.line'].create({
                    'split_id': product_cost_split.id,
                    'component_product_id': component_product_id,
                    'amount': 0.0,  # Set the amount (add logic for the amount)
                    'account_id': [(6, 0, data['account_ids'])],  # Use Many2many field for accounts
                })




    def _get_product_cos_account_mapping(self):
        """
        Retrieve the product to account mapping from ir.config_parameter.
        """
        mapping_string = self.env['ir.config_parameter'].sudo().get_param('machinery.component.account_mapping')
        mapping = {}

        if mapping_string:
            # Example: '0010': 1164, '0020': 1166, ...
            mapping = dict(tuple(entry.split(':')) for entry in mapping_string.split(','))
            mapping = {key.strip(): int(value.strip()) for key, value in mapping.items()}
        
        return mapping
