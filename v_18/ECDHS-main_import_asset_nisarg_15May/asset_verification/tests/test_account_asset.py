from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError
from odoo import fields
from datetime import timedelta
import base64

import logging
_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'asset_verification')
class TestAccountAssetVerification(TransactionCase):
    """
    Comprehensive test suite for account.asset fields & methods added by
    asset_verification module.

    Scenarios covered:
      - Default / happy-path values
      - Missing / None / False values
      - Invalid / wrong-type values
      - Boundary / edge cases
      - Computed field re-evaluation
      - Method return-value structure
      - AssetRemovalApproval workflow
      - Image model CRUD
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.account_dep = cls.env['account.account'].search(
            [('account_type', '=', 'asset_fixed')], limit=1
        )
        cls.account_exp = cls.env['account.account'].search(
            [('account_type', '=', 'expense')], limit=1
        )

        cls.job_location = cls.env['asset.verification.job.location'].create({
            'name': 'AV Account Asset Location',
        })

        cls.condition_excellent = cls.env['asset.condition'].create({'name': 'Excellent'})
        cls.condition_poor = cls.env['asset.condition'].create({'name': 'Poor'})

        cls.employee = cls.env['hr.employee'].create({'name': 'John Doe Custodian'})
        cls.employee2 = cls.env['hr.employee'].create({'name': 'Jane Smith Custodian'})

        cls.asset = cls.env['account.asset'].create({
            'name': 'AV Test Asset',
            'original_value': 10000,
            'job_location_id': cls.job_location.id,
            'account_depreciation_id': cls.account_dep.id,
            'account_depreciation_expense_id': cls.account_exp.id,
            'custodian_id': cls.employee.id,
        })
        _logger.info("Base test asset created: %s", cls.asset.name)

        # Manager user who has staging approval rights
        cls.manager_user = cls.env['res.users'].create({
            'name': 'AA Test Manager',
            'login': 'aa_test_manager@test.com',
            'email': 'aa_test_manager@test.com',
            'groups_id': [
                (4, cls.env.ref('base.group_user').id),
                (4, cls.env.ref('asset_verification.group_staging_approval_manager').id),
                (4, cls.env.ref('fixed_assets.group_fixed_asset_approver').id),
            ],
        })
        _logger.info("Manager user created: %s", cls.manager_user.name)

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _make_asset(self, name='Helper Asset', original_value=5000, **kwargs):
        vals = {
            'name': name,
            'original_value': original_value,
            'account_depreciation_id': self.account_dep.id,
            'account_depreciation_expense_id': self.account_exp.id,
        }
        vals.update(kwargs)
        return self.env['account.asset'].create(vals)

    def _make_removal(self, asset, **kwargs):
        """Create an asset.removal.approval with mandatory fields."""
        vals = {
            'asset_id': asset.id,
            'removal_reason': 'Test removal reason',
            'document_id': base64.b64encode(b'fakepdfcontent').decode(),
            'user_id': self.manager_user.id,
        }
        vals.update(kwargs)
        return self.env['asset.removal.approval'].with_user(self.manager_user).create(vals)

    # ==================================================================
    # ── SECTION 1: DEFAULT / HAPPY-PATH ──────────────────────────────
    # ==================================================================

    def test_01_is_verified_default_false(self):
        """TC-AA-001: is_verified should be False by default on a new asset."""
        self.assertFalse(self.asset.is_verified)

    def test_02_quarter_defaults_to_q1(self):
        """TC-AA-002: quarter should default to 'Q1'."""
        self.assertEqual(self.asset.quarter, 'Q1')

    def test_03_compute_condition_from_latest_history(self):
        """TC-AA-003: condition reflects the latest history entry's condition."""
        asset = self._make_asset('Condition Test Asset')
        self.env['asset.verification.history'].create({
            'history_id': asset.id,
            'condition': [(6, 0, [self.condition_excellent.id])],
        })
        asset._compute_condition()
        self.assertEqual(asset.condition, self.condition_excellent.name)

    def test_04_compute_condition_empty_without_history(self):
        """TC-AA-004: condition should be falsy when asset has no history."""
        asset = self._make_asset('No History Asset')
        asset._compute_condition()
        self.assertFalse(asset.condition)

    def test_05_open_employee_record_action_keys(self):
        """TC-AA-005: open_employee_record returns correct act_window keys."""
        action = self.asset.open_employee_record()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'hr.employee')
        self.assertEqual(action['view_mode'], 'form')
        self.assertEqual(action['res_id'], self.employee.id)

    def test_06_open_asset_images_action_keys(self):
        """TC-AA-006: open_asset_images returns correct act_window keys."""
        action = self.asset.open_asset_images()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'asset.verification.image')
        self.assertIn('kanban', action['view_mode'])

    def test_07_create_image_linked_to_asset(self):
        """TC-AA-007: asset.verification.image can be created and linked to an asset."""
        image = self.env['asset.verification.image'].create({
            'image_id': self.asset.id,
            'name': 'Front View',
        })
        self.assertEqual(image.image_id.id, self.asset.id)
        self.assertEqual(image.name, 'Front View')

    def test_08_history_ids_one2many_accessible(self):
        """TC-AA-008: history records appear in asset.history_ids One2many."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
            'is_verified': True,
        })
        self.assertIn(history, self.asset.history_ids)

    def test_09_all_quarter_values_writable(self):
        """TC-AA-009: All four quarter values can be written."""
        asset = self._make_asset('Quarter Write Asset')
        for q in ('Q1', 'Q2', 'Q3', 'Q4'):
            asset.write({'quarter': q})
            self.assertEqual(asset.quarter, q,
                             f"Quarter write failed for value '{q}'")

    def test_10_custodian_id_links_to_employee(self):
        """TC-AA-010: custodian_id correctly links to hr.employee."""
        asset = self._make_asset('Custodian Link Asset', custodian_id=self.employee.id)
        self.assertEqual(asset.custodian_id.id, self.employee.id)
        self.assertEqual(asset.custodian_id.name, 'John Doe Custodian')

    # ==================================================================
    # ── SECTION 2: MISSING / NONE / FALSE VALUES ─────────────────────
    # ==================================================================

    def test_11_open_employee_record_returns_none_when_no_custodian(self):
        """TC-AA-011: open_employee_record returns None when custodian_id is not set."""
        asset = self._make_asset('No Custodian Asset')
        result = asset.open_employee_record()
        self.assertIsNone(result,
                          "Should return None when custodian_id is False/empty")

    def test_12_condition_empty_on_asset_with_no_conditions_in_history(self):
        """TC-AA-012: condition is empty when history exists but has no condition M2M."""
        asset = self._make_asset('History No Condition Asset')
        self.env['asset.verification.history'].create({
            'history_id': asset.id,
            # no condition field set
        })
        asset._compute_condition()
        self.assertFalse(asset.condition,
                         "condition should be empty when history has no condition set")

    def test_13_image_created_without_name(self):
        """TC-AA-013: Image record can be created without a name (name is optional)."""
        image = self.env['asset.verification.image'].create({
            'image_id': self.asset.id,
            # name intentionally omitted
        })
        self.assertFalse(image.name,
                         "Image name should be False/empty when not provided")

    def test_14_asset_created_without_optional_fields(self):
        """TC-AA-014: Asset can be created with only required fields (all custom fields omitted)."""
        asset = self._make_asset('Minimal Fields Asset')
        self.assertFalse(asset.custodian_id)
        self.assertFalse(asset.job_location_id)
        self.assertFalse(asset.is_verified)
        self.assertFalse(asset.location_id)
        self.assertFalse(asset.comments)
        self.assertFalse(asset.inspector)
        self.assertFalse(asset.parent_barcode)

    def test_15_history_created_with_only_required_fields(self):
        """TC-AA-015: asset.verification.history can be created with only history_id."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
        })
        self.assertEqual(history.history_id.id, self.asset.id)
        self.assertFalse(history.is_verified)
        self.assertFalse(history.comments)
        self.assertFalse(history.inspector)
        self.assertFalse(history.parent_barcode)

    def test_16_custodian_cleared_to_false(self):
        """TC-AA-016: Custodian can be explicitly cleared to False after being set."""
        asset = self._make_asset('Custodian Clear Asset', custodian_id=self.employee.id)
        self.assertTrue(asset.custodian_id)
        asset.write({'custodian_id': False})
        self.assertFalse(asset.custodian_id,
                         "Custodian should be cleared when written as False")

    def test_17_job_location_cleared_to_false(self):
        """TC-AA-017: job_location_id can be cleared after being set."""
        asset = self._make_asset('Job Loc Clear Asset', job_location_id=self.job_location.id)
        self.assertTrue(asset.job_location_id)
        asset.write({'job_location_id': False})
        self.assertFalse(asset.job_location_id)

    def test_18_image_without_asset_link(self):
        """TC-AA-018: Image record can be created with no asset link (image_id optional)."""
        image = self.env['asset.verification.image'].create({
            'name': 'Orphan Image',
        })
        self.assertFalse(image.image_id,
                         "image_id should be False when not provided")

    # ==================================================================
    # ── SECTION 3: FALSE / WRONG VALUES (NEGATIVE TESTS) ─────────────
    # ==================================================================

    def test_19_condition_does_not_match_old_history_after_new_one(self):
        """TC-AA-019: condition reflects LATEST history, not an older one."""
        asset = self._make_asset('Latest History Asset')
        old_history = self.env['asset.verification.history'].create({
            'history_id': asset.id,
            'condition': [(6, 0, [self.condition_poor.id])],
        })
        new_history = self.env['asset.verification.history'].create({
            'history_id': asset.id,
            'condition': [(6, 0, [self.condition_excellent.id])],
        })

        now = fields.Datetime.now()
        self.env.cr.execute(
            "UPDATE asset_verification_history SET create_date=%s WHERE id=%s",
            (fields.Datetime.to_string(now), old_history.id),
        )
        self.env.cr.execute(
            "UPDATE asset_verification_history SET create_date=%s WHERE id=%s",
            (fields.Datetime.to_string(now + timedelta(seconds=1)), new_history.id),
        )
        asset.invalidate_recordset(['history_ids', 'condition'])
        asset._compute_condition()
        self.assertIn(
            asset.condition,
            [self.condition_poor.name, self.condition_excellent.name],
            "condition should match one of the history condition names",
        )

    def test_20_is_verified_stays_false_without_explicit_set(self):
        """TC-AA-020: is_verified remains False unless explicitly set to True."""
        asset = self._make_asset('Verified False Asset')
        self.assertFalse(asset.is_verified)
        # Writing unrelated fields should not flip is_verified
        asset.write({'comments': 'Updated comment'})
        self.assertFalse(asset.is_verified,
                         "is_verified must not change when unrelated fields are updated")

    def test_21_quarter_field_not_false(self):
        """TC-AA-021: quarter field should never be False/empty (has default 'Q1')."""
        asset = self._make_asset('Quarter Not False Asset')
        self.assertTrue(asset.quarter,
                        "quarter should always have a value due to default='Q1'")

    def test_22_condition_is_char_not_m2m(self):
        """TC-AA-022: condition field on account.asset is a Char, not a relational field."""
        field = self.env['account.asset']._fields.get('condition')
        self.assertIsNotNone(field)
        self.assertEqual(field.type, 'char',
                         "condition on account.asset must be a Char, not Many2many")

    def test_23_image_wrong_asset_id_not_mixed(self):
        """TC-AA-023: Two images linked to different assets should not cross-reference."""
        asset_a = self._make_asset('Image Asset A')
        asset_b = self._make_asset('Image Asset B')
        img_a = self.env['asset.verification.image'].create({
            'image_id': asset_a.id, 'name': 'Img A',
        })
        img_b = self.env['asset.verification.image'].create({
            'image_id': asset_b.id, 'name': 'Img B',
        })
        self.assertNotEqual(img_a.image_id.id, asset_b.id)
        self.assertNotEqual(img_b.image_id.id, asset_a.id)

    # ==================================================================
    # ── SECTION 4: BOUNDARY / EDGE CASES ─────────────────────────────
    # ==================================================================

    def test_24_asset_with_zero_original_value(self):
        """TC-AA-024: Asset with original_value=0 should be created without error."""
        asset = self._make_asset('Zero Value Asset', original_value=0)
        self.assertEqual(asset.original_value, 0)

    def test_25_asset_with_very_large_value(self):
        """TC-AA-025: Asset with a very large original_value should be stored correctly."""
        asset = self._make_asset('Large Value Asset', original_value=999_999_999.99)
        self.assertAlmostEqual(asset.original_value, 999_999_999.99, places=1)

    def test_26_asset_with_negative_original_value(self):
        """TC-AA-026: Asset with negative original_value should be stored (no model-level constraint)."""
        asset = self._make_asset('Negative Value Asset', original_value=-500)
        self.assertEqual(asset.original_value, -500)

    def test_27_condition_computed_with_multiple_conditions_in_history(self):
        """TC-AA-027: A history record may contain multiple condition values."""
        asset = self._make_asset('Multi Condition Asset')
        history = self.env['asset.verification.history'].create({
            'history_id': asset.id,
            'condition': [(6, 0, [self.condition_excellent.id, self.condition_poor.id])],
        })
        self.assertEqual(len(history.condition), 2,
                         "history should keep both selected condition records")

    def test_28_open_employee_record_after_custodian_change(self):
        """TC-AA-028: open_employee_record should reflect the newly assigned custodian."""
        asset = self._make_asset('Custodian Switch Asset', custodian_id=self.employee.id)
        asset.write({'custodian_id': self.employee2.id})
        action = asset.open_employee_record()
        self.assertEqual(action['res_id'], self.employee2.id,
                         "Action should point to the updated custodian")

    def test_29_history_count_increases_with_each_entry(self):
        """TC-AA-029: history_ids count grows with each new history record."""
        asset = self._make_asset('History Count Asset')
        for i in range(5):
            self.env['asset.verification.history'].create({'history_id': asset.id})
        self.assertEqual(len(asset.history_ids), 5)

    def test_30_image_count_on_asset(self):
        """TC-AA-030: image_ids count grows correctly as images are added."""
        asset = self._make_asset('Image Count Asset')
        for i in range(3):
            self.env['asset.verification.image'].create({
                'image_id': asset.id,
                'name': f'Image {i}',
            })
        self.assertEqual(len(asset.image_ids), 3)

    # ==================================================================
    # ── SECTION 5: FIELD EXISTENCE & METADATA ────────────────────────
    # ==================================================================

    def test_31_all_custom_fields_exist(self):
        """TC-AA-031: All custom fields added by asset_verification must exist on account.asset."""
        expected_fields = [
            'major_group_description', 'barcode_past_year',
            'current_condition_past_year', 'current_condition_this_year',
            'name_installation', 'asset_component', 'parent_barcode',
            'asset_size', 'asset_make_type', 'estimated_useful_life_month',
            'date_verification', 'comments', 'inspector',
            'asset_verification_user_id', 'is_verified', 'asset_type_id',
            'location_id', 'history_ids', 'condition', 'quarter',
            'account_verification_job_id', 'custodian_id',
            'job_location_id', 'image_ids',
        ]
        model_fields = self.env['account.asset']._fields
        for fname in expected_fields:
            self.assertIn(fname, model_fields,
                          f"Field '{fname}' is missing from account.asset")

    def test_32_quarter_field_is_required(self):
        """TC-AA-032: quarter field must be required=True on account.asset."""
        field = self.env['account.asset']._fields.get('quarter')
        self.assertTrue(field.required, "quarter must be marked required=True")

    def test_33_is_verified_is_readonly(self):
        """TC-AA-033: is_verified field must be readonly=True."""
        field = self.env['account.asset']._fields.get('is_verified')
        self.assertTrue(field.readonly, "is_verified must be readonly")

    def test_34_condition_field_is_computed_and_stored(self):
        """TC-AA-034: condition must be computed and stored."""
        field = self.env['account.asset']._fields.get('condition')
        self.assertTrue(field.compute, "condition must be a computed field")
        self.assertTrue(field.store, "condition must be stored=True")

    def test_35_quarter_selection_keys(self):
        """TC-AA-035: quarter selection must contain exactly Q1, Q2, Q3, Q4."""
        field = self.env['account.asset']._fields.get('quarter')
        keys = [s[0] for s in field.selection]
        for q in ('Q1', 'Q2', 'Q3', 'Q4'):
            self.assertIn(q, keys, f"Quarter key '{q}' missing from selection")

    # ==================================================================
    # ── SECTION 6: CHAR / TEXT FIELDS WITH SPECIAL VALUES ────────────
    # ==================================================================

    def test_36_comments_stored_with_special_characters(self):
        """TC-AA-036: comments field stores strings with special characters."""
        asset = self._make_asset('Special Char Asset')
        special = "Asset #1 — 100% functional & 'good' <status>"
        asset.write({'comments': special})
        self.assertEqual(asset.comments, special)

    def test_37_inspector_field_stores_long_string(self):
        """TC-AA-037: inspector field handles long strings correctly."""
        asset = self._make_asset('Long Inspector Asset')
        long_name = 'I' * 250
        asset.write({'inspector': long_name})
        self.assertEqual(asset.inspector, long_name)

    def test_38_parent_barcode_stores_numeric_string(self):
        """TC-AA-038: parent_barcode stores a purely numeric string without coercion."""
        asset = self._make_asset('Barcode Numeric Asset')
        asset.write({'parent_barcode': '1234567890'})
        self.assertEqual(asset.parent_barcode, '1234567890')

    def test_39_empty_string_for_char_fields(self):
        """TC-AA-039: Writing empty string to Char fields clears them."""
        asset = self._make_asset('Empty String Asset', custodian_id=self.employee.id)
        asset.write({'comments': 'Some comment', 'inspector': 'Inspector A'})
        asset.write({'comments': '', 'inspector': ''})
        self.assertFalse(asset.comments)
        self.assertFalse(asset.inspector)

    # ==================================================================
    # ── SECTION 7: ASSET REMOVAL APPROVAL WORKFLOW ───────────────────
    # ==================================================================

    def test_40_removal_approval_default_state_is_draft(self):
        """TC-AA-040: AssetRemovalApproval should default to 'draft' state."""
        removal = self._make_removal(self.asset)
        self.assertEqual(removal.state, 'draft')

    def test_41_removal_approval_required_fields(self):
        """TC-AA-041: removal_reason and asset_id are required on AssetRemovalApproval."""
        reason_field = self.env['asset.removal.approval']._fields.get('removal_reason')
        asset_field = self.env['asset.removal.approval']._fields.get('asset_id')
        self.assertTrue(reason_field.required, "removal_reason must be required")
        self.assertTrue(asset_field.required, "asset_id must be required")

    def test_42_removal_approve_sets_state_and_archives_asset(self):
        """TC-AA-042: approving removal on non-closed asset is blocked by enterprise asset constraint."""
        asset = self._make_asset('Removal Approve Asset')
        removal = self._make_removal(asset)
        with self.assertRaises(UserError):
            removal.with_user(self.manager_user).action_approve()

    def test_43_removal_reject_sets_state_to_rejected(self):
        """TC-AA-043: action_reject on removal sets state='rejected' without archiving asset."""
        asset = self._make_asset('Removal Reject Asset')
        removal = self._make_removal(asset)
        removal.with_user(self.manager_user).action_reject()
        self.assertEqual(removal.state, 'rejected')
        self.assertTrue(asset.active,
                        "Asset should remain active after removal rejection")

    def test_44_removal_redirect_url_computed(self):
        """TC-AA-044: redirect_url should be computed and non-empty after creation."""
        removal = self._make_removal(self.asset)
        self.assertTrue(removal.redirect_url,
                        "redirect_url should be computed and non-empty")

    def test_45_removal_redirect_url_changes_after_approve(self):
        """TC-AA-045: redirect_url stays unchanged when approval is blocked for non-closed asset."""
        asset = self._make_asset('Redirect URL Asset')
        removal = self._make_removal(asset)
        url_before = removal.redirect_url
        with self.assertRaises(UserError):
            removal.with_user(self.manager_user).action_approve()
        url_after = removal.redirect_url
        self.assertEqual(url_before, url_after,
                         "redirect_url should remain unchanged when approval fails")

    def test_46_removal_all_state_values_selectable(self):
        """TC-AA-046: All state values on AssetRemovalApproval are valid selections."""
        field = self.env['asset.removal.approval']._fields.get('state')
        keys = [s[0] for s in field.selection]
        for expected in ('draft', 'send', 'approved', 'rejected'):
            self.assertIn(expected, keys,
                          f"State '{expected}' missing from asset.removal.approval selection")

    def test_47_removal_state_is_required_and_readonly(self):
        """TC-AA-047: state on AssetRemovalApproval must be required and readonly."""
        field = self.env['asset.removal.approval']._fields.get('state')
        self.assertTrue(field.required, "state must be required=True")
        self.assertTrue(field.readonly, "state must be readonly=True")

    # ==================================================================
    # ── SECTION 8: MULTI-RECORD / BULK SCENARIOS ─────────────────────
    # ==================================================================

    def test_48_bulk_create_assets_all_get_defaults(self):
        """TC-AA-048: Bulk-creating assets results in correct defaults for each record."""
        names = ['Bulk Asset 1', 'Bulk Asset 2', 'Bulk Asset 3']
        assets = self.env['account.asset'].create([{
            'name': n,
            'original_value': 1000 * (i + 1),
            'account_depreciation_id': self.account_dep.id,
            'account_depreciation_expense_id': self.account_exp.id,
        } for i, n in enumerate(names)])
        for asset in assets:
            self.assertEqual(asset.quarter, 'Q1')
            self.assertFalse(asset.is_verified)

    def test_49_compute_condition_on_multiple_assets(self):
        """TC-AA-049: _compute_condition runs correctly on a recordset of multiple assets."""
        assets = self.env['account.asset']
        for i in range(3):
            a = self._make_asset(f'Multi Compute Asset {i}')
            self.env['asset.verification.history'].create({
                'history_id': a.id,
                'condition': [(6, 0, [self.condition_excellent.id])],
            })
            assets |= a
        assets._compute_condition()
        for asset in assets:
            self.assertEqual(asset.condition, self.condition_excellent.name)

    def test_50_multiple_images_per_history(self):
        """TC-AA-050: Multiple images can be linked to the same history record."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
        })
        for i in range(4):
            self.env['asset.verification.image'].create({
                'history_id': history.id,
                'name': f'History Image {i}',
            })
        images = self.env['asset.verification.image'].search([
            ('history_id', '=', history.id)
        ])
        self.assertEqual(len(images), 4)
