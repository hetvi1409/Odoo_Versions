from types import SimpleNamespace
from unittest.mock import patch

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.my_home.controllers import portal as my_home_portal


class _FakeModel:
    def __init__(self, count=0, raise_access=False):
        self._count = count
        self._raise_access = raise_access

    def check_access_rights(self, operation):
        if self._raise_access:
            raise AccessError("No read access")
        return True

    def search_count(self, domain):
        return self._count


class _FakeEnv(dict):
    def __init__(self, user, models):
        super().__init__(models)
        self.user = user

    def __getitem__(self, item):
        return super().__getitem__(item)


@tagged('post_install', '-at_install', 'my_home')
class TestMyHomePortalOverrides(TransactionCase):

    def setUp(self):
        super().setUp()
        partner = SimpleNamespace(ids=[10], commercial_partner_id=SimpleNamespace(id=10))
        self.fake_user = SimpleNamespace(id=7, ids=[7], partner_id=partner)

    def _patch_parent_prepare(self):
        return patch.object(
            my_home_portal.CustomerPortal,
            '_prepare_home_portal_values',
            autospec=True,
            return_value={'base_counter': 1},
        )

    def test_prepare_home_portal_values_adds_counts(self):
        fake_env = _FakeEnv(
            self.fake_user,
            {
                'project.project': _FakeModel(count=3),
                'project.task': _FakeModel(count=5),
            },
        )
        fake_request = SimpleNamespace(env=fake_env)

        controller = my_home_portal.ProjectCustomerPortal()
        with self._patch_parent_prepare(), patch.object(my_home_portal, 'request', fake_request):
            values = controller._prepare_home_portal_values(['project_count', 'task_count'])

        self.assertEqual(values['base_counter'], 1)
        self.assertEqual(values['project_count'], 3)
        self.assertEqual(values['task_count'], 5)

    def test_prepare_home_portal_values_falls_back_to_zero_on_access_error(self):
        fake_env = _FakeEnv(
            self.fake_user,
            {
                'project.project': _FakeModel(count=3, raise_access=True),
                'project.task': _FakeModel(count=5, raise_access=True),
            },
        )
        fake_request = SimpleNamespace(env=fake_env)

        controller = my_home_portal.ProjectCustomerPortal()
        with self._patch_parent_prepare(), patch.object(my_home_portal, 'request', fake_request):
            values = controller._prepare_home_portal_values(['project_count', 'task_count'])

        self.assertEqual(values['project_count'], 0)
        self.assertEqual(values['task_count'], 0)

    def test_get_invoices_domain_contains_my_home_filters(self):
        fake_env = _FakeEnv(self.fake_user, {})
        fake_request = SimpleNamespace(env=fake_env)

        controller = my_home_portal.PortalAccount()
        with patch.object(my_home_portal, 'request', fake_request):
            domain = controller._get_invoices_domain('out')

        self.assertIn(('state', 'not in', ('cancel', 'draft')), domain)
        self.assertIn(('move_type', 'in', ['out_invoice', 'out_refund', 'out_receipt']), domain)
        self.assertIn(('invoice_user_id', '=', self.fake_user.id), domain)
        self.assertIn(('message_partner_ids', 'in', self.fake_user.partner_id.ids), domain)
        self.assertIn(
            ('partner_id', 'child_of', self.fake_user.partner_id.commercial_partner_id.id),
            domain,
        )
