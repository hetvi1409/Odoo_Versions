from odoo.tests.common import TransactionCase
from odoo.addons.kw_mixin.models.alphabet_sorted_mixin import (
    alphabet_sorted, ALPHABETS
)


class TestAlphabetSortedMixin(TransactionCase):

    def setUp(self):
        super().setUp()
        self.mixin_model = self.env['kw.alphabet.sorted.mixin']

    def test_function_alphabet_sorted_default_sort(self):
        test_data = [
            {'name': 'zebra', 'id': 1},
            {'name': 'apple', 'id': 2},
            {'name': 'banana', 'id': 3}
        ]
        result = alphabet_sorted(test_data, 'name')
        expected_names = ['apple', 'banana', 'zebra']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_function_alphabet_sorted_unsupported_alphabet(self):
        test_data = [
            {'name': 'zebra', 'id': 1},
            {'name': 'apple', 'id': 2}
        ]
        result = alphabet_sorted(test_data, 'name', alphabet='unsupported')
        expected_names = ['apple', 'zebra']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_function_alphabet_sorted_russian_alphabet(self):
        test_data = [
            {'name': 'яблоко', 'id': 1},
            {'name': 'апельсин', 'id': 2},
            {'name': 'банан', 'id': 3}
        ]
        result = alphabet_sorted(test_data, 'name', alphabet='ru')
        expected_names = ['апельсин', 'банан', 'яблоко']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_function_alphabet_sorted_ukrainian_alphabet_ua(self):
        test_data = [
            {'name': 'яблуко', 'id': 1},
            {'name': 'апельсин', 'id': 2},
            {'name': 'банан', 'id': 3},
            {'name': 'ґрунт', 'id': 4}
        ]
        result = alphabet_sorted(test_data, 'name', alphabet='ua')
        expected_names = ['апельсин', 'банан', 'ґрунт', 'яблуко']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_function_alphabet_sorted_ukrainian_alphabet_uk(self):
        test_data = [
            {'name': 'яблуко', 'id': 1},
            {'name': 'апельсин', 'id': 2},
            {'name': 'банан', 'id': 3},
            {'name': 'ґрунт', 'id': 4}
        ]
        result = alphabet_sorted(test_data, 'name', alphabet='uk')
        expected_names = ['апельсин', 'банан', 'ґрунт', 'яблуко']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_function_alphabet_sorted_custom_symbols(self):
        test_data = [
            {'name': 'gamma', 'id': 1},
            {'name': 'alpha', 'id': 2},
            {'name': 'beta', 'id': 3}
        ]
        custom_symbols = 'abcdefghijklmnopqrstuvwxyz'
        result = alphabet_sorted(test_data, 'name', symbols=custom_symbols)
        expected_names = ['alpha', 'beta', 'gamma']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_function_alphabet_sorted_mixed_case(self):
        test_data = [
            {'name': 'Zebra', 'id': 1},
            {'name': 'apple', 'id': 2},
            {'name': 'Banana', 'id': 3}
        ]
        result = alphabet_sorted(test_data, 'name', alphabet='ru')
        self.assertEqual(len(result), 3)

    def test_function_alphabet_sorted_empty_list(self):
        test_data = []
        result = alphabet_sorted(test_data, 'name')
        self.assertEqual(result, [])

    def test_function_alphabet_sorted_single_item(self):
        test_data = [{'name': 'single', 'id': 1}]
        result = alphabet_sorted(test_data, 'name')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'single')

    def test_function_alphabet_sorted_symbols_translation(self):
        test_data = [
            {'name': 'яя', 'id': 1},
            {'name': 'аа', 'id': 2},
        ]
        result = alphabet_sorted(test_data, 'name', alphabet='ru')
        expected_names = ['аа', 'яя']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_mixin_alphabet_sorted_method(self):
        test_data = [
            {'name': 'zebra', 'id': 1},
            {'name': 'apple', 'id': 2},
            {'name': 'banana', 'id': 3}
        ]
        result = self.mixin_model.alphabet_sorted(test_data, 'name')
        expected_names = ['apple', 'banana', 'zebra']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_mixin_alphabet_sorted_method_with_alphabet(self):
        test_data = [
            {'name': 'яблоко', 'id': 1},
            {'name': 'апельсин', 'id': 2},
            {'name': 'банан', 'id': 3}
        ]
        result = self.mixin_model.alphabet_sorted(test_data, 'name',
                                                  alphabet='ru')
        expected_names = ['апельсин', 'банан', 'яблоко']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_mixin_alphabet_sorted_method_with_custom_symbols(self):
        test_data = [
            {'name': 'gamma', 'id': 1},
            {'name': 'alpha', 'id': 2},
            {'name': 'beta', 'id': 3}
        ]
        custom_symbols = 'abcdefghijklmnopqrstuvwxyz'
        result = self.mixin_model.alphabet_sorted(test_data, 'name',
                                                  symbols=custom_symbols)
        expected_names = ['alpha', 'beta', 'gamma']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_alphabets_constants(self):
        self.assertIn('ru', ALPHABETS)
        self.assertIn('ua', ALPHABETS)
        self.assertIn('uk', ALPHABETS)
        self.assertEqual(ALPHABETS['ua'], ALPHABETS['uk'])

    def test_alphabet_sorted_complex_data(self):
        test_data = [
            {'name': 'Company Z', 'id': 1, 'category': 'tech'},
            {'name': 'Company A', 'id': 2, 'category': 'finance'},
            {'name': 'Company M', 'id': 3, 'category': 'retail'}
        ]
        result = alphabet_sorted(test_data, 'name')
        expected_names = ['Company A', 'Company M', 'Company Z']
        self.assertEqual([item['name'] for item in result], expected_names)

    def test_alphabet_sorted_numerical_index_edge_case(self):
        test_data = [
            ['zebra', 1],
            ['apple', 2],
            ['banana', 3]
        ]
        result = alphabet_sorted(test_data, 0)
        expected_names = ['apple', 'banana', 'zebra']
        self.assertEqual([item[0] for item in result], expected_names)
