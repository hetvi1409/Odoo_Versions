# CONFIGURATION INTEGRATION ANALYSIS
## How Procurement Methods & Preference Point Systems Flow Through the System

**Date:** February 5, 2026
**Status:** Comprehensive Analysis
**Purpose:** Map configuration usage from APP → Award

---

## EXECUTIVE SUMMARY

### Current State Analysis
✅ **Configurations ARE defined** - All 7 Procurement Methods and 2 Preference Systems are fully configured
❌ **Configurations NOT FULLY INTEGRATED** - The flow from configuration → actual document generation and workflow enforcement is **INCOMPLETE**

### The Core Problem
The system has **excellent configuration data** but **lacks automation** to enforce these configurations throughout the tender lifecycle. Documents, workflow stages, and evaluation criteria are **referenced but not automatically applied**.

---

## DETAILED FLOW ANALYSIS

### 1️⃣ ANNUAL PROCUREMENT PLAN (APP)
**Location:** `models/sagovannual_procurement_plan.py`

#### ✅ What Works:
```python
procurement_method_config_id = fields.Many2one(
    'sagovprocurement.method',
    string='Procurement Method Configuration'
)
preference_point_system_config_id = fields.Many2one(
    'sagovpreference.point.system',
    string='Preference Point System Configuration'
)
```

- **Configuration linked**: APP stores the procurement method based on estimated value
- **Auto-selection**: System suggests method based on value thresholds
- **Configuration flows forward**: Requisition and Tender inherit this config

#### ❌ What's Missing:
- No automatic workflow stage initialization
- No validation that APP aligns with method value ranges
- No document checklist generation at APP level

---

### 2️⃣ PURCHASE REQUISITION
**Location:** `models/sagovpurchase_requisition.py`

#### ✅ What Works:
```python
procurement_method_config_id = fields.Many2one(
    'sagovprocurement.method',
    string='Procurement Method Configuration',
    related='app_id.procurement_method_config_id',
    store=True,
    readonly=True
)
preference_point_system_config_id = fields.Many2one(
    'sagovpreference.point.system',
    related='app_id.preference_point_system_config_id',
    store=True,
    readonly=True
)
```

- **Configuration inherited**: Automatically gets method from APP
- **Read-only enforcement**: Cannot change method at requisition level (good control)

#### ❌ What's Missing:
- No validation that requisition documents match method requirements
- No workflow stage tracking at requisition level
- No enforcement of quotation requirements (e.g., 3 quotations for Method A)

---

### 3️⃣ BUDGET CONFIRMATION
**Location:** `models/sagovbudget_confirmation.py`

#### ✅ What Works:
```python
procurement_method_config_id = fields.Many2one(
    'sagovprocurement.method',
    related='requisition_id.procurement_method_config_id',
    string='Procurement Method Configuration'
)
```

- **Configuration flows**: Procurement method visible at budget stage
- **Reference maintained**: Tracking continues through workflow

#### ❌ What's Missing:
- No validation that budget amount aligns with method value thresholds
- No automatic document requirement generation for budget approval
- No workflow stage integration (e.g., CFO approval for high-value methods)

---

### 4️⃣ TENDER CREATION & SPECIFICATION
**Location:** `models/sagovtender.py`

