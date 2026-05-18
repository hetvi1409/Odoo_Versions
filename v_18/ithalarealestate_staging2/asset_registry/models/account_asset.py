from odoo import api, fields, models, _


class AccountAsset(models.Model):
    """ account.asset model has been inherited for add some fields """
    _inherit = 'account.asset'

    supplier_id = fields.Many2one('res.partner',string='Supplier')
    payment_number = fields.Integer(string='Payment Number')
    order_number = fields.Char(string='Order Number')
    description = fields.Char(string='Description', help='Description '
                                                         'for the asset')
    state = fields.Selection(
        selection_add=[('disposed', 'Disposed'),('damaged', 'Damaged'),('written_off', 'Written Off'),('lost', 'Lost')])
    afs_classification = fields.Many2one('asset.category',string='AFS Classification')
    serial_number = fields.Char(string='Serial Number')
    alternative_ref = fields.Char(string='Barcode Number')
    job_location_id = fields.Many2one('asset.verification.job.location',
                                      'Location & Office number')
    department_id = fields.Many2one('hr.department',string='Chief Directorate & Directorate')
    custodian_id = fields.Many2one('hr.employee', 'Custodian / User', tracking=True)
    condition = fields.Char(string='Condition')
    original_useful_life = fields.Integer('Life Cycle')
    disposal_date = fields.Date(string='Disposal Date')
    disposal_price = fields.Float(string='Disposal Price')
    disposal_method = fields.Char(string='Disposal Method')
