#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Title
title = doc.add_heading('SA Government Tender Management System', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_heading('Complete Process Flow Documentation', level=2)
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()

# Introduction
intro = doc.add_paragraph()
intro.add_run('This document outlines the complete end-to-end process flow for the SA Government Tender Management System, compliant with PFMA, MFMA, PPPFA, and National Treasury regulations.').bold = True

doc.add_page_break()

# Step 0: Annual Procurement Plan
doc.add_heading('Step 0: Annual Procurement Plan (APP)', level=1)
doc.add_paragraph('Model: sagovtender.annual.procurement.plan', style='List Bullet')
doc.add_paragraph('Purpose: Budget planning for procurement', style='List Bullet')
doc.add_paragraph('States: Draft → Submitted → Approved → In Progress → Completed/Cancelled', style='List Bullet')

doc.add_heading('Key Fields:', level=3)
doc.add_paragraph('Fiscal year', style='List Bullet')
doc.add_paragraph('Department', style='List Bullet')
doc.add_paragraph('Budget line', style='List Bullet')
doc.add_paragraph('Estimated value', style='List Bullet')
doc.add_paragraph('Available budget', style='List Bullet')
doc.add_paragraph('Procurement method', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Approved budget allocation for procurement items')

doc.add_paragraph()

# Step 1: Purchase Requisition
doc.add_heading('Step 1: Purchase Requisition', level=1)
doc.add_paragraph('Model: sagovtender.purchase.requisition', style='List Bullet')
doc.add_paragraph('Purpose: Department initiates procurement request', style='List Bullet')
doc.add_paragraph('States: Draft → Submitted → Budget Review → Budget Confirmed → Specification Development → SCM Processing → Approved/Rejected/Cancelled', style='List Bullet')

doc.add_heading('Key Actions:', level=3)
doc.add_paragraph('Link to APP (if item is on approved plan)', style='List Bullet')
doc.add_paragraph('Specify item description, quantity, estimated cost', style='List Bullet')
doc.add_paragraph('Provide motivation (if not on APP)', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Approved requisition linked to APP')

doc.add_paragraph()

# Step 2: Budget Confirmation
doc.add_heading('Step 2: Budget Confirmation', level=1)
doc.add_paragraph('Model: sagovtender.budget.confirm', style='List Bullet')
doc.add_paragraph('Purpose: CFO/Finance confirms budget availability', style='List Bullet')
doc.add_paragraph('States: Draft → Submitted → Confirmed/Rejected', style='List Bullet')

doc.add_heading('Key Validations:', level=3)
doc.add_paragraph('Check available budget against APP', style='List Bullet')
doc.add_paragraph('Verify budget line allocation', style='List Bullet')
doc.add_paragraph('Confirm sufficient funds', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Budget confirmation with confirmed amount')

doc.add_paragraph()

# Step 3: Specification Development
doc.add_heading('Step 3: Specification Development', level=1)
doc.add_paragraph('Model: sagovtender.specification', style='List Bullet')
doc.add_paragraph('Purpose: Technical team develops detailed specifications', style='List Bullet')
doc.add_paragraph('States: Draft → In Progress → Review → Approved/Rejected', style='List Bullet')

doc.add_heading('Key Components:', level=3)
doc.add_paragraph('Technical requirements', style='List Bullet')
doc.add_paragraph('Functional specifications', style='List Bullet')
doc.add_paragraph('Quality standards', style='List Bullet')
doc.add_paragraph('Delivery requirements', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Approved specification document')

doc.add_page_break()

# Step 4: SCM Processing
doc.add_heading('Step 4: SCM Processing', level=1)
doc.add_paragraph('Model: sagovtender.tender', style='List Bullet')
doc.add_paragraph('State: scm_processing', style='List Bullet')
doc.add_paragraph('Action: action_start_scm_processing()', style='List Bullet')
doc.add_paragraph('Purpose: SCM officer prepares tender documentation', style='List Bullet')

doc.add_heading('Activities:', level=3)
doc.add_paragraph('Assign SCM officer', style='List Bullet')
doc.add_paragraph('Prepare tender documents (SBD forms)', style='List Bullet')
doc.add_paragraph('Set tender type and procurement method', style='List Bullet')
doc.add_paragraph('Determine preference point system (80/20 or 90/10)', style='List Bullet')
doc.add_paragraph('Configure functionality evaluation criteria', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Complete tender package ready for advertisement')

doc.add_paragraph()

# Step 5: Advertisement/Publication
doc.add_heading('Step 5: Advertisement/Publication', level=1)
doc.add_paragraph('State: advertised', style='List Bullet')
doc.add_paragraph('Action: action_publish_tender()', style='List Bullet')
doc.add_paragraph('Purpose: Publicly advertise tender', style='List Bullet')

doc.add_heading('Requirements:', level=3)
doc.add_paragraph('Advertisement text prepared', style='List Bullet')
doc.add_paragraph('Tender documents attached', style='List Bullet')
doc.add_paragraph('Closing date/time set', style='List Bullet')
doc.add_paragraph('Opening date/time set', style='List Bullet')

doc.add_heading('Activities:', level=3)
doc.add_paragraph('Publish on government platforms (eTender Portal, National Treasury)', style='List Bullet')
doc.add_paragraph('Set publication date', style='List Bullet')
doc.add_paragraph('Generate public access token for tender URL', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Published tender with public access')

doc.add_paragraph()

# Step 6: Briefing Session
doc.add_heading('Step 6: Briefing Session (Optional/Compulsory)', level=1)
doc.add_paragraph('Model: sagovtender.briefing.session', style='List Bullet')
doc.add_paragraph('States: briefing → bid_submission', style='List Bullet')
doc.add_paragraph('Actions: action_start_briefing(), action_schedule_briefing(), action_complete_briefing()', style='List Bullet')
doc.add_paragraph('Purpose: Clarify tender requirements to potential bidders', style='List Bullet')

doc.add_heading('Activities:', level=3)
doc.add_paragraph('Schedule briefing session(s)', style='List Bullet')
doc.add_paragraph('Register attendees', style='List Bullet')
doc.add_paragraph('Conduct site visits (if applicable)', style='List Bullet')
doc.add_paragraph('Record questions and answers', style='List Bullet')
doc.add_paragraph('Mark attendance (compulsory/optional)', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Completed briefing with attendee records and Q&A log')

doc.add_page_break()

# Step 7: Bid Submission Period
doc.add_heading('Step 7: Bid Submission Period', level=1)
doc.add_paragraph('State: bid_submission', style='List Bullet')
doc.add_paragraph('Action: action_open_bid_submission()', style='List Bullet')
doc.add_paragraph('Purpose: Accept bid submissions from suppliers', style='List Bullet')

doc.add_heading('Activities:', level=3)
doc.add_paragraph('Bidders submit bids via portal or physical submission', style='List Bullet')
doc.add_paragraph('Track submission timestamps', style='List Bullet')
doc.add_paragraph('Ensure bids received before closing date/time', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Collection of submitted bids')

doc.add_paragraph()

# Step 8: Bid Opening
doc.add_heading('Step 8: Bid Opening', level=1)
doc.add_paragraph('Model: sagovtender.bid.opening.register', style='List Bullet')
doc.add_paragraph('State: opening', style='List Bullet')
doc.add_paragraph('Actions: action_close_submission(), action_conduct_opening(), action_close_opening()', style='List Bullet')
doc.add_paragraph('Purpose: Publicly open and register all bids', style='List Bullet')

doc.add_heading('Activities:', level=3)
doc.add_paragraph('Create bid opening register', style='List Bullet')
doc.add_paragraph('Record opening date/time', style='List Bullet')
p = doc.add_paragraph('Register each bid with:', style='List Bullet')
doc.add_paragraph('Bidder name', style='List Bullet 2')
doc.add_paragraph('Bid amount', style='List Bullet 2')
doc.add_paragraph('Validity period', style='List Bullet 2')
doc.add_paragraph('Documents submitted', style='List Bullet 2')
doc.add_paragraph('Witness signatures', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Official bid opening register')

doc.add_paragraph()

# Step 9: Compliance Check
doc.add_heading('Step 9: Compliance Check', level=1)
doc.add_paragraph('Model: sagovtender.compliance.check', style='List Bullet')
doc.add_paragraph('State: compliance', style='List Bullet')
doc.add_paragraph('Actions: action_start_sagovcompliance_check(), action_end_sagovcompliance_check()', style='List Bullet')
doc.add_paragraph('Purpose: Verify bidder compliance with mandatory requirements', style='List Bullet')

doc.add_heading('Verification Items:', level=3)
doc.add_paragraph('CSD (Central Supplier Database) registration', style='List Bullet')
doc.add_paragraph('Tax compliance status', style='List Bullet')
doc.add_paragraph('COID (Compensation for Occupational Injuries) registration', style='List Bullet')
doc.add_paragraph('B-BBEE certificate/affidavit', style='List Bullet')
doc.add_paragraph('SBD forms completion (SBD 1, 4, 6.1, 8, 9)', style='List Bullet')
doc.add_paragraph('Company registration documents', style='List Bullet')
doc.add_paragraph('Valid bid guarantee (if required)', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Compliant/non-compliant status for each bid')

doc.add_page_break()

# Step 10: Declaration of Interest
doc.add_heading('Step 10: Declaration of Interest', level=1)
doc.add_paragraph('Model: sagovtender.declaration.interest', style='List Bullet')
doc.add_paragraph('State: declaration', style='List Bullet')
doc.add_paragraph('Action: action_request_declarations()', style='List Bullet')
doc.add_paragraph('Purpose: BEC members declare any conflicts of interest', style='List Bullet')

doc.add_heading('Requirements:', level=3)
doc.add_paragraph('BEC committee assigned', style='List Bullet')
doc.add_paragraph('Each member completes declaration', style='List Bullet')
doc.add_paragraph('Declare relationships with bidders', style='List Bullet')
doc.add_paragraph('Declare financial interests', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Completed declarations from all BEC members')

doc.add_paragraph()

# Step 11: BEC Evaluation
doc.add_heading('Step 11: BEC Evaluation', level=1)
doc.add_paragraph('Model: sagovtender.bid.evaluation', style='List Bullet')
doc.add_paragraph('State: evaluation', style='List Bullet')
doc.add_paragraph('Action: action_start_evaluation()', style='List Bullet')
doc.add_paragraph('Purpose: Bid Evaluation Committee evaluates compliant bids', style='List Bullet')

doc.add_heading('Evaluation Criteria:', level=3)
p = doc.add_paragraph('Functionality (if applicable):', style='List Bullet')
doc.add_paragraph('Technical evaluation against criteria', style='List Bullet 2')
doc.add_paragraph('Minimum threshold (e.g., 70%)', style='List Bullet 2')
doc.add_paragraph('Price Points: 80 or 90 points based on system', style='List Bullet')
doc.add_paragraph('B-BBEE Points: 20 or 10 points based on system', style='List Bullet')

doc.add_heading('Scoring Formula:', level=3)
doc.add_paragraph('80/20: (Lowest Price / Bid Price × 80) + B-BBEE Points', style='List Bullet')
doc.add_paragraph('90/10: (Lowest Price / Bid Price × 90) + B-BBEE Points', style='List Bullet')

doc.add_heading('Activities:', level=3)
doc.add_paragraph('Create evaluation records for compliant bids', style='List Bullet')
doc.add_paragraph('Score functionality (if applicable)', style='List Bullet')
doc.add_paragraph('Calculate price points', style='List Bullet')
doc.add_paragraph('Award B-BBEE points', style='List Bullet')
doc.add_paragraph('Calculate total scores', style='List Bullet')
doc.add_paragraph('Rank bidders', style='List Bullet')
doc.add_paragraph('Prepare BEC report', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('BEC evaluation report with recommended bidder')

doc.add_page_break()

# Step 12: BAC Review
doc.add_heading('Step 12: BAC Review', level=1)
doc.add_paragraph('Model: sagovtender.bac.review', style='List Bullet')
doc.add_paragraph('State: sagovbac_review', style='List Bullet')
doc.add_paragraph('Action: action_send_to_bac()', style='List Bullet')
doc.add_paragraph('Purpose: Bid Adjudication Committee reviews BEC recommendation', style='List Bullet')

doc.add_heading('Requirements:', level=3)
doc.add_paragraph('BEC evaluation completed', style='List Bullet')
doc.add_paragraph('BAC committee assigned', style='List Bullet')

doc.add_heading('BAC Decisions:', level=3)
doc.add_paragraph('Approve: Accept BEC recommendation', style='List Bullet')
doc.add_paragraph('Reject: Reject recommendation', style='List Bullet')
doc.add_paragraph('Refer Back: Send back to BEC for clarification', style='List Bullet')
doc.add_paragraph('Cancel Tender: Cancel entire tender process', style='List Bullet')

doc.add_heading('Activities:', level=3)
doc.add_paragraph('Review BEC report', style='List Bullet')
doc.add_paragraph('Verify evaluation methodology', style='List Bullet')
doc.add_paragraph('Check compliance with regulations', style='List Bullet')
doc.add_paragraph('Make final recommendation', style='List Bullet')
doc.add_paragraph('BAC members sign off', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('BAC decision and recommendation')

doc.add_paragraph()

# Step 13: Tender Award
doc.add_heading('Step 13: Tender Award', level=1)
doc.add_paragraph('Model: sagovtender.award', style='List Bullet')
doc.add_paragraph('State: awarded', style='List Bullet')
doc.add_paragraph('Action: action_award_tender()', style='List Bullet')
doc.add_paragraph('Purpose: Officially award tender to successful bidder', style='List Bullet')

doc.add_heading('Requirements:', level=3)
doc.add_paragraph('BAC approval received', style='List Bullet')
doc.add_paragraph('BAC review completed', style='List Bullet')

doc.add_heading('Activities:', level=3)
doc.add_paragraph('Create award record', style='List Bullet')
doc.add_paragraph('Specify awarded partner', style='List Bullet')
doc.add_paragraph('Record award value', style='List Bullet')
doc.add_paragraph('Set award date', style='List Bullet')
doc.add_paragraph('Generate award letter', style='List Bullet')
doc.add_paragraph('Notify successful bidder', style='List Bullet')
doc.add_paragraph('Notify unsuccessful bidders', style='List Bullet')
doc.add_paragraph('Create purchase order (optional integration)', style='List Bullet')

doc.add_heading('Output:', level=3)
doc.add_paragraph('Tender award with purchase order')

doc.add_page_break()

# Additional States
doc.add_heading('Additional States', level=1)
doc.add_paragraph('Cancelled: Tender cancelled at any stage (reason recorded)', style='List Bullet')
doc.add_paragraph('Rejected: Tender rejected during approval process', style='List Bullet')

doc.add_paragraph()

# Key Supporting Models
doc.add_heading('Key Supporting Models', level=1)
doc.add_paragraph('Committees (sagovtender.committee): BEC and BAC committee management', style='List Bullet')
doc.add_paragraph('Documents (sagovtender.document): Tender document management', style='List Bullet')
doc.add_paragraph('Bids (sagovtender.bid): Individual bid submissions', style='List Bullet')
doc.add_paragraph('Partners (res.partner): Supplier/bidder information with compliance fields', style='List Bullet')

doc.add_paragraph()

# Compliance Framework
doc.add_heading('Compliance Framework', level=1)
doc.add_paragraph('Constitution Section 217', style='List Bullet')
doc.add_paragraph('PFMA (Public Finance Management Act)', style='List Bullet')
doc.add_paragraph('MFMA (Municipal Finance Management Act)', style='List Bullet')
doc.add_paragraph('PPPFA (Preferential Procurement Policy Framework Act)', style='List Bullet')
doc.add_paragraph('B-BBEE Act', style='List Bullet')
doc.add_paragraph('National Treasury Regulations', style='List Bullet')

doc.add_page_break()

# Process Flow Summary Table
doc.add_heading('Process Flow Summary', level=1)

table = doc.add_table(rows=15, cols=4)
table.style = 'Light Grid Accent 1'

# Header row
header_cells = table.rows[0].cells
header_cells[0].text = 'Step'
header_cells[1].text = 'Stage'
header_cells[2].text = 'Model'
header_cells[3].text = 'State'

# Data rows
data = [
    ['0', 'Annual Procurement Plan', 'sagovtender.annual.procurement.plan', 'draft → approved'],
    ['1', 'Purchase Requisition', 'sagovtender.purchase.requisition', 'draft → approved'],
    ['2', 'Budget Confirmation', 'sagovtender.budget.confirm', 'draft → confirmed'],
    ['3', 'Specification Development', 'sagovtender.specification', 'draft → approved'],
    ['4', 'SCM Processing', 'sagovtender.tender', 'scm_processing'],
    ['5', 'Advertisement/Publication', 'sagovtender.tender', 'advertised'],
    ['6', 'Briefing Session', 'sagovtender.briefing.session', 'briefing'],
    ['7', 'Bid Submission Period', 'sagovtender.tender', 'bid_submission'],
    ['8', 'Bid Opening', 'sagovtender.bid.opening.register', 'opening'],
    ['9', 'Compliance Check', 'sagovtender.compliance.check', 'compliance'],
    ['10', 'Declaration of Interest', 'sagovtender.declaration.interest', 'declaration'],
    ['11', 'BEC Evaluation', 'sagovtender.bid.evaluation', 'evaluation'],
    ['12', 'BAC Review', 'sagovtender.bac.review', 'sagovbac_review'],
    ['13', 'Tender Award', 'sagovtender.award', 'awarded'],
]

for i, row_data in enumerate(data, start=1):
    cells = table.rows[i].cells
    for j, cell_data in enumerate(row_data):
        cells[j].text = cell_data

# Save document
doc.save('SA_Government_Tender_Process_Flow.docx')
print("Document created successfully: SA_Government_Tender_Process_Flow.docx")