#### ✅ What Works:
```python
# Configuration Fields
procurement_method_config_id = fields.Many2one(
    'sagovprocurement.method',
    string='Procurement Method Configuration',
    tracking=True
)
preference_point_system_config_id = fields.Many2one(
    'sagovpreference.point.system',
    string='Preference Point System Configuration',
    tracking=True
)

# Related Fields (Read-Only References)
workflow_stage_ids = fields.One2many(
    related='procurement_method_config_id.workflow_stage_ids',
    string='Workflow Stages',
    readonly=True
)
document_requirement_ids = fields.One2many(
    related='procurement_method_config_id.document_requirement_ids',
    string='Document Requirements',
    readonly=True
)
evaluation_criteria_ids = fields.One2many(
    related='procurement_method_config_id.evaluation_criteria_ids',
    string='Evaluation Criteria',
    readonly=True
)

# Auto-Selection Methods
@api.onchange('requisition_id')
def _onchange_requisition_id(self):
    """Default procurement method from linked requisition/APP"""
    if self.requisition_id and self.requisition_id.app_id:
        method = self.requisition_id.app_id.procurement_method_config_id
        if method:
            self.procurement_method_config_id = method
            if method.preference_point_system_ids:
                self.preference_point_system_config_id = method.preference_point_system_ids[0]

@api.onchange('estimated_value')
def _onchange_estimated_value(self):
    """Suggest procurement method based on estimated value"""
    if self.estimated_value:
        method = self.env['sagovprocurement.method'].get_applicable_method(
            self.estimated_value
        )
        if method:
            self.procurement_method_config_id = method
            if method.preference_point_system_ids:
                self.preference_point_system_config_id = method.preference_point_system_ids[0]

# Helper Methods
def get_workflow_stages(self):
    """Get ordered workflow stages for this tender"""
    if self.procurement_method_config_id:
        return self.procurement_method_config_id.get_workflow_sequence()
    return []

def get_required_documents(self):
    """Get all required documents for this tender"""
    if self.procurement_method_config_id:
        return self.procurement_method_config_id.get_document_requirements()
    return []

def validate_procurement_method_compliance(self):
    """Validate that selected method meets compliance requirements"""
    # Validates value thresholds and preference system applicability
    ...
```

- **Configuration auto-selected**: Based on APP or estimated value
- **Preference system auto-linked**: 80/20 or 90/10 based on method
- **Related fields exposed**: Can VIEW workflow stages, documents, criteria
- **Validation methods exist**: Can check compliance

#### ❌ What's Missing (CRITICAL GAPS):

**A. Document Requirements Not Auto-Generated**
```python
# CURRENT: Only displays as read-only list
document_requirement_ids = fields.One2many(
    related='procurement_method_config_id.document_requirement_ids',
    readonly=True
)

# MISSING: Automatic document record creation
# When tender is created, should automatically create:
# - sagovtender.document records for each requirement
# - Mandatory flag enforcement
# - Document checklist for SCM officer
```

**B. Workflow Stages Not Enforced**
```python
# CURRENT: Manual state transitions
state = fields.Selection([
    ('draft', 'Draft'),
    ('specification', 'Specification'),
    ('scm_processing', 'SCM Processing'),
    ('advertised', 'Advertised'),
    # ... etc
])

# MISSING: Dynamic state enforcement based on workflow_stage_ids
# Should validate transitions match configured workflow stages
# Should enforce responsible_group permissions
# Should track completion of each workflow stage
```

**C. Evaluation Criteria Not Pre-Loaded**
```python
# CURRENT: Manual entry in bid evaluation
def _load_functionality_criteria(self):
    """Load functionality evaluation criteria"""
    # HARDCODED criteria
    criteria_data = [
        {'name': 'Technical Capability', 'weight': 30},
        {'name': 'Experience and Track Record', 'weight': 25},
        # ...
    ]

# MISSING: Should load from procurement_method_config_id.evaluation_criteria_ids
# Should use configured criteria names, weights, types
# Should respect criteria_type (price, functionality, bbbee, etc.)
```

---

### 5️⃣ TENDER PUBLICATION & DOCUMENTS
**Location:** `models/sagovtender_document.py`

#### ✅ What Works:
```python
document_type = fields.Selection([
    ('sagovtender_document', 'Tender Document'),
    ('specification', 'Specification'),
    ('terms_conditions', 'Terms & Conditions'),
    ('sbd_form', 'SBD Form'),
    # ...
])
```

- **Document model exists**: Can store tender documents
- **Document types defined**: Categorization available

#### ❌ What's Missing (MAJOR GAP):
```python
# MISSING: No automatic document creation from procurement method config
# When tender is published, should:
# 1. Read procurement_method_config_id.document_requirement_ids
# 2. Create sagovtender.document record for each requirement
# 3. Mark mandatory documents
# 4. Create checklist for SCM officer to upload

# EXAMPLE - What should happen:
def action_publish_tender(self):
    """Publish tender"""
    # Current code checks documents exist
    if not self.sagovtender_document_ids:
        raise UserError('Please attach tender documents before publishing.')

    # SHOULD ADD: Validate against required documents
    required_docs = self.procurement_method_config_id.document_requirement_ids
    for req_doc in required_docs.filtered(lambda d: d.mandatory):
        # Check if corresponding document exists
        doc_exists = self.sagovtender_document_ids.filtered(
            lambda d: d.name == req_doc.name or
                     d.document_type == req_doc.document_type
        )
        if not doc_exists:
            raise UserError(
                f'Missing mandatory document: {req_doc.name}\n'
                f'Required by {self.procurement_method_config_id.name}'
            )
```

