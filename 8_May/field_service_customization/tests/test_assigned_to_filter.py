# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.addons.industry_fsm.tests.common import TestIndustryFsmCommon


@tagged('post_install', '-at_install')
class TestAssignedToFilter(TestIndustryFsmCommon):
    """
    Test for the 'Assigned To' filter in the FSM calendar view.
    Validates that the calendar view includes user_ids with filters="1"
    and that filtering by user works correctly.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Reuse george_user and marcel_user from TestIndustryFsmCommon as "Fitters"
        cls.user_fitter_1 = cls.george_user
        cls.user_fitter_2 = cls.marcel_user

        # create task for different users
        cls.task_alice = cls.env['project.task'].create({
            'name': 'Task for Fitter 1',
            'project_id': cls.fsm_project.id,
            'user_ids': [(4, cls.user_fitter_1.id)],
            'partner_id': cls.partner.id,
        })
        cls.task_bob = cls.env['project.task'].create({
            'name': 'Task for Fitter 2',
            'project_id': cls.fsm_project.id,
            'user_ids': [(4, cls.user_fitter_2.id)],
            'partner_id': cls.partner.id,
        })
        cls.task_both = cls.env['project.task'].create({
            'name': 'Task for Both Fitters',
            'project_id': cls.fsm_project.id,
            'user_ids': [(4, cls.user_fitter_1.id), (4, cls.user_fitter_2.id)],
            'partner_id': cls.partner.id,
        })
        cls.task_unassigned = cls.env['project.task'].create({
            'name': 'Unassigned Task',
            'project_id': cls.fsm_project.id,
            'user_ids': [],
            'partner_id': cls.partner.id,
        })

    def test_01_calendar_view_has_user_ids_filter(self):
        """
        Test that the calendar view includes the 'Assigned To' filter.
        """
        View = self.env['ir.ui.view']
        calendar_view = self.env.ref('industry_fsm.project_task_view_calendar_fsm')
        arch = self.env['project.task'].get_view(view_id=calendar_view.id, view_type='calendar')['arch']

        self.assertIn('user_ids', arch, "user_ids field should be present in the calendar view")
        self.assertIn('filters', arch, "filters attribute should be present in the calendar view")

    def test_02_filter_single_user(self):
        """
        This test checks if filtering by a single user works correctly.
        When we select a specific user in the 'Assigned To' filter,
        only tasks assigned to that user should be visible.
        """
        tasks = self.env['project.task'].search([
            ('is_fsm', '=', True),
            ('project_id', '=', self.fsm_project.id),
            ('user_ids', 'in', [self.user_fitter_1.id]),
        ])
        self.assertIn(self.task_alice, tasks, "Task assigned to Alice should appear")
        self.assertIn(self.task_both, tasks, "Task assigned to both should appear when filtering Alice")
        self.assertNotIn(self.task_bob, tasks, "Task assigned only to Bob should NOT appear")
        self.assertNotIn(self.task_unassigned, tasks, "Unassigned task should NOT appear")

    def test_03_filter_multiple_users(self):
        """
        This test verifies that when multiple users are selected in the
        'Assigned To' filter, tasks assigned to any of those users
        should be displayed.
        """
        tasks = self.env['project.task'].search([
            ('is_fsm', '=', True),
            ('project_id', '=', self.fsm_project.id),
            ('user_ids', 'in', [self.user_fitter_1.id, self.user_fitter_2.id]),
        ])
        self.assertIn(self.task_alice, tasks, "Task assigned to Alice should appear")
        self.assertIn(self.task_bob, tasks, "Task assigned to Bob should appear")
        self.assertIn(self.task_both, tasks, "Task assigned to both should appear")
        self.assertNotIn(self.task_unassigned, tasks, "Unassigned task should NOT appear")

    def test_04_no_filter_shows_all(self):
        """
        This test checks that when no filters are applied,
        all tasks should be visible in the calendar view.
        """
        all_tasks = self.env['project.task'].search([
            ('is_fsm', '=', True),
            ('project_id', '=', self.fsm_project.id),
        ])
        self.assertIn(self.task_alice, all_tasks)
        self.assertIn(self.task_bob, all_tasks)
        self.assertIn(self.task_both, all_tasks)
        self.assertIn(self.task_unassigned, all_tasks)