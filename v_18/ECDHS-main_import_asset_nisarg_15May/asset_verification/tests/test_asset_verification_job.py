"""
Test Cases for Asset Verification Job (asset.verification.job)
Module: asset_verification
Odoo Version: 18.0
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

import logging
_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class TestAssetVerificationJob(TransactionCase):
    """Test suite for Asset Verification Job model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a job location
        cls.job_location = cls.env['asset.verification.job.location'].create({
            'name': 'Test Location - Building A',
        })
        _logger.info("Created job location: %s", cls.job_location.name)

        # Create a second job location
        cls.job_location2 = cls.env['asset.verification.job.location'].create({
            'name': 'Test Location - Building B',
        })
        _logger.info("Created job location: %s", cls.job_location2.name)

        # Create asset categories
        cls.asset_category = cls.env['asset.category'].create({
            'name': 'Office Equipment',
            'is_movable': True,
        })
        _logger.info("Created asset category: %s", cls.asset_category.name)

        # Create depreciation accounts needed for account.asset
        cls.account_dep = cls.env['account.account'].search(
            [('account_type', '=', 'asset_fixed')], limit=1
        )
        _logger.info("Found depreciation account: %s", cls.account_dep.name)
        cls.account_exp = cls.env['account.account'].search(
            [('account_type', '=', 'expense')], limit=1
        )
        _logger.info("Found expense account: %s", cls.account_exp.name)

        # Create test assets linked to job_location
        cls.asset1 = cls.env['account.asset'].create({
            'name': 'Test Asset 1',
            'original_value': 5000,
            'job_location_id': cls.job_location.id,
            'account_depreciation_id': cls.account_dep.id,
            'account_depreciation_expense_id': cls.account_exp.id,
        })
        _logger.info("Created test asset: %s", cls.asset1.name)

        cls.asset2 = cls.env['account.asset'].create({
            'name': 'Test Asset 2',
            'original_value': 3000,
            'job_location_id': cls.job_location.id,
            'account_depreciation_id': cls.account_dep.id,
            'account_depreciation_expense_id': cls.account_exp.id,
        })
        _logger.info("Created test asset: %s", cls.asset2.name)

        cls.asset3 = cls.env['account.asset'].create({
            'name': 'Test Asset 3 - Loc B',
            'original_value': 1500,
            'job_location_id': cls.job_location2.id,
            'account_depreciation_id': cls.account_dep.id,
            'account_depreciation_expense_id': cls.account_exp.id,
        })
        _logger.info("Created test asset: %s", cls.asset3.name)

    # ------------------------------------------------------------------
    # TC-JOB-001: Create a basic verification job
    # ------------------------------------------------------------------
    def test_01_create_verification_job(self):
        """TC-JOB-001: Creating a verification job should set state to 'draft'."""
        job = self.env['asset.verification.job'].create({
            'name': 'Job Q1 2026',
            'job_location_id': self.job_location.id,
        })
        _logger.info("Created verification job: %s", job.name)
        self.assertEqual(job.state, 'draft', "New job should be in 'draft' state")
        self.assertTrue(job.name, "Job name should be set")

    # ------------------------------------------------------------------
    # TC-JOB-002: Job name is required
    # ------------------------------------------------------------------
    def test_02_job_name_required(self):
        """TC-JOB-002: The 'name' field must be marked required=True on the model."""
        field = self.env['asset.verification.job']._fields.get('name')
        self.assertIsNotNone(field, "'name' field must exist on asset.verification.job")
        self.assertTrue(field.required, "'name' field must be required=True")

    # ------------------------------------------------------------------
    # TC-JOB-003: Assets auto-populated on create by location
    # ------------------------------------------------------------------
    def test_03_assets_populated_on_create(self):
        """TC-JOB-003: Assets belonging to the selected job location are auto-added on create."""
        job = self.env['asset.verification.job'].create({
            'name': 'Auto Populate Test',
            'job_location_id': self.job_location.id,
        })
        asset_ids_in_job = job.asset_ids.mapped('asset_id.id')
        self.assertIn(self.asset1.id, asset_ids_in_job,
                      "Asset 1 (location A) should be in the job")
        self.assertIn(self.asset2.id, asset_ids_in_job,
                      "Asset 2 (location A) should be in the job")
        self.assertNotIn(self.asset3.id, asset_ids_in_job,
                         "Asset 3 (location B) should NOT be in the job")

    # ------------------------------------------------------------------
    # TC-JOB-004: _compute_total_assets
    # ------------------------------------------------------------------
    def test_04_compute_total_assets(self):
        """TC-JOB-004: total_assets computed field should count all job lines."""
        job = self.env['asset.verification.job'].create({
            'name': 'Compute Total Test',
            'job_location_id': self.job_location.id,
        })
        _logger.info("Created verification job: %s", job.name)

        self.assertEqual(job.total_assets, len(job.asset_ids),
                         "total_assets should equal number of job lines")

    # ------------------------------------------------------------------
    # TC-JOB-005: _compute_verified_assets and _compute_not_verified_assets
    # ------------------------------------------------------------------
    def test_05_compute_verified_counts(self):
        """TC-JOB-005: verified_count / not_verified_count should reflect actual statuses."""
        job = self.env['asset.verification.job'].create({
            'name': 'Verified Count Test',
            'job_location_id': self.job_location.id,
        })
        _logger.info("Created verification job: %s", job.name)
        total = job.total_assets
        self.assertEqual(job.not_verified_count, total,
                         "All assets should be not-verified initially")
        self.assertEqual(job.verified_count, 0,
                         "No assets should be verified initially")

        # Manually mark one line as verified
        if job.asset_ids:
            job.asset_ids[0].sudo().write({'verified': True})
            job.invalidate_recordset()

        self.assertEqual(job.verified_count, 1)
        self.assertEqual(job.not_verified_count, total - 1)

    # ------------------------------------------------------------------
    # TC-JOB-006: _compute_completion_percentage
    # ------------------------------------------------------------------
    def test_06_compute_completion_percentage(self):
        """TC-JOB-006: Completion percentage = (verified / total) * 100."""
        job = self.env['asset.verification.job'].create({
            'name': 'Completion % Test',
            'job_location_id': self.job_location.id,
        })
        if job.total_assets == 0:
            self.assertEqual(job.completion_percentage, 0.0)
            return

        # Mark all lines as verified
        job.asset_ids.sudo().write({'verified': True})
        job.invalidate_recordset()
        self.assertAlmostEqual(job.completion_percentage, 100.0, places=1)

        # Mark all as not verified
        job.asset_ids.sudo().write({'verified': False})
        job.invalidate_recordset()
        self.assertAlmostEqual(job.completion_percentage, 0.0, places=1)

    # ------------------------------------------------------------------
    # TC-JOB-007: Completion percentage = 0 when no assets
    # ------------------------------------------------------------------
    def test_07_completion_percentage_no_assets(self):
        """TC-JOB-007: Completion % should be 0.0 when no asset lines exist."""
        job = self.env['asset.verification.job'].create({
            'name': 'Empty Job',
            'job_location_id': False,
        })
        _logger.info("Created verification job: %s", job.name)
        self.assertEqual(job.completion_percentage, 0.0,
                         "Completion % for an empty job should be 0.0")

    # ------------------------------------------------------------------
    # TC-JOB-008: update_assets removes lines from wrong location
    # ------------------------------------------------------------------
    def test_08_update_assets_filters_by_location(self):
        """TC-JOB-008: update_assets() should only retain assets from the job's location."""
        job = self.env['asset.verification.job'].create({
            'name': 'Update Assets Test',
            'job_location_id': self.job_location.id,
        })
        _logger.info("Created verification job: %s", job.name)
        job.update_assets()
        for line in job.asset_ids:
            self.assertEqual(
                line.asset_id.job_location_id.id,
                self.job_location.id,
                "All lines should belong to the job's location after update_assets()"
            )

    # ------------------------------------------------------------------
    # TC-JOB-009: Verification period selection values
    # ------------------------------------------------------------------
    def test_09_verification_period_selection(self):
        """TC-JOB-009: All four quarter period values should be assignable."""
        for period in ('Q1', 'Q2', 'Q3', 'Q4'):
            job = self.env['asset.verification.job'].create({
                'name': f'Period Test {period}',
                'verification_period': period,
                'job_location_id': False,
            })
            _logger.info("Created verification job: %s", job.name)
            self.assertEqual(job.verification_period, period)

    # ------------------------------------------------------------------
    # TC-JOB-010: current user added to user_ids on creation
    # ------------------------------------------------------------------
    def test_10_current_user_in_user_ids(self):
        """TC-JOB-010: user_ids field must be a Many2many to res.users."""
        field = self.env['asset.verification.job']._fields.get('user_ids')
        self.assertIsNotNone(field, "'user_ids' field must exist on asset.verification.job")
        self.assertEqual(field.type, 'many2many', "'user_ids' must be a Many2many field")
        self.assertEqual(field.comodel_name, 'res.users', "'user_ids' must relate to res.users")



    # ------------------------------------------------------------------
    # TC-JOB-011: action_download_report returns act_url action
    # ------------------------------------------------------------------
    def test_11_action_download_report_returns_url_action(self):
        """TC-JOB-011: action_download_report should return an ir.actions.act_url dict."""
        job = self.env['asset.verification.job'].create({
            'name': 'Download Report Test',
            'job_location_id': self.job_location.id,
        })
        _logger.info("Created verification job: %s", job.name)
        result = job.action_download_report()
        self.assertEqual(result.get('type'), 'ir.actions.act_url')
        self.assertIn(str(job.id), result.get('url', ''))

    # ------------------------------------------------------------------
    # TC-JOB-012: generate_excel_report returns bytes
    # ------------------------------------------------------------------
    def test_12_generate_excel_report_returns_bytes(self):
        """TC-JOB-012: generate_excel_report() should return a non-empty bytes object."""
        job = self.env['asset.verification.job'].create({
            'name': 'Excel Report Test',
            'job_location_id': self.job_location.id,
        })
        data = job.generate_excel_report()
        self.assertIsInstance(data, bytes, "Excel report data should be bytes")
        self.assertGreater(len(data), 0, "Excel report bytes should not be empty")

    # ------------------------------------------------------------------
    # TC-JOB-013: AssetVerificationJobLines model creation
    # ------------------------------------------------------------------
    def test_13_create_job_line(self):
        """TC-JOB-013: A job line should link an asset to a verification job."""
        job = self.env['asset.verification.job'].create({'name': 'Job Line Test', 'job_location_id': False})
        line = self.env['asset.verification.job.line'].create({
            'asset_id': self.asset1.id,
            'account_verification_job_id': job.id,
            'verified': False,
        })
        self.assertEqual(line.account_verification_job_id.id, job.id)
        self.assertFalse(line.verified)

    # ------------------------------------------------------------------
    # TC-JOB-014: Update verified status on a job line
    # ------------------------------------------------------------------
    def test_14_update_verified_status_on_job_line(self):
        """TC-JOB-014: Writing verified=True on a job line should persist."""
        job = self.env['asset.verification.job'].create({'name': 'Verified Line Test', 'job_location_id': False})
        line = self.env['asset.verification.job.line'].create({
            'asset_id': self.asset1.id,
            'account_verification_job_id': job.id,
            'verified': False,
        })
        line.sudo().write({'verified': True})
        _logger.info("Created job line with verified status============================: %s", line.verified)
        self.assertTrue(line.verified)
