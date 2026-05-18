# from odoo import models, fields, api


# class skill_academy(models.Model):
#     _name = 'skill_academy.skill_academy'
#     _description = 'skill_academy.skill_academy'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

