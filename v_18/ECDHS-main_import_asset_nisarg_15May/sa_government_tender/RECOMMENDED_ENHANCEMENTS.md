SA GOVERNMENT TENDER MANAGEMENT - RECOMMENDED ENHANCEMENTS
═══════════════════════════════════════════════════════════════════════

COMPLIANCE REVIEW DATE: February 5, 2026
DOCUMENT PURPOSE: Detailed action plan for post-deployment enhancements

═══════════════════════════════════════════════════════════════════════

ENHANCEMENT 1: SOLE SOURCE PROCUREMENT GOVERNANCE
═══════════════════════════════════════════════════════════════════════

PRIORITY: HIGH
TIMELINE: Within 30 days of production deployment
REGULATORY REQUIREMENT: PFMA Section 76(4)(c), MFMA Section 111(2)(d)

CURRENT STATE:
  • Method E (Sole Source) lacks explicit deviation approval workflow
  • No documented justification requirement
  • No price reasonableness verification stage
  • Marked as NOT PPPFA compliant ✓ (correct)

REQUIRED ENHANCEMENTS:

1. Add Field: Deviation Justification (Required)
   Model: sagovprocurement.method or evaluation workflow
   Type: Text/HTML field
   Description: "Explanation of why only one supplier can provide the requirement"
   Requirement: Mandatory for all sole source procurements

2. Add Workflow Stage: Deviation Approval
   Sequence: After specification approval
   Responsible Group: Accounting Officer or CFO
   Required Action: Formal approval of deviation from competitive procurement
   Documentation: Approval certificate with motivation

3. Add Workflow Stage: Price Reasonableness Verification
   Sequence: Before award
   Responsible Group: Finance/Accounting function
   Required Action: Verify price is reasonable and not exploitative
   Documentation: Price verification report

4. Add Field: Deviation Approval Document Reference
   Type: Attachment field
   Description: "Upload deviation approval certificate"

5. Add Field: Price Verification Document Reference
   Type: Attachment field
   Description: "Upload price reasonableness verification report"

IMPLEMENTATION STEPS:
  1. Modify sagovprocurement_workflow_stage.py to add above fields
  2. Add workflow stages in sagovprocurement_method_data.xml for Method E
  3. Update view: sagovprocurement_method_views.xml to display fields
  4. Add validation rules to enforce required fields for sole source
  5. Update documentation: SOLE_SOURCE_POLICY.md

TESTING REQUIREMENTS:
  • Verify deviation approval is mandatory
  • Verify price verification is mandatory
  • Verify audit trail captures all decisions
  • Test with sample sole source procurement


═══════════════════════════════════════════════════════════════════════

ENHANCEMENT 2: EMERGENCY PROCUREMENT GOVERNANCE
═══════════════════════════════════════════════════════════════════════

PRIORITY: HIGH
TIMELINE: Within 30 days of production deployment
REGULATORY REQUIREMENT: PFMA Section 76(4)(b), MFMA Section 111(2)

CURRENT STATE:
  • Method F (Emergency) lacks explicit emergency authorization workflow
  • No documented emergency justification requirement
  • Missing post-procurement BAC review stage
  • Marked as NOT PPPFA/Treasury Regulation compliant ✓ (correct)

REQUIRED ENHANCEMENTS:

1. Add Field: Emergency Justification (Required)
   Model: Emergency procurement record
   Type: Text/HTML field
   Description: "Detailed explanation of why this is a genuine emergency"
   Requirement: Mandatory for all emergency procurements
   Examples: Supply chain disruption, infrastructure damage, critical shortage

2. Add Field: Emergency Justification Date
   Type: DateTime field
   Description: "Date and time emergency was declared"
   Requirement: Auto-populated with current datetime

3. Add Workflow Stage: Emergency Authorization
   Sequence: First stage after identification
   Responsible Group: Accounting Officer or Head of Department
   Required Action: Formal authorization of emergency procurement
   Documentation: Emergency authorization letter

4. Add Workflow Stage: Post-Procurement BAC Review
   Sequence: After completion of procurement
   Responsible Group: BAC or governance committee
   Required Action: Review emergency procurement for appropriateness
   Documentation: BAC review report

5. Add Field: Emergency Authorization Document Reference
   Type: Attachment field
   Description: "Upload emergency authorization"

6. Add Field: BAC Post-Review Document Reference
   Type: Attachment field
   Description: "Upload post-procurement BAC review report"

7. Add Field: Emergency Category
   Type: Selection field
   Options: Supply Chain Disruption, Infrastructure Emergency, Service Failure, Security, Other
   Description: "Category of emergency"

