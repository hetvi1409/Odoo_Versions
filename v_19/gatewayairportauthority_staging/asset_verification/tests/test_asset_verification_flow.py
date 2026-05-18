# -*- coding: utf-8 -*-
import base64

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'asset_verification')
class TestAssetVerificationFlow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company
        cls.good_condition = cls.env.ref('asset_verification.condition_good')
        cls.bad_condition = cls.env.ref('asset_verification.condition_bad')

        cls.custodian = cls.env['hr.employee'].create({
            'name': 'Asset Custodian',
            'company_id': cls.company.id,
        })

        cls.depreciation_account = cls.env['account.account'].create({
            'name': 'Test Depreciation Account',
            'code': f'TDEP{cls.company.id}',
            'account_type': 'asset_current',
        })
        cls.expense_account = cls.env['account.account'].create({
            'name': 'Test Expense Account',
            'code': f'TEXP{cls.company.id}',
            'account_type': 'expense',
        })

        cls.asset_category = cls.env['asset.category'].create({
            'name': 'Test Movable Category',
            'description': 'Category for asset verification tests',
            'is_movable': True,
        })
        cls.asset_type = cls.env['asset.type'].create({
            'name': 'Test Asset Type',
            'category_id': cls.asset_category.id,
        })

        cls.job_location_a = cls.env['asset.verification.job.location'].create({
            'name': 'Office A',
            'code': 'OFF-A',
        })
        cls.job_location_b = cls.env['asset.verification.job.location'].create({
            'name': 'Office B',
            'code': 'OFF-B',
        })

        parent_stock_location = cls.env['stock.location'].search([('usage', '=', 'view')], limit=1)
        cls.stock_location_a = cls.env['stock.location'].create({
            'name': 'Stock Office A',
            'usage': 'internal',
            'location_id': parent_stock_location.id,
        })
        cls.stock_location_b = cls.env['stock.location'].create({
            'name': 'Stock Office B',
            'usage': 'internal',
            'location_id': parent_stock_location.id,
        })

    @classmethod
    def _barcode_for(cls, suffix):
        return f'BC-{suffix}'

    def _create_asset(self, *, name, barcode, serial, job_location, stock_location, original_value=2500.0):
        return self.env['account.asset'].create({
            'name': name,
            'asset_type_id': self.asset_type.id,
            'location_id': stock_location.id,
            'job_location_id': job_location.id,
            'afs_classification': self.asset_category.id,
            'notes': f'Notes for {name}',
            'alternative_ref': barcode,
            'serial_number': serial,
            'original_value': original_value,
            'account_depreciation_id': self.depreciation_account.id,
            'account_depreciation_expense_id': self.expense_account.id,
            'description': f'Description for {name}',
            'custodian_id': self.custodian.id,
            'acquisition_date': fields.Date.today(),
        })

    def _create_job(self, job_location, name='Verification Job'):
        return self.env['asset.verification.job'].create({
            'name': name,
            'job_location_id': job_location.id,
            'verification_period_from': fields.Datetime.now(),
            'verification_period_to': fields.Datetime.now(),
        })

    def _create_verification(self, asset, job, *, description='Verified description', location=None, conditions=None, image_data=None):
        condition_ids = conditions or [self.good_condition.id]
        values = {
            'asset_id': asset.id,
            'barcode_number': asset.alternative_ref,
            'description': description,
            'verification_job_id': job.id,
            'condition': [(6, 0, condition_ids)],
            'custodian_id': self.custodian.id,
        }
        if location:
            values['location_id'] = location.id
        if image_data:
            values['image_ids'] = [(0, 0, {
                'name': 'proof.png',
                'image': image_data,
                'mimetype': 'image/png',
                'image_id': asset.id,
            })]
        return self.env['asset.verification'].with_context(
            default_verification_job_id=job.id,
        ).create(values)

    def test_01_asset_creation_keeps_details_and_job_filters_by_location(self):
        asset_a = self._create_asset(
            name='Asset A',
            barcode=self._barcode_for('A'),
            serial='SN-A',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        asset_b = self._create_asset(
            name='Asset B',
            barcode=self._barcode_for('B'),
            serial='SN-B',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        asset_c = self._create_asset(
            name='Asset C',
            barcode=self._barcode_for('C'),
            serial='SN-C',
            job_location=self.job_location_b,
            stock_location=self.stock_location_b,
        )

        self.assertEqual(asset_a.asset_type_id, self.asset_type)
        self.assertEqual(asset_a.location_id, self.stock_location_a)
        self.assertEqual(asset_a.classification_type, 'movables')
        self.assertEqual(asset_a.afs_classification, self.asset_category)
        self.assertEqual(asset_a.notes, 'Notes for Asset A')
        self.assertEqual(asset_a.alternative_ref, self._barcode_for('A'))
        self.assertEqual(asset_a.serial_number, 'SN-A')
        self.assertEqual(asset_a.original_value, 2500.0)
        self.assertEqual(asset_a.account_depreciation_id, self.depreciation_account)
        self.assertEqual(asset_a.account_depreciation_expense_id, self.expense_account)
        self.assertEqual(asset_a.description, 'Description for Asset A')
        self.assertEqual(asset_a.custodian_id, self.custodian)
        self.assertEqual(asset_a.job_location_id, self.job_location_a)

        job = self._create_job(self.job_location_a, name='Location A Job')
        job_asset_ids = set(job.asset_ids.mapped('asset_id').ids)

        self.assertSetEqual(job_asset_ids, {asset_a.id, asset_b.id})
        self.assertNotIn(asset_c.id, job_asset_ids)
        self.assertEqual(job.total_assets, 2)

    def test_02_verify_asset_creates_history_copies_image_and_completes_single_asset_job(self):
        asset = self._create_asset(
            name='Asset Single',
            barcode=self._barcode_for('SINGLE'),
            serial='SN-SINGLE',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='Single Asset Job')
        image_data = base64.b64encode(b'asset-proof-image')

        verification = self._create_verification(
            asset,
            job,
            description='Verified asset description',
            location=self.job_location_a,
            image_data=image_data,
        )
        verification.with_context(default_verification_job_id=job.id).action_verify()

        history = self.env['asset.verification.history'].search([('history_id', '=', asset.id)])
        job_line = job.asset_ids.filtered(lambda line: line.asset_id == asset)

        self.assertEqual(len(history), 1)
        self.assertEqual(history.parent_barcode, asset.alternative_ref)
        self.assertEqual(history.comments, self.good_condition.name)
        self.assertEqual(history.location_id, self.job_location_a)
        self.assertEqual(history.major_group_description, 'Verified asset description')
        self.assertEqual(len(history.image_ids), 1)
        self.assertEqual(history.image_ids.name, 'proof.png')
        self.assertEqual(history.image_ids.image, image_data)

        self.assertTrue(job_line.verified)
        self.assertEqual(job_line.asset_verification_line_id, verification)
        self.assertEqual(job.state, 'completed')
        self.assertEqual(job.verified_count, 1)
        self.assertEqual(asset.description, 'Verified asset description')
        self.assertEqual(asset.custodian_id, self.custodian)

    def test_03_partial_verification_marks_only_verified_line_and_keeps_job_in_progress(self):
        asset_1 = self._create_asset(
            name='Partial Asset 1',
            barcode=self._barcode_for('PART-1'),
            serial='SN-P1',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        asset_2 = self._create_asset(
            name='Partial Asset 2',
            barcode=self._barcode_for('PART-2'),
            serial='SN-P2',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='Partial Job')

        verification = self._create_verification(asset_1, job, description='Partial verification')
        verification.with_context(default_verification_job_id=job.id).action_verify()

        line_1 = job.asset_ids.filtered(lambda line: line.asset_id == asset_1)
        line_2 = job.asset_ids.filtered(lambda line: line.asset_id == asset_2)

        self.assertTrue(line_1.verified)
        self.assertFalse(line_2.verified)
        self.assertEqual(job.state, 'in_progress')
        self.assertEqual(job.verified_count, 1)
        self.assertEqual(job.not_verified_count, 1)

    def test_04_verifying_remaining_asset_completes_job(self):
        asset_1 = self._create_asset(
            name='Complete Asset 1',
            barcode=self._barcode_for('COMP-1'),
            serial='SN-C1',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        asset_2 = self._create_asset(
            name='Complete Asset 2',
            barcode=self._barcode_for('COMP-2'),
            serial='SN-C2',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='Complete Job')

        verification_1 = self._create_verification(asset_1, job, description='First verification')
        verification_1.with_context(default_verification_job_id=job.id).action_verify()
        verification_2 = self._create_verification(asset_2, job, description='Second verification')
        verification_2.with_context(default_verification_job_id=job.id).action_verify()

        self.assertEqual(job.state, 'completed')
        self.assertEqual(job.verified_count, 2)
        self.assertEqual(job.not_verified_count, 0)
        self.assertTrue(all(job.asset_ids.mapped('verified')))

    def test_05_multiple_conditions_raise_and_do_not_verify_asset(self):
        asset = self._create_asset(
            name='Invalid Condition Asset',
            barcode=self._barcode_for('INVALID'),
            serial='SN-INVALID',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='Invalid Condition Job')
        verification = self._create_verification(
            asset,
            job,
            conditions=[self.good_condition.id, self.bad_condition.id],
        )

        with self.assertRaises(UserError):
            verification.with_context(default_verification_job_id=job.id).action_verify()

        self.assertFalse(job.asset_ids.filtered(lambda line: line.asset_id == asset).verified)
        self.assertEqual(job.state, 'draft')
        self.assertFalse(self.env['asset.verification.history'].search([('history_id', '=', asset.id)]))

    def test_06_history_uses_asset_job_location_when_verification_location_is_empty(self):
        asset = self._create_asset(
            name='Fallback Location Asset',
            barcode=self._barcode_for('FALLBACK'),
            serial='SN-FALLBACK',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='Fallback Location Job')
        verification = self._create_verification(asset, job, description='Fallback location verification')

        verification.with_context(default_verification_job_id=job.id).action_verify()
        history = self.env['asset.verification.history'].search([('history_id', '=', asset.id)], limit=1)

        self.assertEqual(history.location_id, self.job_location_a)
        self.assertEqual(history.parent_barcode, asset.alternative_ref)
        self.assertTrue(job.asset_ids.filtered(lambda line: line.asset_id == asset).verified)

    def test_07_update_assets_marks_previously_verified_assets_from_history(self):
        asset = self._create_asset(
            name='Refresh Verified Asset',
            barcode=self._barcode_for('REFRESH'),
            serial='SN-REFRESH',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        first_job = self._create_job(self.job_location_a, name='Initial Verification Job')
        verification = self._create_verification(asset, first_job, description='Initial verified history')
        verification.with_context(default_verification_job_id=first_job.id).action_verify()

        asset.write({'job_location_id': self.job_location_a.id})

        refreshed_job = self._create_job(self.job_location_a, name='Refreshed Verification Job')
        self.assertFalse(refreshed_job.asset_ids.filtered(lambda line: line.asset_id == asset).verified)

        refreshed_job.write({
            'verification_period_from': False,
            'verification_period_to': False,
        })
        refreshed_job.update_assets()
        refreshed_line = refreshed_job.asset_ids.filtered(lambda line: line.asset_id == asset)

        self.assertTrue(refreshed_line.verified)
        self.assertEqual(refreshed_job.verified_count, 1)
        self.assertEqual(refreshed_job.not_verified_count, refreshed_job.total_assets - 1)

    def test_08_default_get_without_history_sets_fallback_status_and_location(self):
        asset = self._create_asset(
            name='Default Get Asset',
            barcode=self._barcode_for('DEFAULT-NO-HISTORY'),
            serial='SN-DEFAULT-NO-HISTORY',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='Default Get Job')

        defaults = self.env['asset.verification'].with_context(
            default_asset_id=asset.id,
            default_verification_job_id=job.id,
        ).default_get(['asset_last_status', 'location_id'])

        self.assertEqual(defaults['asset_last_status'], 'No previous verification history found.')
        self.assertEqual(defaults['location_id'], self.job_location_a.id)

    def test_09_default_get_with_history_uses_latest_history_values(self):
        asset = self._create_asset(
            name='Default Get History Asset',
            barcode=self._barcode_for('DEFAULT-HISTORY'),
            serial='SN-DEFAULT-HISTORY',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='History Source Job')

        first_verification = self._create_verification(
            asset,
            job,
            description='History one',
            conditions=[self.good_condition.id],
        )
        first_verification.with_context(default_verification_job_id=job.id).action_verify()

        self.env['asset.verification.history'].create({
            'history_id': asset.id,
            'is_verified': True,
            'parent_barcode': asset.alternative_ref,
            'comments': self.bad_condition.name,
            'condition': [(6, 0, [self.bad_condition.id])],
            'location_id': self.job_location_a.id,
            'asset_verification_user_id': self.env.user.id,
        })

        defaults = self.env['asset.verification'].with_context(
            default_asset_id=asset.id,
            default_verification_job_id=job.id,
        ).default_get(['asset_last_status', 'location_id', 'condition'])

        self.assertEqual(defaults['asset_last_status'], self.bad_condition.name)
        self.assertEqual(defaults['location_id'], asset.job_location_id.id)
        self.assertTrue(defaults['condition'])

    def test_10_verify_without_images_or_optional_location_and_custodian_still_works(self):
        asset = self._create_asset(
            name='Optional Empty Asset',
            barcode=self._barcode_for('EMPTY-OPTIONAL'),
            serial='SN-EMPTY-OPTIONAL',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='Optional Empty Job')

        verification = self.env['asset.verification'].with_context(
            default_verification_job_id=job.id,
        ).create({
            'asset_id': asset.id,
            'barcode_number': asset.alternative_ref,
            'description': False,
            'verification_job_id': job.id,
            'condition': [(6, 0, [self.good_condition.id])],
        })
        verification.with_context(default_verification_job_id=job.id).action_verify()

        history = self.env['asset.verification.history'].search([('history_id', '=', asset.id)], limit=1)
        self.assertTrue(history)
        self.assertFalse(history.image_ids)
        self.assertFalse(history.major_group_description)
        self.assertEqual(asset.custodian_id, self.custodian)
        self.assertTrue(job.asset_ids.filtered(lambda line: line.asset_id == asset).verified)

    def test_11_verifying_asset_not_in_job_creates_history_but_does_not_mark_any_job_line(self):
        asset_in_job = self._create_asset(
            name='In Job Asset',
            barcode=self._barcode_for('IN-JOB'),
            serial='SN-IN-JOB',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        asset_not_in_job = self._create_asset(
            name='Out Of Job Asset',
            barcode=self._barcode_for('OUT-JOB'),
            serial='SN-OUT-JOB',
            job_location=self.job_location_b,
            stock_location=self.stock_location_b,
        )
        job = self._create_job(self.job_location_a, name='Mismatched Job')

        verification = self._create_verification(
            asset_not_in_job,
            job,
            description='Out-of-scope verification',
        )
        verification.with_context(default_verification_job_id=job.id).action_verify()

        history = self.env['asset.verification.history'].search([('history_id', '=', asset_not_in_job.id)], limit=1)
        in_job_line = job.asset_ids.filtered(lambda line: line.asset_id == asset_in_job)
        out_job_line = job.asset_ids.filtered(lambda line: line.asset_id == asset_not_in_job)

        self.assertTrue(history)
        self.assertTrue(in_job_line)
        self.assertFalse(in_job_line.verified)
        self.assertFalse(out_job_line)
        self.assertEqual(job.state, 'in_progress')
        self.assertEqual(job.verified_count, 0)

    def test_12_completion_percentage_updates_for_partial_and_complete_jobs(self):
        asset_1 = self._create_asset(
            name='Percent Asset 1',
            barcode=self._barcode_for('PERCENT-1'),
            serial='SN-PERCENT-1',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        asset_2 = self._create_asset(
            name='Percent Asset 2',
            barcode=self._barcode_for('PERCENT-2'),
            serial='SN-PERCENT-2',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='Completion Percentage Job')

        verification_1 = self._create_verification(asset_1, job, description='Half complete')
        verification_1.with_context(default_verification_job_id=job.id).action_verify()
        self.assertEqual(job.completion_percentage, 50.0)

        verification_2 = self._create_verification(asset_2, job, description='Fully complete')
        verification_2.with_context(default_verification_job_id=job.id).action_verify()
        self.assertEqual(job.completion_percentage, 100.0)

    def test_13_asset_condition_uses_latest_history_after_multiple_verifications(self):
        asset = self._create_asset(
            name='Latest Condition Asset',
            barcode=self._barcode_for('LATEST-CONDITION'),
            serial='SN-LATEST-CONDITION',
            job_location=self.job_location_a,
            stock_location=self.stock_location_a,
        )
        job = self._create_job(self.job_location_a, name='Latest Condition Job')

        first_verification = self._create_verification(
            asset,
            job,
            description='Good condition verification',
            conditions=[self.good_condition.id],
        )
        first_verification.with_context(default_verification_job_id=job.id).action_verify()

        second_verification = self._create_verification(
            asset,
            job,
            description='Bad condition verification',
            conditions=[self.bad_condition.id],
        )
        second_verification.with_context(default_verification_job_id=job.id).action_verify()
        asset.invalidate_recordset()
        histories = self.env['asset.verification.history'].search(
            [('history_id', '=', asset.id)]
        )
        history_comments = set(histories.mapped('comments'))

        self.assertIn(self.good_condition.name, history_comments)
        self.assertIn(self.bad_condition.name, history_comments)
        self.assertTrue(asset.latest_verification_history_id)
        self.assertEqual(asset.condition, asset.latest_verification_history_id.condition.name)