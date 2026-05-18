
import textwrap
from odoo import api, fields, models, _


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    answer_name = fields.Char(string="Answer Name", store=True, compute="_compute_answer_name")

    @api.depends('answer_type')
    def _compute_answer_name(self):
        for line in self:
            if line.answer_type == 'char_box':
                line.answer_name = line.value_char_box
            elif line.answer_type == 'text_box' and line.value_text_box:
                line.answer_name = textwrap.shorten(line.value_text_box, width=50, placeholder=" [...]")
            elif line.answer_type == 'numerical_box':
                line.answer_name = line.value_numerical_box
            elif line.answer_type == 'date':
                line.answer_name = fields.Date.to_string(line.value_date)
            elif line.answer_type == 'datetime':
                line.answer_name = fields.Datetime.to_string(line.value_datetime)
            elif line.answer_type == 'suggestion':
                if line.matrix_row_id:
                    line.answer_name = '%s: %s' % (
                        line.suggested_answer_id.value,
                        line.matrix_row_id.value)
                else:
                    line.answer_name = line.suggested_answer_id.value

            if not line.answer_name:
                line.answer_name = _('Skipped')
