from odoo import fields, models


class TenderAdvertisement(models.Model):
    """Class for Tender Advertisement"""
    _name = "tender.advertisement"
    _description = "Tender Advertisement"

    purchase_requisition_id = fields.Many2one('purchase.requisition',
                                              string="Purchase requisition",
                                              help="Purchase Requisition")
    datas = fields.Binary(string='Report', help="Report")
    description = fields.Text(string='Description', help="Description")


    def action_submit(self):
        """Method for submit the form"""
        if self.purchase_requisition_id:
            self.purchase_requisition_id.state = 'advertisement'