---

### 6️⃣ BID EVALUATION
**Location:** `models/sagovbid_evaluation.py`

#### ✅ What Works:
```python
# Price scoring uses preference system
@api.depends('bid_amount', 'tender_id.bid_ids')
def _compute_price_score(self):
    """Calculate price score"""
    # Determine max price points
    if record.tender_id.preference_system == '80_20':
        max_points = 80
    elif record.tender_id.preference_system == '90_10':
        max_points = 90
    # ...

# B-BBEE scoring uses preference system
@api.depends('bbbee_level', 'tender_id.preference_system')
def _compute_bbbee_score(self):
    """Calculate B-BBEE preference points"""
    if record.tender_id.preference_system == '80_20':
        points_map = {1: 20, 2: 18, 3: 14, ...}
    elif record.tender_id.preference_system == '90_10':
        points_map = {1: 10, 2: 9, 3: 6, ...}
```

- **Preference system applied**: Price and B-BBEE scoring uses 80/20 or 90/10
- **Automatic calculations**: Scores computed based on configuration

#### ❌ What's Missing (CRITICAL):
```python
# CURRENT: Hardcoded functionality criteria
def _load_functionality_criteria(self):
    """Load functionality evaluation criteria"""
    criteria_data = [
        {'name': 'Technical Capability', 'weight': 30, 'max_score': 100},
        {'name': 'Experience and Track Record', 'weight': 25, 'max_score': 100},
        {'name': 'Proposed Methodology', 'weight': 25, 'max_score': 100},
        {'name': 'Key Personnel Qualifications', 'weight': 20, 'max_score': 100},
    ]

# SHOULD BE: Load from procurement method configuration
def _load_functionality_criteria(self):
    """Load functionality evaluation criteria from procurement method config"""
    self.ensure_one()
    self.functionality_line_ids.unlink()

    if not self.tender_id.procurement_method_config_id:
        return

    # Load criteria from configuration
    eval_criteria = self.tender_id.procurement_method_config_id.evaluation_criteria_ids

    for criteria in eval_criteria.filtered(lambda c: c.criteria_type == 'functionality'):
        self.env['sagovtender.eval.funct.line'].create({
            'evaluation_id': self.id,
            'criteria': criteria.name,
            'weight': criteria.weight,
            'max_score': 100,  # or criteria.max_score if added to config
            'description': criteria.description,
        })
```

**Additional Gaps:**
- No loading of price evaluation criteria from config
- No loading of compliance criteria from config
- No validation that total weights = 100%
- No enforcement of criteria_type segregation

---

### 7️⃣ BAC REVIEW & AWARD
**Location:** `models/sagovbac_review.py`, `models/sagovtender_award.py`

#### ✅ What Works:
- Configuration reference maintained through tender linkage
- Can view procurement method used

#### ❌ What's Missing:
- No validation that BAC review is required (based on `requires_bac_review` flag)
- No validation that delegated authority threshold is met
- No workflow stage validation before award
- No automatic approval routing based on method configuration

---

## CONFIGURATION DATA COMPLETENESS

### ✅ Fully Configured in Data Files

**Procurement Methods** (`data/sagovprocurement_method_data.xml`):
- ✅ 7 Methods defined (A through G)
- ✅ Value thresholds set (min/max values)
- ✅ Quotation requirements configured
- ✅ Committee requirements defined (BSC, BEC, BAC)
- ✅ Compliance flags set (PFMA, MFMA, PPPFA)
- ✅ **86 Workflow Stages** defined across all methods
- ✅ **65 Document Requirements** defined across all methods
- ✅ **42 Evaluation Criteria** defined across all methods

**Preference Point Systems** (`data/sagovprocurement_method_data.xml`):
- ✅ 80/20 System (R30k - R500k)
- ✅ 90/10 System (> R500k)
- ✅ B-BBEE point allocations defined
- ✅ Linked to applicable procurement methods

