from odoo import models, fields


class TUEmploymentInfo(models.TransientModel):
    _name = "tu.employment.info.wizard"
    _description = "TU Employment Information"

    enquiry_id = fields.Many2one('property.enquiry',string="Property Enquiry")
    name = fields.Char(string="Name", placeholder="Name...")
    employer = fields.Char(string="Employer")
    occupation = fields.Char(string="Occupation")
    date = fields.Date(string="Date")
    employment_period = fields.Char(string="Employment Period")

    score_card = fields.Char(string="Score Card")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    work_number = fields.Char('Work Number')

    def action_save_close(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    def action_save_new(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tu.employment.info.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }



class TUCellNumber(models.TransientModel):
    _name = "tu.employment.cell.wizard"
    _description = "TU Employment Cell Number"

    date = fields.Date('Date')
    enquiry_id = fields.Many2one('property.enquiry',string="Property Enquiry")
    cell_number = fields.Char('Cell Number')
    years = fields.Float('Years')
    score_card = fields.Char(string="Score Card")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def action_save_close(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    def action_save_new(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tu.employment.cell.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

class TUJudgment(models.TransientModel):
    _name = "tu.judgment.cell.wizard"
    _description = "TU Judgement"

    enquiry_id = fields.Many2one('property.enquiry',string="Property Enquiry")
    name = fields.Char(string="Name", placeholder="Name...")
    date = fields.Date('Judgement Date')
    plaintiff = fields.Char('Plaintiff')
    amount = fields.Float('Amount')
    court_name = fields.Char('Court Name')
    score_card = fields.Char(string="Score Card")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    is_company = fields.Boolean('Is Company')

    def action_save_close(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    def action_save_new(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tu.judgment.cell.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

class TUAddress(models.TransientModel):
    _name = "tu.address.wizard"
    _description = "TU Address"

    enquiry_id = fields.Many2one('property.enquiry',string="Property Enquiry")
    date = fields.Date('Date')
    street_1 = fields.Char('Street 1')
    street_2 = fields.Char('Street 2')
    city = fields.Char('City')
    province = fields.Char('Province')
    owner = fields.Char('Owner')

    def action_save_close(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    def action_save_new(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tu.address.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }