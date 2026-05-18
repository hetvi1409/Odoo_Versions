from odoo import models, fields, api
from odoo.exceptions import UserError


class FacilitiesInvestigation(models.Model):
    _name = "facilities.investigation"
    _description = "Facilities Investigation Report"

    enquiry_id = fields.Many2one('property.enquiry', string="Property Enquiry", required=True)
    type = fields.Selection([('swimming_pool', 'Swimming Pool'),
                             ('generator', 'Generator'),
                             ('water_storage', 'Water Storage'),
                             ('conceige', 'Conceige'),
                             ('security', 'Security'),
                             ('basement_parking', 'Basement Parking'),
                             ('park', 'Park'),
                             ('open_parking', 'Open Parking'),
                             ('children_facilities', 'Children Facilities'),
                             ('gym', 'Gym'),
                             ('residential_lifts', 'Residential Lifts'),
                             ('fireman_service_lift', 'Fireman/Service Lift'),
                             ])
    facility = fields.Char(string="Facility", required=True)
    feedback = fields.Text(string="Feedback / Comments")
    suitable = fields.Selection([('yes','Yes'),('no','No')], string="Suitable for Nature of Business")
