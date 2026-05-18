from odoo import fields, models


class ProjectCapitalSegment(models.Model):
    _name = 'project.capital.segment'
    _description = 'Project Capital Segment'

    name = fields.Char(string="Name",
                       help="Name of the project capital segment",
                       required=True)
    capital_type = fields.Selection([('Infrastructure', 'Infrastructure'),
                                     ('Non Infrastructure',
                                      'Non Infrastructure')], string="Capital",
                                    required=True,
                                    help='Capital')
    infrastructure_type = fields.Selection(
        [('Existing', 'Existing'), ('New', 'New')],
        string="Infrastructure Type", help='Infrastructure Type')
    non_infrastructure_type = fields.Selection(
        [('Existing', 'Existing'), ('New', 'New')],
        string="Non Infrastructure Type", help='Non Infrastructure Type')
    segment_ids = fields.One2many('project.capital.segment.line', 'segment_id')

class ProjectCapitalSegmentLine(models.Model):
    _name = 'project.capital.segment.line'
    _description = 'Project Capital Segment Line'

    name = fields.Char(string="Name",
                       help="Name of the project capital segment",
                       required=True)
    segment_id = fields.Many2one('project.capital.segment')