#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Create figure with larger size for better visibility
fig, ax = plt.subplots(figsize=(20, 28))
ax.set_xlim(0, 10)
ax.set_ylim(0, 30)
ax.axis('off')

# Define colors for different phases
color_planning = '#E8F4F8'  # Light blue
color_preparation = '#FFF4E6'  # Light orange
color_submission = '#E8F5E9'  # Light green
color_evaluation = '#F3E5F5'  # Light purple
color_award = '#FFEBEE'  # Light red
color_decision = '#FFF9C4'  # Light yellow

# Title
title = ax.text(5, 29, 'SA Government Tender Management System\nProcess Flow Diagram', 
                ha='center', va='top', fontsize=20, fontweight='bold')

# Helper function to create process boxes
def create_box(ax, x, y, width, height, text, color, step_num=''):
    box = FancyBboxPatch((x, y), width, height, 
                         boxstyle="round,pad=0.1", 
                         edgecolor='black', 
                         facecolor=color, 
                         linewidth=2)
    ax.add_patch(box)
    
    if step_num:
        ax.text(x + 0.3, y + height - 0.3, step_num, 
                fontsize=10, fontweight='bold', 
                bbox=dict(boxstyle='circle', facecolor='white', edgecolor='black'))
    
    ax.text(x + width/2, y + height/2, text, 
            ha='center', va='center', fontsize=10, fontweight='bold', wrap=True)

# Helper function to create arrows
def create_arrow(ax, x1, y1, x2, y2, label=''):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=20, 
                           linewidth=2, color='black')
    ax.add_patch(arrow)
    
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, fontsize=8, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Helper function for decision diamonds
def create_decision(ax, x, y, size, text, color):
    diamond = mpatches.FancyBboxPatch((x - size/2, y - size/2), size, size,
                                     boxstyle="round,pad=0.05",
                                     transform=ax.transData,
                                     edgecolor='black',
                                     facecolor=color,
                                     linewidth=2)
    # Rotate to make diamond
    t = mpatches.transforms.Affine2D().rotate_deg_around(x, y, 45) + ax.transData
    diamond.set_transform(t)
    ax.add_patch(diamond)
    
    ax.text(x, y, text, ha='center', va='center', 
            fontsize=9, fontweight='bold', wrap=True)

# PHASE 1: PLANNING & INITIATION
phase_y = 27
ax.text(5, phase_y, '═══ PHASE 1: PLANNING & INITIATION ═══', 
        ha='center', fontsize=12, fontweight='bold', 
        bbox=dict(boxstyle='round', facecolor=color_planning, edgecolor='black', linewidth=2))

# Step 0: Annual Procurement Plan
create_box(ax, 0.5, 24.5, 2, 1.5, 'Step 0:\nAnnual Procurement\nPlan (APP)', color_planning, '0')
ax.text(0.5, 23.8, 'Model: sagovtender.annual.procurement.plan\nState: draft → approved', 
        fontsize=7, style='italic')

# Step 1: Purchase Requisition
create_box(ax, 3.5, 24.5, 2, 1.5, 'Step 1:\nPurchase\nRequisition', color_planning, '1')
ax.text(3.5, 23.8, 'Model: sagovtender.purchase.requisition\nState: draft → approved', 
        fontsize=7, style='italic')

# Step 2: Budget Confirmation
create_box(ax, 6.5, 24.5, 2, 1.5, 'Step 2:\nBudget\nConfirmation', color_planning, '2')
ax.text(6.5, 23.8, 'Model: sagovtender.budget.confirm\nState: draft → confirmed', 
        fontsize=7, style='italic')

# Arrows for Phase 1
create_arrow(ax, 2.5, 25.25, 3.5, 25.25)
create_arrow(ax, 5.5, 25.25, 6.5, 25.25)

# PHASE 2: PREPARATION
phase_y = 22.5
ax.text(5, phase_y, '═══ PHASE 2: PREPARATION ═══', 
        ha='center', fontsize=12, fontweight='bold', 
        bbox=dict(boxstyle='round', facecolor=color_preparation, edgecolor='black', linewidth=2))

# Step 3: Specification Development
create_box(ax, 0.5, 20, 2, 1.5, 'Step 3:\nSpecification\nDevelopment', color_preparation, '3')
ax.text(0.5, 19.3, 'Model: sagovtender.specification\nState: draft → approved', 
        fontsize=7, style='italic')

