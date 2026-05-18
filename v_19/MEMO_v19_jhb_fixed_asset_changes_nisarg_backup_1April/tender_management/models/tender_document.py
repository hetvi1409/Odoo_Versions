from odoo import models, fields


class TenderDocument(models.Model):
    """
    Model representing a document related to a tender.
    """
    _name = 'tender.document'
    _description = 'Tender Document'

    name = fields.Char(string='Document Name', required=True,
                       help='The name of the document')
    file = fields.Binary(string='File', required=True, related="attachment_id.datas",
                         help='The binary file of the document')
    tender_id = fields.Many2one('tender.tender', string='Tender',
                                help='The tender associated with this document')
    tender_rfq_id = fields.Many2one('tender.tender', string='RFQ Tender',
                                help='The tender associated with this document')
    bid_id = fields.Many2one('tender.bid', string='Bid ',
                             help='The Bid associated with this document')
    attachment_id = fields.Many2one('ir.attachment', 'Documents')
