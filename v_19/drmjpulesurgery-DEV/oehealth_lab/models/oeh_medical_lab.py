##############################################################################
#    Copyright (C) 2015 - Present, oeHealth (<https://www.oehealth.in>). All Rights Reserved
#    oeHealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, oeHealth.in, braincrewapps.com, or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################

from odoo import api, fields, models, _
import time
import datetime
from odoo.exceptions import UserError


# Lab Units Management
class OeHealthLabTestUnits(models.Model):
    _name = 'oeh.medical.lab.units'
    _description = 'Lab Test Units'

    name = fields.Char(string='Unit Name', size=25, required=True)
    code = fields.Char(string='Code', size=25, required=True)

    _sql_constraints = [('name_uniq', 'unique(name)', 'The Lab unit name must be unique')]


# Lab Test Department
class OeHealthLabTestDepartment(models.Model):
    _name = 'oeh.medical.labtest.department'
    _description = 'Lab Test Departments'

    name = fields.Char(string='Name', size=128, required=True)


# Lab Test Types Management
class OeHealthLabTestCriteria(models.Model):
    _name = 'oeh.medical.labtest.criteria'
    _description = 'Lab Test Criteria'

    name = fields.Char(string='Tests', size=128, required=True)
    normal_range = fields.Text(string='Normal Range')
    units = fields.Many2one('oeh.medical.lab.units', string='Units')
    sequence = fields.Integer(string='Sequence')
    medical_type_id = fields.Many2one('oeh.medical.labtest.types', string='Lab Test Types')

    _order = "sequence"


class OeHealthLabTestTypes(models.Model):
    _name = 'oeh.medical.labtest.types'
    _description = 'Lab Test Types'

    name = fields.Char(string='Lab Test Name', size=128, required=True, help="Test type, eg X-Ray, Hemogram, Biopsy...")
    code = fields.Char(string='Code', size=128, help="Short code for the test")
    info = fields.Text(string='Description')
    test_charge = fields.Float(string='Test Charge', default=lambda *a: 0.0)
    lab_criteria = fields.One2many('oeh.medical.labtest.criteria', 'medical_type_id', string='Lab Test Cases')
    lab_department = fields.Many2one('oeh.medical.labtest.department', string='Department')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    # lab_test_types = fields.Many2one('oeh.medical.labtest.types', string='Test Types')

    # @api.onchange('name')
    # def change(self):
    #     print("============90================",self.lab_test_types)