# Step 4: SCM Processing
create_box(ax, 3.5, 20, 2, 1.5, 'Step 4:\nSCM Processing\n& Documentation', color_preparation, '4')
ax.text(3.5, 19.3, 'Model: sagovtender.tender\nState: scm_processing', 
        fontsize=7, style='italic')

# Step 5: Advertisement
create_box(ax, 6.5, 20, 2, 1.5, 'Step 5:\nAdvertisement/\nPublication', color_preparation, '5')
ax.text(6.5, 19.3, 'Model: sagovtender.tender\nState: advertised', 
        fontsize=7, style='italic')

# Arrows for Phase 2
create_arrow(ax, 1.5, 23.8, 1.5, 21.5)
create_arrow(ax, 2.5, 20.75, 3.5, 20.75)
create_arrow(ax, 5.5, 20.75, 6.5, 20.75)

# PHASE 3: BID SUBMISSION
phase_y = 18
ax.text(5, phase_y, '═══ PHASE 3: BID SUBMISSION ═══', 
        ha='center', fontsize=12, fontweight='bold', 
        bbox=dict(boxstyle='round', facecolor=color_submission, edgecolor='black', linewidth=2))

# Decision: Briefing Required?
create_decision(ax, 2, 16, 1.5, 'Briefing\nRequired?', color_decision)
ax.text(2.8, 16, 'Yes', fontsize=8, fontweight='bold')
ax.text(1.2, 15.2, 'No', fontsize=8, fontweight='bold')

# Step 6: Briefing Session
create_box(ax, 3.5, 15.5, 2, 1.5, 'Step 6:\nBriefing Session\n(Optional)', color_submission, '6')
ax.text(3.5, 14.8, 'Model: sagovtender.briefing.session\nState: briefing', 
        fontsize=7, style='italic')

# Step 7: Bid Submission Period
create_box(ax, 0.5, 13.5, 2, 1.5, 'Step 7:\nBid Submission\nPeriod', color_submission, '7')
ax.text(0.5, 12.8, 'Model: sagovtender.tender\nState: bid_submission', 
        fontsize=7, style='italic')

# Step 8: Bid Opening
create_box(ax, 3.5, 13.5, 2, 1.5, 'Step 8:\nBid Opening\nRegister', color_submission, '8')
ax.text(3.5, 12.8, 'Model: sagovtender.bid.opening.register\nState: opening', 
        fontsize=7, style='italic')

# Arrows for Phase 3
create_arrow(ax, 7.5, 20, 7.5, 16.5)
create_arrow(ax, 7.5, 16.5, 2.7, 16.5)
create_arrow(ax, 2.7, 16, 3.5, 16.25)
create_arrow(ax, 2, 15.2, 1.5, 15)
create_arrow(ax, 5.5, 16.25, 6.5, 16.25)
create_arrow(ax, 6.5, 16.25, 6.5, 14.25)
create_arrow(ax, 6.5, 14.25, 2.5, 14.25)
create_arrow(ax, 1.5, 15, 1.5, 13.5)
create_arrow(ax, 2.5, 14.25, 3.5, 14.25)

# PHASE 4: COMPLIANCE & EVALUATION
phase_y = 11.5
ax.text(5, phase_y, '═══ PHASE 4: COMPLIANCE & EVALUATION ═══', 
        ha='center', fontsize=12, fontweight='bold', 
        bbox=dict(boxstyle='round', facecolor=color_evaluation, edgecolor='black', linewidth=2))

# Step 9: Compliance Check
create_box(ax, 0.5, 9, 2, 1.5, 'Step 9:\nCompliance\nCheck', color_evaluation, '9')
ax.text(0.5, 8.3, 'Model: sagovtender.compliance.check\nState: compliance', 
        fontsize=7, style='italic')

# Step 10: Declaration of Interest
create_box(ax, 3.5, 9, 2, 1.5, 'Step 10:\nDeclaration of\nInterest', color_evaluation, '10')
ax.text(3.5, 8.3, 'Model: sagovtender.declaration.interest\nState: declaration', 
        fontsize=7, style='italic')

# Step 11: BEC Evaluation
create_box(ax, 6.5, 9, 2, 1.5, 'Step 11:\nBEC Evaluation\n(Scoring)', color_evaluation, '11')
ax.text(6.5, 8.3, 'Model: sagovtender.bid.evaluation\nState: evaluation', 
        fontsize=7, style='italic')

