from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AuditRequest(models.Model):
    """Audit Request"""
    _name = "audit.request"
    _description = "Audit Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", default="New")

#     state = fields.Selection(
#         [('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
#          ('approve', 'Approve')], tracking=True,
#         default="new", string="State")
#     requested_date = fields.Date(string="Requested Date",
#                                  default=fields.Date.today())
#     arp_id = fields.Many2one("project.project", string="ARP",
#                              domain="[('plan_id', '=?', False)]")
#     aop_id = fields.Many2one("project.task", string="AOP",
#                              domain="[('plan_id', '=?', False), ('project_id', '=?', arp_id)]")
#     annual_plan_id = fields.Many2one('annual.plan', required=False)
#     custom_audit_class_of_transaction_id = fields.Many2one(
#         'custom.audit.request', string="Custom Audit Class Of Transactions",
#         readonly=True)
#     audit_class_of_transaction_count = fields.Integer(
#         string="- Audit Class Of Transactions",
#         compute="_compute_audit_class_of_transaction_count")
#     custom_audit_disclosure_id = fields.Many2one('custom.audit.request',
#                                                  string="Custom Audit Disclosures",
#                                                  readonly=True)
#     audit_disclosure_count = fields.Integer(
#         string="- Audit Disclosures",
#         compute="_compute_audit_disclosure_count")
#     custom_audit_predetermined_objective_id = fields.Many2one(
#         'custom.audit.request', string="Custom Audit Predetermined Objectives",
#         readonly=True)
#     predetermined_objective_count = fields.Integer(
#         string="- Predetermined Objectives",
#         compute="_compute_predetermined_objective_count")
#     complaince_count = fields.Integer(
#         string="- Complaince",
#         compute="_compute_complaince_count")
#     custom_audit_complaince_id = fields.Many2one('custom.audit.request',
#                                                  string="Custom Audit Complaince",
#                                                  readonly=True)
#     audit_material_irregularities_count = fields.Integer(
#         string="- Material Irregularities",
#         compute="_compute_audit_material_irregularities")
#     custom_audit_material_irregularities_id = fields.Many2one(
#         'custom.audit.request', string="Custom Audit Material Irregularities",
#         readonly=True)
#     audit_evidence_count = fields.Integer(
#         string="- Audit Evidence",
#         compute="_compute_audit_evidence")
#     custom_audit_evidence_id = fields.Many2one('custom.audit.request',
#                                                string="Custom Audit Evidence",
#                                                readonly=True)
#     uncorrected_misstatements_and_conclude_count = fields.Integer(
#         string="- Uncorrected Misstatements And Conclude",
#         compute="_compute_uncorrected_misstatements_and_conclude")
#     custom_audit_uncorrected_misstatements_and_conclude_id = fields.Many2one(
#         'custom.audit.request',
#         string="Custom Audit Uncorrected Misstatements And Conclude",
#         readonly=True)
#     deficiencies_in_internal_control_count = fields.Integer(
#         string="- Deficiencies In Internal Control",
#         compute="_compute_deficiencies_in_internal_control")
#     custom_audit_deficiencies_in_internal_control_id = fields.Many2one(
#         'custom.audit.request',
#         string="Custom Audit Deficiencies In Internal Control", readonly=True)
#     custom_understanding_business_id = fields.Many2one(
#         'custom.audit.request',
#         string="Custom Understanding Of Business", readonly=True)
#     understanding_business_count = fields.Integer(
#         string='- Understanding Of Business Count',
#         compute="_compute_understanding_business_count")
#     custom_compliance_materiality_id = fields.Many2one(
#         'custom.audit.request',
#         string="Custom Compliance Scoping and Materiality", readonly=True)
#     compliance_materiality_count = fields.Integer(
#         string='- Compliance Scoping and Materiality Count',
#         compute="_compute_compliance_materiality_count")
#     custom_communication_correspondence_id = fields.Many2one(
#         'custom.audit.request',
#         string="Communication And Correspondence - Communicate With Auditee Management",
#         readonly=True)
#     communication_correspondence_auditee_count = fields.Integer(
#         string='- Communicate With Auditee Management Count',
#         compute="_compute_communication_correspondence_auditee_count")
#     custom_audit_team_id = fields.Many2one(
#         'custom.audit.request',
#         string="Custom Communication And Correspondence - Communicate Within Audit Team",
#         readonly=True)
#     communication_correspondence_team_count = fields.Integer(
#         string='- Communicate Within Audit Team',
#         compute="_compute_communication_correspondence_team_count")
#     custom_information_id = fields.Many2one(
#         'custom.audit.request',
#         string="Custom Communication And Correspondence - Request For Information",
#         readonly=True)
#     communication_correspondence_info_count = fields.Integer(
#         string='- Request For Information',
#         compute="_compute_communication_correspondence_info_count")
#     custom_finding_id = fields.Many2one(
#         'custom.audit.request',
#         string="Custom Communication And Correspondence - Communicate Audit Finding",
#         readonly=True)
#     communication_correspondence_find_count = fields.Integer(
#         string='- Communicate Audit Finding',
#         compute="_compute_communication_correspondence_find_count")
#     custom_audit_oversight_id = fields.Many2one(
#         'custom.audit.request', string="Audit Oversight",
#         readonly=True)
#     audit_oversight_count = fields.Integer(
#         string='- Audit Oversight',
#         compute="_compute_audit_oversight_count")
#     custom_management_representation_id = fields.Many2one(
#         'custom.audit.request', string="Obtain Management Representation",
#         readonly=True)
#     management_representation_count = fields.Integer(
#         string='- Obtain Management Representation',
#         compute="_compute_management_representation_count")
#     custom_perform_analytical_procedure_id = fields.Many2one(
#         'custom.audit.request', string='Perform Analytical Procedures',
#         readonly=True)
#     analytical_procedure_count = fields.Integer(
#         string='- Perform Analytical Procedures',
#         compute="_compute_analytical_procedure_count")
#     custom_material_misstatements_id = fields.Many2one(
#         'custom.audit.request',
#         string='Assess And Plan Response To Risks Of Material Misstatement',
#         readonly=True)
#     material_misstatements_count = fields.Integer(
#         string='- Assess And Plan Response To Risks Of Material Misstatement',
#         compute="_compute_material_misstatements_count")
#     custom_risk_assessment_response_id = fields.Many2one(
#         'custom.audit.request', string='Risk Assessment And Response',
#         readonly=True)
#     risk_assessment_count = fields.Integer(
#         string='- Risk Assessment And Response',
#         compute="_compute_risk_assessment_count")
#     custom_fraud_risk_assessment_id = fields.Many2one(
#         'custom.audit.request', string='Fraud Risk Assessment',
#         readonly=True)
#     fraud_risk_assessment_count = fields.Integer(
#         string='- Fraud Risk Assessment',
#         compute="_compute_fraud_risk_assessment_count")
#     custom_allegation_compliance_id = fields.Many2one(
#         'custom.audit.request',
#         string='Allegations and Non - Compliance with Laws and Regulations',
#         readonly=True)
#     allegation_compliance_count = fields.Integer(
#         string='- Compliance with Laws and Regulations',
#         compute="_compute_allegation_compliance_count")
#     custom_entity_internal_control_id = fields.Many2one(
#         'custom.audit.request',
#         string='Understand The Entity  Internal Controls',
#         readonly=True)
#     entity_internal_control_count = fields.Integer(
#         string="- Understand The Entity's Internal Controls",
#         compute="_compute_entity_internal_control_count")
#     custom_business_process_relevant_control_id = fields.Many2one(
#         'custom.audit.request',
#         string='Understand The Business Processes And Relevant Controls',
#         readonly=True)
#     business_process_relevant_control_count = fields.Integer(
#         string="- Understand The Business Processes And Relevant Controls",
#         compute="_compute_business_process_relevant_control_count")
#     custom_internal_control_adequacy_assessment_id = fields.Many2one(
#         'custom.audit.request',
#         string='Internal Controls Adequacy Assessment',
#         readonly=True)
#     internal_control_adequacy_assessment_count = fields.Integer(
#         string="- Internal Controls Adequacy Assessment",
#         compute="_compute_internal_control_adequacy_assessment_count")
#
#     # Audit Governance
#     audit_methodology_id = fields.Many2one(
#         'audit.methodology',
#         string="Audit Methodology",
#         readonly=True
#     )
#     audit_methodology = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                          default="yes", string="Need to Create")
#     audit_methodology_state = fields.Selection(
#         related='audit_methodology_id.state',
#         string="Audit Methodology Status",
#         readonly=True)
#
#     # guidance_id = fields.Many2one(
#     #     'guidance.and.information',
#     #     string="Guidance And Other Information",
#     #     readonly=True
#     # )
#     guidance = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                 default="yes", string="Need to Create")
#     # guidance_state = fields.Selection(
#     #     related='guidance_id.state',
#     #     string="Guidance Status",
#     #     readonly=True)
#
#     financial_statement_id = fields.Many2one(
#         'financial.statement',
#         string="Financial Statements And Performance Report",
#         readonly=True
#     )
#     financial_statement = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                            default="yes",
#                                            string="Need to Create")
#     financial_statement_state = fields.Selection(
#         related='financial_statement_id.state',
#         string="Financial Statement Status",
#         readonly=True)
#
#     internal_quality_control_id = fields.Many2one(
#         "internal.quality.control",
#         string="Quality Control - Internal Review Framework",
#         readonly=True
#     )
#     internal_quality_control = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                                 default="yes",
#                                                 string="Need to Create")
#     internal_quality_control_state = fields.Selection(
#         related='internal_quality_control_id.state',
#         string="Internal Quality Control Status",
#         readonly=True)
#
#     quality_control_peer_id = fields.Many2one(
#         'quality.control.peer',
#         string="Quality Control - Internal Peer Review",
#         readonly=True
#     )
#     quality_control_peer = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                             default="yes",
#                                             string="Need to Create")
#     quality_control_peer_state = fields.Selection(
#         related='quality_control_peer_id.state',
#         string="Quality Control Peer Review Status",
#         readonly=True)
#
#     quality_control_outsourced_peer_id = fields.Many2one(
#         'quality.control.outsourced.peer',
#         string="Quality Control - Outsourced Peer Review",
#         readonly=True
#     )
#
#     quality_control_outsourced_peer = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes", string="Need to Create")
#     quality_control_outsourced_peer_state = fields.Selection(
#         related='quality_control_outsourced_peer_id.state',
#         string="Quality Control Outsourced Peer Review Status",
#         readonly=True)
#
#     internal_audit_charter_id = fields.Many2one(
#         'internal.audit.charter',
#         string="Internal Audit Charter",
#         readonly=True
#     )
#     internal_audit_charter = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                               default="yes",
#                                               string="Need to Create")
#     internal_audit_charter_state = fields.Selection(
#         related='internal_audit_charter_id.state',
#         string="Internal Audit Charter Status",
#         readonly=True)
#
#     audit_committee_charter_id = fields.Many2one(
#         'audit.committee.charter',
#         string="Audit Committee Charter",
#         readonly=True
#     )
#     audit_committee_charter = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                                default="yes",
#                                                string="Need to Create")
#     audit_committee_charter_state = fields.Selection(
#         related='audit_committee_charter_id.state',
#         string="Audit Committee Charter Status",
#         readonly=True)
#
#     internal_audit_plan_id = fields.Many2one(
#         'internal.audit.plan',
#         string="Internal Audit Plan",
#         readonly=True
#     )
#     internal_audit_plan = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                            default="yes",
#                                            string="Need to Create")
#     internal_audit_plan_state = fields.Selection(
#         related='internal_audit_plan_id.state',
#         string="Internal Audit Plan Status",
#         readonly=True)
#     # Create Audit
#     title = fields.Char(string="Title", required=True)
#     date_from = fields.Date(string="From Date", required=True)
#     date_to = fields.Date(string="To Date", required=True)
#     # tracking
#     audit_request_tracking_ids = fields.One2many('audit.request.tracking',
#                                                  'audit_request_id',
#                                                  string='Tracking')
#
#     # @api.onchange('internal_audit_plan_id')
#     # def _onchange_internal_audit_plan(self):
#     #     """Change date based on audit plan"""
#     #     self.date_from = self.internal_audit_plan_id.date_from if self.internal_audit_plan_id else None
#     #     self.date_to = self.internal_audit_plan_id.date_to if self.internal_audit_plan_id else None
#
#     # Overall Audit Approach
#     understanding_business_id = fields.Many2one('understanding.business',
#                                                 readonly=True,
#                                                 string="Understanding Of Business")
#     understanding_business = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                               default="yes",
#                                               string="Need to Create")
#
#     compliance_materiality_id = fields.Many2one('compliance.materiality',
#                                                 readonly=True,
#                                                 string="Compliance Scoping and Materiality")
#     compliance_materiality = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                               default="yes",
#                                               string="Need to Create")
#     communication_correspondence_id = fields.Many2one(
#         'communication.correspondence',
#         string="Communication And Correspondence - Communicate With Auditee Management",
#         readonly=True)
#     communication_correspondence = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes", string="Need to Create")
#     audit_team_id = fields.Many2one('communication.correspondence',
#                                     string="Communication And Correspondence - Communicate Within Audit Team",
#                                     readonly=True)
#     audit_team = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                   default="yes", string="Need to Create")
#     information_id = fields.Many2one('communication.correspondence',
#                                      string="Communication And Correspondence - Request For Information",
#                                      readonly=True)
#     information = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                    default="yes", string="Need to Create")
#     finding_id = fields.Many2one('communication.correspondence',
#                                  string="Communication And Correspondence - Communicate Audit Finding",
#                                  readonly=True)
#     finding = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="yes",
#                                string="Need to Create")
#     audit_oversight_id = fields.Many2one('audit.oversight',
#                                          string="Audit Oversight",
#                                          readonly=True)
#     audit_oversight = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                        default="yes", string="Need to Create")
#     management_representation_id = fields.Many2one('management.representation',
#                                                    string="Obtain Management Representation",
#                                                    readonly=True)
#     management_representation = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                                  default="yes",
#                                                  string="Need to Create")
#     perform_analytical_procedure_id = fields.Many2one(
#         'perform.analytical.procedures', string='Perform Analytical Procedures',
#         readonly=True)
#     perform_analytical_procedure = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes",
#         string="Need to Create")
#     material_misstatements_id = fields.Many2one('material.misstatements',
#                                                 string='Assess And Plan Response To Risks Of Material Misstatement',
#                                                 readonly=True)
#     material_misstatements = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes",
#         string="Need to Create")
#     risk_assessment_response_id = fields.Many2one('risk.assessment.response',
#                                                   string='Risk Assessment And Response',
#                                                   readonly=True)
#     risk_assessment_response = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes",
#         string="Need to Create")
#     fraud_risk_assessment_id = fields.Many2one('fraud.risk.assessment',
#                                                string='Fraud Risk Assessment',
#                                                readonly=True)
#     fraud_risk_assessment = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes",
#         string="Need to Create")
#     allegation_compliance_id = fields.Many2one('allegations.non.compliance',
#                                                string='Allegations and Non - Compliance with Laws and Regulations',
#                                                readonly=True)
#     allegation_compliance = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes",
#         string="Need to Create")
#     entity_internal_control_id = fields.Many2one('internal.control',
#                                                  string='Understand The Entity s Internal Controls',
#                                                  readonly=True)
#     entity_internal_control = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes",
#         string="Need to Create")
#     business_process_relevant_control_id = fields.Many2one('relevant.control',
#                                                            string='Understand The Business Processes And Relevant Controls',
#                                                            readonly=True)
#     business_process_relevant_control = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes",
#         string="Need to Create")
#     internal_control_adequacy_assessment_id = fields.Many2one(
#         'relevant.control',
#         string='Internal Controls Adequacy Assessment',
#         readonly=True)
#     internal_control_adequacy_assessment = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes",
#         string="Need to Create")
#
#     # State fields with related attribute
#     audit_planning_understanding_business_state = fields.Selection(
#         related='custom_understanding_business_id.state',
#         string="Understanding Of Business Status",
#         readonly=True)
#
#     compliance_materiality_state = fields.Selection(
#         related='custom_compliance_materiality_id.state',
#         string="Compliance Scoping and Materiality Status",
#         readonly=True)
#
#     communication_correspondence_state = fields.Selection(
#         related='custom_communication_correspondence_id.state',
#         string="Communication And Correspondence - Communicate With Auditee Management Status",
#         readonly=True)
#
#     audit_team_state = fields.Selection(
#         related='custom_audit_team_id.state',
#         string="Communication And Correspondence - Communicate Within Audit Team Status",
#         readonly=True)
#
#     information_state = fields.Selection(
#         related='custom_information_id.state',
#         string="Communication And Correspondence - Request For Information Status",
#         readonly=True)
#
#     finding_state = fields.Selection(
#         related='custom_finding_id.state',
#         string="Communication And Correspondence - Communicate Audit Finding Status",
#         readonly=True)
#
#     audit_oversight_state = fields.Selection(
#         related='custom_audit_oversight_id.state',
#         string="Audit Oversight Status",
#         readonly=True)
#
#     management_representation_state = fields.Selection(
#         related='custom_management_representation_id.state',
#         string="Obtain Management Representation Status",
#         readonly=True)
#     perform_analytical_procedure_state = fields.Selection(
#         related='custom_perform_analytical_procedure_id.state',
#         string="Perform Analytical Procedures Status",
#         readonly=True)
#     material_misstatements_state = fields.Selection(
#         related='custom_material_misstatements_id.state',
#         string="Assess And Plan Response To Risks Of Material Misstatement Status",
#         readonly=True)
#     risk_assessment_responses_state = fields.Selection(
#         related='custom_risk_assessment_response_id.state',
#         string="Risk Assessment And Response Status",
#         readonly=True)
#     fraud_risks_assessment_state = fields.Selection(
#         related='custom_fraud_risk_assessment_id.state',
#         string="Fraud Risk Assessment",
#         readonly=True)
#     allegation_compliance_state = fields.Selection(
#         related='custom_allegation_compliance_id.state',
#         string="Allegations and Non - Compliance with Laws and Regulations",
#         readonly=True)
#     entity_internal_control_state = fields.Selection(
#         related='custom_entity_internal_control_id.state',
#         string="Understand The Entity's Internal Controls",
#         readonly=True)
#     business_process_relevant_control_state = fields.Selection(
#         related='custom_business_process_relevant_control_id.state',
#         string="Understand The Business Processes And Relevant Controls",
#         readonly=True)
#     internal_control_adequacy_assessment_state = fields.Selection(
#         related='custom_internal_control_adequacy_assessment_id.state',
#         string="Internal Controls Adequacy Assessment", readonly=True)
#
#     # Plan Audit
#     entity_environment_id = fields.Many2one('entity.environment', readonly=True,
#                                             string="Understand The Entity And It's Environment")
#     terms_engagement_id = fields.Many2one('terms.engagement',
#                                           string="Communicate Terms Of Engagement",
#                                           readonly=True)
#     audit_strategy_id = fields.Many2one('audit.strategy',
#                                         string="Audit Strategy", readonly=True)
#     audit_project_id = fields.Many2one('audit.project', string="Audit Project",
#                                        readonly=True)
#     revise_materiality_id = fields.Many2one('revise.materiality',
#                                             string="Revise Materiality",
#                                             readonly=True)
#     audit_location_id = fields.Many2one('audit.location',
#                                         string="Audit Of Multiple Locations",
#                                         readonly=True)
#     # State fields with related attribute
#     understanding_business_state = fields.Selection(
#         related='understanding_business_id.state',
#         string="Understanding Of Business Status",
#         readonly=True)
#
#     terms_engagement_state = fields.Selection(
#         related='terms_engagement_id.state',
#         string="Communicate Terms Of Engagement Status",
#         readonly=True)
#
#     audit_strategy_state = fields.Selection(
#         related='audit_strategy_id.state',
#         string="Audit Strategy Status",
#         readonly=True)
#
#     audit_project_state = fields.Selection(
#         related='audit_project_id.state',
#         string="Audit Project Status",
#         readonly=True)
#
#     revise_materiality_state = fields.Selection(
#         related='revise_materiality_id.state',
#         string="Revise Materiality Status",
#         readonly=True)
#
#     audit_location_state = fields.Selection(
#         related='audit_location_id.state',
#         string="Audit Of Multiple Locations Status",
#         readonly=True)
#
#     # Understand system of internal COntrol
#     internal_control_id = fields.Many2one('internal.control',
#                                           string="Understand The Entity's Internal Controls",
#                                           readonly=True)
#     relevant_control_id = fields.Many2one('relevant.control',
#                                           string="Understand The Business Processes And Relevant Controls",
#                                           readonly=True)
#     # Define the related state fields
#     internal_control_state = fields.Selection(
#         related='internal_control_id.state',
#         string="Internal Control Status",
#         readonly=True)
#     relevant_control_state = fields.Selection(
#         related='relevant_control_id.state',
#         string="Relevant Control Status",
#         readonly=True)
#     # Perform Risk Assessment
#     perform_procedures_id = fields.Many2one('perform.analytical.procedures',
#                                             string="Perform Analytical Procedures",
#                                             readonly=True)
#     perform_procedures_state = fields.Selection(
#         related="perform_procedures_id.state",
#         string="Perform Analytical Procedures Status")
#     material_misstatement_id = fields.Many2one('material.misstatement',
#                                                string="Misstatement",
#                                                readonly=True)
#     material_misstatement_state = fields.Selection(
#         related="material_misstatement_id.state",
#         string="Misstatement")
#     risk_assessment_response_id = fields.Many2one('risk.assessment.response',
#                                                   string="Risk Assessment Response",
#                                                   readonly=True)
#     risk_assessment_response_state = fields.Selection(
#         related="risk_assessment_response_id.state",
#         string="Risk Assessment Response")
#     access_use_work_id = fields.Many2one('access.use.work',
#                                          string="Access Use of Work of Others",
#                                          readonly=True)
#     access_use_work_state = fields.Selection(
#         related="access_use_work_id.state",
#         string="Access Use of Work of Others")
#     fraud_risk_assessment_id = fields.Many2one('fraud.risk.assessment',
#                                                string="Fraud Risk Assessment",
#                                                readonly=True)
#     fraud_risk_assessment_state = fields.Selection(
#         related="fraud_risk_assessment_id.state",
#         string="Fraud Risk Assessment")
#     allegations_non_compliance_laws_regulations_id = fields.Many2one(
#         'allegations.non.compliance',
#         string="Allegations and Non - Compliance with Laws and Regulations",
#         readonly=True)
#     allegations_non_compliance_laws_regulations_state = fields.Selection(
#         related="allegations_non_compliance_laws_regulations_id.state",
#         string="Allegations and Non - Compliance with Laws and Regulations")
#
#     # Audit Execution
#     # audit_class_of_transactions_id = fields.Many2one(
#     #     'audit.transactions',
#     #     string="Audit Class Of Transactions",
#     #     readonly=True
#     # )
#     class_of_transactions = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                              default="yes",
#                                              string="Need to Create")
#     audit_disclosures_id = fields.Many2one(
#         'audit.disclosures',
#         string="Audit Disclosures",
#         readonly=True
#     )
#     audit_disclosures = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                          default="yes",
#                                          string="Need to Create")
#     predetermined_objectives_id = fields.Many2one(
#         'predetermined.objectives',
#         string="Predetermined Objectives",
#         readonly=True
#     )
#     predetermined_objectives = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                                 default="yes",
#                                                 string="Need to Create")
#     complaince_id = fields.Many2one(
#         'audit.complaince',
#         string="Complaince",
#         readonly=True
#     )
#     complaince = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                   default="yes",
#                                   string="Need to Create")
#     material_irregularities_id = fields.Many2one(
#         'material.irregularities',
#         string="Material Irregularities",
#         readonly=True
#     )
#     material_irregularities = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                                default="yes",
#                                                string="Need to Create")
#     audit_evidence_id = fields.Many2one(
#         'audit.evidence',
#         string="Audit Evidence",
#         readonly=True
#     )
#     audit_evidence = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                       default="yes",
#                                       string="Need to Create")
#     uncorrected_misstatements_and_conclude_id = fields.Many2one(
#         'uncorrected.misstatements',
#         string="Uncorrected Misstatements And Conclude",
#         readonly=True
#     )
#     uncorrected_misstatements_and_conclude = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes", string="Need to Create")
#     deficiencies_in_internal_control_id = fields.Many2one(
#         'deficiencies.internal.control',
#         string="Deficiencies In Internal Control",
#         readonly=True
#     )
#     deficiencies_in_internal_control = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes", string="Need to Create")
#     # state
#     audit_class_of_transactions_state = fields.Selection(
#         related="custom_audit_class_of_transaction_id.state",
#         string="Audit Class Of Transactions State",
#         readonly=True
#     )
#
#     audit_disclosures_state = fields.Selection(
#         related="custom_audit_disclosure_id.state",
#         string="Audit Disclosures State",
#         readonly=True
#     )
#
#     predetermined_objectives_state = fields.Selection(
#         related="custom_audit_predetermined_objective_id.state",
#         string="Predetermined Objectives State",
#         readonly=True
#     )
#
#     complaince_state = fields.Selection(
#         related="custom_audit_complaince_id.state",
#         string="Compliance State",
#         readonly=True
#     )
#
#     material_irregularities_state = fields.Selection(
#         related="custom_audit_material_irregularities_id.state",
#         string="Material Irregularities State",
#         readonly=True
#     )
#
#     audit_evidence_state = fields.Selection(
#         related="custom_audit_evidence_id.state",
#         string="Audit Evidence State",
#         readonly=True
#     )
#
#     uncorrected_misstatements_and_conclude_state = fields.Selection(
#         related="custom_audit_uncorrected_misstatements_and_conclude_id.state",
#         string="Uncorrected Misstatements and Conclude State",
#         readonly=True
#     )
#
#     deficiencies_in_internal_control_state = fields.Selection(
#         related="custom_audit_deficiencies_in_internal_control_id.state",
#         string="Deficiencies In Internal Control State",
#         readonly=True
#     )
#     # Reporting
#     custom_key_audit_matters_id = fields.Many2one(
#         'custom.audit.request',
#         string="Key Audit Matters", readonly=True)
#     key_audit_matters = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                          default="yes", string="Need to Create")
#     key_audit_matters_state = fields.Selection(
#         related="custom_key_audit_matters_id.state",
#         string="Key Audit Matters State",
#         readonly=True
#     )
#     key_audit_matters_count = fields.Integer(string="Key Audit Matters",
#                                              compute="_compute_key_audit_matters_count")
#
#     custom_prepare_management_reports_id = fields.Many2one(
#         'custom.audit.request',
#         string="Prepare Management Reports", readonly=True)
#     prepare_management_reports = fields.Selection(
#         [('yes', 'Yes'), ('no', 'No')],
#         default="yes", string="Need to Create")
#     prepare_management_reports_state = fields.Selection(
#         related="custom_prepare_management_reports_id.state",
#         string="Prepare Management Reports State",
#         readonly=True
#     )
#     prepare_management_reports_count = fields.Integer(
#         string="Prepare Management Reports",
#         compute="_compute_prepare_management_reports_count")
#
#     custom_prepare_auditor_report_id = fields.Many2one(
#         'custom.audit.request',
#         string="Prepare Auditor's Report", readonly=True)
#     prepare_auditor_report = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                               default="yes",
#                                               string="Need to Create")
#     prepare_auditor_report_state = fields.Selection(
#         related="custom_prepare_auditor_report_id.state",
#         string="Prepare Auditor's Report State",
#         readonly=True
#     )
#     prepare_auditor_report_count = fields.Integer(
#         string="Draft Report",
#         compute="_compute_prepare_auditor_report_count")
#
#     custom_prepare_dashboard_report_id = fields.Many2one(
#         'custom.audit.request',
#         string="Prepare Dashboard Report", readonly=True)
#     prepare_dashboard_report = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                                 default="yes",
#                                                 string="Need to Create")
#     prepare_dashboard_report_state = fields.Selection(
#         related="custom_prepare_dashboard_report_id.state",
#         string="Prepare Dashboard Report State",
#         readonly=True
#     )
#     prepare_dashboard_report_count = fields.Integer(
#         string='Prepare Dashboard Report',
#         compute="_compute_prepare_dashboard_report_count")
#
#     custom_prepare_sector_report_id = fields.Many2one(
#         'custom.audit.request',
#         string="Prepare Sector Report", readonly=True)
#
#     prepare_sector_report = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                              default="yes",
#                                              string="Need to Create")
#     prepare_sector_report_state = fields.Selection(
#         related="custom_prepare_sector_report_id.state",
#         string="Prepare Sector Report State",
#         readonly=True
#     )
#     prepare_sector_report_count = fields.Integer(
#         string='Prepare Sector Report',
#         compute="_compute_prepare_sector_report_count")
#
#     custom_final_report_id = fields.Many2one(
#         'custom.audit.request',
#         string="Prepare Final Report", readonly=True)
#
#     prepare_final_report = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                              default="yes",
#                                              string="Need to Create")
#     prepare_final_report_state = fields.Selection(
#         related="custom_final_report_id.state",
#         string="Prepare Sector Report State",
#         readonly=True
#     )
#     prepare_final_report_count = fields.Integer(
#         string='Prepare Final Report',
#         compute="_compute_final_report_count")
#
#     custom_prepare_general_report_id = fields.Many2one(
#         'custom.audit.request',
#         string="Prepare General Report", readonly=True)
#     prepare_general_report = fields.Selection([('yes', 'Yes'),
#                                                ('no', 'No')], default="yes",
#                                               string="Need to Create")
#     prepare_general_report_state = fields.Selection(
#         related="custom_prepare_general_report_id.state",
#         string="Prepare General Report State",
#         readonly=True
#     )
#     prepare_general_report_count = fields.Integer(
#         string='AFS And APR Report',
#         compute="_compute_prepare_general_report_count")
#
#     custom_form_overall_conclusion_id = fields.Many2one(
#         'custom.audit.request', string="Form Overall Conclusion", readonly=True)
#     form_overall_conclusion = fields.Selection([('yes', 'Yes'), ('no', 'No')],
#                                                default="yes",
#                                                string="Need to Create")
#     form_overall_conclusion_state = fields.Selection(
#         related="custom_form_overall_conclusion_id.state",
#         string="Form Overall Conclusion State",
#         readonly=True
#     )
#     form_overall_conclusion_count = fields.Integer(
#         string='Form Overall Conclusion Count',
#         compute="_compute_form_overall_conclusion_count")
#
#     @api.onchange('arp_id', 'aop_id')
#     def _onchange_arp_aop(self):
#         """Adding values to the date to and date from fields"""
#         date_from = ""
#         date_to = ""
#         if self.arp_id:
#             date_from = self.arp_id.date_start
#             date_to = self.arp_id.date
#             if self.aop_id:
#                 date_from = self.aop_id.planned_date_begin
#                 date_to = self.aop_id.date_deadline
#         else:
#             if self.aop_id:
#                 date_from = self.aop_id.planned_date_begin
#                 date_to = self.aop_id.date_deadline
#         self.date_from = date_from
#         self.date_to = date_to
#
#     def action_open_arp(self):
#         """Action open ARP"""
#         return {
#             'name': _('ARP'),
#             'type': 'ir.actions.act_window',
#             'res_model': 'project.project',
#             'view_mode': 'form',
#             'res_id': self.arp_id.id,
#             'context': {
#                 'create': False,
#             }
#         }
#
#     def action_open_aop(self):
#         """Action open ARP"""
#         return {
#             'name': _('AOP'),
#             'type': 'ir.actions.act_window',
#             'res_model': 'project.task',
#             'view_mode': 'form',
#             'res_id': self.aop_id.id,
#             'context': {
#                 'create': False,
#             }
#         }
#
#     @api.constrains('date_to', 'date_from')
#     def _check_date(self):
#         for record in self:
#             if record.date_to and record.date_to < record.date_from:
#                 raise ValidationError(_('Please add a porper period'))
#             # if record.annual_plan_id:
#             #     if record.annual_plan_id.date_to <= record.date_to:
#             #         raise ValidationError(_('The end date must be equal '
#             #                                 'or less that the date in '
#             #                                 'annual plan'))
#             #     if record.annual_plan_id.date_from >= record.date_from:
#             #         raise ValidationError(_('The start date must be equal '
#             #                                 'or grater that the date '
#             #                                 'in annual plan'))
#
#     @api.model
#     def create(self, values):
#         """Updating values to audit request"""
#         if values.get('name', _('New')) == _('New'):
#             values['name'] = self.env['ir.sequence'].next_by_code(
#                 'audit.request') or _('New')
#         return super().create(values)
#
#     def action_risk_assessment_response(self):
#         """Method for generating Risk Assessment And Response"""
#         return {
#             'name': _('Risk Assessment And Response'),
#             'view_mode': 'form',
#             'res_model': 'risk.assessment.response',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_access_use_work(self):
#         """Method for generating Risk Assessment And Response"""
#         return {
#             'name': _('Access Use of Work of Others'),
#             'view_mode': 'form',
#             'res_model': 'access.use.work',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_fraud_risk_assessment(self):
#         """Method for generating Risk Assessment And Response"""
#         return {
#             'name': _('Fraud Risk Assessment'),
#             'view_mode': 'form',
#             'res_model': 'fraud.risk.assessment',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_allegations_non_compliance_laws_regulations(self):
#         """Method for generating Risk Assessment And Response"""
#         return {
#             'name': _(
#                 'Allegations and Non - Compliance with Laws and Regulations'),
#             'view_mode': 'form',
#             'res_model': 'allegations.non.compliance',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def create_governance(self):
#         """Method for generating"""
#         return {
#             'name': _('Audit Methodology'),
#             'view_mode': 'form',
#             'res_model': 'audit.methodology',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_create_guidance(self):
#         """Method for generating guidance and information"""
#         return {
#             'name': _('Guidance And Other Information'),
#             'view_mode': 'form',
#             'res_model': 'guidance.and.information',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_create_financial_statement(self):
#         """Method for generating financial and statement"""
#         return {
#             'name': _('Financial Statements And Performance Report'),
#             'view_mode': 'form',
#             'res_model': 'financial.statement',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_create_internal_quality_control(self):
#         """Method for generating internal quality control"""
#         return {
#             'name': _('Quality Control - Internal Review Framework'),
#             'view_mode': 'form',
#             'res_model': 'internal.quality.control',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_create_quality_control_peer(self):
#         """Method for generating internal quality control"""
#         return {
#             'name': _('Quality Control - Internal Peer Review'),
#             'view_mode': 'form',
#             'res_model': 'quality.control.peer',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_quality_control_outsourced_peer(self):
#         """Method for generating internal quality control"""
#         return {
#             'name': _('Quality Control - Outsourced Peer Review'),
#             'view_mode': 'form',
#             'res_model': 'quality.control.outsourced.peer',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_internal_audit_charter(self):
#         """Method for generating internal quality control"""
#         return {
#             'name': _('Internal Audit Charter'),
#             'view_mode': 'form',
#             'res_model': 'internal.audit.charter',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_audit_committee_charter(self):
#         """Method for generating internal quality control"""
#         return {
#             'name': _('Audit Committee Charter'),
#             'view_mode': 'form',
#             'res_model': 'audit.committee.charter',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_internal_audit_plan(self):
#         """Method for generating internal quality control"""
#         return {
#             'name': _('Internal Audit Plan'),
#             'view_mode': 'form',
#             'res_model': 'internal.audit.plan',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def _compute_understanding_business_count(self):
#         for record in self:
#             record.understanding_business_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=', 'understanding_business')])
#
#     def action_view_understanding_business_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'understanding_business')],
#         }
#
#     def action_understanding_business(self):
#         """Method for generating understanding of business"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'understanding_business',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Understanding Of Business',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_compliance_materiality_count(self):
#         for record in self:
#             record.compliance_materiality_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'compliance_scoping_material')])
#
#     def action_view_compliance_materiality_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'compliance_scoping_material')],
#         }
#
#     def action_compliance_materiality(self):
#         """Method for generating Compliance Scoping and Materiality"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'compliance_scoping_material',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Compliance Scoping and Materiality',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_communication_correspondence_auditee_count(self):
#         for record in self:
#             record.communication_correspondence_auditee_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'communicate_auditee_manage')])
#
#     def action_view_communication_correspondence_auditee_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'communicate_auditee_manage')],
#         }
#
#     def action_communication_correspondence(self):
#         """Method for generating Communication And Correspondence - Communicate With Auditee Management"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'communicate_auditee_manage',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Communication And Correspondence - Communicate With Auditee Management',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_communication_correspondence_team_count(self):
#         for record in self:
#             record.communication_correspondence_team_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'communicate_audite_team')])
#
#     def action_view_communication_correspondence_team_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'communicate_audite_team')],
#         }
#
#     def action_communication_correspondence_audit_team(self):
#         """Method for generating Communication And Correspondence - Communicate With Auditee Management"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'communicate_audite_team',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Communication And Correspondence - Communicate Within Audit Team',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_communication_correspondence_info_count(self):
#         for record in self:
#             record.communication_correspondence_info_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'request_for_information')])
#
#     def action_view_communication_correspondence_info_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'request_for_information')],
#         }
#
#     def action_communication_correspondence_information(self):
#         """Method for generating Communication And Correspondence - Communicate With Auditee Management"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'request_for_information',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Communication And Correspondence - Request For Information',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_communication_correspondence_find_count(self):
#         for record in self:
#             record.communication_correspondence_find_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'communicate_audite_finding')])
#
#     def action_view_communication_correspondence_find_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'communicate_audite_finding')],
#         }
#
#     def action_communication_correspondence_funding(self):
#         """Method for generating Communication And Correspondence - Communicate With Auditee Management"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'communicate_audite_finding',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Communication And Correspondence - Communicate Audit Finding',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_audit_oversight_count(self):
#         for record in self:
#             record.audit_oversight_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'audit_oversighting')])
#
#     def action_view_audit_oversight_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'audit_oversighting')],
#         }
#
#     def action_audit_oversight(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'audit_oversighting',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Audit Oversight',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_management_representation_count(self):
#         for record in self:
#             record.management_representation_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'obtain_management_rep')])
#
#     def action_view_management_representation_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'obtain_management_rep')],
#         }
#
#     def action_management_representation(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'obtain_management_rep',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Obtain Management Representation',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_analytical_procedure_count(self):
#         for record in self:
#             record.analytical_procedure_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'perform_analytical_procedure')])
#
#     def action_view_analytical_procedure_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'perform_analytical_procedure')],
#         }
#
#     def action_perform_analytical_procedure(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'perform_analytical_procedure',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Perform Analytical Procedures',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_material_misstatements_count(self):
#         for record in self:
#             record.material_misstatements_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'material_misstatements')])
#
#     def action_view_material_misstatements_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'material_misstatements')],
#         }
#
#     def action_material_misstatements(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'material_misstatements',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Assess And Plan Response To Risks Of Material Misstatement',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_risk_assessment_count(self):
#         for record in self:
#             record.risk_assessment_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'risk_assessment_responses')])
#
#     def action_view_risk_assessment_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'risk_assessment_responses')],
#         }
#
#     def action_risk_assessment_responses(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'risk_assessment_responses',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Risk Assessment And Response',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_fraud_risk_assessment_count(self):
#         for record in self:
#             record.fraud_risk_assessment_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'fraud_risk_assessment')])
#
#     def action_view_fraud_risk_assessment_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'fraud_risk_assessment')],
#         }
#
#     def action_fraud_risks_assessment(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'fraud_risk_assessment',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Fraud Risk Assessment',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_allegation_compliance_count(self):
#         for record in self:
#             record.allegation_compliance_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'allegation_compliance')])
#
#     def action_view_allegation_compliance_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'allegation_compliance')],
#         }
#
#     def action_allegation_compliance(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'allegation_compliance',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Allegations and Non - Compliance with Laws and Regulations',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_entity_internal_control_count(self):
#         for record in self:
#             record.entity_internal_control_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'entity_internal_control')])
#
#     def action_view_entity_internal_control_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'entity_internal_control')],
#         }
#
#     def action_entity_internal_control(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'entity_internal_control',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + "Understand The Entity's Internal Controls",
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_business_process_relevant_control_count(self):
#         for record in self:
#             record.business_process_relevant_control_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'business_process_relevant_control')])
#
#     def action_view_business_process_relevant_control_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'business_process_relevant_control')],
#         }
#
#     def action_business_process_relevant_control(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'business_process_relevant_control',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + "Understand The Business Processes And Relevant Controls",
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_internal_control_adequacy_assessment_count(self):
#         for record in self:
#             record.internal_control_adequacy_assessment_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_planning_sections', '=',
#                   'internal_control_adequacy_assessment')])
#
#     def action_view_internal_control_adequacy_assessment_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_planning_sections', '=',
#                         'internal_control_adequacy_assessment')],
#         }
#
#     def action_internal_control_adequacy_assessment(self):
#         """Method for generating Audit Oversight"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_planning_sections': 'internal_control_adequacy_assessment',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + "Internal Controls Adequacy Assessment",
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def action_entity_environment(self):
#         """Method for generating Understand The Entity And It's Environment"""
#         return {
#             'name': _("Understand The Entity And It's Environment"),
#             'view_mode': 'form',
#             'res_model': 'entity.environment',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_terms_engagement(self):
#         """Method for generating Understand The Entity And It's Environment"""
#         return {
#             'name': _("Communicate Terms Of Engagement"),
#             'view_mode': 'form',
#             'res_model': 'terms.engagement',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_audit_strategy(self):
#         """Method for generating Understand The Entity And It's Environment"""
#         return {
#             'name': _("Audit Strategy"),
#             'view_mode': 'form',
#             'res_model': 'audit.strategy',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_audit_project(self):
#         """Method for generating Audit Project"""
#         return {
#             'name': _("Audit Project"),
#             'view_mode': 'form',
#             'res_model': 'audit.project',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_revise_materiality(self):
#         """Method for generating Revise Materiality"""
#         return {
#             'name': _("Revise Materiality"),
#             'view_mode': 'form',
#             'res_model': 'revise.materiality',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_audit_location(self):
#         """Method for generating Audit Of Multiple Locations"""
#         return {
#             'name': _("Audit Of Multiple Locations"),
#             'view_mode': 'form',
#             'res_model': 'audit.location',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_internal_control(self):
#         """Method for generating Audit Of Multiple Locations"""
#         return {
#             'name': _("Understand The Entity's Internal Controls"),
#             'view_mode': 'form',
#             'res_model': 'internal.control',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_relevant_control(self):
#         """Method for generating Understand The Business Processes And Relevant Controls"""
#         return {
#             'name': _(
#                 "Understand The Business Processes And Relevant Controls"),
#             'view_mode': 'form',
#             'res_model': 'relevant.control',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_perform_procedures(self):
#         """Method for generating Perform Analytical Procedures"""
#         return {
#             'name': _(
#                 "Perform Analytical Procedures"),
#             'view_mode': 'form',
#             'res_model': 'perform.analytical.procedures',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def action_material_misstatement(self):
#         """Assess And Plan Response To Risks Of Material Misstatement"""
#         return {
#             'name': _(
#                 "Assess And Plan Response To Risks Of Material Misstatement"),
#             'view_mode': 'form',
#             'res_model': 'material.misstatement',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': {
#                 'default_audit_id': self.id,
#             }
#         }
#
#     def _compute_audit_class_of_transaction_count(self):
#         for record in self:
#             record.audit_class_of_transaction_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_sections', '=',
#                   'class_of_transaction')])
#
#     def action_view_audit_class_of_transactions_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_sections', '=',
#                         'class_of_transaction')],
#         }
#
#     def create_audit_class_of_transactions(self):
#         """Method for generating"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_sections': 'class_of_transaction',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Audit Class Of Transactions',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def create_audit_disclosures(self):
#         """Method for generating"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_sections': 'audit_disclosures',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Audit Disclosures',
#                 'default_audit_request_id': self.id,
#             },
#         }
#     def _compute_audit_disclosure_count(self):
#         for record in self:
#             record.audit_disclosure_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_sections', '=',
#                   'audit_disclosures')])
#
#     def action_view_audit_disclosure_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_sections', '=',
#                         'audit_disclosures')],
#         }
#
#     def create_predetermined_objectives(self):
#         """Method for generating"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_sections': 'predetermined_objectives',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Predetermined Objectives',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_predetermined_objective_count(self):
#         for record in self:
#             record.predetermined_objective_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_sections', '=',
#                   'predetermined_objectives')])
#
#     def action_view_predetermined_objective_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_sections', '=',
#                         'predetermined_objectives')],
#         }
#
#     def create_complaince(self):
#         """Method for generating"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_sections': 'complaince',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Complaince',
#                 'default_audit_request_id': self.id,
#             },
#         }
#     def _compute_complaince_count(self):
#         for record in self:
#             record.complaince_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_sections', '=',
#                   'complaince')])
#
#     def action_view_complaince_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_sections', '=',
#                         'complaince')],
#         }
#
#
#     def create_material_irregularities(self):
#         """Method for generating"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_sections': 'material_irregularities',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Material Irregularities',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_audit_material_irregularities(self):
#         for record in self:
#             record.audit_material_irregularities_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_sections', '=',
#                   'material_irregularities')])
#
#     def action_view_material_irregularities_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_sections', '=',
#                         'material_irregularities')],
#         }
#
#     def create_audit_evidence(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_sections': 'audit_evidence',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Audit Evidence',
#                 'default_audit_request_id': self.id,
#             },
#         }
#     def _compute_audit_evidence(self):
#         for record in self:
#             record.audit_evidence_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_sections', '=',
#                   'audit_evidence')])
#
#     def action_view_audit_evidence_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_sections', '=',
#                         'audit_evidence')],
#         }
#
#     def create_uncorrected_misstatements_and_conclude(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_sections': 'uncorrected_misstatements',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Uncorrected Misstatements And Conclude',
#                 'default_audit_request_id': self.id,
#             },
#         }
#     def _compute_uncorrected_misstatements_and_conclude(self):
#         for record in self:
#             record.uncorrected_misstatements_and_conclude_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_sections', '=',
#                   'uncorrected_misstatements')])
#
#     def action_view_uncorrected_misstatements_and_conclude_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_sections', '=',
#                         'uncorrected_misstatements')],
#         }
#
#
#     def create_deficiencies_in_internal_control(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_sections': 'deficiency_internal_control',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Deficiencies In Internal Control',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_deficiencies_in_internal_control(self):
#         for record in self:
#             record.deficiencies_in_internal_control_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_sections', '=',
#                   'deficiency_internal_control')])
#
#     def action_view_deficiencies_in_internal_control_count(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_sections', '=',
#                         'deficiency_internal_control')],
#         }
#
#     def _compute_key_audit_matters_count(self):
#         for record in self:
#             record.key_audit_matters_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_report_sections', '=', 'key_audit_matter')])
#
#     def action_view_key_audit_matters(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_report_sections', '=', 'key_audit_matter')],
#         }
#
#     def create_key_audit_matters(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_report_sections': 'key_audit_matter',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Key Audit Matters',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_prepare_management_reports_count(self):
#         for record in self:
#             record.prepare_management_reports_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_report_sections', '=', 'prepare_management_report')])
#
#     def action_view_prepare_management_reports(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_report_sections', '=',
#                         'prepare_management_report')],
#         }
#
#     def create_prepare_management_reports(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_report_sections': 'prepare_management_report',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + 'Prepare Management Report',
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_prepare_auditor_report_count(self):
#         for record in self:
#             record.prepare_auditor_report_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_report_sections', '=', 'prepare_auditor_report')])
#
#     def action_prepare_auditor_report(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_report_sections', '=',
#                         'prepare_management_report')],
#         }
#
#     def create_prepare_auditor_report(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_report_sections': 'prepare_auditor_report',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + "Prepare Auditor's Report",
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_prepare_dashboard_report_count(self):
#         for record in self:
#             record.prepare_dashboard_report_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_report_sections', '=', 'prepare_dashboard_report')])
#
#     def action_prepare_dashboard_report(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_report_sections', '=',
#                         'prepare_dashboard_report')],
#         }
#
#     def create_prepare_dashboard_report(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_report_sections': 'prepare_dashboard_report',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + "Prepare Dashboard Report",
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_prepare_sector_report_count(self):
#         for record in self:
#             record.prepare_sector_report_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_report_sections', '=', 'prepare_sector_report')])
#
#     def _compute_final_report_count(self):
#         for record in self:
#             record.prepare_final_report_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_report_sections', '=', 'prepare_final_report')])
#
#     def action_prepare_sector_report(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_report_sections', '=', 'prepare_sector_report')],
#         }
#
#     def action_prepare_final_report(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_report_sections', '=', 'prepare_final_report')],
#         }
#
#     def create_prepare_sector_report(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_report_sections': 'prepare_sector_report',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + "Prepare Sector Report",
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def create_prepare_final_report(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_report_sections': 'prepare_final_report',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + "Prepare Final Report",
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_prepare_general_report_count(self):
#         for record in self:
#             record.prepare_general_report_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_report_sections', '=', 'prepare_general_report')])
#
#     def action_prepare_general_report(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        (
#                            'audit_report_sections', '=',
#                            'prepare_general_report')],
#         }
#
#     def create_prepare_general_report(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_report_sections': 'prepare_general_report',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + "Prepare General Report",
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def _compute_form_overall_conclusion_count(self):
#         for record in self:
#             record.form_overall_conclusion_count = self.env[
#                 'custom.audit.request'].search_count(
#                 [('audit_request_id', '=', record.id),
#                  ('audit_report_sections', '=', 'form_overall_conclusion')])
#
#     def action_form_overall_conclusion(self):
#         return {
#             'name': 'Custom Audit Requests',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'tree,form',
#             'res_model': 'custom.audit.request',
#             'domain': [('audit_request_id', '=', self.id),
#                        ('audit_report_sections', '=',
#                         'form_overall_conclusion')],
#         }
#
#     def create_form_overall_conclusion(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Audit Request',
#             'res_model': 'custom.audit.request',
#             'view_mode': 'form',
#             'view_id': False,
#             # Optional: You can specify a specific view ID if needed
#             'target': 'new',  # This opens the form in a new modal window
#             'context': {
#                 'default_audit_report_sections': 'form_overall_conclusion',
#                 'default_arp_id': self.arp_id.id,  # Automatically fill arp_id
#                 'default_aop_id': self.aop_id.id,  # Automatically fill aop_id
#                 'default_name': self.title + '-' + "Form Overall Conclusion",
#                 'default_audit_request_id': self.id,
#             },
#         }
#
#     def action_review(self):
#         """Move to review State"""
#         self.state = 'review'
#
#     def action_approve(self):
#         """Move to approve State"""
#         self.state = 'approve'
#
#     def action_refuse(self):
#         """Move to refuse State"""
#         self.state = 'refuse'
#
# class AnnualPlan(models.Model):
#     """Annual Plan"""
#     _name = 'annual.plan'
#     _description = "Annual Plan"
#
#     name = fields.Char(string="Plan Name", required=True)
#     date_from = fields.Date(string="From Date", required=True)
#     date_to = fields.Date(string="To Date", required=True)
#     active = fields.Boolean(string="Active", default=True)
#
#     @api.constrains('date_to', 'date_from')
#     def _check_date(self):
#         for record in self:
#             if record.date_to and record.date_to < record.date_from:
#                 raise ValidationError(_('Please add a porper period'))