class OeHealthLabTests(models.Model):
    _name = 'oeh.medical.lab.test'
    _description = 'Lab Tests'
    _inherit = ['mail.thread']

    LABTEST_STATE = [
        ('Draft', 'Draft'),
        ('Test In Progress', 'Test In Progress'),
        ('Completed', 'Completed'),
    ]

    name = fields.Char(string='Lab Test #', size=16, readonly=True, required=True, help="Lab result ID",
                       default=lambda *a: '/')
    lab_request = fields.Many2one('oeh.medical.lab.request', string='Lab Requested')
    # lab_department = fields.Many2one('oeh.medical.labtest.department', string='Department', readonly=True,
    #                                  states={'Draft': [('readonly', False)]})
    # test_type = fields.Many2one('oeh.medical.labtest.types', string='Test Type',
    #                             domain="[('lab_department', '=', lab_department)]",
    #                             help="Lab test type")
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,
                              readonly=True)
    pathologist = fields.Many2one('oeh.medical.physician', string='Pathologist', help="Pathologist"
                                  )
    requestor = fields.Char(string='Doctor who requested the test', help="Doctor who requested the test", readonly=True)
    results = fields.Text(string='Results', readonly=True)
    diagnosis = fields.Text(string='Diagnosis', readonly=True)
    lab_test_criteria = fields.One2many('oeh.medical.lab.resultcriteria', 'medical_lab_test_id',
                                        string='Lab Test Result', readonly=True)
    date_requested = fields.Datetime(string='Date requested', readonly=True,
                                     default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    date_analysis = fields.Datetime(string='Date of the Analysis', readonly=True)
    state = fields.Selection(LABTEST_STATE, string='State', readonly=True, default=lambda *a: 'Draft')
    institution = fields.Many2one('oeh.medical.health.center', string='Health Center', help="Medical Center",
                                  readonly=True)
    appointment = fields.Many2one('oeh.medical.appointment', string='Appointment #')
    move_id = fields.Many2one('account.move', string='Invoice #', copy=False)
    lab_technician_id = fields.Many2one('oeh.medical.physician', domain="[('staff_type', '=', 'lab technician')]",
                                        string="Lab Technician")

    lab_test_type_ids = fields.Many2many('oeh.medical.labtest.types')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                sequence = self.env['ir.sequence'].next_by_code('oeh.medical.lab.test')
                vals['name'] = sequence or '/'
        return super(OeHealthLabTests, self).create(vals_list)

    # Fetching lab test types
    # @api.onchange('test_type')
    # def onchange_test_type_id(self):
    #     lab_test_criteria = []
    #     if self.test_type and self.test_type.lab_criteria:
    #         self.lab_test_criteria = False
    #         for criteria in self.test_type.lab_criteria:
    #             lab_test_criteria.append((0, 0, {
    #                 'name': criteria.name,
    #                 'normal_range': criteria.normal_range,
    #                 'units': criteria.units and criteria.units.id or False,
    #                 'sequence': criteria.sequence,
    #             }))
    #         self.lab_test_criteria = lab_test_criteria
    #     else:
    #         self.lab_test_criteria = False

    # This function prints the lab test
    def print_patient_labtest(self):
        return self.env.ref('oehealth_lab.action_report_patient_labtest').report_action(self)

    def set_to_test_inprogress(self):
        return self.write({'state': 'Test In Progress', 'date_analysis': datetime.datetime.now()})

    def set_to_test_complete(self):
        return self.write({'state': 'Completed'})

    def unlink(self):
        for labtest in self.filtered(lambda labtest: labtest.state not in ['Draft']):
            raise UserError(_('You can not delete a lab test which is not in "Draft" state !!'))
        return super(OeHealthLabTests, self).unlink()

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def action_lab_invoice_create(self):
        res = {}
        for lab in self:
            # Create Invoice
            if lab.patient:
                invoice_lines = []
                default_journal = self._get_default_journal()

                if not default_journal:
                    raise UserError(_('No accounting journal with type "Sale" defined !'))

                sequence_count = 1
                invoice_lines.append((0, 0, {
                    'name': 'Lab Test',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence_count,
                }))

                sequence_count += 1

                invoice_lines.append((0, 0, {
                    'display_type': 'product',
                    'name': lab.test_type.name,
                    'price_unit': lab.test_type.test_charge,
                    'quantity': 1,
                    'product_uom_id': self.env.ref('uom.product_uom_unit') and self.env.ref(
                        'uom.product_uom_unit').id or False,
                    'sequence': sequence_count,
                }))

                invoice = self.env['account.move'].sudo().create({
                    'move_type': 'out_invoice',
                    'journal_id': default_journal.id,
                    'partner_id': lab.patient.partner_id.id,
                    'patient': lab.patient.id,
                    'invoice_date': datetime.datetime.now().date(),
                    'date': datetime.datetime.now().date(),
                    'ref': "Lab Test # : " + lab.name,
                    'labtest': lab.id,
                    'invoice_line_ids': invoice_lines
                })
                if self.env.company.stock_deduction_method == 'invoice_create':
                    invoice.oeh_process_inventories()
                # res = lab.write({'state': 'Invoiced', 'move_id': invoice.id})
        return res


class OeHealthLabTestsResultCriteria(models.Model):
    _name = 'oeh.medical.lab.resultcriteria'
    _description = 'Lab Test Result Criteria'

    name = fields.Char(string='Tests', size=128, required=True)
    result = fields.Text(string='Result')
    normal_range = fields.Text(string='Normal Range')
    units = fields.Many2one('oeh.medical.lab.units', string='Units')
    sequence = fields.Integer(string='Sequence')
    seq = fields.Integer(string='Sequence')
    # sec_name = fields.Text()
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note')
        ,
    ], default=False, help="Technical field for UX purpose.")
    medical_lab_test_id = fields.Many2one('oeh.medical.lab.test', string='Lab Tests')

    _order = "sequence"
    #
    # @api.model
    # def create(self, values):
    #     if values.get('display_type', self.default_get(['display_type'])['display_type']):
    #         values.update(sequence=False, name=False, result=False, normal_range=False, units=False)
    #     line = super(OeHealthLabTestsResultCriteria, self).create(values)
    #     return line
    #
    # def write(self, values):
    #     if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
    #         raise UserError(
    #             "You cannot change the type of a sale order line. Instead you should delete the current line and create a new line of the proper type.")
    #     result = super(OeHealthLabTestsResultCriteria, self).write(values)
    #     return result


