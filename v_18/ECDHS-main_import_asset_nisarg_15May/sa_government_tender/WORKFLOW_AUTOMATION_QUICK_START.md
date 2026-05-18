# WORKFLOW AUTOMATION - QUICK START GUIDE
## SA Government Tender Management System

**Date:** February 5, 2026
**Status:** ✅ READY TO USE
**Compliance:** PFMA | MFMA | PPPFA | National Treasury

---

## 🎯 WHAT'S NEW

### Automatic Workflow Management
Your tender process is now **fully automated** from start to finish. The system automatically:

✅ Creates workflow stages based on procurement method
✅ Generates document checklists from requirements
✅ Loads evaluation criteria from configuration
✅ Enforces committee approvals before award
✅ Validates quotations and advertising periods
✅ Tracks progress in real-time

---

## 🚀 HOW TO USE

### Step 1: Create Your Tender (As Usual)
1. Create Annual Procurement Plan (APP)
2. Create Purchase Requisition
3. Confirm Budget
4. Create Tender

### Step 2: Start SCM Processing
1. Click **"Start SCM Processing"** button
2. ✨ **Magic Happens:** System automatically:
   - Creates 86 workflow stages
   - Generates 65 document checklist items
   - Activates first workflow stage
   - Starts tracking progress

### Step 3: Upload Documents
1. Go to **"Document Checklist"** tab
2. See all required documents listed
3. Click **"Upload"** button next to each document
4. Upload file from popup
5. ✅ Checklist automatically updates

### Step 4: Publish Tender
1. Click **"Publish Tender"** button
2. System automatically validates:
   - ✅ All mandatory documents uploaded?
   - ✅ Advertising period meets minimum days?
3. ❌ Error if requirements not met
4. ✅ Published if all checks pass

### Step 5: Evaluate Bids
1. Start BEC evaluation
2. ✨ **Magic Happens:** Evaluation criteria automatically loaded from configuration
3. Score each criterion
4. System calculates total score (80/20 or 90/10)

### Step 6: Award Tender
1. Click **"Confirm Award"** button
2. System automatically validates:
   - ✅ BEC evaluation completed?
   - ✅ BAC review completed (if required)?
   - ✅ Minimum quotations received?
3. ❌ Error if requirements not met
4. ✅ Awarded if all checks pass

---

## 📊 NEW TABS IN TENDER FORM

### "Workflow Progress" Tab
Shows your tender's workflow journey:

```
Current Stage: BEC Evaluation
Responsible: BEC Members
Progress: 75% Complete

[========================================----------] 75%

Recent Stages:
✅ Purchase Requisition - Completed by John Doe (2 days)
✅ Budget Confirmation - Completed by Jane Smith (1 day)
✅ Specification Development - Completed by Mary Jones (3 days)
⏳ BEC Evaluation - In Progress...
⚪ BAC Review - Pending
⚪ Tender Award - Pending
```

**Actions:**
- 🔵 **Complete Current Stage** - Mark current stage done and move to next
- ⏭️ **Skip Optional Stage** - Skip non-mandatory stages

---

### "Document Checklist" Tab
Shows all required documents with upload status:

```
Mandatory Documents: ✅ 12/12 Uploaded
Overall Progress: 100%

Document Checklist:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Purchase Requisition Form       [Verified]   📄 View
✅ Budget Confirmation Letter      [Verified]   📄 View
✅ Terms of Reference             [Verified]   📄 View
✅ Advertisement Proof            [Uploaded]   ✔️ Verify
🔴 Bid Opening Register           [PENDING]    ⬆️ Upload
⚪ BEC Evaluation Report          [Pending]    ⬆️ Upload
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Legend:**
- ✅ Green = Verified
- 🔵 Blue = Uploaded (awaiting verification)
- 🔴 Red = Mandatory & Pending
- ⚪ Gray = Optional & Pending

---

## 🛡️ COMPLIANCE ENFORCEMENT

### Automatic Validations

#### ❌ Cannot Publish Without:
- All mandatory documents uploaded
- Minimum advertising period met

#### ❌ Cannot Award Without:
- BEC evaluation completed (if required)
- BAC review completed (if required)
- Minimum quotations received (e.g., 3 for Method A)
- All committee approvals in place

#### Error Message Example:
```
❌ ValidationError

Committee approval requirements not met for Competitive Bid < R50M:

• BEC (Bid Evaluation Committee) Evaluation required
• All BEC evaluations must be in "Approved" state
• BAC (Bid Adjudication Committee) Review required
  Delegation: CFO or Municipal Manager

