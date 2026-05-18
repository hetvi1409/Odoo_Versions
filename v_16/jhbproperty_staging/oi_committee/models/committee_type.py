
from odoo import models, fields

class CommitteeType(models.Model):
    _name = 'committee.type'
    _description = 'Committee Type'
    
    group_id = fields.Many2one('res.groups', required = True, delegate = True, ondelete='cascade')
    model_id = fields.Many2one('ir.model', domain = [('transient', '=', False)])    
    committee_ids = fields.One2many('committee', 'type_id', domain = [('state','=', 'active')], string='Active Committee')
    
    xml_id = fields.Char(compute = '_calc_xml_id')
    code = fields.Char()
    
    
    def _update_members(self):
        records = self or self.search([])
        today = fields.Date.today()
        for record in records:
            committee_ids = self.env['committee'].search([('type_id','=', record.id), 
                                                          ('state','=', 'active'), 
                                                          ('date_start', '<=', today),
                                                          '|',
                                                          ('date_end', '>=', today),
                                                          ('date_end', '=', False),
                                                          ])
            user_ids=committee_ids.mapped('member_ids.employee_id.user_id.id')
            record.group_id.write({'users' : [(6,0, user_ids)]})
                
    def _calc_xml_id(self):
        xml_ids = self.get_external_id()
        for record in self:
            record.xml_id = xml_ids[record.id]