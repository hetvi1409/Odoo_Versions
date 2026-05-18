from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestTenderWorkflowStageTransition(TransactionCase):
    def setUp(self):
        super().setUp()
        self.method = self.env['sagovprocurement.method'].create({
            'name': 'Unit Test Method',
            'code': 'unit_test_method',
            'currency_id': self.env.company.currency_id.id,
        })
        self.stage1 = self.env['sagovprocurement.workflow.stage'].create({
            'method_id': self.method.id,
            'name': 'Draft',
            'sequence': 1,
            'responsible_group': 'scm',
        })
        self.stage2 = self.env['sagovprocurement.workflow.stage'].create({
            'method_id': self.method.id,
            'name': 'Advertised',
            'sequence': 2,
            'responsible_group': 'scm',
        })
        self.stage3 = self.env['sagovprocurement.workflow.stage'].create({
            'method_id': self.method.id,
            'name': 'Evaluation',
            'sequence': 3,
            'responsible_group': 'scm',
        })
        self.tender = self.env['sagovtender.tender'].create({
            'name': 'T-001',
            'title': 'Test Tender',
            'procurement_method_config_id': self.method.id,
        })

    def test_next_stage_action_advances_once(self):
        self.assertEqual(self.tender.current_workflow_stage_id, self.stage1)
        self.tender.action_next_workflow_stage()
        self.assertEqual(self.tender.current_workflow_stage_id, self.stage2)

    def test_forward_skip_is_blocked(self):
        with self.assertRaises(UserError):
            self.tender.write({'current_workflow_stage_id': self.stage3.id})

    def test_backward_move_is_allowed(self):
        self.tender.write({'current_workflow_stage_id': self.stage2.id})
        self.tender.write({'current_workflow_stage_id': self.stage1.id})
        self.assertEqual(self.tender.current_workflow_stage_id, self.stage1)
