# Configurable Procurement Methods & Preference Point Systems - Implementation Guide

## Overview

This implementation introduces a configurable framework for procurement methods and preference point systems per South African government compliance regulations (PFMA, MFMA, PPPFA, and National Treasury regulations).

**Key Benefits:**
- 🎯 Centralized configuration of all procurement methods
- 🔄 Flexible workflow definition per method
- 📊 Configurable preference point systems (80/20, 90/10, custom)
- ✅ Built-in compliance tracking (PFMA, MFMA, PPPFA, National Treasury)
- 📋 Audit trails for all configurations
- 🔗 Full linkage between procurement methods and preference systems

---

## New Models Created

### 1. **sagovprocurement.method**
**Location:** `models/sagovprocurement_method.py`

Defines configurable procurement methods with:
- **Basic Info:** Name, Code, Description, Sequence, Active Status
- **Value Thresholds:** Min/Max procurement values
- **Quotation Requirements:** Number required, period, format
- **Committee Requirements:** BSC, BEC, BAC approval needs
- **Briefing Configuration:** Session requirements (mandatory/optional)
- **Advertising & Compliance:** Advertising period, late bid rejection, compliance checks
- **Workflow Stages:** Complete workflow definition (One2many)
- **Document Requirements:** Required documents for each method (One2many)
- **Evaluation Criteria:** Scoring criteria used (One2many)
- **Preference Systems:** Linked preference point systems (Many2many)
- **Regulatory Compliance:** PFMA, MFMA, PPPFA, National Treasury flags
- **Audit Fields:** Created/Modified by user tracking

**Key Methods:**
```python
get_applicable_method(estimated_value)  # Get method for a value
get_workflow_sequence()                  # Get workflow stages in order
get_document_requirements()              # Get required documents
get_evaluation_criteria()                # Get evaluation criteria
validate_compliance()                    # Validate compliance rules
```

---

### 2. **sagovpreference.point.system**
**Location:** `models/sagovpreference_point_system.py`

Defines preference point systems with:
- **Basic Info:** Name, Code, Type (80/20, 90/10, Custom), Description
- **Weighting:** Price weight %, Preference points weight %
- **Preference Points:** Total available, allocation by criteria
  - B-BBEE Compliance (Level-based)
  - Women Empowerment
  - Youth Entrepreneurs (18-35 years)
  - Local Content/Manufacturing
  - Small & Medium Enterprises (SME)
  - Persons with Disability (PWD) Owners
- **Price Scoring:** Formula selection (Lowest wins, Lowest scored, Custom)
- **Preference Criteria:** Detailed scoring rules (One2many)
- **Applicability:** Applicable procurement methods, minimum value
- **Compliance:** PPPFA compliance flag, legal references
- **Audit Fields:** Created/Modified tracking

**Key Methods:**
```python
get_preference_criteria()                        # Get all criteria
calculate_preference_score(supplier_attrs)      # Calculate supplier score
calculate_final_score(price_score, pref_score)  # Combined weighted score
validate_system()                               # Validate configuration
```

---

### 3. **sagovprocurement.workflow.stage**
**Location:** `models/sagovprocurement_method.py` (One2many model)

Defines workflow stages for each method:
- **Stage Details:** Name, Sequence, Description
- **Responsibility:** Responsible group (End User, SCM, BSC, BEC, BAC, Delegated Authority, Supplier)
- **Type:** Information gathering, Approval, Evaluation, Execution, Payment
- **Requirements:** Mandatory/Optional, Auto-transition flag

---

### 4. **sagovprocurement.document.requirement**
**Location:** `models/sagovprocurement_method.py` (One2many model)

Defines required documents:
- **Document Info:** Name, Type (Compliance, Technical, Commercial, Legal, Financial)
- **Requirements:** Mandatory/Optional, Validity period
- **Sequence:** Order in list

---

### 5. **sagovpreference.point.criteria**
**Location:** `models/sagovpreference_point_system.py` (One2many model)

