# Quick Reference - Procurement Methods & Preference Systems

## 🚀 Quick Start

### Access Configuration
- **Path:** Administration > SCM Configuration
- **Procurement Methods:** Procurement Methods (Tree/Form/Kanban)
- **Preference Systems:** Preference Point Systems (Tree/Form)

---

## 📋 Procurement Methods At-a-Glance

### A. Quotation < R30,000
```
Value:        R0 - R30,000
Quotations:   1 (written)
Period:       5 days
Committees:   None
Documents:    None required
Workflow:     8 steps
Preference:   None
Compliance:   PFMA, Treasury
```

### B. Open RFQ (R30k - R300k)
```
Value:        R30,000 - R300,000
Quotations:   3 preferred (written)
Period:       10 days
Advertising:  7 days minimum
Committees:   None
Documents:    None required
Workflow:     10 steps
Preference:   None
Compliance:   PFMA, MFMA, Treasury
```

### C. Competitive Bid < R50M
```
Value:        R300,000 - R50,000,000
Quotations:   1+ (open bidding)
Period:       21 days
Advertising:  21 days minimum
Committees:   BSC, BEC, BAC (all required)
Briefing:     Optional
Documents:    CSD, Tax, COID, B-BBEE
Workflow:     12 steps
Preference:   80/20 (< R500k) or 90/10 (≥ R500k)
Compliance:   PFMA, MFMA, PPPFA, Treasury
```

### D. Competitive Bid > R50M
```
Value:        > R50,000,000
Quotations:   1+ (open bidding)
Period:       30 days
Advertising:  30 days minimum (newspapers)
Committees:   BSC, BEC, BAC (all required)
Briefing:     Mandatory
Treasury:     Concurrence required (Departments)
Documents:    CSD, Tax, COID, B-BBEE
Workflow:     15 steps
Preference:   90/10
Compliance:   PFMA, MFMA, PPPFA, Treasury
Negotiation:  Allowed
```

### E. Sole Source
```
Value:        Any
Quotations:   1 (from sole supplier)
Documents:    Compliance check
Justification: Written motivation required
Committees:   None
Compliance:   PFMA only (non-PPPFA)
Approval:     Accounting Officer deviation
```

### F. Emergency Procurement
```
Value:        Any
Quotations:   1
Timeframe:    Urgent (1 day)
Documents:    Minimal
Justification: Written motivation required
Compliance:   PFMA only (non-PPPFA)
Approval:     Accounting Officer deviation
Reporting:    To oversight committees
```

### G. Panel Suppliers
```
Value:        Any (within panel scope)
Panel:        Must be competitive-established
Quotations:   1+ (from panel members)
Advertising:  None (pre-established)
Negotiation:  Pre-approved pricing
Compliance:   PFMA, MFMA, PPPFA, Treasury
```

---

## 🎯 Preference Point Systems

### 80/20 System
```
Applicable:   R30,000 - R500,000
Formula:      (Price Score × 80%) + (Preference × 20%)
Total Points: 20 points

B-BBEE Level 1-4:   15 points
B-BBEE Level 5-8:   7.5 points
Women Empowerment:  3 points
Youth (18-35):      3 points
Local Content 100%: 4 points
Local Content 50%:  3 points
SME:                2 points
PWD Owner:          1 point
```

### 90/10 System
```
Applicable:   > R500,000
Formula:      (Price Score × 90%) + (Preference × 10%)
Total Points: 10 points

B-BBEE Level 1-4:   8 points
B-BBEE Level 5-8:   4 points
Women Empowerment:  1 point
Youth (18-35):      1 point
Local Content 100%: 2 points
Local Content 50%:  1.5 points
SME:                1 point
PWD Owner:          0.5 points
```

---

## ⚙️ Key Fields per Method

### Basic Configuration
- **Name** - Method display name (e.g., "Competitive Bid < R50M")
- **Code** - System identifier (e.g., "competitive_bid_r50m")
- **Sequence** - Order in lists (10, 20, 30...)
- **Active** - Enabled/Disabled toggle
- **Description** - Full process description (HTML)

