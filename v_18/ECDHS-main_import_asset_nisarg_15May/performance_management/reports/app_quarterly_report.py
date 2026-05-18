from odoo import api, models


class AppQuarterlyReport(models.AbstractModel):
    _name = 'report.performance_management.report_template_quarterly_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Provide context for the quarterly report template.

        Expected keys in data:
        - 'target_id' (optional): integer id of an indicator.target (preferred)
        - 'target_name' (optional): name/label of a target period (used as fallback)
        - 'indicator_id' or 'target_id' or other ids used by the caller to fetch indicators (kept for backward compatibility)

        Returned values:
        - 'target_name' : the target label passed in (if any)
        - 'annual_target': the indicator.target record (if found)
        - 'target_quarters': quarterly records (indicator.target.quarter) ordered by sequence
        - 'outcome_indicator': the output.indicator record(s) to iterate in template
        """
        if data is None:
            data = {}

        annual_target = False
        target_quarters = self.env['indicator.target.quarter'].browse()

        # Prefer an explicit target_id (id of indicator.target)
        if data.get('target_id'):
            try:
                tid = int(data.get('target_id'))
            except (TypeError, ValueError):
                tid = False
            if tid:
                annual_target = self.env['indicator.target'].sudo().browse(tid)
                if not annual_target.exists():
                    annual_target = False

        # Fallback: find by target name label
        if not annual_target and data.get('target_name'):
            annual_target = self.env['indicator.target'].sudo().search(
                [('name', '=', data.get('target_name'))])

        if annual_target:
            # Use recordset.sorted to ensure quarters are in sequence order
            target_quarters = annual_target.quarter_ids.sorted('sequence')

        # Maintain backward compatible behavior for outcome_indicator: caller may pass
        # target_id as an indicator id in some flows, keep original fallback.
        outcome_indicator = self.env['output.indicator'].sudo()

        if data.get('target_id'):
            # If target_id actually refers to an output.indicator id in the caller data
            try:
                out_id = int(data.get('target_id'))
                program_id = int(data.get('programe'))

            except (TypeError, ValueError):
                out_id = False
                program_id = False
            indicator_target = {}
            if out_id:
                indicator = self.env['indicator.target'].sudo().browse(out_id).name
                outcome_indicator = self.env['output.indicator'].sudo().search([('target_ids.name','=',indicator)])
                indicator_target = self.env['indicator.target'].sudo().search([('name','ilike',indicator),('indicator_id','in',outcome_indicator.ids),('indicator_id.programme_id','=',program_id)])
        # additional caller conventions might pass indicator_id explicitly
        if not outcome_indicator and data.get('indicator_id'):
            try:
                out_id = int(data.get('indicator_id'))
            except (TypeError, ValueError):
                out_id = False
            if out_id:
                outcome_indicator = self.env['output.indicator'].sudo().search([])

        return {
            'docids': docids,
            'target_name': data.get('target_name'),
            'target_indicator': annual_target,
            'outcome_indicator': outcome_indicator,
            'annual_targets': indicator_target,
            'target_quarters': target_quarters,
        }