---

## THE INTEGRATION GAP

### Configuration Exists, But Enforcement Missing

| Configuration Element | Defined in Data | Referenced in Models | **Auto-Applied in Workflow** |
|----------------------|----------------|---------------------|------------------------------|
| Procurement Method | ✅ Yes | ✅ Yes | ⚠️ **Partial** |
| Preference System | ✅ Yes | ✅ Yes | ✅ **Yes** (in evaluation) |
| **Workflow Stages (86)** | ✅ Yes | ✅ Yes (related field) | ❌ **NO** |
| **Document Requirements (65)** | ✅ Yes | ✅ Yes (related field) | ❌ **NO** |
| **Evaluation Criteria (42)** | ✅ Yes | ✅ Yes (related field) | ❌ **NO** |
| Value Threshold Validation | ✅ Yes | ✅ Yes | ✅ **Yes** |
| Committee Requirement Flags | ✅ Yes | ✅ Yes | ❌ **NO** |
| Quotation Count Requirements | ✅ Yes | ❌ No | ❌ **NO** |
| Advertising Period Requirements | ✅ Yes | ❌ No | ❌ **NO** |

---

## CRITICAL MISSING INTEGRATIONS

### 🔴 Priority 1: Document Requirements Automation

**Problem:** 65 document requirements are defined but never automatically created as document records.

**Impact:**
- SCM officers don't get automatic checklist
- No validation of mandatory documents before publication
- Manual process to determine which documents are needed

**Solution Needed:**
```python
# In sagovtender.py - when tender moves to scm_processing state
def action_start_scm_processing(self):
    """Move to SCM processing and create document checklist"""
    self._create_document_checklist()
    self.write({'state': 'scm_processing'})

def _create_document_checklist(self):
    """Create document records from procurement method requirements"""
    self.ensure_one()
    if not self.procurement_method_config_id:
        return

    # Get required documents from configuration
    doc_requirements = self.procurement_method_config_id.document_requirement_ids

    # Create document record for each requirement
    for req in doc_requirements:
        # Check if document already exists
        existing = self.sagovtender_document_ids.filtered(
            lambda d: d.name == req.name
        )
        if not existing:
            self.env['sagovtender.document'].create({
                'tender_id': self.id,
                'name': req.name,
                'document_type': req.document_type,
                'mandatory': req.mandatory,
                'description': req.description,
                'sequence': req.sequence,
            })
```

---

### 🔴 Priority 2: Evaluation Criteria Pre-Loading

**Problem:** 42 evaluation criteria are defined but hardcoded criteria are used instead.

**Impact:**
- Configuration ignored during evaluation
- Inconsistent scoring across different procurement methods
- Manual configuration of criteria for each tender

**Solution Needed:**
```python
# In sagovbid_evaluation.py
def _load_functionality_criteria(self):
    """Load functionality evaluation criteria from tender config"""
    self.ensure_one()
    self.functionality_line_ids.unlink()

    if not self.tender_id.procurement_method_config_id:
        return

    # Load from configuration instead of hardcoded values
    config_criteria = self.tender_id.evaluation_criteria_ids.filtered(
        lambda c: c.criteria_type == 'functionality'
    )

    if not config_criteria:
        # Fallback to defaults if none configured
        config_criteria = self._get_default_criteria()

    for criteria in config_criteria:
        self.env['sagovtender.eval.funct.line'].create({
            'evaluation_id': self.id,
            'criteria': criteria.name,
            'weight': criteria.weight,
            'max_score': 100,
            'description': criteria.description,
            'sequence': criteria.sequence,
        })
```

---

### 🟡 Priority 3: Workflow Stage Enforcement

**Problem:** 86 workflow stages defined but state transitions are manual.

**Impact:**
- No validation of workflow sequence
- No enforcement of responsible group permissions
- No tracking of stage completion

