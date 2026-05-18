from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TenderDocument(models.Model):
    """
    Model representing a document related to a tender.
    """
    _name = 'tender.document'
    _description = 'Tender Document'

    name = fields.Char(string='Document Name', required=True,
                       help='The name of the document')
    file = fields.Binary(string='File', required=True,
                         help='The binary file of the document')
    tender_id = fields.Many2one('tender.tender', string='Tender',
                                help='The tender associated with this document')
    tender_rfq_id = fields.Many2one('tender.tender', string='RFQ Tender',
                                help='The tender associated with this document')
    bid_id = fields.Many2one('tender.bid', string='Bid ',
                             help='The Bid associated with this document')
    attachment_id = fields.Many2one('ir.attachment', 'Documents')

    def _get_linked_tender(self, vals=None):
        """Resolve linked tender for create/write validation."""
        vals = vals or {}

        tender_id = vals.get('tender_id') or self.tender_id.id
        if tender_id:
            return self.env['tender.tender'].browse(tender_id)

        tender_rfq_id = vals.get('tender_rfq_id') or self.tender_rfq_id.id
        if tender_rfq_id:
            return self.env['tender.tender'].browse(tender_rfq_id)

        bid_id = vals.get('bid_id') or self.bid_id.id
        if bid_id:
            bid = self.env['tender.bid'].browse(bid_id)
            return bid.tender_id

        return self.env['tender.tender']

    def _ensure_parent_tender_draft(self, tender):
        if self.env.context.get('allow_non_draft_tender_document_write'):
            return
        if tender and tender.exists() and tender.state != 'draft':
            raise UserError(
                _("You can only modify documents while the linked tender status is Draft.")
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            tender = self._get_linked_tender(vals)
            self._ensure_parent_tender_draft(tender)
        return super().create(vals_list)

    def write(self, vals):
        for record in self:
            tender = record._get_linked_tender(vals)
            record._ensure_parent_tender_draft(tender)
        return super().write(vals)

    def unlink(self):
        for record in self:
            tender = record._get_linked_tender()
            record._ensure_parent_tender_draft(tender)
        return super().unlink()

    def init(self):
        self._cr.execute(
            """
            ALTER TABLE tender_document
            ADD COLUMN IF NOT EXISTS tender_rfq_id integer
            """
        )
