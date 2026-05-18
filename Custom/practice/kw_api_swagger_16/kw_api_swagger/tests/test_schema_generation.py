from odoo.tests import tagged, TransactionCase
from odoo.addons.kw_api_swagger.controllers.main import SwaggerController


@tagged('post_install', '-at_install')
class TestSchemaGeneration(TransactionCase):
    """Test schema generation from Odoo field types"""

    def setUp(self):
        super().setUp()
        self.controller = SwaggerController()

    def test_char_field_schema(self):
        """Test schema generation for char field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_char',
            'field_description': 'Test Char',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'char',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(schema['type'], 'string', 'Char should map to string')
        self.assertIn('example', schema, 'Schema should have example')

    def test_text_field_schema(self):
        """Test schema generation for text field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_text',
            'field_description': 'Test Text',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'text',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(schema['type'], 'string', 'Text should map to string')

    def test_integer_field_schema(self):
        """Test schema generation for integer field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_integer',
            'field_description': 'Test Integer',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'integer',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(
            schema['type'], 'integer',
            'Integer should map to integer'
        )
        self.assertIsInstance(
            schema['example'], int,
            'Integer example should be int type'
        )

    def test_float_field_schema(self):
        """Test schema generation for float field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_float',
            'field_description': 'Test Float',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'float',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(
            schema['type'], 'number', 'Float should map to number'
        )
        self.assertEqual(
            schema['format'], 'float',
            'Float should have float format'
        )
        self.assertIsInstance(
            schema['example'], float,
            'Float example should be float type'
        )

    def test_boolean_field_schema(self):
        """Test schema generation for boolean field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_boolean',
            'field_description': 'Test Boolean',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'boolean',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(
            schema['type'], 'boolean',
            'Boolean should map to boolean'
        )
        self.assertIsInstance(
            schema['example'], bool,
            'Boolean example should be bool type'
        )

    def test_date_field_schema(self):
        """Test schema generation for date field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_date',
            'field_description': 'Test Date',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'date',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(schema['type'], 'string', 'Date should map to string')
        self.assertEqual(
            schema['format'], 'date',
            'Date should have date format'
        )
        self.assertIn('example', schema, 'Date should have example')
        # Check example format (YYYY-MM-DD)
        example = schema['example']
        self.assertRegex(
            example, r'^\d{4}-\d{2}-\d{2}$',
            'Date example should be in YYYY-MM-DD format'
        )

    def test_datetime_field_schema(self):
        """Test schema generation for datetime field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_datetime',
            'field_description': 'Test Datetime',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'datetime',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(
            schema['type'], 'string',
            'Datetime should map to string'
        )
        self.assertEqual(
            schema['format'], 'date-time',
            'Datetime should have date-time format'
        )
        self.assertIn('example', schema, 'Datetime should have example')

    def test_many2one_field_schema(self):
        """Test schema generation for many2one field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_many2one',
            'field_description': 'Test Many2one',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'many2one',
            'relation': 'res.country',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(
            schema['type'], 'integer',
            'Many2one should map to integer (ID)'
        )
        self.assertIsInstance(
            schema['example'], int,
            'Many2one example should be int'
        )

    def test_selection_field_schema(self):
        """Test schema generation for selection field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_selection',
            'field_description': 'Test Selection',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'selection',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(
            schema['type'], 'string',
            'Selection should map to string'
        )
        self.assertIn('example', schema, 'Selection should have example')

    def test_one2many_field_schema(self):
        """Test schema generation for one2many field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_one2many',
            'field_description': 'Test One2many',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'one2many',
            'relation': 'res.partner.bank',
            'relation_field': 'partner_id',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(schema['type'], 'array', 'One2many should be array')
        self.assertIn('items', schema, 'Array should have items definition')
        self.assertEqual(
            schema['items']['type'], 'object',
            'Array items should be objects'
        )
        self.assertIn(
            'example', schema,
            'One2many should have example array'
        )
        self.assertIsInstance(
            schema['example'], list,
            'Example should be a list'
        )

    def test_many2many_field_schema(self):
        """Test schema generation for many2many field"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_many2many',
            'field_description': 'Test Many2many',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'many2many',
            'relation': 'res.partner.category',
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(
            schema['type'], 'array',
            'Many2many should be array'
        )
        self.assertIn('items', schema, 'Array should have items definition')
        self.assertEqual(
            schema['items']['type'], 'object',
            'Array items should be objects'
        )
        self.assertIn(
            'example', schema,
            'Many2many should have example array'
        )

    def test_unknown_field_type_fallback(self):
        """Test that unknown field types fallback to string"""
        field = self.env['ir.model.fields'].create({
            'name': 'x_test_unknown',
            'field_description': 'Test Unknown',
            'model_id': self.env.ref('base.model_res_partner').id,
            'ttype': 'binary',  # Using binary as an "unsupported" type
            'state': 'manual',
        })

        schema = self.controller.get_field_input_schema(field)

        self.assertEqual(
            schema['type'], 'string',
            'Unknown types should fallback to string'
        )
        self.assertIn('example', schema, 'Should have example')

    def test_schema_from_fields_generates_properties(self):
        """Test field schema has proper structure"""
        # Test individual field schemas directly
        # (The generate_swagger_schema_from_fields uses request object
        # which is not available in unit tests, so we test the
        # underlying get_field_input_schema method instead)

        # Test that char field generates proper schema
        field = self.env['ir.model.fields'].search([
            ('model', '=', 'res.partner'),
            ('name', '=', 'name'),
        ], limit=1)

        if field:
            schema = self.controller.get_field_input_schema(field)
            self.assertIsInstance(
                schema, dict,
                'Should return a dictionary'
            )
            self.assertIn(
                'type', schema,
                'Schema should have type'
            )
            self.assertIn(
                'example', schema,
                'Schema should have example'
            )

        # Test email field
        email_field = self.env['ir.model.fields'].search([
            ('model', '=', 'res.partner'),
            ('name', '=', 'email'),
        ], limit=1)

        if email_field:
            schema = self.controller.get_field_input_schema(email_field)
            self.assertEqual(
                schema['type'], 'string',
                'Email should be string type'
            )
