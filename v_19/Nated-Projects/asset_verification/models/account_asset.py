from odoo import models, fields


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    """Inherited Account Asset fo asset verification"""

    major_group_description = fields.Char(string="Major Group Description",
                                          help="Major Group Description")
    barcode_past_year = fields.Char(string="Barcode Past Year",
                                    help="Barcode Past Year")

    alternative_ref = fields.Char(string='Barcode Number')
    current_condition_past_year = fields.Char(
        string="Current Condition Past Year",
        help="Current Condition Past Year")
    current_condition_this_year = fields.Char(
        string="Current Condition This Year",
        help="Current Condition This Year")
    name_installation = fields.Char(string="Name Installation",
                                    help="Name Installation")
    asset_component = fields.Char(string="Asset Component",
                                  help="Asset Component")
    parent_barcode = fields.Char(string="Parent Barcode", help="Parent Barcode")
    asset_size = fields.Char(string="Asset Size", help="Asset Size")
    asset_make_type = fields.Many2one("asset.type", help="Asset Make Type")
    estimated_useful_life_month = fields.Char(
        string="Estimated Useful Life Month",
        help="Estimated Useful Life Month")
    date_verification = fields.Date(string="Date of verification",
                       help="Date of verification")
    comments = fields.Char(string="Comments", help="Comments")
    inspector = fields.Char(string="Inspector", help="Inspector")
    asset_verification_user_id = fields.Many2one('res.users',
                                                 string="Verification User")
    is_verified = fields.Boolean(string="Verified", readonly=True)

    quarter = fields.Selection([
        ('Q1', 'Q1 (Jan - Mar)'),
        ('Q2', 'Q2 (Apr - Jun)'),
        ('Q3', 'Q3 (Jul - Sep)'),
        ('Q4', 'Q4 (Oct - Dec)'),
    ], string='Quarter', default='Q1', required=True, help="Select the quarter for which the asset is being verified.")

    account_verification_job_id = fields.Many2one('asset.verification.job')

    custodian_id = fields.Many2one('hr.employee','Custodian')

    job_location_id = fields.Many2one('asset.verification.job.location','Job Location')

    def open_employee_record(self):

        if self.custodian_id:

            employee_record = self.env['hr.employee'].search([('id','=',self.custodian_id.id)])

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'hr.employee',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'res_id': employee_record.id,
            }