**Solution Needed:**
```python
# Add workflow stage tracking to tender
workflow_stage_history_ids = fields.One2many(
    'sagovtender.workflow.stage.history',
    'tender_id',
    string='Workflow Stage History'
)
current_workflow_stage_id = fields.Many2one(
    'sagovprocurement.workflow.stage',
    string='Current Workflow Stage',
    compute='_compute_current_workflow_stage',
    store=True
)

def action_next_workflow_stage(self):
    """Move to next workflow stage in sequence"""
    current_stage = self.current_workflow_stage_id
    if not current_stage:
        # Start at first stage
        next_stage = self.workflow_stage_ids.sorted('sequence')[0]
    else:
        # Get next stage
        stages = self.workflow_stage_ids.sorted('sequence')
        current_index = list(stages).index(current_stage)
        if current_index + 1 < len(stages):
            next_stage = stages[current_index + 1]
        else:
            raise UserError('Already at final workflow stage')

    # Validate responsible group
    if not self._user_in_responsible_group(next_stage.responsible_group):
        raise UserError(
            f'Only {next_stage.responsible_group} can proceed to {next_stage.name}'
        )

    # Create history record
    self.env['sagovtender.workflow.stage.history'].create({
        'tender_id': self.id,
        'stage_id': next_stage.id,
        'user_id': self.env.user.id,
        'timestamp': fields.Datetime.now(),
    })
```

---

### 🟡 Priority 4: Quotation Requirement Validation

**Problem:** Methods specify quotations_required (1, 3, etc.) but no validation exists.

**Impact:**
- Method A requires 3 quotations but system doesn't enforce
- No validation of quotation count before award
- Non-compliance with Treasury regulations

**Solution Needed:**
```python
# In sagovtender.py or sagovbid_evaluation.py
def validate_quotation_requirements(self):
    """Validate minimum quotations received"""
    self.ensure_one()
    if not self.procurement_method_config_id:
        return True

    method = self.procurement_method_config_id
    required_count = method.quotations_required

    # Count compliant bids/quotations
    compliant_bids = self.bid_ids.filtered(lambda b: b.is_compliant)

    if len(compliant_bids) < required_count:
        raise ValidationError(
            f'{method.name} requires at least {required_count} '
            f'quotations/bids. Only {len(compliant_bids)} received.'
        )

    return True
```

---

### 🟡 Priority 5: Committee Requirement Enforcement

**Problem:** Methods specify requires_bsc_approval, requires_bec_evaluation, requires_bac_review but not enforced.

**Impact:**
- Can award tender without required committee approvals
- Non-compliance with delegation of authority
- Audit failures

**Solution Needed:**
```python
# In sagovtender_award.py
def action_approve_award(self):
    """Approve tender award with committee validation"""
    self.ensure_one()
    method = self.tender_id.procurement_method_config_id

    # Validate BSC approval if required
    if method.requires_bsc_approval:
        if self.tender_id.state != 'bsc_approved':  # Example
            raise UserError(
                f'{method.name} requires BSC Approval before award.\n'
                'Delegation: BSC Sub-Committee'
            )

    # Validate BEC evaluation if required
    if method.requires_bec_evaluation:
        if not self.tender_id.evaluation_ids:
            raise UserError(
                f'{method.name} requires BEC Evaluation before award.'
            )
        if not all(e.state == 'approved' for e in self.tender_id.evaluation_ids):
            raise UserError('All BEC evaluations must be approved before award')

    # Validate BAC review if required
    if method.requires_bac_review:
        if not self.tender_id.bac_review_ids:
            raise UserError(
                f'{method.name} requires BAC Review before award.'
            )
        if not all(b.state == 'approved' for b in self.tender_id.bac_review_ids):
            raise UserError('All BAC reviews must be approved before award')

    # Proceed with award
    self.write({'state': 'approved'})
```

---

## VISUALIZATION: CURRENT VS DESIRED FLOW

### Current Flow (Disconnected)
```
APP (Method Selected)
  ↓ (method_id stored)
Requisition (Method Referenced)
  ↓ (method_id passed)
Budget (Method Visible)
  ↓ (method_id passed)
Tender (Method Selected)
  ↓ (related fields VIEWABLE ONLY)
  ├── workflow_stage_ids (read-only)
  ├── document_requirement_ids (read-only)  ❌ NOT APPLIED
  └── evaluation_criteria_ids (read-only)   ❌ NOT APPLIED
    ↓
Documents (Manual Upload) ❌ NO CHECKLIST
    ↓
Publication (No Validation) ❌ NO DOC CHECK
    ↓
Bid Evaluation (Hardcoded Criteria) ❌ IGNORES CONFIG
    ↓
Award (No Committee Check) ❌ NO ENFORCEMENT
```