# Inheriting Patient module to add "Lab" screen reference
class OeHealthPatient(models.Model):
    _inherit = 'oeh.medical.patient'

    def _labtest_count(self):
        oe_labs = self.env['oeh.medical.lab.test']
        for ls in self:
            domain = [('patient', '=', ls.id)]
            lab_ids = oe_labs.search(domain)
            labs = oe_labs.browse(lab_ids)
            labs_count = 0
            for lab in labs:
                labs_count += 1
            ls.labs_count = labs_count
        return True

    lab_test_ids = fields.One2many('oeh.medical.lab.test', 'patient', string='Lab Test IDs')
    labs_count = fields.Integer(compute=_labtest_count, string="Lab Tests")


class AccountMoveLab(models.Model):
    _inherit = 'account.move'

    labtest_id = fields.Many2one('oeh.medical.lab.request', string="Lab Request #")


class OeHealthAppointmentLab(models.Model):
    _inherit = 'oeh.medical.appointment'

    labtest_line = fields.One2many('oeh.medical.lab.test', 'appointment', string='Lab Test Lines',
                                   readonly=False, )

    def get_appointment_items_invoice_lines(self, with_consultancy=False):
        invoice_lines = []
        for acc in self:
            sequence = 0

            if with_consultancy:
                consultancy_invoice_lines = acc.get_consultation_invoice_lines()
                invoice_lines.extend(consultancy_invoice_lines)
                sequence = 2

            # Create Invoice lines for Treatment
            # if acc.treatment_line:
            #     sequence += 1
            #     invoice_lines.append((0, 0, {
            #         'name': 'Treatment',
            #         'display_type': 'line_section',
            #         'account_id': False,
            #         'sequence': sequence,
            #     }))
            #     for treat_line in acc.treatment_line:
            #         if treat_line.treatment_items:
            #             for item in treat_line.treatment_items:
            #                 sequence += 1
            #                 invoice_lines.append((0, 0, {
            #                     'display_type': False,
            #                     'quantity': item.qty,
            #                     'name': item.name.name,
            #                     'price_unit': item.name.list_price,
            #                     'product_id': item.name.id,
            #                     'product_uom_id': item.name.uom_id and item.name.uom_id.id or False,
            #                     'sequence': sequence,
            #                 }))

            # Create Invoice lines for Labs
            if acc.labtest_line:
                sequence += 1
                invoice_lines.append((0, 0, {
                    'name': 'Lab Tests',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence,
                }))

                for lab in acc.labtest_line:
                    lab_test_name = lab.name

                    invoice_lines.append((0, 0, {
                        'display_type': 'line_section',
                        'name': lab_test_name,
                        'quantity': 1,
                        'product_uom_id': self.env.ref('uom.product_uom_unit') and self.env.ref(
                            'uom.product_uom_unit').id or False,
                        'sequence': sequence,
                    }))

            # Create Invoice lines for Prescription
            # if acc.prescription_line:
            #     sequence += 1
            #     invoice_lines.append((0, 0, {
            #         'name': 'Medicines',
            #         'display_type': 'line_section',
            #         'account_id': False,
            #         'sequence': sequence,
            #     }))
            #
            #     for pres_line in acc.prescription_line:
            #         if pres_line.prescription_line:
            #             for pres in pres_line.prescription_line:
            #                 sequence += 1
            #                 invoice_lines.append((0, 0, {
            #                     'display_type': False,
            #                     'quantity': pres.qty,
            #                     'name': pres.name.product_id.name,
            #                     'product_id': pres.name.product_id.id,
            #                     'product_uom_id': pres.name.product_id.uom_id and pres.name.product_id.uom_id.id or False,
            #                     'price_unit': pres.name.product_id.list_price,
            #                     'sequence': sequence,
            #                 }))
            #             pres_line.write({'state': 'Invoiced'})
        return invoice_lines


