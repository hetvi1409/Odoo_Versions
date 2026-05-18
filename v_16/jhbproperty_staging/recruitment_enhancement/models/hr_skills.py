from odoo import api, fields, models, _


class HrJobSkill(models.Model):
    _name = "hr.job.skill"
    _rec_name = "skill_id"

    job_id = fields.Many2one(
        comodel_name="hr.job",
        required=True,
        index=True,
        ondelete="cascade",
    )
    skill_id = fields.Many2one('hr.skill', compute='_compute_skill_id', store=True,
        domain="[('skill_type_id', '=', skill_type_id)]", readonly=False, required=True, ondelete='cascade')

    skill_level_id = fields.Many2one('hr.skill.level', compute='_compute_skill_level_id',
        domain="[('skill_type_id', '=', skill_type_id)]", store=True, readonly=False, required=True, ondelete='cascade')

    def _default_skill_type_id(self):
        if self.env.context.get('certificate_skill', False):
            return self.env['hr.skill.type'].search([('is_certification', '=', True)], limit=1)
        return self.env['hr.skill.type'].search([], limit=1)

    skill_type_id = fields.Many2one('hr.skill.type',
                                    default=_default_skill_type_id,
                                    required=True, ondelete='cascade')
    level_progress = fields.Integer(related='skill_level_id.level_progress')
    valid_to = fields.Date(string="Validity Stop")

    @api.depends('skill_type_id')
    def _compute_skill_id(self):
        for record in self:
            if record.skill_type_id:
                record.skill_id = record.skill_type_id.skill_ids[0] if record.skill_type_id.skill_ids else False
            else:
                record.skill_id = False

