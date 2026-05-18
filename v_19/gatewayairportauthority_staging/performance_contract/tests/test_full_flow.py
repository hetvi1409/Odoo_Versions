# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError, AccessError
from odoo import fields
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'performance_contract')
class TestPerformanceContractFullFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # ---- Department & Job ----
        cls.department = cls.env['hr.department'].create({
            'name': 'Test Engineering Dept',
        })
        cls.job = cls.env['hr.job'].create({
            'name': 'Test Software Engineer',
            'department_id': cls.department.id,
        })

        # ---- Manager user (has ERP manager group for manager signing) ----
        cls.manager_user = cls.env['res.users'].create({
            'name': 'Test Manager User',
            'login': 'test_pc_manager@test.com',
            'email': 'test_pc_manager@test.com',
            'group_ids': [
                (4, cls.env.ref('base.group_user').id),
                (4, cls.env.ref('base.group_erp_manager').id),
            ],
        })

        # ---- Regular employee user (for employee signing) ----
        cls.employee_user = cls.env['res.users'].create({
            'name': 'Test Employee User',
            'login': 'test_pc_employee@test.com',
            'email': 'test_pc_employee@test.com',
            'group_ids': [
                (4, cls.env.ref('base.group_user').id),
            ],
        })

        # ---- Another user (unauthorized - no special groups) ----
        cls.unauthorized_user = cls.env['res.users'].create({
            'name': 'Test Unauthorized User',
            'login': 'test_pc_unauth@test.com',
            'email': 'test_pc_unauth@test.com',
            'group_ids': [
                (4, cls.env.ref('base.group_user').id),
            ],
        })

        # ---- Approver users (for multi-step approval) ----
        cls.approver_user_1 = cls.env['res.users'].create({
            'name': 'Approver One',
            'login': 'test_pc_approver1@test.com',
            'email': 'test_pc_approver1@test.com',
            'group_ids': [(4, cls.env.ref('base.group_user').id)],
        })
        cls.approver_user_2 = cls.env['res.users'].create({
            'name': 'Approver Two',
            'login': 'test_pc_approver2@test.com',
            'email': 'test_pc_approver2@test.com',
            'group_ids': [(4, cls.env.ref('base.group_user').id)],
        })

        # ---- Manager employee (linked to manager_user) ----
        cls.manager_employee = cls.env['hr.employee'].create({
            'name': 'Test Manager',
            'user_id': cls.manager_user.id,
            'department_id': cls.department.id,
            'job_id': cls.job.id,
            'work_email': 'test_pc_manager@test.com',
        })

        # ---- Regular employee (linked to employee_user, reports to manager) ----
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
            'user_id': cls.employee_user.id,
            'department_id': cls.department.id,
            'job_id': cls.job.id,
            'parent_id': cls.manager_employee.id,
            'work_email': 'test_pc_employee@test.com',
        })

        # ---- Approval Team with 2 approvers ----
        cls.approval_team = cls.env['approval.team'].create({
            'name': 'Test Approval Team',
            'model': 'performance.contract',
            'line_ids': [
                (0, 0, {'user_id': cls.approver_user_1.id, 'sequence': 1}),
                (0, 0, {'user_id': cls.approver_user_2.id, 'sequence': 2}),
            ],
        })

        _logger.info("Performance Contract full-flow setup complete.")

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _create_contract(self, employee=None, **kwargs):
        """
        Helper: create a performance contract with sane defaults.
        Auto-assigns the test employee if none given.
        """
        vals = {
            'employee_id': (employee or self.employee).id,
        }
        vals.update(kwargs)
        return self.env['performance.contract'].create(vals)

    def _create_goal(self, name='Test Goal', weightage=50, employee=None, **kwargs):
        """
        Helper: create an appraisal goal with given weightage.
        """
        emp = employee or self.employee
        vals = {
            'name': name,
            'employee_id': emp.id,
            'employee_ids': [(6, 0, [emp.id])],
            'weightage': weightage,
            'deadline': date.today() + timedelta(days=30),
        }
        vals.update(kwargs)
        return self.env['hr.appraisal.goal'].create(vals)

    def _create_contract_with_goals_100(self):
        """
        Helper: create a contract with goals totaling exactly 100% weightage.
        Returns (contract, [goal1, goal2]).
        """
        goal1 = self._create_goal('Goal A', weightage=60)
        goal2 = self._create_goal('Goal B', weightage=40)
        contract = self._create_contract(
            goal_ids=[(6, 0, [goal1.id, goal2.id])]
        )
        return contract, [goal1, goal2]

    # ==================================================================
    # This flow tests the complete lifecycle of a contract with all correct inputs
    # ==================================================================

    def test_flow1_01_create_contract_correct_values(self):
        """
        FLOW 1  Step 1: Create a contract with all correct values.
        Contract should get auto-sequence name, default state='draft',
        start_date=today, end_date=Dec 31 of current year.
        """
        contract = self._create_contract()

        # Contract should be created successfully
        self.assertTrue(contract.id, "Contract should be created successfully")

        # Auto-sequence name should not be 'New'
        self.assertNotEqual(contract.name, 'New',
                            "Sequence should generate a proper name")

        # Default state should be 'draft'
        self.assertEqual(contract.state, 'draft',
                         "New contract should be in draft state")

        # Start date should be today
        self.assertEqual(contract.start_date, date.today(),
                         "Start date should default to today")

        # End date should be Dec 31 of current year
        self.assertEqual(contract.end_date, date.today().replace(month=12, day=31),
                         "End date should default to Dec 31 of current year")

        # Related fields should populate from employee
        self.assertEqual(contract.manager_id, self.manager_employee.name,
                         "Manager should come from employee's parent")
        self.assertEqual(contract.department_id, self.department.name,
                         "Department should come from employee")
        self.assertEqual(contract.job_id, self.job.name,
                         "Job position should come from employee")

        _logger.info("FLOW 1 Step 1 PASSED: Contract created with correct values.")

    def test_flow1_02_submit_for_approval_with_100_weightage(self):
        """
        FLOW 1 Step 2: Submit contract for approval.
        Weightage must total 100. State should move to 'in_process'.
        """
        contract, goals = self._create_contract_with_goals_100()

        # Verify total weightage is 100
        self.assertEqual(contract.total_weightage, 100,
                         "Total weightage should be 100")

        # Submit for approval
        contract.action_submit_for_approval()

        self.assertEqual(contract.state, 'in_process',
                         "State should be 'in_process' after submission")
        _logger.info("FLOW 1 Step 2 PASSED: Contract submitted with 100%% weightage.")

    def test_flow1_03_employee_signs_contract(self):
        """
        FLOW 1 Step 3: Employee signs the contract.
        Must be done by the employee user linked to the contract.
        State should move to 'signed_by_employee'.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()

        # Employee signs (using the correct employee user)
        contract.with_user(self.employee_user).employee_sign_contract()

        self.assertEqual(contract.state, 'signed_by_employee',
                         "State should be 'signed_by_employee' after employee signs")
        self.assertTrue(contract.signed_by_employee,
                        "signed_by_employee flag should be True")
        self.assertTrue(contract.employee_sign_date,
                        "Employee sign date should be set")
        _logger.info("FLOW 1 Step 3 PASSED: Employee signed the contract.")

    def test_flow1_04_manager_signs_contract(self):
        """
        FLOW 1 Step 4: Manager signs the contract.
        Must be done by a user with ERP manager group.
        State should move to 'signed_by_manager'.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()

        # Manager signs (using the manager user who has ERP manager group)
        contract.with_user(self.manager_user).manager_sign_contract()

        self.assertEqual(contract.state, 'signed_by_manager',
                         "State should be 'signed_by_manager' after manager signs")
        self.assertTrue(contract.signed_by_manager,
                        "signed_by_manager flag should be True")
        self.assertTrue(contract.manager_sign_date,
                        "Manager sign date should be set")
        _logger.info("FLOW 1 Step 4 PASSED: Manager signed the contract.")

    def test_flow1_05_mark_signed_with_both_signatures(self):
        """
        FLOW 1 Step 5: Mark contract as signed.
        Both employee_sign and manager_sign binary fields must be present.
        State should move to 'signed'.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()

        # Simulate actual signature binaries
        contract.employee_sign = 'iVBORw0KGgo='  # dummy base64 data
        contract.manager_sign = 'iVBORw0KGgo='   # dummy base64 data

        contract.action_mark_signed()

        self.assertEqual(contract.state, 'signed',
                         "State should be 'signed' after both signatures confirmed")
        _logger.info("FLOW 1 Step 5 PASSED: Contract marked as signed.")

    def test_flow1_06_start_approval_process(self):
        """
        FLOW 1 Step 6: Start the multi-step approval process.
        Approval team lines should be created. State → 'approval_in_process'.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()

        # Set approval team and start process
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()

        self.assertEqual(contract.state, 'approval_in_process',
                         "State should be 'approval_in_process'")
        self.assertEqual(contract.approval_status, 'partially_approved',
                         "Approval status should be 'partially_approved'")
        self.assertEqual(len(contract.approval_line_ids), 2,
                         "Should have 2 approval lines from the team")
        self.assertEqual(contract.current_approver_id, self.approver_user_1,
                         "First approver should be the current approver")
        _logger.info("FLOW 1 Step 6 PASSED: Approval process started.")

    def test_flow1_07_first_approver_approves(self):
        """
        FLOW 1 Step 7: First approver approves the contract.
        Status should remain 'partially_approved' since second approver is pending.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()

        # First approver approves
        contract.with_user(self.approver_user_1).acction_approve_contract()

        # First line should be approved
        first_line = contract.approval_line_ids.filtered(
            lambda l: l.user_id == self.approver_user_1
        )
        self.assertEqual(first_line.status, 'approved',
                         "First approver's line should be 'approved'")
        self.assertTrue(first_line.approved,
                        "First approver's approved flag should be True")
        self.assertTrue(first_line.approval_date,
                        "Approval date should be set")

        # Second approver should now be current
        self.assertEqual(contract.current_approver_id, self.approver_user_2,
                         "Second approver should now be the current approver")
        _logger.info("FLOW 1 Step 7 PASSED: First approver approved.")

    def test_flow1_08_second_approver_approves_fully_approved(self):
        """
        FLOW 1 Step 8: Second approver approves → fully approved.
        State should move to 'approved', approval_status to 'fully_approved'.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()
        contract.with_user(self.approver_user_1).acction_approve_contract()

        # Second approver approves
        contract.with_user(self.approver_user_2).acction_approve_contract()

        self.assertEqual(contract.state, 'approved',
                         "State should be 'approved' after all approvers approve")
        self.assertEqual(contract.approval_status, 'fully_approved',
                         "Approval status should be 'fully_approved'")
        _logger.info("FLOW 1 Step 8 PASSED: All approvers approved, contract fully approved.")

    def test_flow1_09_mark_done(self):
        """
        FLOW 1 Step 9: Mark contract as done (completed).
        State should move to 'done'.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()
        contract.with_user(self.approver_user_1).acction_approve_contract()
        contract.with_user(self.approver_user_2).acction_approve_contract()

        # Mark as done
        contract.action_mark_done()

        self.assertEqual(contract.state, 'done',
                         "State should be 'done' after marking complete")
        _logger.info("FLOW 1 Step 9 PASSED: Contract marked as done.")

    def test_flow1_10_set_to_draft_resets_state(self):
        """
        FLOW 1 Step 10: Reset contract back to draft.
        State should return to 'draft' from any state.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()

        # Contract is in 'in_process'
        self.assertEqual(contract.state, 'in_process')

        # Reset to draft
        contract.action_set_to_draft()

        self.assertEqual(contract.state, 'draft',
                         "State should be 'draft' after reset")
        _logger.info("FLOW 1 Step 10 PASSED: Contract reset to draft.")

    # ==================================================================
    # FLOW 2 – WRONG / INVALID VALUES
    # ==================================================================

    def test_flow2_01_submit_without_100_weightage_raises_error(self):
        """
        FLOW 2 Wrong value: Submit when total weightage is NOT 100.
        Should raise UserError because weightage must equal 100 to submit.
        """
        # Create a goal with only 50% weightage (not 100)
        goal = self._create_goal('Partial Goal', weightage=50)
        contract = self._create_contract(
            goal_ids=[(6, 0, [goal.id])]
        )
        self.assertEqual(contract.total_weightage, 50,
                         "Weightage should be 50, not 100")

        # Submitting should raise UserError
        with self.assertRaises(UserError):
            contract.action_submit_for_approval()

        _logger.info("FLOW 2 Test 1 PASSED: Error raised for weightage != 100.")

    def test_flow2_02_unauthorized_employee_sign_raises_error(self):
        """
        FLOW 2 Wrong user: A different user tries to sign as employee.
        Should raise AccessError because only the linked employee can sign.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()

        # Unauthorized user tries to sign as employee
        with self.assertRaises(AccessError):
            contract.with_user(self.unauthorized_user).employee_sign_contract()

        _logger.info("FLOW 2 Test 2 PASSED: Error raised for unauthorized employee sign.")

    def test_flow2_03_non_manager_cannot_sign_as_manager(self):
        """
        FLOW 2 Wrong user: A regular user (no ERP manager group) tries
        to sign as manager. Should raise AccessError.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()

        # Regular employee user tries to sign as manager (no ERP manager group)
        with self.assertRaises(AccessError):
            contract.with_user(self.employee_user).manager_sign_contract()

        _logger.info("FLOW 2 Test 3 PASSED: Error raised for non-manager trying to sign.")

    def test_flow2_04_mark_signed_without_both_signatures_raises_error(self):
        """
        FLOW 2 Missing data: Try to mark as signed when one or both
        signature binary fields are empty. Should raise UserError.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()

        # Do NOT set signature binaries — leave employee_sign and manager_sign empty
        # Only set employee_sign, leave manager_sign empty
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = False

        with self.assertRaises(UserError):
            contract.action_mark_signed()

        _logger.info("FLOW 2 Test 4 PASSED: Error raised when signatures missing.")

    def test_flow2_05_unauthorized_approver_raises_error(self):
        """
        FLOW 2 Wrong user: User who is NOT the current approver tries
        to approve the contract. Should raise AccessError.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()

        # Approver 2 tries to approve FIRST (but approver 1 should go first)
        with self.assertRaises(AccessError):
            contract.with_user(self.approver_user_2).acction_approve_contract()

        _logger.info("FLOW 2 Test 5 PASSED: Error raised for wrong order approver.")

    def test_flow2_06_unauthorized_rejector_raises_error(self):
        """
        FLOW 2 Wrong user: User who is NOT the current approver tries
        to reject the contract. Should raise AccessError.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()

        # Unauthorized user tries to reject
        with self.assertRaises(AccessError):
            contract.with_user(self.unauthorized_user).action_reject_contract()

        _logger.info("FLOW 2 Test 6 PASSED: Error raised for unauthorized rejection.")

    def test_flow2_07_weightage_exceeding_100_raises_error(self):
        """
        FLOW 2 Wrong value: Goals with total weightage > 100.
        Should raise UserError from the constraint check.
        """
        goal1 = self._create_goal('Over Goal A', weightage=70)
        goal2 = self._create_goal('Over Goal B', weightage=40)

        # Creating contract with goals totaling 110% should trigger constraint
        with self.assertRaises(UserError):
            self._create_contract(
                goal_ids=[(6, 0, [goal1.id, goal2.id])]
            )

        _logger.info("FLOW 2 Test 7 PASSED: Error raised for weightage > 100.")

    def test_flow2_08_double_approve_raises_error(self):
        """
        FLOW 2 Wrong action: Same approver tries to approve twice.
        Should raise AccessError (already approved, no pending line).
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()

        # First approve (should succeed)
        contract.with_user(self.approver_user_1).acction_approve_contract()

        # Try to approve again (should fail - already approved)
        with self.assertRaises(AccessError):
            contract.with_user(self.approver_user_1).acction_approve_contract()

        _logger.info("FLOW 2 Test 8 PASSED: Error raised for double approval.")

    # ==================================================================
    # FLOW 3 – NULL / EMPTY VALUES
    # ==================================================================

    def test_flow3_01_create_contract_without_goals(self):
        """
        FLOW 3 – Null goals: Create a contract with no goals.
        Should create successfully. Total weightage should be 0.
        """
        contract = self._create_contract()

        self.assertTrue(contract.id, "Contract should be created without goals")
        self.assertEqual(len(contract.goal_ids), 0,
                         "No goals should be linked")
        self.assertEqual(contract.total_weightage, 0,
                         "Total weightage should be 0 with no goals")
        _logger.info("FLOW 3 Test 1 PASSED: Contract created without goals.")

    def test_flow3_02_contract_default_priority(self):
        """
        FLOW 3 – Default priority: Contract should default to '1' (Normal).
        """
        contract = self._create_contract()

        self.assertEqual(contract.priority, '1',
                         "Default priority should be '1' (Normal)")
        _logger.info("FLOW 3 Test 2 PASSED: Default priority is Normal.")

    def test_flow3_03_contract_no_attachments(self):
        """
        FLOW 3 – No attachments: New contract should have attachment_count = 0.
        """
        contract = self._create_contract()

        self.assertEqual(contract.attachment_count, 0,
                         "Attachment count should be 0 for new contract")
        _logger.info("FLOW 3 Test 3 PASSED: No attachments by default.")

    def test_flow3_04_contract_no_approval_team(self):
        """
        FLOW 3 – Null approval team: Start approval without an explicit team.
        If exactly one team exists for this model, it auto-assigns.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()

        # Don't set an approval team — let the system find one
        # Note: this may auto-assign if only one team exists,
        # or raise UserError if multiple teams exist
        existing_teams = self.env['approval.team'].search([
            ('model', '=', 'performance.contract')
        ])
        if len(existing_teams) == 1:
            contract.action_start_approval_process()
            self.assertEqual(contract.approval_team_id, existing_teams,
                             "Should auto-assign the only available team")
        elif len(existing_teams) > 1:
            with self.assertRaises(UserError):
                contract.action_start_approval_process()
        else:
            # No teams exist — should still not crash
            contract.action_start_approval_process()
            self.assertFalse(contract.approval_line_ids,
                             "No approval lines without a team")

        _logger.info("FLOW 3 Test 4 PASSED: Approval process handles null team.")

    def test_flow3_05_no_employee_signatures_initially(self):
        """
        FLOW 3 – Null signatures: New contract should have no signatures.
        """
        contract = self._create_contract()

        self.assertFalse(contract.employee_sign,
                         "Employee signature should be empty initially")
        self.assertFalse(contract.manager_sign,
                         "Manager signature should be empty initially")
        self.assertFalse(contract.signed_by_employee,
                         "signed_by_employee should be False initially")
        self.assertFalse(contract.signed_by_manager,
                         "signed_by_manager should be False initially")
        self.assertFalse(contract.employee_sign_date,
                         "Employee sign date should be empty initially")
        self.assertFalse(contract.manager_sign_date,
                         "Manager sign date should be empty initially")
        _logger.info("FLOW 3 Test 5 PASSED: No signatures on new contract.")

    def test_flow3_06_approval_status_default(self):
        """
        FLOW 3 – Default approval status: Should be 'not_started' initially.
        """
        contract = self._create_contract()

        self.assertEqual(contract.approval_status, 'not_started',
                         "Default approval status should be 'not_started'")
        _logger.info("FLOW 3 Test 6 PASSED: Default approval_status is not_started.")

    # ==================================================================
    # FLOW 4 – APPROVAL PROCESS FLOW
    # ==================================================================

    def test_flow4_01_rejection_by_first_approver(self):
        """
        FLOW 4 – Rejection: First approver rejects the contract.
        State should move to 'rejected', approval_status to 'rejected'.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()

        # First approver rejects
        contract.with_user(self.approver_user_1).action_reject_contract()

        self.assertEqual(contract.state, 'rejected',
                         "State should be 'rejected' after rejection")
        self.assertEqual(contract.approval_status, 'rejected',
                         "Approval status should be 'rejected'")

        # The rejected line should have status 'rejected'
        rejected_line = contract.approval_line_ids.filtered(
            lambda l: l.user_id == self.approver_user_1
        )
        self.assertEqual(rejected_line.status, 'rejected',
                         "Rejected user's line should have status 'rejected'")
        _logger.info("FLOW 4 Test 1 PASSED: First approver rejection works.")

    def test_flow4_02_action_reject_resets_all(self):
        """
        FLOW 4 – Full rejection: action_reject sets state to 'rejected'
        and resets all approval lines to approved=False.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()

        # Use the direct action_reject method
        contract.action_reject()

        self.assertEqual(contract.state, 'rejected',
                         "State should be 'rejected'")

        # All approval lines should have approved=False
        for line in contract.approval_line_ids:
            self.assertFalse(line.approved,
                             f"Approval line for {line.user_id.name} should be False")
        _logger.info("FLOW 4 Test 2 PASSED: Full reject resets all lines.")

    def test_flow4_03_approval_lines_created_in_order(self):
        """
        FLOW 4 – Order: Approval lines should be created in the correct
        sequence order matching the approval team.
        """
        contract, goals = self._create_contract_with_goals_100()
        contract.action_submit_for_approval()
        contract.with_user(self.employee_user).employee_sign_contract()
        contract.with_user(self.manager_user).manager_sign_contract()
        contract.employee_sign = 'iVBORw0KGgo='
        contract.manager_sign = 'iVBORw0KGgo='
        contract.action_mark_signed()
        contract.approval_team_id = self.approval_team.id
        contract.action_start_approval_process()

        sorted_lines = contract.approval_line_ids.sorted('sequence')

        # First line should be approver 1
        self.assertEqual(sorted_lines[0].user_id, self.approver_user_1,
                         "First approval line should be approver 1")
        # Second line should be approver 2
        self.assertEqual(sorted_lines[1].user_id, self.approver_user_2,
                         "Second approval line should be approver 2")

        # All should start as 'pending'
        for line in sorted_lines:
            self.assertEqual(line.status, 'pending',
                             f"All lines should start as 'pending', got {line.status}")
            self.assertFalse(line.approved, "approved should be False initially")
        _logger.info("FLOW 4 Test 3 PASSED: Approval lines in correct order.")

    def test_flow4_04_mark_as_completed_shortcut(self):
        """
        FLOW 4 – Shortcut: mark_as_complated() sets state to 'done' directly.
        """
        contract = self._create_contract()
        contract.mark_as_complated()

        self.assertEqual(contract.state, 'done',
                         "mark_as_complated should set state to 'done'")
        _logger.info("FLOW 4 Test 4 PASSED: mark_as_complated works.")

    # ==================================================================
    # FLOW 5 – COMPUTED FIELDS & CONSTRAINTS
    # ==================================================================

    def test_flow5_01_total_weightage_computed_correctly(self):
        """
        FLOW 5 – Compute: total_weightage should sum all goal weightages.
        """
        goal1 = self._create_goal('Compute Goal A', weightage=30)
        goal2 = self._create_goal('Compute Goal B', weightage=25)
        goal3 = self._create_goal('Compute Goal C', weightage=45)
        contract = self._create_contract(
            goal_ids=[(6, 0, [goal1.id, goal2.id, goal3.id])]
        )

        self.assertEqual(contract.total_weightage, 100,
                         "30 + 25 + 45 should equal 100")
        _logger.info("FLOW 5 Test 1 PASSED: Total weightage computed correctly.")

    def test_flow5_02_total_weightage_zero_no_goals(self):
        """
        FLOW 5 – Compute: total_weightage = 0 when no goals linked.
        """
        contract = self._create_contract()

        self.assertEqual(contract.total_weightage, 0,
                         "Weightage should be 0 with no goals")
        _logger.info("FLOW 5 Test 2 PASSED: Zero weightage with no goals.")

    def test_flow5_03_is_locked_compute(self):
        """
        FLOW 5 – Compute: is_locked should be False for 'draft',
        True for all other states.
        """
        contract = self._create_contract()

        # Draft state
        self.assertFalse(contract.is_locked,
                         "Draft contract should NOT be locked")

        # Change to in_process
        contract.state = 'in_process'
        contract.invalidate_recordset()
        self.assertTrue(contract.is_locked,
                        "in_process contract should be locked")

        # Change to signed
        contract.state = 'signed'
        contract.invalidate_recordset()
        self.assertTrue(contract.is_locked,
                        "signed contract should be locked")

        # Change to done
        contract.state = 'done'
        contract.invalidate_recordset()
        self.assertTrue(contract.is_locked,
                        "done contract should be locked")
        _logger.info("FLOW 5 Test 3 PASSED: is_locked computed for all states.")

    def test_flow5_04_final_result_computation(self):
        """
        FLOW 5 – Compute: final_result is the weighted average of results / 100.
        Formula: sum(result * weightage) / total_weightage / 100
        """
        goal1 = self._create_goal('Result Goal A', weightage=60, result=80)
        goal2 = self._create_goal('Result Goal B', weightage=40, result=90)
        contract = self._create_contract(
            goal_ids=[(6, 0, [goal1.id, goal2.id])]
        )

        # Expected: ((80*60) + (90*40)) / 100 / 100 = (4800 + 3600) / 100 / 100 = 0.84
        expected_result = ((80 * 60) + (90 * 40)) / 100 / 100
        self.assertAlmostEqual(contract.final_result, expected_result, places=2,
                               msg="Final result should be weighted average / 100")
        _logger.info("FLOW 5 Test 4 PASSED: final_result computed correctly.")

    def test_flow5_05_final_result_zero_when_no_weightage(self):
        """
        FLOW 5 – Compute: final_result = 0 when total_weightage is 0.
        Avoids division by zero.
        """
        contract = self._create_contract()  # No goals

        self.assertEqual(contract.final_result, 0.0,
                         "Final result should be 0 with no weightage")
        _logger.info("FLOW 5 Test 5 PASSED: final_result 0 with no goals.")

    def test_flow5_06_goal_status_based_on_result(self):
        """
        FLOW 5 – Compute: Goal status should be computed based on result value.
        80-100 = good, 50-79 = average, 25-49 = below_average, else = poor.
        """
        # Good (80-100)
        goal_good = self._create_goal('Good Goal', result=85)
        self.assertEqual(goal_good.status, 'good',
                         "Result 85 should be 'good'")

        # Average (50-79)
        goal_avg = self._create_goal('Average Goal', result=65)
        self.assertEqual(goal_avg.status, 'average',
                         "Result 65 should be 'average'")

        # Below Average (25-49)
        goal_below = self._create_goal('Below Average Goal', result=30)
        self.assertEqual(goal_below.status, 'below_average',
                         "Result 30 should be 'below_average'")

        # Poor (< 25)
        goal_poor = self._create_goal('Poor Goal', result=10)
        self.assertEqual(goal_poor.status, 'poor',
                         "Result 10 should be 'poor'")

        # Boundary: exactly 80 → good
        goal_boundary_80 = self._create_goal('Boundary 80', result=80)
        self.assertEqual(goal_boundary_80.status, 'good',
                         "Result 80 should be 'good' (boundary)")

        # Boundary: exactly 50 → average
        goal_boundary_50 = self._create_goal('Boundary 50', result=50)
        self.assertEqual(goal_boundary_50.status, 'average',
                         "Result 50 should be 'average' (boundary)")

        # Boundary: exactly 25 → below_average
        goal_boundary_25 = self._create_goal('Boundary 25', result=25)
        self.assertEqual(goal_boundary_25.status, 'below_average',
                         "Result 25 should be 'below_average' (boundary)")

        # Boundary: 0 → poor
        goal_zero = self._create_goal('Zero Result', result=0)
        self.assertEqual(goal_zero.status, 'poor',
                         "Result 0 should be 'poor'")
        _logger.info("FLOW 5 Test 6 PASSED: Goal status computed for all ranges.")

    def test_flow5_07_goal_status_boundary_values(self):
        """
        FLOW 5 – Boundary: Test goal status at exact boundaries.
        79 = average, 49 = below_average, 24 = poor, 100 = good.
        """
        goal_79 = self._create_goal('Boundary 79', result=79)
        self.assertEqual(goal_79.status, 'average',
                         "Result 79 should be 'average'")

        goal_49 = self._create_goal('Boundary 49', result=49)
        self.assertEqual(goal_49.status, 'below_average',
                         "Result 49 should be 'below_average'")

        goal_24 = self._create_goal('Boundary 24', result=24)
        self.assertEqual(goal_24.status, 'poor',
                         "Result 24 should be 'poor'")

        goal_100 = self._create_goal('Boundary 100', result=100)
        self.assertEqual(goal_100.status, 'good',
                         "Result 100 should be 'good'")
        _logger.info("FLOW 5 Test 7 PASSED: All boundary values correct.")

    def test_flow5_08_attachment_count_compute(self):
        """
        FLOW 5 – Compute: attachment_count should reflect linked attachments.
        """
        contract = self._create_contract()

        # Initially no attachments
        self.assertEqual(contract.attachment_count, 0)

        # Create an attachment linked to this contract
        self.env['ir.attachment'].create({
            'name': 'Test Attachment',
            'res_model': 'performance.contract',
            'res_id': contract.id,
            'datas': 'dGVzdA==',  # base64 of "test"
        })

        # Invalidate cache and recheck
        contract.invalidate_recordset()
        self.assertEqual(contract.attachment_count, 1,
                         "Attachment count should be 1 after adding one")
        _logger.info("FLOW 5 Test 8 PASSED: Attachment count computed correctly.")

    def test_flow5_09_action_open_attachments_returns_action(self):
        """
        FLOW 5 – Action: action_open_attachments should return a valid
        window action dict with correct domain.
        """
        contract = self._create_contract()
        action = contract.action_open_attachments()

        self.assertEqual(action['type'], 'ir.actions.act_window',
                         "Should return a window action")
        self.assertEqual(action['res_model'], 'ir.attachment',
                         "Action should target ir.attachment model")
        self.assertIn('domain', action, "Action should have a domain")
        _logger.info("FLOW 5 Test 9 PASSED: Attachment action returns valid dict.")

    # ==================================================================
    # FLOW 6 – WIZARD TESTS (Multi Goal Management)
    # ==================================================================

    def test_flow6_01_multi_goal_wizard_creates_goals(self):
        """
        FLOW 6 – Wizard: Multi goal management wizard should create
        a separate goal for each selected employee.
        """
        # Create a second employee for testing
        emp2 = self.env['hr.employee'].create({
            'name': 'Second Test Employee',
            'department_id': self.department.id,
        })

        goal_count_before = self.env['hr.appraisal.goal'].search_count([])

        # Run the wizard
        wizard = self.env['multi.goal.managment'].create({
            'employee_ids': [(6, 0, [self.employee.id, emp2.id])],
            'name': 'Wizard Goal For All',
            'deadline': date.today() + timedelta(days=60),
            'description': '<p>Test description from wizard</p>',
        })
        wizard.action_apply_goals()

        goal_count_after = self.env['hr.appraisal.goal'].search_count([])

        # Should have created 2 new goals (one per employee)
        self.assertEqual(goal_count_after - goal_count_before, 2,
                         "Wizard should create 1 goal per employee (2 total)")

        # Verify goals exist for each employee
        goals_emp1 = self.env['hr.appraisal.goal'].search([
            ('name', '=', 'Wizard Goal For All'),
            ('employee_id', '=', self.employee.id),
        ])
        goals_emp2 = self.env['hr.appraisal.goal'].search([
            ('name', '=', 'Wizard Goal For All'),
            ('employee_id', '=', emp2.id),
        ])
        self.assertTrue(goals_emp1, "Goal should exist for employee 1")
        self.assertTrue(goals_emp2, "Goal should exist for employee 2")
        _logger.info("FLOW 6 Test 1 PASSED: Wizard creates goal per employee.")

    def test_flow6_02_wizard_goal_has_correct_data(self):
        """
        FLOW 6 – Wizard data: Goals created by wizard should have
        the correct name, deadline, and description.
        """
        wizard = self.env['multi.goal.managment'].create({
            'employee_ids': [(6, 0, [self.employee.id])],
            'name': 'Wizard Data Check Goal',
            'deadline': date(2026, 6, 30),
            'description': '<p>Wizard test description</p>',
        })
        wizard.action_apply_goals()

        goal = self.env['hr.appraisal.goal'].search([
            ('name', '=', 'Wizard Data Check Goal'),
            ('employee_id', '=', self.employee.id),
        ], limit=1)

        self.assertTrue(goal, "Goal should be created")
        self.assertEqual(goal.name, 'Wizard Data Check Goal')
        self.assertEqual(goal.deadline, date(2026, 6, 30))
        self.assertEqual(goal.employee_id.id, self.employee.id)
        _logger.info("FLOW 6 Test 2 PASSED: Wizard goal has correct data.")

    # ==================================================================
    # FLOW 7 – CRON JOB TESTS
    # ==================================================================

    def test_flow7_01_expired_contract_cron(self):
        """
        FLOW 7 – Cron: Contracts past their end_date should be marked as 'expired'.
        The cron checks for contracts where end_date < today and state != 'expired'.
        """
        # Create a contract with a past end_date
        contract = self._create_contract()
        contract.write({
            'end_date': date.today() - timedelta(days=5),  # 5 days in the past
        })

        # State should still be draft (cron hasn't run yet)
        self.assertEqual(contract.state, 'draft')

        # Simulate the cron job
        self.env['performance.contract'].performance_contract_expire_check()

        # Contract should now be expired
        contract.invalidate_recordset()
        self.assertEqual(contract.state, 'expired',
                         "Contract with past end_date should be marked 'expired'")
        _logger.info("FLOW 7 Test 1 PASSED: Expired contract cron works.")

    def test_flow7_02_non_expired_contract_not_affected(self):
        """
        FLOW 7 – Cron: Contracts with future end_date should NOT be expired.
        """
        contract = self._create_contract()  # end_date = Dec 31 (future)

        # Run cron
        self.env['performance.contract'].performance_contract_expire_check()

        contract.invalidate_recordset()
        self.assertNotEqual(contract.state, 'expired',
                            "Contract with future end_date should NOT be expired")
        _logger.info("FLOW 7 Test 2 PASSED: Future contract not affected by cron.")

    def test_flow7_03_already_expired_not_reprocessed(self):
        """
        FLOW 7 – Cron: Already expired contracts should not be reprocessed.
        The cron filters state != 'expired', so already expired ones are skipped.
        """
        contract = self._create_contract()
        contract.write({
            'end_date': date.today() - timedelta(days=10),
            'state': 'expired',
        })

        # Run cron — should not modify already expired contract
        self.env['performance.contract'].performance_contract_expire_check()

        contract.invalidate_recordset()
        self.assertEqual(contract.state, 'expired',
                         "Already expired contract should stay expired")
        _logger.info("FLOW 7 Test 3 PASSED: Already expired contract not reprocessed.")

    def test_flow7_04_goal_deadline_reminder_cron(self):
        """
        FLOW 7 – Cron: Goal deadline reminder should find goals whose deadline
        matches today + send_mail_before days and progression != 100.
        This test just verifies the method runs without errors.
        """
        # Set send_mail_before parameter
        self.env['ir.config_parameter'].sudo().set_param(
            'performance_contract.send_mail_before', '3'
        )

        # Create a goal with deadline = today + 3 days
        goal = self._create_goal(
            'Reminder Test Goal',
            deadline=date.today() + timedelta(days=3),
        )
        # Ensure goal progression is not 100
        goal.progression = '000'

        # Run the reminder cron — should not crash
        # (actual email sending may not happen in test env but method should execute)
        try:
            self.env['performance.contract'].send_goal_deadline_reminders()
            cron_ran = True
        except Exception:
            cron_ran = False

        self.assertTrue(cron_ran,
                        "Goal deadline reminder cron should run without errors")
        _logger.info("FLOW 7 Test 4 PASSED: Goal reminder cron runs successfully.")

    # ==================================================================
    # ██  FLOW ADDITIONAL – TEMPLATE & CONFIG TESTS
    # ==================================================================

    def test_extra_01_performance_contract_template_create(self):
        """
        EXTRA – Template: Create a performance contract template.
        Should be active by default.
        """
        template = self.env['performance.contract.template'].create({
            'name': 'Test Template',
            'description': 'A test template for performance contracts',
        })

        self.assertTrue(template.id, "Template should be created")
        self.assertEqual(template.name, 'Test Template')
        self.assertTrue(template.active, "Template should be active by default")
        _logger.info("EXTRA Test 1 PASSED: Template created and active.")

    def test_extra_02_res_config_settings_send_mail_before(self):
        """
        EXTRA Config: send_mail_before parameter should be settable
        via config settings and retrievable.
        """
        # Set value
        self.env['ir.config_parameter'].sudo().set_param(
            'performance_contract.send_mail_before', '7'
        )

        # Read back
        value = int(self.env['ir.config_parameter'].sudo().get_param(
            'performance_contract.send_mail_before', default=3
        ))
        self.assertEqual(value, 7,
                         "send_mail_before should be 7 after setting")
        _logger.info("EXTRA Test 2 PASSED: Config parameter works correctly.")

    def test_extra_03_approval_team_model_compute(self):
        """
        EXTRA  Approval Team: model_id computed field should return
        the correct ir.model record for the 'performance.contract' model.
        """
        team = self.approval_team

        expected_model = self.env['ir.model']._get('performance.contract')
        self.assertEqual(team.model_id, expected_model,
                         "model_id should match performance.contract model")
        self.assertEqual(team.model, 'performance.contract',
                         "model field should be 'performance.contract'")
        _logger.info("EXTRA Test 3 PASSED: Approval team model compute works.")

    def test_extra_04_current_employee_skills_compute(self):
        """
        EXTRA  Compute: current_employee_skill_new_ids should return
        the skills linked to the contract's employee.
        """
        contract = self._create_contract()

        # If the employee has skills, they should appear; if not, should be empty
        employee_skills = self.employee.employee_skill_ids
        self.assertEqual(
            len(contract.current_employee_skill_new_ids),
            len(employee_skills),
            "Skills on contract should match employee's skills"
        )
        _logger.info("EXTRA Test 4 PASSED: Employee skills compute works.")