class OeHealthPhysician(models.Model):
    _inherit = 'oeh.medical.physician'

    staff_type = fields.Selection(selection_add=[('lab technician', 'Lab Technician')])

    def _lab_tests_count(self):
        oe_labs = self.env['oeh.medical.lab.test']
        for ls in self:
            domain = [('lab_technician_id', '=', ls.id)]
            lab_ids = oe_labs.search(domain)
            labs = oe_labs.browse(lab_ids)
            lab_test = 0
            for lab in labs:
                lab_test += 1
            ls.lab_test = lab_test
        return True

    lab_test = fields.Integer(compute=_lab_tests_count, string='Lab Tests')


class OeHealthLabRequest(models.Model):
    _name = 'oeh.medical.lab.request'
    _description = 'Lab Requests'
    # _rec_name = 'patient'

    LABREQUEST_STATE = [
        ('Draft', 'Draft'),
        ('Sample Taken', 'Sample Taken'),
        ('Invoiced', 'Invoiced'),
        ('Pushed For Testing', 'Pushed For Testing'),
    ]

    name = fields.Char(string='Lab Request #', size=16, readonly=True, required=True, help="Lab Request ID",
                       default=lambda *a: '/')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True)

    institution = fields.Many2one('oeh.medical.health.center', string='Health Center', help="Medical Center")

    date_requested = fields.Datetime(string='Date requested',
                                     default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))

    requestor = fields.Char(string='Doctor who requested the test', help="Doctor who requested the test")

    state = fields.Selection(LABREQUEST_STATE, string='State', readonly=True, default=lambda *a: 'Draft')

    lab_test_ids = fields.Many2many('oeh.medical.labtest.types', 'lab_test_types', string='Lab Test types')

    lab_sample_ids = fields.One2many('oeh.medical.lab.samples', 'sample_id')
    total = fields.Float(string='Total', store=True, compute='_amount_total', readonly=True)
    invoice_count = fields.Integer(string="Invoices")
    chief_complaint = fields.Text(string='Chief Complaint')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.onchange('patient')
    def onchange_patient(self):
        self.currency_id = self.env.user.company_id.currency_id

    @api.onchange('institution')
    def compute_currency(self):
        comp = self.institution.company_id.currency_id
        self.currency_id = comp
        for i in self.lab_test_ids:
            i.currency_id = comp

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                sequence = self.env['ir.sequence'].next_by_code('oeh.medical.lab.request')
                vals['name'] = sequence or '/'
        return super(OeHealthLabRequest, self).create(vals_list)

    @api.depends('lab_test_ids')
    def _amount_total(self):
        total = 0.0
        for line in self.lab_test_ids:
            total += line.test_charge
            self.total = total

    @api.onchange('lab_test_ids')
    def onchange_lab_test_ids(self):
        currency = self.env.user.company_id.currency_id
        if self.institution:
            comp = self.institution.company_id.currency_id
            for i in self.lab_test_ids:
                i.currency_id = comp
        else:
            for i in self.lab_test_ids:
                i.currency_id = currency

    def add_sample(self):
        return {
            'name': _('Add Sample'),
            'type': 'ir.actions.act_window',
            'res_model': 'oeh.medical.samples.wizard',
            'view_mode': 'form',
            'target': 'new',
            'domain': [('samples_ids', 'in', self.lab_test_ids.ids)],
            'context': {
                'default_samples_ids': self.lab_test_ids.ids
            }
        }

    def finished_sample(self):
        return self.write({'state': 'Sample Taken'})

    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal

    def create_invoice(self):
        res = {}
        for lab in self:
            # Create Invoice
            if lab.patient:
                invoice_lines = []
                default_journal = self._get_default_journal()

                if not default_journal:
                    raise UserError(_('No accounting journal with type "Sale" defined !'))

                sequence_count = 1
                invoice_lines.append((0, 0, {
                    'name': 'Lab Tests',
                    'display_type': 'line_section',
                    'account_id': False,
                    'sequence': sequence_count,
                }))

                sequence_count += 1

                for i in lab.lab_test_ids:
                    lab_test_name = i.name
                    price_unit = i.test_charge
                    invoice_lines.append((0, 0, {
                        'display_type': 'product',
                        'name': lab_test_name,
                        'price_unit': price_unit,
                        'quantity': 1,
                        'product_uom_id': self.env.ref('uom.product_uom_unit') and self.env.ref(
                            'uom.product_uom_unit').id or False,
                        'sequence': sequence_count,
                    }))

                invoice = self.env['account.move'].sudo().create({
                    'move_type': 'out_invoice',
                    'journal_id': default_journal.id,
                    'partner_id': lab.patient.partner_id.id,
                    'patient': lab.patient.id,
                    'invoice_date': datetime.datetime.now().date(),
                    'date': datetime.datetime.now().date(),
                    # 'ref': "Lab Test # : " + lab.name,
                    'labtest_id': lab.id,
                    'invoice_line_ids': invoice_lines
                })
                if self.env.company.stock_deduction_method == 'invoice_create':
                    invoice.oeh_process_inventories()
                # res = lab.write({'state': 'Invoiced', 'move_id': invoice.id})
            self.write({'state': 'Invoiced'})
        return res

    def push_for_testing(self):
        action = self.env["ir.actions.actions"]._for_xml_id("oehealth_lab.oeh_medical_lab_test_action_tree")
        test_name = []
        if self.lab_test_ids:
            sequence_count = 0
            for test in self.lab_test_ids:
                seq_lab = 0
                test_name.append((0, 0, {
                    'name': test.name,
                    'display_type': 'line_section',
                    'sequence': sequence_count,
                }))

                if test.lab_criteria:
                    for criteria in test.lab_criteria:
                        sequence_count += 1
                        seq_lab += 1
                        test_name.append((0, 0, {
                            'name': criteria.name,
                            'normal_range': criteria.normal_range,
                            'units': criteria.units and criteria.units.id or False,
                            'sequence': sequence_count,
                            'seq': seq_lab
                        }))

        action['context'] = {
            'default_institution': self.institution.id,
            'default_patient': self.patient.id,
            'default_date_requested': self.date_requested,
            'default_requestor': self.requestor,
            'default_lab_request': self.id,
            'default_lab_test_type_ids': [(6, 0, self.lab_test_ids.ids)],
            'default_lab_test_criteria': test_name
        }
        action['views'] = [(self.env.ref('oehealth_lab.oeh_medical_lab_test_form').id, 'form')]
        self.write({'state': 'Pushed For Testing'})

        return action


class OeHealthSampleType(models.Model):
    _name = "oeh.medical.sample.types"
    _description = "Lab Sample Types "

    name = fields.Char(string='Sample Types', size=256, required=True)


class OeHealthSamples(models.Model):
    _name = "oeh.medical.lab.samples"
    _description = "Lab Samples"

    comments = fields.Text(string='Comments')
    samples_ids = fields.Many2many('oeh.medical.labtest.types')
    sample_type = fields.Many2one('oeh.medical.sample.types', required=True, string='Sample Type')
    sample_id = fields.Many2one('oeh.medical.lab.request')
