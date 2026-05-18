"""
Test Cases for Asset Verification History (asset.verification.history)
Module: asset_verification
Odoo Version: 18.0
"""

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo import fields

import logging
_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestAssetVerificationHistory(TransactionCase):
    """Test suite for AssetVerificationHistory model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.account_dep = cls.env['account.account'].search(
            [('account_type', '=', 'asset_fixed')], limit=1
        )
        cls.account_exp = cls.env['account.account'].search(
            [('account_type', '=', 'expense')], limit=1
        )

        cls.asset = cls.env['account.asset'].create({
            'name': 'History Test Asset',
            'original_value': 5000,
            'account_depreciation_id': cls.account_dep.id,
            'account_depreciation_expense_id': cls.account_exp.id,
        })
        _logger.info("Created test asset: %s", cls.asset.name)

        cls.job_location = cls.env['asset.verification.job.location'].create({
            'name': 'History Test Location',
        })
        _logger.info("Created job location: %s", cls.job_location.name)
        cls.condition_good = cls.env['asset.condition'].create({'name': 'Good'})
        _logger.info("Created condition: %s", cls.condition_good.name)
        cls.condition_fair = cls.env['asset.condition'].create({'name': 'Fair'})
        _logger.info("Created condition: %s", cls.condition_fair.name)

    # ------------------------------------------------------------------
    # TC-HIST-001: Create a history record
    # ------------------------------------------------------------------
    def test_01_create_history_record(self):
        """TC-HIST-001: A history record should be creatable with minimal fields."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
            'is_verified': True,
        })
        self.assertEqual(history.history_id.id, self.asset.id)
        self.assertTrue(history.is_verified)

    # ------------------------------------------------------------------
    # TC-HIST-002: _rec_name is history_id
    # ------------------------------------------------------------------
    def test_02_rec_name_is_history_id(self):
        """TC-HIST-002: The display name should come from history_id (the asset)."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
        })
        self.assertEqual(
            str(history.display_name),
            self.asset.name,
            "_rec_name resolves to the linked asset's name"
        )

    # ------------------------------------------------------------------
    # TC-HIST-003: Multiple histories linked to one asset
    # ------------------------------------------------------------------
    def test_03_multiple_histories_per_asset(self):
        """TC-HIST-003: Multiple history entries can be created for the same asset."""
        for year_offset in range(3):
            self.env['asset.verification.history'].create({
                'history_id': self.asset.id,
                'is_verified': True,
                'this_year': str(2024 + year_offset),
                'past_year': str(2023 + year_offset),
            })
        count = self.env['asset.verification.history'].search_count(
            [('history_id', '=', self.asset.id)]
        )
        self.assertGreaterEqual(count, 3,
                                "At least 3 history records should exist for the asset")

    # ------------------------------------------------------------------
    # TC-HIST-004: cron_copy_comments_to_condition syncs comments → condition
    # ------------------------------------------------------------------
    def test_04_cron_copy_comments_to_condition(self):
        """TC-HIST-004: cron_copy_comments_to_condition should populate condition from comments."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
            'comments': 'Good',
        })
        history.cron_copy_comments_to_condition()
        self.assertIn(self.condition_good, history.condition,
                      "Condition 'Good' should be linked after cron execution")

    # ------------------------------------------------------------------
    # TC-HIST-005: cron_copy_comments_to_condition with empty comments clears M2M
    # ------------------------------------------------------------------
    def test_05_cron_clears_condition_when_no_comments(self):
        """TC-HIST-005: When comments are empty, condition Many2many should be cleared."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
            'comments': '',
            'condition': [(6, 0, [self.condition_good.id])],
        })
        history.cron_copy_comments_to_condition()
        self.assertFalse(history.condition,
                         "Condition M2M should be empty when comments are blank")

    # ------------------------------------------------------------------
    # TC-HIST-006: open_kanban_view returns correct window action
    # ------------------------------------------------------------------
    def test_06_open_kanban_view_action(self):
        """TC-HIST-006: open_kanban_view should return an act_window action for images."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
        })
        action = history.open_kanban_view()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'asset.verification.image')
        self.assertIn('kanban', action['view_mode'])
        self.assertEqual(
            action['context'].get('default_history_id'), history.id
        )

    # ------------------------------------------------------------------
    # TC-HIST-007: is_verified field defaults to False
    # ------------------------------------------------------------------
    def test_07_is_verified_defaults_to_false(self):
        """TC-HIST-007: is_verified should be False when not explicitly set."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
        })
        self.assertFalse(history.is_verified,
                         "is_verified should default to False")

    # ------------------------------------------------------------------
    # TC-HIST-008: date_verification field stores a date correctly
    # ------------------------------------------------------------------
    def test_08_date_verification_stored(self):
        """TC-HIST-008: date_verification should persist the date it was set to."""
        today = fields.Date.today()
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
            'date_verification': today,
        })
        self.assertEqual(history.date_verification, today)

    # ------------------------------------------------------------------
    # TC-HIST-009: Multiple conditions can be linked (Many2many)
    # ------------------------------------------------------------------
    def test_09_multiple_conditions_m2m(self):
        """TC-HIST-009: Multiple condition records can be linked to a single history."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
            'condition': [(6, 0, [self.condition_good.id, self.condition_fair.id])],
        })
        self.assertEqual(len(history.condition), 2,
                         "Two conditions should be linked to the history record")

    # ------------------------------------------------------------------
    # TC-HIST-010: history linked through asset history_ids One2many
    # ------------------------------------------------------------------
    def test_10_asset_history_ids_one2many(self):
        """TC-HIST-010: asset.history_ids should surface this history record."""
        history = self.env['asset.verification.history'].create({
            'history_id': self.asset.id,
            'is_verified': True,
        })
        _logger.info("Created history record=============================================================: %s", history)
        self.assertIn(history, self.asset.history_ids,
                      "History record should appear in asset's history_ids")