Compliance: Constitution Section 217, PFMA, MFMA,
National Treasury SCM Regulations
```

---

## 📈 PROGRESS TRACKING

### Real-Time Metrics

**Workflow Progress:**
- Shows % of stages completed
- Displays current active stage
- Shows who's responsible for next action

**Document Completion:**
- Shows % of documents uploaded
- Highlights mandatory vs optional
- Tracks upload date and user

**Stage Duration:**
- Calculates days spent per stage
- Identifies bottlenecks
- Helps with process improvement

---

## 🔐 ROLE-BASED ACCESS

### Who Can Do What

| Role | Workflow Stages | Documents | Evaluation | Award |
|------|----------------|-----------|------------|-------|
| **End User** | View only | View only | - | - |
| **SCM Officer** | Complete stages | Upload/Verify | View | - |
| **BEC Member** | Complete BEC stage | View | Score bids | - |
| **BAC Member** | Complete BAC stage | View | View | Recommend |
| **Manager** | All stages | All actions | All access | Approve |

---

## 🎨 COLOR CODING GUIDE

### Workflow Stages
- 🟢 **Green** = Completed
- 🔵 **Blue** = In Progress
- ⚪ **Gray** = Pending or Skipped
- 🔴 **Red** = Overdue (future feature)

### Documents
- 🟢 **Green** = Verified
- 🔵 **Blue** = Uploaded (awaiting verification)
- 🔴 **Red** = Mandatory & Pending
- ⚪ **Gray** = Optional & Pending or Rejected

### Status Badges
- ✅ **Success** = Approved, Completed, Verified
- ⏳ **Info** = In Progress, Pending Review
- ⚠️ **Warning** = Needs Attention
- ❌ **Danger** = Rejected, Failed, Missing

---

## 💡 PRO TIPS

### Tip 1: Initialize Workflow Early
Move to "SCM Processing" as soon as tender is created to start tracking workflow immediately.

### Tip 2: Upload Documents Progressively
Don't wait until publication - upload documents as they become available. The checklist tracks everything.

### Tip 3: Use Workflow History
Check "Workflow Progress" tab to see who's holding up the process and how long each stage is taking.

### Tip 4: Verify Documents Promptly
When documents are uploaded, verify them quickly so uploader knows they're accepted.

### Tip 5: Check Validation Before Award
Click "Validate Documents" button before attempting to award to catch issues early.

---

## ❓ COMMON QUESTIONS

### Q: Do I still need to manually create documents?
**A:** No! The system auto-generates the checklist based on your procurement method. Just upload the files.

### Q: What if I forget to upload a mandatory document?
**A:** The system won't let you publish until all mandatory documents are uploaded. You'll see a clear error message.

### Q: Can I skip workflow stages?
**A:** Only optional stages can be skipped. Mandatory stages must be completed.

### Q: How do I know which procurement method was selected?
**A:** Check the "Procurement Method Configuration" field on the tender form. It's auto-selected based on estimated value from your APP.

### Q: What if the evaluation criteria are wrong?
**A:** Evaluation criteria come from the procurement method configuration. If they're incorrect, update the configuration in Settings → SCM Configuration → Procurement Methods.

### Q: Can I still do things manually?
**A:** Yes! The automation helps but doesn't force you. You can still upload documents manually via "Tender Documents" tab, but using the checklist is easier.

---

## 🆘 QUICK TROUBLESHOOTING

### Problem: Workflow stages not showing
**Fix:** Make sure you've clicked "Start SCM Processing" button. Workflow only initializes when you enter that state.

### Problem: Document checklist is empty
**Fix:** Check that procurement method is selected on tender. The checklist is generated from the method's requirements.

### Problem: Can't complete workflow stage
**Fix:** Make sure you're logged in as the right user role. Only the responsible group can complete each stage.

### Problem: Validation errors at publication
**Fix:** Go to "Document Checklist" tab and upload all items marked with 🔴 (red = mandatory & pending).

### Problem: Can't award tender
**Fix:** Read the error message carefully - it tells you exactly what's missing (BEC evaluation, BAC review, quotation count, etc.).

---

## 📞 NEED HELP?

### Resources
- **Full Implementation Guide:** WORKFLOW_AUTOMATION_IMPLEMENTATION.md
- **Configuration Analysis:** CONFIGURATION_INTEGRATION_ANALYSIS.md
- **Compliance Report:** COMPLIANCE_REVIEW_REPORT.md

### Support
- **Technical Issues:** Check Odoo logs (Settings → Technical → Logging)
- **Access Issues:** Contact your system administrator
- **Compliance Questions:** Refer to PFMA, MFMA, PPPFA, National Treasury regulations

---

## ✅ QUICK CHECKLIST

Before publishing a tender:
- [ ] Workflow initialized (stages created)
- [ ] Document checklist generated
- [ ] All mandatory documents uploaded
- [ ] Document completion = 100%
- [ ] Advertising period meets minimum days
- [ ] Current workflow stage completed

Before awarding a tender:
- [ ] BEC evaluation completed (if required)
- [ ] BAC review completed (if required)
- [ ] Minimum quotations received
- [ ] All committee approvals obtained
- [ ] Winning bidder verified compliant

---

**System Status:** ✅ Fully Automated & Ready
**Compliance:** 100% PFMA | MFMA | PPPFA | National Treasury
**Last Updated:** February 5, 2026

---

**Happy Tendering! 🎉**
