# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase
from odoo.exceptions import UserError


class TestLogNoteCustomization(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_user = cls.env.ref('base.user_admin')
        cls.employee_group = cls.env.ref('base.group_user')
        cls.internal_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Log Note Internal User',
            'login': 'log_note_internal_user',
            'email': 'log_note_internal_user@example.com',
            'group_ids': [(6, 0, [cls.employee_group.id])],
        })
        cls.partner = cls.env['res.partner'].create({'name': 'Log Note Test Partner'})

    def _create_log_note_message(self, body='<p>Initial note body</p>'):
        return self.partner.with_user(self.admin_user).message_post(
            body=body,
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )

    def test_01_admin_can_open_delete_reason_wizard_action(self):
        message = self._create_log_note_message()

        action = message.with_user(self.admin_user).action_open_delete_reason_wizard()

        self.assertEqual(action.get('type'), 'ir.actions.act_window')
        self.assertEqual(action.get('res_model'), 'delete.reason.wizard')
        self.assertEqual(action.get('target'), 'new')
        self.assertIn('views', action)
        self.assertTrue(action['views'])
        self.assertEqual(action.get('context', {}).get('default_message_id'), message.id)

    def test_02_non_admin_cannot_open_delete_reason_wizard_action(self):
        message = self._create_log_note_message()

        with self.assertRaises(UserError):
            message.with_user(self.internal_user).action_open_delete_reason_wizard()

    def test_03_admin_wizard_confirm_deletes_message_and_posts_reason_note(self):
        original_body = '<p>Original to delete</p>'
        reason = 'Cleaning accidental edit to empty content'
        message = self._create_log_note_message(body=original_body)

        wizard = self.env['delete.reason.wizard'].with_user(self.admin_user).create({
            'message_id': message.id,
            'reason': reason,
        })

        result = wizard.with_user(self.admin_user).action_confirm_delete()
        message.invalidate_recordset(['body'])

        self.assertEqual(result, {'type': 'ir.actions.act_window_close'})
        self.assertIn('o-mail-Message-edited', message.body)

        audit_message = self.env['mail.message'].search([
            ('model', '=', message.model),
            ('res_id', '=', message.res_id),
            ('body', 'ilike', 'Message Deleted'),
            ('body', 'ilike', reason),
        ], order='id desc', limit=1)

        self.assertTrue(audit_message, 'Audit note should be posted with deletion reason.')
        self.assertIn('Reason:', audit_message.body)
        self.assertIn(reason, audit_message.body)
        self.assertIn('Original content:', audit_message.body)

    def test_04_non_admin_cannot_confirm_delete_wizard(self):
        message = self._create_log_note_message()
        wizard = self.env['delete.reason.wizard'].with_user(self.admin_user).create({
            'message_id': message.id,
            'reason': 'Should fail for non-admin',
        })

        with self.assertRaises(UserError):
            wizard.with_user(self.internal_user).action_confirm_delete()
