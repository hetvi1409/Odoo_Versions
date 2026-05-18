from odoo import api, models


class AssetMovableReport(models.AbstractModel):
    _name = 'report.asset_movable_report.report_asset_barcode_document'
    _description = 'Asset Movable Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not docids:
            docs = self.env['account.asset'].search([('state', '!=', 'model')])
        else:
            docs = self.env['account.asset'].browse(docids)
        total_asset = len(docs)
        good_assets = self.env['account.asset'].search_count([('id', '=', docs.ids),
                                                        ('condition', 'ilike', 'Good')])
        damaged_assets = self.env['account.asset'].search_count([('id', '=', docs.ids),
                                                        ('condition', 'ilike', 'Damaged')])
        disposed_assets = self.env['account.asset'].search_count([('id', '=', docs.ids),
                                                        ('condition', 'ilike', 'Disposed')])
        lost_assets = self.env['account.asset'].search_count([('id', '=', docs.ids),
                                                        ('condition', 'ilike', 'Lost')])
        written_off_assets = self.env['account.asset'].search_count([('id', '=', docs.ids),
                                                        ('condition', 'ilike', 'Written Off')])

        return {
            'doc_ids': docids,
            'doc_model': 'account.asset',
            'docs': docs,
            'data': {
                'total_asset': total_asset,
                'good_assets': good_assets,
                'damaged_assets': damaged_assets,
                'disposed_assets': disposed_assets,
                'lost_assets': lost_assets,
                'written_off_assets': written_off_assets,
            }
        }


class AssetMovableMinorMajorReport(models.AbstractModel):
    _name = 'report.asset_movable_report.report_asset_minor_movable_report'
    _description = 'Asset Movable Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print(data, "dasfdgfdsadfg")
        data['type']
        domain = [('state', '!=', 'model')]
        if data['type'] == 'minor':
            domain.append(('original_value', '<', 5000))
            heading_name = "Minor Asset Movable Report"
        elif data['type'] == 'major':
            domain.append(('original_value', '>=', 5000))
            heading_name = "Major Asset Movable Report"
        assets = self.env['account.asset'].search(domain)

        return {
            'doc_ids': docids,
            'doc_model': 'account.asset',
            'docs': assets,
            'data': {
                'heading_name': heading_name
            }
        }