# Arrows for Phase 4
create_arrow(ax, 4.5, 13.5, 4.5, 11)
create_arrow(ax, 4.5, 11, 1.5, 11)
create_arrow(ax, 1.5, 11, 1.5, 10.5)
create_arrow(ax, 2.5, 9.75, 3.5, 9.75)
create_arrow(ax, 5.5, 9.75, 6.5, 9.75)

# PHASE 5: ADJUDICATION & AWARD
phase_y = 7
ax.text(5, phase_y, '═══ PHASE 5: ADJUDICATION & AWARD ═══', 
        ha='center', fontsize=12, fontweight='bold', 
        bbox=dict(boxstyle='round', facecolor=color_award, edgecolor='black', linewidth=2))

# Step 12: BAC Review
create_box(ax, 1.5, 4.5, 2.5, 1.5, 'Step 12:\nBAC Review\n& Decision', color_award, '12')
ax.text(1.5, 3.8, 'Model: sagovtender.bac.review\nState: sagovbac_review', 
        fontsize=7, style='italic')

# BAC Decision Diamond
create_decision(ax, 5.5, 5.25, 1.5, 'BAC\nDecision', color_decision)

# Step 13: Tender Award
create_box(ax, 4, 2, 3, 1.5, 'Step 13:\nTender Award\n& Purchase Order', color_award, '13')
ax.text(4, 1.3, 'Model: sagovtender.award\nState: awarded', 
        fontsize=7, style='italic')

# Cancelled/Rejected boxes
create_box(ax, 7.5, 5, 1.5, 0.8, 'Cancelled', '#FFCDD2')
create_box(ax, 7.5, 3.5, 1.5, 0.8, 'Rejected', '#FFCDD2')
create_box(ax, 7.5, 2, 1.5, 0.8, 'Refer Back\nto BEC', '#FFE082')

# Arrows for Phase 5
create_arrow(ax, 7.5, 9, 7.5, 6)
create_arrow(ax, 7.5, 6, 2.75, 6)
create_arrow(ax, 2.75, 6, 2.75, 6)
create_arrow(ax, 4, 5.25, 5, 5.25)
create_arrow(ax, 6, 5.25, 5.5, 3.5, 'Approve')
create_arrow(ax, 6.2, 5.5, 7.5, 5.4)
create_arrow(ax, 6.2, 5, 7.5, 3.9)
create_arrow(ax, 6, 4.8, 7.5, 2.4)

# Final arrow to completion
create_arrow(ax, 5.5, 2, 5.5, 0.5)

# Completion box
create_box(ax, 4, 0.2, 3, 0.8, 'TENDER COMPLETED', '#C8E6C9')

# Add legend
legend_elements = [
    mpatches.Patch(facecolor=color_planning, edgecolor='black', label='Planning & Initiation'),
    mpatches.Patch(facecolor=color_preparation, edgecolor='black', label='Preparation'),
    mpatches.Patch(facecolor=color_submission, edgecolor='black', label='Bid Submission'),
    mpatches.Patch(facecolor=color_evaluation, edgecolor='black', label='Compliance & Evaluation'),
    mpatches.Patch(facecolor=color_award, edgecolor='black', label='Adjudication & Award'),
    mpatches.Patch(facecolor=color_decision, edgecolor='black', label='Decision Point'),
]

ax.legend(handles=legend_elements, loc='upper right', fontsize=9, 
         title='Process Phases', title_fontsize=10)

# Add compliance note
compliance_text = ('Compliant with: PFMA | MFMA | PPPFA | B-BBEE Act | '
                  'National Treasury Regulations | Constitution Section 217')
ax.text(5, -0.5, compliance_text, ha='center', fontsize=8, style='italic',
       bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# Adjust layout and save
plt.tight_layout()
plt.savefig('SA_Government_Tender_Process_Flow_Diagram.png', dpi=300, bbox_inches='tight')
print("Process flow diagram created successfully: SA_Government_Tender_Process_Flow_Diagram.png")

# Also save as PDF for better quality
plt.savefig('SA_Government_Tender_Process_Flow_Diagram.pdf', bbox_inches='tight')
print("Process flow diagram created successfully: SA_Government_Tender_Process_Flow_Diagram.pdf")

plt.close()