Detailed preference criteria:
- **Criteria Info:** Name, Key (for data lookup), Description
- **Scoring:** Type (Binary, Level, Percentage, Points, Custom)
- **Rules:** Scoring rule (All-or-nothing, Proportional, Tiered)
- **Points:** Available points, tiered definitions

---

## Procurement Methods Configured

### A. **Quotation < R30,000** (`quotation_r30k`)
- **Value Range:** R0 - R30,000
- **Quotations:** 1 minimum (written)
- **Period:** 5 days
- **Workflow:** 8 steps (simple process)
- **Committees:** None
- **Compliance Check:** No
- **Declaration of Interest:** No
- **Briefing:** No

**Process:**
1. Demand Identification
2. Requisition Capture
3. Obtain Written Quotation
4. Evaluation & Selection
5. Approval of Award
6. Purchase Order Issued
7. Delivery/Service
8. Invoice & Payment

---

### B. **Open RFQ (R30,000 - R300,000)** (`open_rfq_r30k_r300k`)
- **Value Range:** R30,000 - R300,000
- **Quotations:** 3 minimum (written)
- **Period:** 10 days
- **Advertising:** 7 days minimum
- **Workflow:** 10 steps
- **Committees:** None
- **Compliance Check:** No
- **Briefing:** No

**Process:**
1. Demand Identification
2. Requisition Capture
3. Requisition Approval
4. RFQ Creation/Advertisement
5. RFQ Closing
6. Evaluation & Selection
7. Approval of Award
8. Purchase Order Issued
9. Delivery/Service
10. Invoice & Payment

---

### C. **Competitive Bid < R50 Million** (`competitive_bid_r50m`)
- **Value Range:** R300,000 - R50,000,000
- **Quotations:** 1 (open bidding)
- **Period:** 21 days
- **Advertising:** 21 days minimum
- **Workflow:** 12 steps (full formal process)
- **Committees:** BSC, BEC, BAC (all required)
- **Briefing:** Yes (optional)
- **Compliance Check:** Yes (CSD, Tax, COID, B-BBEE)
- **Declaration of Interest:** Yes
- **Preference Systems:** 80/20 (< R500,000), 90/10 (≥ R500,000)

**Process:**
1. Demand Identification & Planning
2. Specification Development
3. BSC Review & Approval
4. Bid Advertisement
5. Briefing Session (if applicable)
6. Bid Closing
7. BEC Evaluation (Administrative, Technical, Price & Preference)
8. BAC Adjudication
9. Award Approval
10. Contract/PO Issued
11. Contract Management
12. Invoice & Payment

---

### D. **Competitive Bid > R50 Million** (`competitive_bid_over_r50m`)
- **Value Range:** R50,000,000 - Unlimited
- **Period:** 30 days
- **Advertising:** 30 days minimum (National newspapers)
- **Workflow:** 15 steps (extended process)
- **Committees:** BSC, BEC, BAC (all required)
- **Briefing:** Yes (mandatory)
- **Compliance Check:** Yes
- **Declaration of Interest:** Yes
- **Treasury Review:** Required for Departments
- **Negotiation:** Allowed
- **Dedicated Contract Manager:** Required

**Process:**
1. Demand Management & Requisition
2. Specification Development
3. BSC Review & Approval
4. Accounting Officer Approval
5. Bid Advertisement (Extended)
6. Briefing Session (Compulsory)
7. Bid Closing
8. BEC Evaluation (Multi-stage)
9. BAC Adjudication
10. Oversight/Treasury Review
11. Award Approval
12. Contract Signing
13. Contract Management
14. Payment Processing
15. Performance Monitoring

---

### E. **Sole Source Procurement** (`sole_source`)
- **Value Range:** Any (requires justification)
- **Quotations:** 1 (from single supplier)
- **Compliance Check:** Yes
- **PPPFA Compliant:** No (requires deviation)
- **Negotiation:** Allowed
- **Framework Agreements:** Allowed