IMPLEMENTATION STEPS:
  1. Modify emergency procurement workflow stages in data file
  2. Add required fields to model
  3. Update view to display emergency fields prominently
  4. Add validation to ensure emergency justification is provided
  5. Create emergency authorization template document
  6. Update documentation: EMERGENCY_PROCUREMENT_PROCEDURE.md

TESTING REQUIREMENTS:
  • Verify emergency justification is mandatory
  • Verify emergency authorization is captured
  • Verify post-procurement BAC review is mandatory
  • Verify all emergency procurements are flagged for audit
  • Test with sample emergency procurement


═══════════════════════════════════════════════════════════════════════

ENHANCEMENT 3: ETHICS & FRAUD PREVENTION CONTROLS
═══════════════════════════════════════════════════════════════════════

PRIORITY: MEDIUM
TIMELINE: Within 60 days of production deployment
REGULATORY REQUIREMENT: PFMA SCM Instruction Notes, King IV Governance

CURRENT STATE:
  • Requires Declaration of Interest for competitive bids ✓
  • No explicit fields for bid-rigging prevention
  • No BEE fronting prevention controls
  • No supplier blacklist/debarment checking

REQUIRED ENHANCEMENTS:

1. Add Field: Conflict of Interest Declaration (Enhanced)
   Current: Boolean flag for requirement
   Enhancement: Make it structured with:
     - Supplier name
     - Related party names
     - Nature of relationship
     - Mitigation measures
     - Signatory name and date
   Model: sagovdeclaration.interest (existing)
   Status: ✓ May already be implemented

2. Add Field: Bid-Rigging Prevention Declaration
   Type: Boolean with required signed document
   Description: "Supplier confirms not involved in bid-rigging or collusion"
   Requirement: Mandatory for all competitive bids

3. Add Field: BEE Fronting Prevention Declaration
   Type: Boolean with required certification
   Description: "Supplier confirms not engaged in BEE fronting practices"
   Requirement: Mandatory for all procurements with B-BBEE preference

4. Add Field: Supplier Debarment Status
   Type: Boolean field
   Description: "Supplier is not on government debarment list"
   Requirement: Mandatory - check against CIDB, BEC lists
   Integration: Link to supplier debarment register (if available)

5. Add Field: Previous Performance Issues
   Type: Text area
   Description: "Any known performance or conduct issues with this supplier"
   Requirement: For reference in BAC/BEC evaluation

6. Add Workflow Stage: Ethics & Compliance Verification
   Sequence: During compliance check
   Responsible Group: Compliance officer
   Required Action: Verify declarations and debarment status
   Documentation: Compliance verification report

IMPLEMENTATION STEPS:
  1. Create/enhance sagovcompliance.check model with ethics fields
  2. Add workflow stage for ethics verification
  3. Create ethics verification template/checklist
  4. Integrate with supplier debarment registry (if available)
  5. Add validation to ensure all ethics declarations are signed
  6. Update views to display ethics information clearly

TESTING REQUIREMENTS:
  • Verify conflict of interest declarations are captured
  • Verify bid-rigging prevention is required
  • Verify BEE fronting prevention is checked
  • Verify debarment status blocks procurement (if debarred)
  • Test ethics verification workflow


═══════════════════════════════════════════════════════════════════════

ENHANCEMENT 4: AUDIT TRAIL & ACCOUNTABILITY
═════════════════════════════════════════════

PRIORITY: MEDIUM
TIMELINE: Within 60 days of production deployment
REGULATORY REQUIREMENT: PFMA Section 63, King IV Principle 4

CURRENT STATE:
  • Workflow stages defined ✓
  • Decision points mostly tracked ✓
  • Audit trail inheritance from mail.thread ✓
  • May lack comprehensive exception logging

REQUIRED ENHANCEMENTS:

1. Add Field: Exception/Deviation Flag
   Type: Boolean
   Description: "Procurement involved deviation from normal process"
   Requirement: Auto-set when deviation/emergency/sole source used

2. Add Field: Exception Reason
   Type: Text
   Description: "Reason for any exceptions or deviations"
   Requirement: Required when exception flag is set

3. Add Field: Approval Timeline Tracking
   Type: Datetime fields for each key stage
   Examples: BSC approval date, BEC completion date, BAC decision date
   Requirement: Auto-populated at each stage

4. Add Field: Decision Maker Verification
   Type: Many2one (res.users)
   Description: "User who made the decision/approval"
   Requirement: Auto-populated at each approval point

5. Add Field: Decision Justification (where not obvious)
   Type: Text
   Description: "Rationale for decision (especially if non-lowest price)"
   Requirement: Required for all BAC awards to non-lowest-price supplier

6. Add Audit Report Generation
   Feature: Ability to generate full audit trail for any procurement
   Include: All decisions, all approvals, all changes, all exceptions
   Export: PDF/Excel format

