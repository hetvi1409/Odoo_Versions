from odoo import models,fields

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    sign_request_id = fields.Many2one('sign.request',string='Sign Request')

    def action_sign(self):
        self.ensure_one()

        # Fetch the attachment for the approval request
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'approval.request'),
            ('res_id', '=', self.id)
        ], limit=1)

        sign_template = self.env['sign.template'].create({
            'attachment_id': attachment.id,
            'name': attachment.name,
        })

        # Ensure that sign roles exist for each approver and store them
        role_model = self.env['sign.item.role']
        role_mapping = {}  # Dictionary to store roles mapped to approvers

        for approver in self.approver_ids:
            role = role_model.create({
                'name': f"Role for {approver.user_id.name}",
            })
            role_mapping[approver.id] = role  # Store role for reuse

        # Create signature fields for each role
        sign_items = []
        for approver in self.approver_ids:
            role = role_mapping[
                approver.id]  # Retrieve previously created role

            sign_item = self.env['sign.item'].sudo().create({
                'type_id': self.env.ref('sign.sign_item_type_signature').id,
                'required': True,
                'responsible_id': role.id,
                'page': 1,
                'posX': 0.273,
                'posY': 0.158 + (
                            0.1 * list(self.approver_ids).index(approver)),
                # Adjust Y position for multiple signatures
                'template_id': sign_template.id,
                'width': 0.150,
                'height': 0.015,
            })
            sign_items.append(sign_item)

        # Create one sign request with all approvers instead of multiple sign requests
        sign_request = self.env['sign.request'].create({
            'template_id': sign_template.id,
            'reference': attachment.name,
            'subject': f'Signature Request - {attachment.name}',
            'request_item_ids': [(0, 0, {
                'partner_id': approver.user_id.partner_id.id,
                'role_id': role_mapping[approver.id].id
            }) for approver in self.approver_ids]  # Assign all signers at once
        })

        self.sign_request_id = sign_request.id


class SignRequest(models.Model):
    _inherit = 'sign.request'

    def write(self, vals):
        res = super(SignRequest, self).write(vals)
        if 'state' in vals:
            approval = self.env['approval.request'].search(
                [('sign_request_id', '=', self.id)], limit=1)
            if approval:
                if vals['state'] == 'signed':
                    approval.state = 'approved'  # Change approval state to "Approved"
                elif vals['state'] == 'refused':
                    approval.state = 'refused'  # Change approval state to "Refused"
        return res