### Desired Flow (Integrated)
```
APP (Method Auto-Selected by Value)
  ↓ (method_id + validation)
Requisition (Method Inherited + Validated)
  ↓ (quotation requirements enforced)
Budget (Method Validated + Threshold Checked)
  ↓ (approval routing based on value)
Tender (Method Applied + Config Loaded)
  ↓ (automatic initialization)
  ├── ✅ Workflow stages activated
  ├── ✅ Document checklist created
  └── ✅ Evaluation criteria pre-loaded
    ↓
Documents (Checklist Generated)
  ├── ✅ Mandatory docs flagged
  ├── ✅ Upload tracking
  └── ✅ Validation before publish
    ↓
Publication (Requirements Validated)
  ├── ✅ All mandatory docs present
  ├── ✅ Advertising period correct
  └── ✅ Compliance checks passed
    ↓
Bid Evaluation (Config-Driven)
  ├── ✅ Criteria loaded from config
  ├── ✅ Weights validated (total=100%)
  └── ✅ Preference system applied
    ↓
Committee Review (Enforced)
  ├── ✅ BSC approval (if required)
  ├── ✅ BEC evaluation (if required)
  └── ✅ BAC review (if required)
    ↓
Award (Validated)
  ├── ✅ Quotation count met
  ├── ✅ Committee approvals complete
  └── ✅ Delegated authority confirmed
```

---

## RECOMMENDATIONS

### Phase 1: Document Requirements Integration (HIGH PRIORITY)
**Timeline:** 2 weeks
**Effort:** Medium
**Impact:** High

1. Create `_create_document_checklist()` method
2. Call method when tender enters `scm_processing` state
3. Add validation in `action_publish_tender()` to check mandatory documents
4. Update tender form view to show checklist with upload status

### Phase 2: Evaluation Criteria Pre-Loading (HIGH PRIORITY)
**Timeline:** 1 week
**Effort:** Low
**Impact:** High

1. Modify `_load_functionality_criteria()` to read from config
2. Add support for other criteria types (price, compliance, technical)
3. Validate total weights = 100%
4. Test with all 7 procurement methods

### Phase 3: Committee Requirement Enforcement (MEDIUM PRIORITY)
**Timeline:** 2 weeks
**Effort:** Medium
**Impact:** Medium

1. Add validation in award approval process
2. Check BSC, BEC, BAC requirements before award
3. Add workflow state checks
4. Add delegation of authority validation

### Phase 4: Workflow Stage Tracking (MEDIUM PRIORITY)
**Timeline:** 3 weeks
**Effort:** High
**Impact:** Medium

1. Create workflow stage history model
2. Add current stage tracking
3. Implement stage transition validation
4. Add responsible group permission checks

### Phase 5: Quotation & Period Validation (LOW PRIORITY)
**Timeline:** 1 week
**Effort:** Low
**Impact:** Low

1. Validate quotation count before evaluation
2. Validate advertising period before publication
3. Add submission period tracking
4. Enforce late bid rejection flag

---

## CONCLUSION

### The Good News ✅
Your system has **excellent configuration infrastructure**. All procurement methods, workflow stages, document requirements, evaluation criteria, and preference systems are fully defined and compliant with SA government regulations.

### The Challenge ❌
These configurations exist as **reference data** but are **not enforced in the workflow**. The system can show users what SHOULD happen, but doesn't automatically make it happen.

### The Solution 🔧
Implement the **5 Priority Phases** above to:
1. **Auto-generate document checklists** from requirements
2. **Pre-load evaluation criteria** from configurations
3. **Enforce committee approvals** based on method rules
4. **Track workflow stages** and validate transitions
5. **Validate quotation counts** and advertising periods

### Estimated Total Effort
- **Development:** 4-6 weeks
- **Testing:** 2 weeks
- **Deployment:** 1 week
- **Total:** 7-9 weeks for complete integration

### Expected Outcome
A fully integrated system where procurement method configurations **automatically drive** the tender workflow, ensuring compliance and reducing manual errors.

---

**Report Generated:** February 5, 2026
**System Version:** Odoo 18.0 Enterprise
**Module:** sa_government_tender v18.0.1.0.0