IMPLEMENTATION STEPS:
  1. Add fields to sagovprocurement.method and related models
  2. Enhance mail.thread tracking with custom audit fields
  3. Create audit report wizard
  4. Update views to display audit information
  5. Add automated audit trail queries

TESTING REQUIREMENTS:
  • Verify all decisions are time-stamped
  • Verify all approvers are recorded
  • Verify exceptions are flagged
  • Verify audit reports can be generated
  • Verify audit trail is immutable (read-only after record)


═══════════════════════════════════════════════════════════════════════

ENHANCEMENT 5: SUPPLY CHAIN RISK MANAGEMENT
═════════════════════════════════════════════

PRIORITY: LOW (Strategic value, not required for compliance)
TIMELINE: Within 120 days of production deployment
REGULATORY REQUIREMENT: Best practice (not legislated)

RECOMMENDED ENHANCEMENTS:

1. Add Field: Supply Chain Risk Assessment
   Type: Selection
   Options: Low, Medium, High, Critical
   Description: "Risk level for this procured item/service"
   Requirement: Optional but recommended for strategic procurements

2. Add Field: Business Continuity Impact
   Type: Boolean
   Description: "Is this critical for business continuity?"
   Requirement: Optional

3. Add Field: Supplier Risk Level
   Type: Selection
   Options: Low, Medium, High
   Description: "Historical performance/stability risk of supplier"
   Requirement: Optional - can be auto-calculated from history

4. Add Field: Geopolitical Risk
   Type: Boolean
   Description: "Are there geopolitical risks in supply chain?"
   Requirement: Optional - for high-value/strategic items

5. Add Mitigation Measures Field
   Type: Text
   Description: "Planned mitigation for identified risks"
   Requirement: Optional but recommended for high-risk items

IMPLEMENTATION STEPS:
  1. Add fields to sagovprocurement.method
  2. Create risk assessment template
  3. Add risk visualization to procurement dashboard
  4. Document risk assessment methodology
  5. Create optional risk reporting

BENEFITS:
  • Better strategic procurement planning
  • Early identification of supply chain risks
  • Documented risk mitigation strategies
  • Support for business continuity planning


═══════════════════════════════════════════════════════════════════════

ENHANCEMENT 6: SUSTAINABILITY & GREEN PROCUREMENT
══════════════════════════════════════════════════

PRIORITY: LOW (Strategic value, not required for compliance)
TIMELINE: Within 120 days of production deployment
REGULATORY REQUIREMENT: Best practice (aligns with National Development Plan)

RECOMMENDED ENHANCEMENTS:

1. Add Field: Sustainability Requirement
   Type: Boolean
   Description: "This procurement includes sustainability criteria"
   Requirement: Optional

2. Add Field: Environmental Compliance Required
   Type: Boolean
   Description: "Supplier must have environmental compliance certification"
   Requirement: Optional

3. Add Evaluation Criteria: Environmental Compliance
   Type: Percentage weight in evaluation
   Description: "Weight given to environmental compliance in evaluation"
   Requirement: Optional - can be 0-15%

4. Add Evaluation Criteria: Green Procurement
   Type: Percentage weight in evaluation
   Description: "Weight given to green/sustainable solutions"
   Requirement: Optional - can be 0-10%

5. Add Field: Sustainability Certifications Accepted
   Type: Multi-select
   Options: ISO 14001, Green Star, LEED, Energy Star, Carbon Neutral, Other
   Description: "Environmental certifications that qualify"
   Requirement: Optional

6. Add Supplier Green Rating
   Type: Selection
   Options: Not Rated, Bronze, Silver, Gold, Platinum
   Description: "Environmental maturity rating of supplier"
   Requirement: Optional - for supplier management

IMPLEMENTATION STEPS:
  1. Add sustainability fields to evaluation criteria
  2. Create green procurement guidelines
  3. Add sustainability reporting
  4. Document environmental compliance requirements

BENEFITS:
  • Supports government environmental objectives
  • Promotes supplier environmental responsibility
  • Enables tracking of green procurement achievements
  • Supports corporate social responsibility


═══════════════════════════════════════════════════════════════════════

ENHANCEMENT 7: OPTIONAL PREFERENCE POINTS (Future Enhancement)
════════════════════════════════════════════════════════════════

PRIORITY: VERY LOW (Framework already supports this)
TIMELINE: On demand - when policy requires
REGULATORY REQUIREMENT: Optional per entity policy

CURRENT STATE:
  • Framework supports women empowerment points ✓ (currently 0)
  • Framework supports youth development points ✓ (currently 0)
  • Framework supports local content points ✓ (currently 0)
  • Framework supports SME development points ✓ (currently 0)
  • Framework supports PWD participation points ✓ (currently 0)