### Value Thresholds
- **Min Value** - Minimum procurement value (in ZAR)
- **Max Value** - Maximum value (0 = unlimited)
- **Currency** - ZAR (South African Rand)

### Quotation Requirements
- **Quotations Required** - Minimum number (1, 3, etc.)
- **Period Days** - Days to submit responses (5, 10, 21, 30)
- **Written Only** - Email/Letterhead/PDF flag

### Committee Requirements
- **Requires BSC** - Bid Specification Committee approval
- **Requires BEC** - Bid Evaluation Committee evaluation
- **Requires BAC** - Bid Adjudication Committee review
- **Briefing Session** - Required or optional
- **Briefing Mandatory** - Compulsory vs optional

### Advertising & Compliance
- **Min Advertising Days** - Minimum announcement period (0, 7, 21, 30)
- **Late Bids Rejected** - Auto-reject late submissions
- **Compliance Check** - CSD, Tax, COID, B-BBEE verification
- **Declaration of Interest** - Supplier conflict disclosure

### Preferences & Framework
- **Preference Systems** - Linked 80/20, 90/10, custom
- **Allows Negotiation** - Post-award negotiation allowed
- **Allows Framework** - Framework agreements permitted
- **Allows Panel** - Panel supplier use allowed

### Regulatory
- **PFMA Compliant** - Public Finance Management Act
- **MFMA Compliant** - Municipal Finance Management Act
- **PPPFA Compliant** - Preferential Procurement Policy
- **Treasury Compliant** - National Treasury regulations

---

## 📊 Workflow Stages Structure

Each method has workflow stages with:
- **Name** - Stage description
- **Sequence** - Order (10, 20, 30...)
- **Responsible** - Who does it (End User, SCM, BSC, BEC, BAC, Authority, Supplier)
- **Type** - What kind (Information, Approval, Evaluation, Execution, Payment)
- **Required** - Mandatory or optional
- **Auto Transition** - Auto-advance flag

### Example: Competitive Bid < R50M Stages
1. Demand Identification & Planning (End User - Info)
2. Specification Development (End User - Info)
3. BSC Review & Approval (BSC - Approval)
4. Bid Advertisement (SCM - Info)
5. Briefing Session (SCM - Info) [Optional]
6. Bid Closing (SCM - Info)
7. BEC Evaluation (BEC - Evaluation)
8. BAC Adjudication (BAC - Evaluation)
9. Award Approval (Authority - Approval)
10. Contract/PO Issued (SCM - Execution)
11. Contract Management (SCM - Execution)
12. Invoice & Payment (SCM - Payment)

---

## 📄 Document Requirements

Common documents per method:

### Compliance Documents
- **Tax Clearance** - SARS compliance
- **CSD** - Central Supplier Database
- **COID** - Company Registration
- **B-BBEE Certificate** - Black Economic Empowerment

### Tender Documents
- **Tender Specifications** - Technical requirements
- **Bid Documents (SBD)** - Standard Bidding Documents
- **Declaration Forms** - Conflict of interest, etc.

### Financial Documents
- **Bank Statement** - Last 3 months
- **Financial Statements** - Last 2 years
- **Payment Proof** - PO and invoice matching

---

## 🔍 Evaluation Criteria Structure

Each criterion has:
- **Name** - Criteria description
- **Type** - Category (Admin, Technical, Price, Preference, Financial, Other)
- **Weight %** - Percentage in overall score (0-100)
- **Pass/Fail** - Binary or scored
- **Min Score** - Minimum achievable points
- **Max Score** - Maximum achievable points

### Example: Competitive Bid Criteria
1. **Administrative Compliance** (Type: Admin, Weight: 10%, Pass/Fail: Yes)
2. **Technical Compliance** (Type: Technical, Weight: 30%, Score: 0-100)
3. **Price Score** (Type: Price, Weight: 70%, Score: 0-100)
4. **Preference Points** (Type: Preference, Weight: Varies, Score: 0-20)