**Process:**
1. Demand Identification
2. Sole Source Motivation
3. Market Analysis / Proof of Uniqueness
4. Approval for Sole Source (Accounting Officer)
5. Request Written Quotation
6. Evaluation of Quotation
7. Award Approval
8. PO/Contract Issued
9. Delivery/Performance
10. Invoice & Payment

---

### F. **Emergency/Deviation Procurement** (`emergency_procurement`)
- **Value Range:** Any
- **Timeframe:** 1 day (minimal)
- **Written Quotation:** Not required
- **PPPFA Compliant:** No
- **Approval Required:** Yes (Accounting Officer)
- **Reporting:** To oversight committees

**Process:**
1. Emergency Identification (Risk to life, service, assets)
2. Immediate Risk Assessment
3. Deviation/Emergency Motivation
4. Approval of Deviation
5. Procurement from Suitable Supplier
6. PO/Emergency Contract Issued
7. Delivery/Service Rendered
8. Post-Procurement Reporting
9. Invoice & Payment

---

### G. **Panel Suppliers / Framework Agreement** (`panel_suppliers`)
- **Value Range:** Any (within panel scope)
- **Quotations:** 1+ (from panel members)
- **Advertising:** None (pre-established panel)
- **Panel Requirement:** Must be from competitive panel
- **Direct Call-off:** Allowed if pre-approved pricing

**Process:**
1. Demand Identification
2. Panel Confirmation
3. Request Quotations/Call-Off
4. Evaluation of Panel Responses
5. Award Approval
6. PO/Call-Off Order Issued
7. Delivery/Service Performance
8. Invoice & Payment

---

## Preference Point Systems

### **80/20 System** (`system_80_20`)
**Applicable Range:** R30,000 - R500,000

**Scoring:** Final = (Price Score × 0.80) + (Preference Score × 0.20)

**Preference Points Allocation (Total: 20 points):**
- B-BBEE Compliance: 15 points (level-based: BEE 1-4 full points, 5-8 half points)
- Women Empowerment: 3 points
- Youth Entrepreneurs (18-35 years): 3 points
- Local Content/Manufacturing: 4 points (100% = full, 50% = 75%, 25% = 50%)
- Small & Medium Enterprise (SME): 2 points
- Persons with Disability (PWD) Owner: 1 point

---

### **90/10 System** (`system_90_10`)
**Applicable Range:** Above R500,000

**Scoring:** Final = (Price Score × 0.90) + (Preference Score × 0.10)

**Preference Points Allocation (Total: 10 points):**
- B-BBEE Compliance: 8 points
- Women Empowerment: 1 point
- Youth Entrepreneurs (18-35 years): 1 point
- Local Content/Manufacturing: 2 points
- Small & Medium Enterprise (SME): 1 point
- Persons with Disability (PWD) Owner: 0.5 points

---

## Views & User Interface

### **Procurement Method Configuration**
- **Location:** `views/sagovprocurement_method_views.xml`
- **Menu Path:** Administration > SCM Configuration > Procurement Methods
- **Views:** Tree (editable), Form (detailed), Kanban (cards), Search
- **Features:**
  - Tree view with drag-drop sequencing
  - Form with tabs for different sections
  - Kanban board grouped by status
  - Advanced search/filtering
  - Compliance validation button

### **Preference Point System Configuration**
- **Location:** Same XML file
- **Menu Path:** Administration > SCM Configuration > Preference Point Systems
- **Views:** Tree (editable), Form (detailed), Search
- **Features:**
  - Weight validation (must = 100%)
  - Points validation (total ≤ available)
  - System type templates (80/20, 90/10, Custom)

---

## Data Configuration

### **File:** `data/sagovprocurement_method_data.xml`
Contains:
1. 7 pre-configured procurement methods (A-G above)
2. 2 pre-configured preference point systems (80/20, 90/10)
3. Workflow stages for each method
4. Legal framework references

