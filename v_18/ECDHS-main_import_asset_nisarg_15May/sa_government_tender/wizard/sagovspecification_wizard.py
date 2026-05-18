# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SpecificationWizard(models.TransientModel):
    """Wizard for creating/editing specification from requisition"""
    _name = 'sagovtender.specification.wizard'
    _description = 'Specification Wizard'

    requisition_id = fields.Many2one(
        'sagovtender.purchase.requisition',
        string='Purchase Requisition',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('default_requisition_id'),
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    specification_id = fields.Many2one(
        'sagovtender.specification',
        string='Specification',
        readonly=True,
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )

    def action_open_specification(self):
        """Open specification form"""
        self.ensure_one()

        # Create specification if it doesn't exist
        if not self.requisition_id.specification_id:
            spec = self.env['sagovtender.specification'].create({
                'requisition_id': self.requisition_id.id,
                'name': f'Specification for {self.requisition_id.name}',
                'description': self.requisition_id.description,
            })
            self.requisition_id.specification_id = spec.id
            self.specification_id = spec.id
        else:
            self.specification_id = self.requisition_id.specification_id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Specification'),
            'res_model': 'sagovtender.specification',
            'res_id': self.specification_id.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'form_view_initial_mode': 'edit',
            }
        }
