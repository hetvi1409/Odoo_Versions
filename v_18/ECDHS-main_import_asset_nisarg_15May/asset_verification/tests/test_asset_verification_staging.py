from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install', 'asset_verification')
class TestAssetVerificationStaging(TransactionCase):
    """Test suite for AssetVerificationStaging model"""

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
            'name': 'Staging Test Location',
        })

        cls.verification_job = cls.env['asset.verification.job'].create({
            'name': 'Staging Verification Job',
            'job_location_id': False,
        })

        cls.condition_good = cls.env['asset.condition'].search(
            [('name', '=', 'Good')], limit=1
        ) or cls.env['asset.condition'].create({'name': 'Good'})

        cls.category = cls.env['asset.category'].create({
            'name': 'Staging Category',
            'is_movable': True,
        })

        # Create a user for manager group tests
        cls.manager_user = cls.env['res.users'].create({
            'name': 'Staging Manager',
            'login': 'staging_manager_test@test.com',
            'email': 'staging_manager_test@test.com',
            'groups_id': [
                (4, cls.env.ref('base.group_user').id),
                (4, cls.env.ref('asset_verification.group_staging_approval_manager').id),
                (4, cls.env.ref('fixed_assets.group_fixed_asset_approver').id),
            ],
        })
        _logger.info("Created manager user============: %s", cls.manager_user.name)

    def _create_staging(self, name='Staging Asset 001', **kwargs):
        """Helper to quickly create a staging record."""
        vals = {
            'name': name,
            'barcode': f'BCODE-{name}',
            'verification_job_id': self.verification_job.id,
            'condition': [(6, 0, [self.condition_good.id])],
        }
        vals.update(kwargs)
        _logger.info('vals============================== >: %s',vals)
        return self.env['asset.verification.staging'].create(vals)

    # ------------------------------------------------------------------
    # TC-STAG-001: Create staging asset with required fields
    # ------------------------------------------------------------------
    def test_01_create_staging_asset(self):
        """TC-STAG-001: A staging asset should be created with state 'draft'."""
        staging = self._create_staging()
        _logger.info('staging>>>>>>>>>>>>>>: %s',staging)
        self.assertEqual(staging.state, 'draft')
        self.assertTrue(staging.name)
        self.assertTrue(staging.barcode)

    # ------------------------------------------------------------------
    # TC-STAG-002: name is required
    # ------------------------------------------------------------------
    def test_02_name_required(self):
        """TC-STAG-002: The 'name' field must be marked required=True on the model."""
        field = self.env['asset.verification.staging']._fields.get('name')
        self.assertIsNotNone(field, "'name' field must exist on asset.verification.staging")
        self.assertTrue(field.required, "'name' field must be required=True")

    # ------------------------------------------------------------------
    # TC-STAG-003: barcode is required
    # ------------------------------------------------------------------
    def test_03_barcode_required(self):
        """TC-STAG-003: The 'barcode' field must be marked required=True on the model."""
        field = self.env['asset.verification.staging']._fields.get('barcode')
        self.assertIsNotNone(field, "'barcode' field must exist on asset.verification.staging")
        self.assertTrue(field.required, "'barcode' field must be required=True")

    # ------------------------------------------------------------------
    # TC-STAG-004: action_submit_for_approval changes state to awaiting_approval
    # ------------------------------------------------------------------
    def test_04_submit_for_approval_changes_state(self):
        """TC-STAG-004: action_submit_for_approval should set state to 'awaiting_approval'."""
        staging = self._create_staging('Submit Test Asset')
        _logger.info('Staging before submit: %s', staging)
        staging.action_submit_for_approval()
        _logger.info('Staging after submit: %s', staging)
        self.assertEqual(staging.state, 'awaiting_approval')

    # ------------------------------------------------------------------
    # TC-STAG-005: action_approve by non-manager raises UserError
    # ------------------------------------------------------------------
    def test_05_approve_by_non_manager_raises_error(self):
        """TC-STAG-005: A non-manager user should NOT be able to approve staging."""
        staging = self._create_staging('Non Manager Approve')
        _logger.info('Staging before submit: %s', staging)
        staging.action_submit_for_approval()
        _logger.info('Staging after submit: %s', staging)
        with self.assertRaises(UserError):
            staging.with_user(self.env.user).action_approve()

    # ------------------------------------------------------------------
    # TC-STAG-006: action_approve by manager creates an account.asset
    # ------------------------------------------------------------------
    def test_06_approve_by_manager_creates_asset(self):
        """TC-STAG-006: Manager approval should create a new account.asset record."""
        staging = self._create_staging('Manager Approve Asset')
        staging.action_submit_for_approval()

        asset_count_before = self.env['account.asset'].search_count([
            ('name', '=', 'Manager Approve Asset')
        ])

        staging.with_user(self.manager_user).action_approve()

        asset_count_after = self.env['account.asset'].search_count([
            ('name', '=', 'Manager Approve Asset')
        ])
        _logger.info("Verification history count before==========: %s, after=====: %s", asset_count_before, asset_count_after)
        self.assertGreater(asset_count_after, asset_count_before,
                           "Approval should create a new account.asset")


    # ------------------------------------------------------------------
    # TC-STAG-007: action_approve archives the staging record
    # ------------------------------------------------------------------
    def test_07_approve_archives_staging(self):
        """TC-STAG-007: After manager approval, the staging record should be archived."""
        staging = self._create_staging('Archive On Approve')
        staging.action_submit_for_approval()
        staging.with_user(self.manager_user).action_approve()
        self.assertFalse(staging.active,
                         "Staging record should be archived after approval")

    # ------------------------------------------------------------------
    # TC-STAG-008: action_approve sets state to 'approved'
    # ------------------------------------------------------------------
    def test_08_approve_sets_state_to_approved(self):
        """TC-STAG-008: Staging state should be 'approved' after manager approves."""
        staging = self._create_staging('State Approved Test')
        staging.action_submit_for_approval()
        staging.with_user(self.manager_user).action_approve()
        self.assertEqual(staging.state, 'approved')

    # ------------------------------------------------------------------
    # TC-STAG-009: action_reject by non-manager raises UserError
    # ------------------------------------------------------------------
    def test_09_reject_by_non_manager_raises_error(self):
        """TC-STAG-009: A non-manager should NOT be able to reject staging."""
        staging = self._create_staging('Non Manager Reject')
        staging.action_submit_for_approval()
        with self.assertRaises(UserError):
            staging.with_user(self.env.user).action_reject()

    # ------------------------------------------------------------------
    # TC-STAG-010: action_reject by manager changes state to 'rejected'
    # ------------------------------------------------------------------
    def test_10_reject_by_manager_changes_state(self):
        """TC-STAG-010: Manager can reject staging; state should become 'rejected'."""
        staging = self._create_staging('Manager Reject Asset')
        staging.action_submit_for_approval()
        staging.with_user(self.manager_user).action_reject()
        self.assertEqual(staging.state, 'rejected')

    # ------------------------------------------------------------------
    # TC-STAG-011: condition field defaults to 'Good'
    # ------------------------------------------------------------------
    def test_11_default_condition_is_good(self):
        """TC-STAG-011: Default condition should be 'Good'."""
        staging = self._create_staging('Default Condition Test')
        condition_names = staging.condition.mapped('name')
        self.assertIn('Good', condition_names,
                      "Default condition should include 'Good'")

    # ------------------------------------------------------------------
    # TC-STAG-012: verify selection field accepts 'yes' and 'no'
    # ------------------------------------------------------------------
    def test_12_verify_selection_values(self):
        """TC-STAG-012: verify field should accept 'yes' and 'no' values."""
        for value in ('yes', 'no'):
            staging = self._create_staging(f'Verify {value}', verify=value)
            self.assertEqual(staging.verify, value)

    # ------------------------------------------------------------------
    # TC-STAG-013: Staging linked to a verification job
    # ------------------------------------------------------------------
    def test_13_staging_linked_to_verification_job(self):
        """TC-STAG-013: A staging record can be linked to a verification job."""
        staging = self._create_staging('Job Linked Asset')
        self.assertEqual(staging.verification_job_id.id, self.verification_job.id)

    # ------------------------------------------------------------------
    # TC-STAG-014: action_approve creates verification history record
    # ------------------------------------------------------------------
    def test_14_approve_creates_history_record(self):
        """TC-STAG-014: Approving a staging asset should also create a verification history."""
        staging = self._create_staging('History On Approve')
        staging.action_submit_for_approval()

        hist_count_before = self.env['asset.verification.history'].search_count([])
        staging.with_user(self.manager_user).action_approve()
        hist_count_after = self.env['asset.verification.history'].search_count([])

        _logger.info("Verification history count before==========: %s, after=====: %s", hist_count_before, hist_count_after)
        self.assertGreater(hist_count_after, hist_count_before,
                           "An asset.verification.history record should be created on approval")