**Key Compliance References:**
- PPPFA (Preferential Procurement Policy Framework Act)
- PFMA (Public Finance Management Act) Section 76
- MFMA (Municipal Finance Management Act) Section 111
- National Treasury SCM Instruction Notes
- B-BBEE Act & Compliance
- Constitution Section 217

---

## Integration Points

### **With Existing Tender Models**
To link existing tender models, add these fields:

```python
# In sagovtender.py, sagovannual_procurement_plan.py
procurement_method_id = fields.Many2one(
    'sagovprocurement.method',
    string='Procurement Method',
    help='Link to configurable procurement method'
)

preference_point_system_id = fields.Many2one(
    'sagovpreference.point.system',
    string='Preference Point System',
    help='Link to configurable preference point system'
)
```

### **Dynamic Workflow Trigger**
```python
def _get_workflow_stages(self):
    """Get workflow stages based on selected procurement method"""
    if self.procurement_method_id:
        return self.procurement_method_id.workflow_stage_ids
    return []
```

---

## Usage & Management

### **1. Configure Procurement Methods**
1. Go to Administration > SCM Configuration > Procurement Methods
2. Click Create
3. Fill basic information (Name, Code, Value Range)
4. Set quotation requirements
5. Configure committee requirements
6. Add workflow stages (drag to reorder)
7. Add document requirements
8. Add evaluation criteria
9. Link applicable preference systems
10. Save and Validate Compliance

### **2. Configure Preference Point Systems**
1. Go to Administration > SCM Configuration > Preference Point Systems
2. Click Create
3. Select system type (80/20, 90/10, Custom)
4. Set price/preference weightings (must = 100%)
5. Allocate preference points to criteria
6. Add detailed scoring rules
7. Specify applicability (value range, methods)
8. Save

### **3. Apply to Procurement**
When creating a tender/requisition:
1. Select estimated value
2. System suggests applicable procurement method
3. Automatically selects appropriate preference system
4. Loads workflow stages from configuration
5. Applies document requirements
6. Sets evaluation criteria

---

## Compliance Framework

### **Regulatory Coverage**

| Framework | Methods | Implementation |
|-----------|---------|-----------------|
| **PFMA Section 76** | All | Audit trails, approval workflows, thresholds |
| **MFMA Section 111** | RFQ, Competitive | Municipal value ranges, approval hierarchies |
| **PPPFA** | Competitive Bids | 80/20, 90/10 preference systems, BEE criteria |
| **Treasury Regulations** | All | Value ranges, advertising periods, reporting |
| **B-BBEE Act** | Competitive | Preference criteria, scoring, compliance checks |
| **Constitution S217** | All | Fair, equitable, transparent processes |

### **Audit Trail**
- Created by/Last modified by users tracked
- Configuration change history maintained
- Method application decisions logged
- Workflow stage transitions recorded

---

## Benefits & Features

✅ **Centralized Configuration** - Single source of truth for all procurement methods
✅ **Regulatory Compliance** - Built-in PFMA, MFMA, PPPFA, Treasury validation
✅ **Flexible Workflows** - Define exact steps per method
✅ **Preference Systems** - 80/20, 90/10, and custom support
✅ **Document Tracking** - Required documents per method
✅ **Evaluation Criteria** - Predefined criteria with weights
✅ **Audit Ready** - Complete compliance tracking & logging
✅ **User-Friendly** - No coding required to configure
✅ **Scalable** - Add custom methods/systems as needed
✅ **Linked** - Complete integration with tender workflow

---

## Next Steps

1. **Link to Tender Models** - Add Many2one fields to sagovtender and related models
2. **Update Views** - Modify tender form to use configurable method/preference dropdowns
3. **Workflow Integration** - Implement workflow stage progression based on configuration
4. **Reporting** - Add reports for procurement method usage and compliance
5. **API Endpoints** - Create REST endpoints for method/system access
6. **Dashboard** - Add procurement method analytics dashboard
7. **Mobile App** - Enable mobile access to configurations

---

## Support & Documentation

For questions or custom configurations, contact the SCM Configuration team.

All configurations must be validated for compliance before approval and use.