---

## 🎨 Preference Criteria Details

### B-BBEE Scoring
```
Level 1 (First-time BEE):    Full points
Level 2 (Compliant BEE):     Full points
Level 3 (Strong BEE):        Full points
Level 4 (Broad BEE):         Full points
Level 5 (Generic BEE):       50% of points
Level 6-8 (Other BEE):       50% of points
Non-BEE:                     0 points
```

### Women Empowerment
```
Women-owned (>50%):       Full points
Women-managed (key roles): Full points
Otherwise:                0 points
```

### Youth Entrepreneur
```
Owner age 18-35:          Full points
Age > 35:                 0 points
```

### Local Content
```
100% Local Manufacturing: Full points
50% Local Content:        75% of points
25% Local Content:        50% of points
< 25% Local:             0 points
```

---

## 🔐 Compliance Checklist

### Before Publishing Tender
- [ ] Procurement method selected
- [ ] Estimated value falls within method range
- [ ] Preference system auto-selected (if required)
- [ ] Required committee approvals obtained
- [ ] Advertising period started on schedule
- [ ] Declaration of interest forms distributed
- [ ] Compliance documents requested
- [ ] Workflow stages confirmed

### Before Evaluation
- [ ] All quotations/bids received
- [ ] Late submissions rejected
- [ ] Closing register generated
- [ ] Administrative compliance checked
- [ ] Documents validated (CSD, Tax, COID, B-BBEE)
- [ ] Preference points calculated
- [ ] BEC evaluation prepared (if required)

### Before Award
- [ ] BEC evaluation completed (if required)
- [ ] BAC review completed (if required)
- [ ] Final score calculated
- [ ] Award recommended
- [ ] Delegated authority approved
- [ ] Award decision recorded

---

## 💡 Common Scenarios

### Scenario 1: R45,000 Procurement
```
Estimated Value: R45,000
→ Suggested Method: Open RFQ (R30k - R300k)
→ Quotations: 3 minimum
→ Period: 10 days
→ No preference points
→ Compliance: Basic
→ Timeline: ~15 days
```

### Scenario 2: R3,500,000 Procurement
```
Estimated Value: R3,500,000
→ Suggested Method: Competitive Bid < R50M
→ Quotations: Open bidding
→ Preference System: 80/20
→ Committees: BSC, BEC, BAC all required
→ Compliance: Full (CSD, Tax, COID, B-BBEE)
→ Timeline: ~60 days
```

### Scenario 3: R75,000,000 Procurement (Dept)
```
Estimated Value: R75,000,000
→ Suggested Method: Competitive Bid > R50M
→ Quotations: Open bidding
→ Preference System: 90/10
→ Committees: BSC, BEC, BAC all required
→ Treasury: Concurrence required
→ Compliance: Full + National/Provincial advert
→ Timeline: ~90 days
```

### Scenario 4: Sole Source (OEM Software)
```
Estimated Value: R2,500,000
→ Method: Sole Source (Non-competitive)
→ Justification: OEM only authorized distributor
→ Approval: Accounting Officer deviation required
→ Compliance: Deviation register entry
→ Status: Non-PPPFA compliant (requires variance)
```

---

## 📞 Contacts & Support

**Configuration Questions:** SCM Manager
**Technical Issues:** System Administrator
**Regulatory Questions:** Compliance Officer
**Training:** SCM Training Team

---

## 📚 Full Documentation

- **PROCUREMENT_METHODS_IMPLEMENTATION.md** - Complete feature guide
- **INTEGRATION_GUIDE.md** - Development integration examples
- **CONFIGURATION_SUMMARY.md** - Detailed overview
- **This Document** - Quick reference (you are here)

---

## ✅ Status

**Implementation:** ✅ Complete
**Testing:** ✅ Ready
**Documentation:** ✅ Complete
**Deployment:** ✅ Ready

**Version:** 1.0
**Last Updated:** February 2026
**SA Government Compliance:** PFMA, MFMA, PPPFA, National Treasury ✨