ACTIVATION OPTION:
  If entity policy requires additional preferences, system can:
  1. Allocate points to women empowerment category
  2. Allocate points to youth development category
  3. Allocate points to local content category
  4. Allocate points to SME participation category
  5. Allocate points to PWD (Persons with Disabilities) category

  This would be done by:
  - Modifying preference_point_system records
  - Adding points to each category (reducing B-BBEE points accordingly)
  - Updating evaluation criteria to include new categories
  - Rebalancing 80/20 and 90/10 systems

CURRENT ALLOCATION (80/20 System):
  B-BBEE: 20 points (100%)
  Women: 0 points
  Youth: 0 points
  Local Content: 0 points
  SME: 0 points
  PWD: 0 points
  TOTAL: 20 points ✓

EXAMPLE ALTERNATIVE ALLOCATION (if policy changes):
  B-BBEE: 8 points (40%)
  Women: 3 points (15%)
  Youth: 3 points (15%)
  Local Content: 3 points (15%)
  SME: 2 points (10%)
  PWD: 1 point (5%)
  TOTAL: 20 points ✓

NOTE: This requires policy decision - current framework is correct per PPPFA


═══════════════════════════════════════════════════════════════════════

IMPLEMENTATION ROADMAP
═════════════════════════════════════════════════════════════════════════

PHASE 1 - BEFORE PRODUCTION (Current - Do Not Deploy Without):
  Status: COMPLETE ✓
  • Fix field name errors
  • Fix invalid field values
  • Verify all models and data
  ✓ Ready for production

PHASE 2 - IMMEDIATE POST-DEPLOYMENT (Days 1-30):
  Priority: HIGH - MUST IMPLEMENT
  1. Sole Source governance (deviation, justification, price verification)
  2. Emergency governance (authorization, BAC review)
  3. Deploy, test, document

PHASE 3 - SHORT TERM (Days 31-90):
  Priority: MEDIUM - SHOULD IMPLEMENT
  1. Ethics & fraud prevention controls
  2. Audit trail enhancements
  3. Test, document, train users

PHASE 4 - MEDIUM TERM (Days 91-180):
  Priority: LOW - NICE TO HAVE
  1. Supply chain risk management
  2. Sustainability & green procurement
  3. Advanced reporting

PHASE 5 - LONG TERM (6+ months):
  Priority: STRATEGIC
  1. Treasury e-Procurement integration
  2. Advanced analytics
  3. Supplier performance management
  4. Contract lifecycle management


═══════════════════════════════════════════════════════════════════════

RESOURCE REQUIREMENTS
═════════════════════════════════════════════════════════════════════════

ENHANCEMENT 1 (Sole Source): 16-24 hours
  • Model modifications: 4 hours
  • Data/workflow updates: 6 hours
  • View updates: 4 hours
  • Testing: 6 hours
  • Documentation: 2 hours

ENHANCEMENT 2 (Emergency): 16-24 hours
  • Model modifications: 4 hours
  • Data/workflow updates: 6 hours
  • View updates: 4 hours
  • Testing: 6 hours
  • Documentation: 2 hours

ENHANCEMENT 3 (Ethics): 24-32 hours
  • Model modifications: 6 hours
  • Workflow/integration: 8 hours
  • View updates: 6 hours
  • Testing: 8 hours
  • Documentation: 4 hours

ENHANCEMENT 4 (Audit): 20-28 hours
  • Model modifications: 6 hours
  • Audit tracking: 8 hours
  • Report generation: 8 hours
  • Testing: 6 hours

ENHANCEMENT 5 (Risk): 16-20 hours (OPTIONAL)

ENHANCEMENT 6 (Sustainability): 12-16 hours (OPTIONAL)

TOTAL (Phase 2 + 3): 76-112 hours
TOTAL (Phases 2-4): 120-172 hours


═══════════════════════════════════════════════════════════════════════

COMPLIANCE AFTER ENHANCEMENTS
═════════════════════════════════════════════════════════════════════════

After Phase 2 (30 days):
  Expected Compliance Level: 95%
  Remaining Gap: Ethics/Fraud prevention (addressed in Phase 3)

After Phase 3 (90 days):
  Expected Compliance Level: 98%
  Remaining Gap: Supply chain risk, sustainability (optional enhancements)

After Phase 4 (180 days):
  Expected Compliance Level: 100% (for scope addressed)
  All core requirements + strategic enhancements implemented


═══════════════════════════════════════════════════════════════════════

SIGN-OFF & APPROVAL
═════════════════════════════════════════════════════════════════════════

This enhancement plan is recommended by the Compliance Audit team.
Approval required from:
  1. System Owner
  2. Chief Procurement Officer / SCM Head
  3. Chief Financial Officer (for deviation/emergency requirements)
  4. Governance/Compliance Officer

Implementation to be scheduled and tracked through project management system.

═══════════════════════════════════════════════════════════════════════
