# -*- coding: utf-8 -*-
"""
Generate comprehensive User Guide Word document for xf_partner_contract module.
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
import copy

# ─── Colour palette ───────────────────────────────────────────────────────────
DARK_BLUE   = RGBColor(0x1F, 0x39, 0x64)   # headings
MID_BLUE    = RGBColor(0x2E, 0x74, 0xB5)   # sub-headings / accents
LIGHT_BLUE  = RGBColor(0xBD, 0xD7, 0xEE)   # table header fill
GREEN       = RGBColor(0x37, 0x86, 0x30)
ORANGE      = RGBColor(0xED, 0x7D, 0x31)
RED         = RGBColor(0xC0, 0x00, 0x00)
GREY_TEXT   = RGBColor(0x40, 0x40, 0x40)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
YELLOW_BG   = RGBColor(0xFF, 0xFF, 0xCC)
LIGHT_GREEN = RGBColor(0xE2, 0xEF, 0xDA)
LIGHT_RED   = RGBColor(0xFF, 0xE5, 0xE5)
LIGHT_GREY  = RGBColor(0xF2, 0xF2, 0xF2)

# ─── Low-level XML helpers ─────────────────────────────────────────────────────
def set_cell_bg(cell, hex_color: str):
    """Set cell background colour using hex string e.g. '2E74B5'."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)


def set_cell_border(cell, **kwargs):
    """Set borders on a table cell. kwargs: top, bottom, left, right each = dict."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        tag = OxmlElement(f'w:{edge}')
        if edge in kwargs:
            tag.set(qn('w:val'),   kwargs[edge].get('val',   'single'))
            tag.set(qn('w:sz'),    kwargs[edge].get('sz',    '4'))
            tag.set(qn('w:space'), kwargs[edge].get('space', '0'))
            tag.set(qn('w:color'), kwargs[edge].get('color', 'auto'))
        else:
            tag.set(qn('w:val'), 'none')
        tcBorders.append(tag)
    tcPr.append(tcBorders)


def set_paragraph_border_bottom(paragraph, color='2E74B5', sz='12'):
    pPr  = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    sz)
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), color)
    pBdr.append(bot)
    pPr.append(pBdr)


def add_page_break(doc):
    doc.add_page_break()


def shade_row(row, hex_color: str):
    for cell in row.cells:
        set_cell_bg(cell, hex_color)


# ─── Style helpers ─────────────────────────────────────────────────────────────
def style_run(run, bold=False, italic=False, size=None, color=None, underline=False):
    run.bold      = bold
    run.italic    = italic
    run.underline = underline
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color


def add_heading(doc, text, level=1, color=DARK_BLUE, size=None):
    """Add a styled heading with coloured text."""
    h = doc.add_heading(text, level=level)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in h.runs:
        run.font.color.rgb = color
        if size:
            run.font.size = Pt(size)
    return h


def add_body(doc, text, bold=False, italic=False, color=None, size=11,
             indent=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.space_before = Pt(2)
    if indent is not None:
        p.paragraph_format.left_indent = Cm(indent)
    run = p.add_run(text)
    style_run(run, bold=bold, italic=italic, size=size, color=color)
    return p


def add_bullet(doc, text, level=0, bold_prefix=None, color=None):
    style = 'List Bullet' if level == 0 else 'List Bullet 2'
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.space_before = Pt(1)
    if bold_prefix:
        r1 = p.add_run(bold_prefix + ': ')
        style_run(r1, bold=True, size=10.5, color=DARK_BLUE)
    r2 = p.add_run(text)
    style_run(r2, size=10.5, color=color or GREY_TEXT)
    return p


def add_numbered(doc, text, level=0):
    style = 'List Number' if level == 0 else 'List Number 2'
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.space_before = Pt(1)
    run = p.add_run(text)
    style_run(run, size=10.5, color=GREY_TEXT)
    return p


def add_note(doc, text, label='NOTE', bg='FFFACD'):
    """Add a highlighted note / tip box."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = 'Table Grid'
    cell = tbl.cell(0, 0)
    set_cell_bg(cell, bg)
    p = cell.paragraphs[0]
    r1 = p.add_run(f'  {label}: ')
    style_run(r1, bold=True, size=10, color=DARK_BLUE)
    r2 = p.add_run(text)
    style_run(r2, size=10, color=GREY_TEXT)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    doc.add_paragraph()


def add_step_box(doc, step_no, title, instructions):
    """Add a numbered step box with title + instructions list."""
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = 'Table Grid'
    tbl.columns[0].width = Cm(1.6)
    tbl.columns[1].width = Cm(14.8)

    # Left cell – step number
    left = tbl.cell(0, 0)
    set_cell_bg(left, '1F3964')
    left.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = left.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f'STEP\n{step_no}')
    style_run(r, bold=True, size=11, color=WHITE)

    # Right cell – content
    right = tbl.cell(0, 1)
    set_cell_bg(right, 'EBF3FB')
    p = right.paragraphs[0]
    r = p.add_run(title)
    style_run(r, bold=True, size=11, color=DARK_BLUE)
    for inst in instructions:
        ip = right.add_paragraph(style='List Bullet')
        ip.paragraph_format.space_after  = Pt(2)
        ip.paragraph_format.space_before = Pt(0)
        ip.paragraph_format.left_indent  = Cm(0.4)
        ir = ip.add_run(inst)
        style_run(ir, size=10, color=GREY_TEXT)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


# ─── Table builder ─────────────────────────────────────────────────────────────
def add_styled_table(doc, headers, rows, col_widths=None):
    tbl = doc.add_table(rows=1+len(rows), cols=len(headers))
    tbl.style = 'Table Grid'

    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_bg(hdr_cells[i], '1F3964')
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        style_run(r, bold=True, size=10, color=WHITE)

    # Data rows
    for ri, row_data in enumerate(rows):
        row_cells = tbl.rows[ri+1].cells
        bg = 'F2F2F2' if ri % 2 == 0 else 'FFFFFF'
        for ci, cell_text in enumerate(row_data):
            set_cell_bg(row_cells[ci], bg)
            p = row_cells[ci].paragraphs[0]
            r = p.add_run(str(cell_text))
            style_run(r, size=9.5, color=GREY_TEXT)

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in tbl.rows:
                row.cells[i].width = Cm(w)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return tbl


# ─── BPMN-style swimlane table ─────────────────────────────────────────────────
def add_bpmn_swimlane(doc, title, lanes):
    """
    lanes = list of (actor, [list_of_step_strings])
    Renders a two-column swimlane table.
    """
    add_heading(doc, title, level=2, color=MID_BLUE)

    tbl = doc.add_table(rows=len(lanes)+1, cols=2)
    tbl.style = 'Table Grid'
    tbl.columns[0].width = Cm(4)
    tbl.columns[1].width = Cm(12.4)

    # Header
    set_cell_bg(tbl.cell(0, 0), '1F3964')
    set_cell_bg(tbl.cell(0, 1), '1F3964')
    p0 = tbl.cell(0, 0).paragraphs[0]
    r0 = p0.add_run('Actor / Role')
    style_run(r0, bold=True, size=10, color=WHITE)
    p1 = tbl.cell(0, 1).paragraphs[0]
    r1 = p1.add_run('Process Steps')
    style_run(r1, bold=True, size=10, color=WHITE)

    lane_colors = ['EBF3FB', 'E2EFD9', 'FFF2CC', 'FCE4D6', 'EDEDED']
    arrow = '  \u27a4  '   # ➤

    for li, (actor, steps) in enumerate(lanes):
        row = tbl.rows[li+1]
        bg  = lane_colors[li % len(lane_colors)]

        # Actor cell
        ac = row.cells[0]
        set_cell_bg(ac, bg)
        ac.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        ap = ac.paragraphs[0]
        ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ar = ap.add_run(actor)
        style_run(ar, bold=True, size=10, color=DARK_BLUE)

        # Steps cell
        sc = row.cells[1]
        set_cell_bg(sc, bg)
        for si, step in enumerate(steps):
            if si == 0:
                sp = sc.paragraphs[0]
            else:
                sp = sc.add_paragraph()
            sp.paragraph_format.space_after  = Pt(2)
            sp.paragraph_format.space_before = Pt(2)
            # Prefix with arrow and step number
            sr = sp.add_run(f'{si+1}. {step}')
            style_run(sr, size=9.5, color=GREY_TEXT)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)


def add_flow_diagram(doc, title, nodes):
    """
    A simple horizontal flow strip.
    nodes = list of (label, color_hex, shape_hint)
    """
    add_body(doc, title, bold=True, color=DARK_BLUE, size=11)

    tbl = doc.add_table(rows=1, cols=len(nodes)*2-1)
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    node_w = 2.5
    arr_w  = 0.6
    idx = 0
    for ni, (label, color, _) in enumerate(nodes):
        cell = tbl.cell(0, idx)
        cell.width = Cm(node_w)
        set_cell_bg(cell, color)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(label)
        style_run(r, bold=True, size=9, color=WHITE)
        idx += 1
        if ni < len(nodes)-1:
            arr_cell = tbl.cell(0, idx)
            arr_cell.width = Cm(arr_w)
            set_cell_bg(arr_cell, 'FFFFFF')
            arr_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            ap = arr_cell.paragraphs[0]
            ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ar = ap.add_run('\u27a4')
            style_run(ar, bold=True, size=12, color=DARK_BLUE)
            idx += 1

    doc.add_paragraph().paragraph_format.space_after = Pt(6)


# ─── Screenshot placeholder ────────────────────────────────────────────────────
def add_screenshot_placeholder(doc, caption, path=None):
    """Insert existing screenshot or a labelled placeholder box."""
    if path and os.path.exists(path):
        doc.add_picture(path, width=Inches(5.5))
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        tbl = doc.add_table(rows=1, cols=1)
        tbl.style = 'Table Grid'
        cell = tbl.cell(0, 0)
        set_cell_bg(cell, 'D9E1F2')
        cell.width = Cm(14)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(f'[Screenshot: {caption}]')
        style_run(r, italic=True, size=9.5, color=MID_BLUE)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after  = Pt(10)

    cap_p = doc.add_paragraph()
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_p.paragraph_format.space_after = Pt(10)
    cr = cap_p.add_run(f'Figure: {caption}')
    style_run(cr, italic=True, size=9, color=GREY_TEXT)


# ══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT GENERATION
# ══════════════════════════════════════════════════════════════════════════════
def build_document():
    doc = Document()

    # ── Page margins ────────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.0)

    # ════════════════════════════════════════════════════════════════════════
    #  COVER PAGE
    # ════════════════════════════════════════════════════════════════════════
    doc.add_paragraph('\n\n')

    cover_title = doc.add_paragraph()
    cover_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ct = cover_title.add_run('CONTRACT MANAGEMENT SYSTEM')
    style_run(ct, bold=True, size=28, color=DARK_BLUE)

    cover_sub = doc.add_paragraph()
    cover_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cs = cover_sub.add_run('User Guide & Process Manual')
    style_run(cs, bold=True, size=20, color=MID_BLUE)

    doc.add_paragraph('\n')

    cover_line = doc.add_paragraph()
    cover_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_border_bottom(cover_line, color='2E74B5', sz='24')

    doc.add_paragraph('\n')

    for label, value in [
        ('System',    'Odoo – xf_partner_contract Module'),
        ('Version',   '17.0'),
        ('Audience',  'Contract Users · Team Leaders · Managers · Approvers'),
        ('Date',      'March 2026'),
        ('Prepared by', 'ECDHS System Administration'),
    ]:
        lp = doc.add_paragraph()
        lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        lr = lp.add_run(f'{label}:  ')
        style_run(lr, bold=True, size=12, color=DARK_BLUE)
        vr = lp.add_run(value)
        style_run(vr, size=12, color=GREY_TEXT)

    doc.add_paragraph('\n\n\n')
    add_note(doc,
             'This document is intended for internal use only. It provides '
             'step-by-step instructions for every user role within the Odoo '
             'Contract Management module. No prior Odoo experience is assumed.',
             label='IMPORTANT', bg='FFF2CC')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  TABLE OF CONTENTS (manual)
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, 'Table of Contents', level=1)

    toc_entries = [
        ('1.', 'Introduction & System Overview',                         2),
        ('2.', 'Getting Started with Odoo',                              2),
        ('3.', 'User Roles & Permissions',                               3),
        ('4.', 'System Configuration (Administrator / Manager)',         4),
        ('5.', 'BPMN Process Flowcharts',                                6),
        ('  5.1', 'Contract Lifecycle – Master Flow',                    6),
        ('  5.2', 'Contract Creation Process',                           6),
        ('  5.3', 'Contract Approval Process',                           7),
        ('  5.4', 'Invoice / Bill Generation Process',                   7),
        ('  5.5', 'Contract Renewal & Closure Process',                  7),
        ('6.', 'User Guide – Contract User',                             8),
        ('  6.1', 'Navigating to Contracts',                             8),
        ('  6.2', 'Creating a New Contract',                             8),
        ('  6.3', 'Uploading Supporting Documents',                      10),
        ('  6.4', 'Adding Bill of Quantities / Deliverables',            10),
        ('  6.5', 'Confirming (Submitting) a Contract',                  11),
        ('  6.6', 'Viewing and Tracking Contracts',                      11),
        ('7.', 'User Guide – Approver',                                  12),
        ('  7.1', 'Receiving an Approval Request',                       12),
        ('  7.2', 'Reviewing the Contract',                              12),
        ('  7.3', 'Approving a Contract',                                13),
        ('  7.4', 'Returning a Contract for Correction',                 13),
        ('8.', 'User Guide – Team Leader',                               14),
        ('  8.1', 'Creating & Managing Approval Teams',                  14),
        ('  8.2', 'Configuring Approver Rules',                          15),
        ('9.', 'User Guide – Manager / Administrator',                   16),
        ('  9.1', 'Module Settings',                                     16),
        ('  9.2', 'Managing Contracts in Bulk',                          16),
        ('  9.3', 'Cancelling or Closing Contracts',                     17),
        ('10.', 'Invoice & Billing Workflow',                            18),
        ('11.', 'Contract Renewal Workflow',                             19),
        ('12.', 'Email Notifications Reference',                         20),
        ('13.', 'Troubleshooting & FAQs',                                21),
        ('14.', 'Glossary',                                              22),
    ]

    for num, entry, _ in toc_entries:
        tp = doc.add_paragraph()
        tp.paragraph_format.space_after  = Pt(3)
        tp.paragraph_format.space_before = Pt(1)
        nt = tp.add_run(f'{num}  {entry}')
        style_run(nt, size=10.5, color=GREY_TEXT,
                  bold=('.' in num and num.count('.') == 1 and '  ' not in num))

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 1 – INTRODUCTION
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '1.  Introduction & System Overview', level=1)
    add_body(doc,
        'The Contract Management module (xf_partner_contract) is a custom Odoo '
        'application built to manage the full lifecycle of contracts between your '
        'organisation and its vendors, service providers, or customers. It supports '
        'multiple contract types, a configurable multi-level approval workflow, '
        'invoice/bill generation linked directly to contract lines, and a document '
        'repository for storing contract-related files.',
        size=11, color=GREY_TEXT)

    add_heading(doc, 'What Can You Do in This Module?', level=2, color=MID_BLUE)
    bullets = [
        ('Create & manage contracts', 'Draft contracts for Sale, Purchase, Funding Agreement, Service Level Agreements, MOUs, Deeds of Sale, and more.'),
        ('Route contracts for approval', 'Assign approval teams with sequential approvers, configurable by amount thresholds and custom business rules.'),
        ('Track contract status', 'Monitor contracts through states: Draft → Approval → Running → To Renew → Expired → Closed / Cancelled.'),
        ('Generate invoices & bills', 'Create customer invoices (for Sale contracts) or vendor bills (for Purchase contracts) directly from a running contract.'),
        ('Upload supporting documents', 'Attach Appointment Letters, Acceptance Letters, SLA documents, Variation Orders, Completion Certificates, and more.'),
        ('Receive email notifications', 'Automated emails notify approvers and responsible users at each workflow step.'),
        ('Search, filter & group', 'Use the list, kanban, or search views to quickly locate contracts by partner, type, state, region, etc.'),
    ]
    for bold, text in bullets:
        add_bullet(doc, text, bold_prefix=bold)

    add_heading(doc, 'Contract Types Supported', level=2, color=MID_BLUE)
    add_styled_table(doc,
        headers=['Contract Type', 'Description'],
        rows=[
            ['Sale',                     'Contracts where your organisation sells goods or services to a customer.'],
            ['Purchase',                 'Contracts where your organisation buys goods or services from a vendor.'],
            ['Funding Agreement',        'Grant or funding agreements with donors or government bodies.'],
            ['Addendum to Funding Agmt', 'Amendments or extensions to an existing Funding Agreement.'],
            ['Cession for Payment',      'Assignment of payment rights to a third party.'],
            ['Notice of Default',        'Formal notice issued when a party is in breach of contract terms.'],
            ['Termination',              'Formal contract termination documentation.'],
            ['Service Level Agreement',  'SLA governing the quality and delivery standards of services.'],
            ['Deed of Sale',             'Legal deed used to transfer ownership of an asset.'],
            ['MOU',                      'Memorandum of Understanding – a non-binding agreement of intent.'],
        ],
        col_widths=[5, 11.4]
    )

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 2 – GETTING STARTED WITH ODOO
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '2.  Getting Started with Odoo', level=1)
    add_body(doc,
        'If you have never used Odoo before, this section will walk you through '
        'the basics of logging in and navigating to the Contract Management module.',
        size=11, color=GREY_TEXT)

    add_heading(doc, '2.1  Logging In', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Open your web browser',
        ['Open Google Chrome, Microsoft Edge, or Mozilla Firefox.',
         'Type the Odoo URL provided by your system administrator into the address bar '
         '(e.g. https://your-company.odoo.com) and press Enter.'])
    add_step_box(doc, 2, 'Enter your credentials',
        ['On the login screen you will see two fields: Email Address and Password.',
         'Type your work email address in the Email field.',
         'Type your password in the Password field.',
         'Click the blue Log in button.'])
    add_screenshot_placeholder(doc, 'Odoo Login Screen')
    add_step_box(doc, 3, 'Odoo Home / App Menu',
        ['After a successful login you will land on the Odoo home screen.',
         'The home screen shows coloured tiles representing all installed applications.',
         'Look for the tile labelled "Contract Management" (it has a document icon).'])
    add_note(doc,
             'If you cannot see the Contract Management tile, contact your system '
             'administrator – you may need to be assigned the correct user role.',
             label='NOTE', bg='FFF2CC')

    add_heading(doc, '2.2  Understanding the Odoo Interface', level=2, color=MID_BLUE)
    add_body(doc, 'Every Odoo screen shares the same layout. The key areas are:', size=11, color=GREY_TEXT)
    add_styled_table(doc,
        headers=['Area', 'Location on Screen', 'Purpose'],
        rows=[
            ['Top Navigation Bar',   'Very top of every page',             'App switcher, search bar, notifications, user menu.'],
            ['Menu Bar',             'Horizontal bar just below the top',  'Module-level menus: Contracts, Configuration, etc.'],
            ['Action Buttons',       'Top of a form, highlighted in blue', 'Confirm, Approve, Create Invoice, etc.'],
            ['Status Bar',           'Top-right of a form',                'Shows the current state (Draft, Running, etc.).'],
            ['Form Fields',          'Body of a form',                     'All the data fields you fill in.'],
            ['Notebook Tabs',        'Tabbed area in the lower form body', 'Lines, Terms, Approval, Documents, Invoices, etc.'],
            ['Chatter / Log',        'Bottom of a form',                   'Message thread, activity log, and change history.'],
            ['List View Icon',       'Top-right of a list page',           'Switch between List ≡ and Kanban ▦ views.'],
        ],
        col_widths=[4, 5, 7.4]
    )
    add_screenshot_placeholder(doc, 'Odoo Contract Form – Annotated Interface Overview')

    add_heading(doc, '2.3  Navigating to Contract Management', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Click the App Switcher (grid icon)',
        ['Look at the very top-left corner of the screen.',
         'Click the small grid / waffle icon (☰) to open the App Menu.'])
    add_step_box(doc, 2, 'Select Contract Management',
        ['Scroll through the app tiles until you find "Contract Management".',
         'Click on it. The module will open and you will see the Contracts list.'])
    add_step_box(doc, 3, 'Explore the module menus',
        ['You will see a menu bar at the top: Contracts | Configuration.',
         '"Contracts" lists all contracts you have access to.',
         '"Configuration" (visible to Team Leaders and Managers) contains Settings and Approval Teams.'])
    add_screenshot_placeholder(doc, 'Contract Management Module Home – List View')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 3 – USER ROLES & PERMISSIONS
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '3.  User Roles & Permissions', level=1)
    add_body(doc,
        'The Contract Management module uses three distinct roles. Each role '
        'inherits all permissions of the role below it.',
        size=11, color=GREY_TEXT)

    add_styled_table(doc,
        headers=['Role', 'Who Uses It', 'Key Permissions'],
        rows=[
            ['Contract User',
             'Staff responsible for creating and managing contracts (e.g. procurement officers, project managers)',
             'Create, edit, view, and delete own contracts. Submit for approval. View approval status. Generate invoices/bills from running contracts.'],
            ['Team Leader',
             'Senior staff who lead approval teams (e.g. departmental managers, supply chain managers)',
             'All User permissions PLUS: Create and configure Approval Teams. Add approvers to teams. Define approval rules (amount thresholds, custom conditions).'],
            ['Manager / Administrator',
             'System administrator or module owner',
             'All Team Leader permissions PLUS: Access System Settings. Configure approval mode (None / Optional / Required). Manage all contracts regardless of ownership. Archive contracts.'],
        ],
        col_widths=[3.5, 5, 8]
    )

    add_note(doc,
             'A "Contract Approver" is not a separate Odoo role – any user with at '
             'least the Contract User role can be added to an Approval Team as an approver. '
             'The system will automatically notify them when their approval is needed.',
             label='IMPORTANT', bg='FFF2CC')

    add_heading(doc, 'Permission Summary Matrix', level=2, color=MID_BLUE)
    add_styled_table(doc,
        headers=['Action', 'Base User (read-only)', 'Contract User', 'Team Leader', 'Manager'],
        rows=[
            ['View (own) contracts',            '✓', '✓', '✓', '✓'],
            ['View all contracts',              '✓', '✓', '✓', '✓'],
            ['Create contracts',                '✗', '✓', '✓', '✓'],
            ['Edit own contracts (Draft only)', '✗', '✓', '✓', '✓'],
            ['Submit for approval',             '✗', '✓', '✓', '✓'],
            ['Approve contracts',               '✗', '✓*','✓', '✓'],
            ['Return for Correction',           '✗', '✓*','✓', '✓'],
            ['Create approval teams',           '✗', '✗', '✓', '✓'],
            ['Configure module settings',       '✗', '✗', '✗', '✓'],
            ['Cancel contracts',                '✗', '✓*','✓', '✓'],
            ['Close contracts',                 '✗', '✓*','✓', '✓'],
            ['Archive contracts',               '✗', '✗', '✗', '✓'],
        ],
        col_widths=[6, 3, 3, 3, 1.4]
    )
    add_body(doc, '* Only when the user is the Responsible User or a member of the assigned Approval Team.',
             italic=True, size=9.5, color=GREY_TEXT)

    add_heading(doc, 'How to Assign a Role to a User', level=2, color=MID_BLUE)
    add_body(doc, 'Only an Odoo Administrator can assign roles. Steps:', size=11, color=GREY_TEXT)
    add_step_box(doc, 1, 'Go to Settings',
        ['Click the App Switcher (top-left grid icon).',
         'Click on the "Settings" app tile.'])
    add_step_box(doc, 2, 'Open the Users list',
        ['In the Settings menu, click on "Users & Companies" then "Users".',
         'A list of all users in the system will appear.'])
    add_step_box(doc, 3, 'Open the user record',
        ['Click on the name of the user you want to configure.'])
    add_step_box(doc, 4, 'Assign the Contract Management role',
        ['Scroll down to the "Contract Management" section in the Access Rights area.',
         'Click the dropdown next to "Contract Management".',
         'Select one of: User, Team Leader, or Manager.',
         'Click Save (or the floppy disk icon).'])
    add_screenshot_placeholder(doc, 'Odoo User Record – Contract Management Access Rights Section')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 4 – SYSTEM CONFIGURATION
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '4.  System Configuration (Administrator / Manager)', level=1)
    add_body(doc,
        'Before contracts can be created and routed for approval, an Administrator '
        'must configure the module settings. This only needs to be done once.',
        size=11, color=GREY_TEXT)

    add_heading(doc, '4.1  Accessing Module Settings', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Open Contract Management',
        ['Click the App Switcher.',
         'Click "Contract Management".'])
    add_step_box(doc, 2, 'Open Configuration > Settings',
        ['In the Contract Management menu bar, click "Configuration".',
         'From the dropdown, click "Settings".'])
    add_screenshot_placeholder(doc, 'Contract Management – Configuration Menu')

    add_heading(doc, '4.2  Contract Approval Setting', level=2, color=MID_BLUE)
    add_body(doc,
        'The most important setting is the Contract Approval mode. This controls '
        'whether approval teams are used.',
        size=11, color=GREY_TEXT)
    add_styled_table(doc,
        headers=['Option', 'Meaning', 'When to Use'],
        rows=[
            ['No Approval Required',
             'Contracts skip the approval stage and go directly to "Running" when confirmed.',
             'Very small organisations or low-risk contracts where no formal sign-off is needed.'],
            ['Approval Optional',
             'An approval team can be assigned but is not mandatory.',
             'Mixed environments where some contracts need approval and others do not.'],
            ['Approval Required',
             'Every contract MUST have an approval team assigned. The Approval Team field becomes mandatory.',
             'Organisations with strict governance and procurement policies.'],
        ],
        col_widths=[4, 6, 6.4]
    )
    add_step_box(doc, 1, 'Select the Approval Mode',
        ['In the Settings page, locate the "Contract Approval" radio buttons.',
         'Select the appropriate option for your organisation.',
         'Click the "Save" button at the top of the page.'])
    add_screenshot_placeholder(doc, 'Contract Management Settings Page – Approval Mode Options')

    add_heading(doc, '4.3  Company Abbreviation', level=2, color=MID_BLUE)
    add_body(doc,
        'The system auto-generates contract reference numbers using the Company Abbreviation '
        '(e.g. ECDHS-SAL-001-2026). You must set this abbreviation on your company record.',
        size=11, color=GREY_TEXT)
    add_step_box(doc, 1, 'Set the Company Abbreviation',
        ['Go to Settings → Companies (or Settings → General Settings → Company).',
         'Open your company record.',
         'Find the "Company Abbreviation" field (next to the Currency field).',
         'Enter a short abbreviation (e.g. ECDHS, MUN, DEPT).',
         'Click Save.'])
    add_note(doc,
             'If the Company Abbreviation is not set, contract reference numbers '
             'will be incomplete. Set it before creating any contracts.',
             label='WARNING', bg='FFE5E5')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 5 – BPMN PROCESS FLOWCHARTS
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '5.  BPMN Process Flowcharts', level=1)
    add_body(doc,
        'The following swimlane diagrams show how each key process flows through '
        'the system, who performs each action, and where they click in Odoo.',
        size=11, color=GREY_TEXT)

    # ── 5.1 Master Lifecycle Flow ────────────────────────────────────────────
    add_heading(doc, '5.1  Contract Lifecycle – Master State Flow', level=2, color=MID_BLUE)
    add_body(doc,
        'Every contract moves through the following states. The coloured strip '
        'below shows the sequential flow.',
        size=11, color=GREY_TEXT)
    add_flow_diagram(doc, 'Contract State Progression:', [
        ('DRAFT',     '1F3964', 'rect'),
        ('APPROVAL',  'ED7D31', 'rect'),
        ('RUNNING',   '378630', 'rect'),
        ('TO RENEW',  '2E74B5', 'rect'),
        ('EXPIRED',   'C00000', 'rect'),
        ('CLOSED',    '404040', 'rect'),
    ])
    add_body(doc,
        'A contract can also move to CANCELLED from the Draft, Approval, or '
        'Running states if it is no longer required.',
        size=10, italic=True, color=GREY_TEXT)
    doc.add_paragraph()

    # ── 5.2 Contract Creation BPMN ───────────────────────────────────────────
    add_bpmn_swimlane(doc, '5.2  BPMN – Contract Creation Process', [
        ('Contract\nUser',
         [
             'Navigate to Contract Management → Contracts.',
             'Click the "New" button (top-left, blue).',
             'Fill in mandatory fields: Contract Title, Contract Type, Vendor/Partner, Start Date, Contract Amount Type, Contract Duration.',
             'Select an Approval Team (if required by company settings).',
             'Add Bill of Quantities/Deliverables lines on the "Lines" tab.',
             'Upload supporting documents on the "Documents" tab (Appointment Letter, SLA, etc.).',
             'Fill in additional details: Classification, Tender Number, Region, Municipality, Project.',
             'Click "Confirm" button to submit.',
         ]),
        ('System\n(Odoo)',
         [
             'Auto-generates Contract Number using pattern: [CompanyAbbr]-[TypeCode]-[Sequence]-[Year].',
             'Validates Start Date < End Date.',
             'If no Approval Team is set → moves contract directly to "Running" state.',
             'If Approval Team is set → moves contract to "Approval" state and sends email to first approver.',
             'Posts a log entry in the Chatter.',
         ]),
        ('Manager /\nAdministrator',
         [
             'Reviews contract if escalated.',
             'Receives notification if contract is fully approved.',
         ]),
    ])

    # ── 5.3 Approval BPMN ────────────────────────────────────────────────────
    add_bpmn_swimlane(doc, '5.3  BPMN – Contract Approval Process', [
        ('System\n(Odoo)',
         [
             'Contract is in "Approval" state.',
             'Sends email notification to Current Approver: "You have been requested to approve the contract [Name]."',
             'Shows "Approve" button ONLY to the current approver in the sequence.',
         ]),
        ('Current\nApprover',
         [
             'Receives email notification with a link to the contract.',
             'Clicks the link (or navigates: Contract Management → Contracts).',
             'Opens the contract and reviews all fields, lines, and attached documents.',
             'Decision: Approve OR Return for Correction.',
             'To APPROVE: Click the green "Approve" button in the header.',
             'To RETURN: Click "Return for Correction", enter comments in the popup, click "Return for Correction".',
         ]),
        ('System\n(Odoo)',
         [
             'On Approval: marks current approver as "Approved". Checks for next approver in sequence.',
             'If next approver exists → sends approval request email to next approver.',
             'If all approvers have approved (fully approved) → sends "Contract Approved" notification to Responsible User.',
             'Moves contract to "Running" state.',
             'On Return for Correction: moves contract back to "Draft". Sends correction email to Responsible User with comments.',
         ]),
        ('Responsible\nUser (Creator)',
         [
             'Receives email: "Contract returned for correction – [comments]".',
             'Opens the contract (now back in Draft).',
             'Edits the required fields.',
             'Clicks "Confirm" again to re-submit for approval.',
         ]),
    ])

    # ── 5.4 Invoice / Bill BPMN ──────────────────────────────────────────────
    add_bpmn_swimlane(doc, '5.4  BPMN – Invoice / Vendor Bill Generation', [
        ('Contract\nUser',
         [
             'Open a contract that is in "Running" state.',
             'For SALE contracts: Click "Create Customer Invoice" button in the header.',
             'For PURCHASE contracts: Click "Create Vendor Bill" button in the header.',
             'Review the auto-populated invoice/bill (partner, lines, payment terms).',
             'Make any necessary adjustments.',
             'Click "Confirm" on the invoice/bill to post it.',
         ]),
        ('System\n(Odoo)',
         [
             'Creates a draft invoice/bill pre-filled from the contract lines.',
             'Links the invoice/bill back to the contract (visible in the "Invoices" tab).',
             'Updates the invoice count on the contract (shown as a stat button).',
         ]),
        ('Finance\nUser',
         [
             'Receives invoice/bill in the Accounting module.',
             'Processes payment as per normal accounting workflow.',
         ]),
    ])

    # ── 5.5 Renewal & Closure ────────────────────────────────────────────────
    add_bpmn_swimlane(doc, '5.5  BPMN – Contract Renewal & Closure Process', [
        ('System\n(Odoo)',
         [
             'Scheduled daily task checks all contracts with an End Date.',
             'If today\'s date ≥ End Date → automatically moves contract to the "Expiring State" configured on the contract (Expired, Closed, or To Renew).',
             'Kanban card turns red when the contract has expired.',
         ]),
        ('Contract\nUser',
         [
             'Monitors contracts nearing expiry (Days Left field).',
             'To RENEW: Open expired/closed contract → Click "To Renew" button → Edit dates/terms → Click "Confirm" to run again.',
             'To CLOSE manually: Open a running/expired contract → Click "Close" button → Confirm the dialog.',
             'To CANCEL: Open a contract in Draft or Approval state → Click "Cancel" → Confirm the dialog.',
         ]),
        ('Manager',
         [
             'Reviews contracts flagged "To Renew".',
             'Can reset any contract to Draft via "Reset to Draft" button for major renegotiations.',
         ]),
    ])

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 6 – USER GUIDE: CONTRACT USER
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '6.  User Guide – Contract User', level=1)
    add_body(doc,
        'This section is for staff who create and manage contracts day-to-day. '
        'Follow every step carefully the first time you use the system.',
        size=11, color=GREY_TEXT)

    # ── 6.1 Navigating ───────────────────────────────────────────────────────
    add_heading(doc, '6.1  Navigating to the Contracts List', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Open Contract Management',
        ['From the Odoo home screen, click the "Contract Management" app tile.',
         'The Contracts list view will open. It shows all contracts you have access to.'])
    add_step_box(doc, 2, 'Switch between views',
        ['List View (rows of data): Click the ≡ list icon at the top-right.',
         'Kanban View (cards): Click the ▦ kanban icon.',
         'Kanban cards are colour-coded: Green = Running, Red = Expired, Blue = To Renew.'])
    add_step_box(doc, 3, 'Search and filter',
        ['Use the Search bar at the top-right to type a contract name, reference, or partner name.',
         'Click the dropdown arrow in the search bar to apply Filters (e.g. "Running", "My Contracts") or Group By (e.g. Type, State, Partner).'])
    add_screenshot_placeholder(doc, 'Contracts List View with Search Bar and Filters')

    # ── 6.2 Creating a Contract ───────────────────────────────────────────────
    add_heading(doc, '6.2  Creating a New Contract', level=2, color=MID_BLUE)
    add_body(doc,
        'Creating a contract requires you to fill in all mandatory fields (marked with a red asterisk *) '
        'before you can save.',
        size=11, color=GREY_TEXT)

    add_step_box(doc, 1, 'Click the "New" button',
        ['In the Contracts list view, click the blue "New" button in the top-left corner.',
         'A blank contract form will open in edit mode.'])

    add_step_box(doc, 2, 'Enter the Contract Title',
        ['At the top of the form you will see a large text field labelled "Contract Title" (placeholder text: Contract Title).',
         'Click on it and type a descriptive name for the contract.',
         'Example: "Supply of Office Furniture – ABC Suppliers 2026"'])

    add_step_box(doc, 3, 'Fill in the top section (Left column)',
        ['Contract Number (Ref): This is auto-generated when you save. Leave as "000".',
         'Contract Type: Click the dropdown and select the appropriate type (e.g. Purchase, Sale, Funding Agreement).',
         'Vendor: Click the Vendor field and start typing the vendor/partner name. Select from the autocomplete dropdown.'])

    add_step_box(doc, 4, 'Fill in the top section (Right column)',
        ['Responsible User: Defaults to you. Change if creating on behalf of someone else.',
         'Approval Team: If approval is configured, click and select the relevant team from the dropdown.',
         '  - This field is mandatory if the system is set to "Approval Required" mode.'])

    add_step_box(doc, 5, 'Set Dates',
        ['Start Date: Defaults to today. Click and select the actual contract start date.',
         'End Date: Click and select the contract end date (for fixed-term contracts).',
         'Date Document Signed: Enter the date the physical document was signed.',
         'Last Payment Date: Optionally set a date after which no payments should be made.',
         'Expiring State: Choose what happens when the contract expires (Expired, Closed, or To Renew).'])

    add_step_box(doc, 6, 'Enter Financial & Contract Details',
        ['Contract Amount: Enter the total monetary value of the contract.',
         'Contract Amount Type: Select "Fixed Value" or "Rate Based".',
         'Contract Duration: Enter the duration in months (e.g. 12 for a one-year contract).',
         'Classification: Select "Capital Commitments" or "Operating Agreement".',
         'Tender Number: Enter the tender/bid reference number if applicable.',
         'Variation Order Amount: If there are variations, enter the total variation amount.',
         'Raised Contract Amount: The system calculates Initial Amount + Variation Order Amount.',
         'Variation Order Percentage: Note – this must not exceed 20% of the Contract Award Amount.'])

    add_step_box(doc, 7, 'Set Location & Project Details',
        ['Region: Click and select the geographic region.',
         'Municipality: Click and select the municipality (filtered by region).',
         'Project: Link this contract to an existing project if applicable.',
         'SCMU: Enter the SCMU reference if required by your organisation.'])

    add_screenshot_placeholder(doc, 'Contract Form – Top Section with All Mandatory Fields Filled In')

    add_step_box(doc, 8, 'Save the Contract',
        ['Click the Save button (floppy disk icon, top-left) or simply navigate away – Odoo auto-saves.',
         'The Contract Number field will now auto-populate with a reference like: ECDHS-SAL-001-2026.',
         'The contract is now in DRAFT state (shown in the status bar at the top-right).'])

    add_note(doc,
             'The contract reference number is auto-generated using the pattern: '
             '[Company Abbreviation]-[First 3 chars of Type]-[Sequence Number]-[Year]. '
             'Example: ECDHS-PUR-005-2026 for a Purchase contract.',
             label='HOW THE REF IS GENERATED', bg='E2EFD9')

    add_screenshot_placeholder(doc, 'Contract Form After Save – Contract Number Auto-Generated, Status = Draft')

    # ── 6.3 Uploading Documents ───────────────────────────────────────────────
    add_heading(doc, '6.3  Uploading Supporting Documents', level=2, color=MID_BLUE)
    add_body(doc,
        'You can attach official contract documents directly to the contract record. '
        'These are stored securely inside Odoo.',
        size=11, color=GREY_TEXT)

    add_step_box(doc, 1, 'Click the "Documents" tab',
        ['On the open contract form, scroll down to the notebook tabs.',
         'Click the tab labelled "Documents".'])

    add_step_box(doc, 2, 'Upload each document',
        ['You will see upload fields for each document type.',
         'Click the upload/paperclip icon next to the relevant field.',
         'A file browser will open. Navigate to the file on your computer.',
         'Select the file and click Open. The file name will appear next to the field.'])

    add_styled_table(doc,
        headers=['Document Field', 'What to Upload'],
        rows=[
            ['Appointment Letter',          'Formal letter appointing the vendor/service provider.'],
            ['Acceptance Letter',           'Letter confirming acceptance of the contract terms.'],
            ['SLA / Contract',              'The signed Service Level Agreement or main contract document (PDF).'],
            ['Project Plan',                'Detailed project plan or work programme.'],
            ['Terms of Reference',          'TOR document outlining scope, objectives, and deliverables.'],
            ['Public Liability',            'Proof of public liability insurance certificate.'],
            ['Extension of Time',           'Any approved time extension documentation.'],
            ['Penalties & Correspondence',  'Documentation related to penalties or formal correspondence.'],
            ['Completion Certificate',      'Certificate issued upon project/service completion.'],
            ['Arrival Letter',              'Letter confirming vendor/goods arrival on site.'],
            ['Variation Orders',            'Approved variation order documentation.'],
        ],
        col_widths=[5, 11.4]
    )

    add_screenshot_placeholder(doc, 'Contract Form – Documents Tab with Uploaded Files')

    # ── 6.4 Bill of Quantities ────────────────────────────────────────────────
    add_heading(doc, '6.4  Adding Bill of Quantities / Deliverables (Lines)', level=2, color=MID_BLUE)
    add_body(doc,
        'The Lines tab allows you to itemise the contract into specific deliverables, '
        'products, or services. These lines are then used to auto-populate invoices/bills.',
        size=11, color=GREY_TEXT)

    add_step_box(doc, 1, 'Enable Lines',
        ['At the top of the contract form, find the "Bill of Quantities/Deliverables" checkbox.',
         'Ensure it is ticked (checked). If unchecked, the Lines tab will not appear.',
         'Note: You cannot uncheck this once lines have been added.'])

    add_step_box(doc, 2, 'Click the "Lines" tab',
        ['In the notebook section of the form, click the "Lines" tab.'])

    add_step_box(doc, 3, 'Add a line',
        ['Click "Add a line" at the bottom of the lines table.',
         'A new row will appear with empty fields.'])

    add_step_box(doc, 4, 'Fill in each line',
        ['Product: Click and select the product or service item. Filtered by contract type (sale/purchase).',
         'Description: Auto-fills from product; edit to describe the specific deliverable.',
         'Quantity: Enter the number of units.',
         'UoM (Unit of Measure): Shown if UoM is enabled. Select the unit (e.g. Each, Hours, m²).',
         'Price: Enter the unit price.',
         'Disc.%: Optionally enter a discount percentage.',
         'Taxes: Select applicable taxes if required.'])

    add_step_box(doc, 5, 'Add more lines as needed',
        ['Repeat steps 3–4 for each product/service in the contract.',
         'Use the drag handle (≡) on the left of each row to reorder lines.',
         'To delete a line, click the trash icon on the right.'])

    add_screenshot_placeholder(doc, 'Contract Form – Lines Tab with Bill of Quantities Items')

    # ── 6.5 Confirming a Contract ─────────────────────────────────────────────
    add_heading(doc, '6.5  Confirming (Submitting) a Contract', level=2, color=MID_BLUE)
    add_body(doc,
        'Once all information is complete and documents are uploaded, you confirm '
        'the contract to trigger the next workflow step.',
        size=11, color=GREY_TEXT)

    add_step_box(doc, 1, 'Click the "Confirm" button',
        ['At the top of the contract form, click the blue "Confirm" button.',
         'This button is only visible when the contract is in DRAFT state.'])

    add_step_box(doc, 2, 'What happens next',
        ['SCENARIO A – No Approval Team assigned: The contract moves directly to RUNNING state. A green "Running" ribbon appears on the form.',
         'SCENARIO B – Approval Team assigned: The contract moves to APPROVAL state. An orange ribbon may appear. The first approver receives an email notification automatically.',
         'A log entry is posted in the Chatter at the bottom of the form.'])

    add_note(doc,
             'If the "Confirm" button is not visible, check: (1) Is the contract in Draft state? '
             '(2) Are you the Responsible User? Both conditions must be true to see the Confirm button.',
             label='TROUBLESHOOTING', bg='FFF2CC')

    add_screenshot_placeholder(doc, 'Contract Form – "Confirm" Button Visible in Draft State')
    add_screenshot_placeholder(doc, 'Contract Form – After Confirmation, Status = Approval or Running')

    # ── 6.6 Viewing & Tracking ────────────────────────────────────────────────
    add_heading(doc, '6.6  Viewing and Tracking Contracts', level=2, color=MID_BLUE)

    add_body(doc, 'Key monitoring features:', size=11, color=GREY_TEXT)
    add_bullet(doc, 'Days Left field: Shows how many days remain before the End Date (visible in the list view optional columns).', bold_prefix='Days Left')
    add_bullet(doc, 'Kanban State indicator: The coloured circle at the top-right of the form title indicates the kanban status (Draft, Running, Expired).', bold_prefix='Kanban State')
    add_bullet(doc, 'Invoices stat button: The button at the top of the form shows how many invoices/bills have been raised against this contract. Click it to view them.', bold_prefix='Invoice Counter')
    add_bullet(doc, 'Chatter (bottom of form): All state changes, approvals, and corrections are logged here automatically.', bold_prefix='Audit Trail')
    add_bullet(doc, 'Filters: Use "Running" filter to see only active contracts. Use "My Contracts" to see only contracts you are responsible for.', bold_prefix='Quick Filters')

    add_screenshot_placeholder(doc, 'Contract Form – Chatter Showing State Changes and Approval Log')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 7 – USER GUIDE: APPROVER
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '7.  User Guide – Approver', level=1)
    add_body(doc,
        'This section is for users who have been added to an Approval Team as an approver. '
        'You will receive an email notification when a contract is waiting for your approval.',
        size=11, color=GREY_TEXT)

    # ── 7.1 Receiving Notification ────────────────────────────────────────────
    add_heading(doc, '7.1  Receiving an Approval Request', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Check your email',
        ['You will receive an email from Odoo with the subject line containing the contract name.',
         'The email body will read: "Dear [Your Name], You have been requested to approve the contract [Contract Title]."',
         'The email contains a "View Contract" link.'])

    add_step_box(doc, 2, 'Click "View Contract" in the email',
        ['Click the "View Contract" hyperlink in the email.',
         'Your browser will open and Odoo will load the contract form directly.',
         'You may be asked to log in first if your session has expired.'])

    add_note(doc,
             'Alternatively, you can find the contract manually: Log in to Odoo → '
             'Contract Management → Contracts. Look for contracts in "Approval" state. '
             'The Approval tab on the contract shows all approvers and their current status.',
             label='ALTERNATIVE METHOD', bg='E2EFD9')

    add_screenshot_placeholder(doc, 'Approval Request Email – "View Contract" Link Highlighted')

    # ── 7.2 Reviewing the Contract ────────────────────────────────────────────
    add_heading(doc, '7.2  Reviewing the Contract Before Deciding', level=2, color=MID_BLUE)
    add_body(doc,
        'Before approving or rejecting, carefully review all sections of the contract.',
        size=11, color=GREY_TEXT)

    add_step_box(doc, 1, 'Review the main contract details',
        ['Check the Contract Title, Contract Number, Type, Vendor, and Dates.',
         'Verify the Contract Amount, Amount Type, Duration, and Variation Orders.',
         'Check the Classification, Tender Number, Region, Municipality, and Project.'])

    add_step_box(doc, 2, 'Review the Lines tab (Bill of Quantities)',
        ['Click the "Lines" tab.',
         'Review each line item: product, description, quantity, unit price, and taxes.',
         'Verify the totals match the Contract Amount.'])

    add_step_box(doc, 3, 'Review the Documents tab',
        ['Click the "Documents" tab.',
         'Verify all required supporting documents have been uploaded.',
         'Click on each document name to download and review it.'])

    add_step_box(doc, 4, 'Review the Approval tab',
        ['Click the "Approval" tab.',
         'You can see the full list of approvers, their roles, and their current status.',
         'Statuses: "To Approve" = waiting, "Pending" = currently being reviewed, "Approved" = completed.'])

    add_step_box(doc, 5, 'Check the Chatter history',
        ['Scroll to the bottom of the form.',
         'The Chatter shows all previous comments, state changes, and return-for-correction notes.'])

    add_screenshot_placeholder(doc, 'Contract Form in Approval State – Approval Tab Showing Approver Statuses')

    # ── 7.3 Approving ────────────────────────────────────────────────────────
    add_heading(doc, '7.3  Approving the Contract', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Click the "Approve" button',
        ['At the top of the contract form, you will see a green "Approve" button.',
         'This button is ONLY visible to the current approver in the sequence.',
         'If you do not see the "Approve" button, either it is not your turn yet, or you are not in the approval sequence for this contract.'])

    add_step_box(doc, 2, 'Confirm your approval',
        ['Click "Approve". There is no additional confirmation popup – the approval is processed immediately.',
         'A log entry "Contract approved by [Your Name]" is posted in the Chatter.',
         'If you are the last approver: the contract automatically moves to "Running" state and the Responsible User receives an email notification.',
         'If there are more approvers after you: the next approver will receive an email notification and the contract stays in "Approval" state.'])

    add_screenshot_placeholder(doc, 'Contract Form – "Approve" Button Visible to Current Approver')
    add_screenshot_placeholder(doc, 'Contract Form – After Final Approval, Status Bar Shows "Running", Green Ribbon Appears')

    # ── 7.4 Return for Correction ─────────────────────────────────────────────
    add_heading(doc, '7.4  Returning a Contract for Correction', level=2, color=MID_BLUE)
    add_body(doc,
        'If the contract has errors or missing information, you can send it back to '
        'the Responsible User with your comments.',
        size=11, color=GREY_TEXT)

    add_step_box(doc, 1, 'Click "Return for Correction"',
        ['At the top of the contract form, click the "Return for Correction" button.',
         'A popup dialog will appear asking for your comments.'])

    add_step_box(doc, 2, 'Enter your comments',
        ['In the "Comments" field of the popup, type a clear description of what needs to be corrected.',
         'Example: "Please attach the signed SLA document and update the End Date to 31 Dec 2026."',
         'The Comments field is mandatory – you cannot proceed without entering text.'])

    add_step_box(doc, 3, 'Click "Return for Correction" in the popup',
        ['Click the blue "Return for Correction" button inside the popup.',
         'The popup closes.',
         'The contract moves back to "Draft" state.',
         'An email is sent to the Responsible User containing your comments.',
         'All previous approval progress is reset.'])

    add_screenshot_placeholder(doc, '"Return for Correction" Popup Dialog – Comments Field')
    add_note(doc,
             'The Responsible User will receive an email with the subject "Contract Returned '
             'for Correction: [Contract Title]" containing your exact comments. They must '
             'correct the contract and click "Confirm" again to restart the approval process.',
             label='NOTE', bg='FFF2CC')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 8 – USER GUIDE: TEAM LEADER
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '8.  User Guide – Team Leader', level=1)
    add_body(doc,
        'Team Leaders are responsible for creating and maintaining Approval Teams. '
        'An Approval Team defines who approves a contract and in what sequence.',
        size=11, color=GREY_TEXT)

    # ── 8.1 Creating Approval Teams ───────────────────────────────────────────
    add_heading(doc, '8.1  Creating & Managing Approval Teams', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Navigate to Approval Teams',
        ['In the Contract Management module, click "Configuration" in the top menu bar.',
         'Click "Contract Approval Teams".',
         'A list of all existing approval teams is displayed.'])

    add_step_box(doc, 2, 'Create a new team',
        ['Click the blue "New" button.',
         'A blank Approval Team form opens.'])

    add_step_box(doc, 3, 'Enter team details',
        ['Team Name: Enter a descriptive name (e.g. "Finance Approval Team", "Procurement Review Board").',
         'Team Leader: Defaults to you. This is the person responsible for managing the team.',
         'Company: Defaults to your company. Change if creating a team for another company (multi-company setup).'])

    add_step_box(doc, 4, 'Add approvers on the "Approvers" tab',
        ['Click the "Approvers" tab.',
         'Click "Add a line" to add each approver.',
         'For each approver, fill in the following fields (see Section 8.2 for details):',
         '  - Approver (user name)',
         '  - Role / Position',
         '  - Can Edit (checkbox)',
         '  - Minimum Amount (optional)',
         '  - Maximum Amount (optional)',
         '  - Custom Condition Code (optional, advanced)',
         'Use the drag handle (≡) to arrange approvers in the correct sequential order.'])

    add_step_box(doc, 5, 'Save the team',
        ['Click "Save". The team is now available for selection when creating contracts.'])

    add_screenshot_placeholder(doc, 'Approval Team Form – Team Name, Leader, and Approvers List')

    # ── 8.2 Configuring Approver Rules ────────────────────────────────────────
    add_heading(doc, '8.2  Configuring Approver Rules (Amount Thresholds & Conditions)', level=2, color=MID_BLUE)
    add_body(doc,
        'Each approver in a team can have rules that control when they are included '
        'or skipped in the approval chain.',
        size=11, color=GREY_TEXT)

    add_styled_table(doc,
        headers=['Field', 'What It Does', 'Example'],
        rows=[
            ['Approver',         'The Odoo user who will be asked to approve.',
                                 'Jane Smith'],
            ['Role / Position',  'Descriptive title shown on the contract. Auto-detected from HR employee profile if available.',
                                 'Finance Director'],
            ['Can Edit',         'If ticked, this approver is allowed to edit contract fields before giving their approval. Useful for reviewers who may need to fix minor errors.',
                                 'Tick for Chief Procurement Officer'],
            ['Minimum Amount',   'Approver is ONLY included if the contract amount is GREATER THAN OR EQUAL TO this value. Leave blank to always include.',
                                 'R 500,000 – only involve CFO for contracts above R500k'],
            ['Maximum Amount',   'Approver is ONLY included if the contract amount is LESS THAN OR EQUAL TO this value. Leave blank to always include.',
                                 'R 2,000,000 – skip this approver for very large contracts'],
            ['Custom Condition', 'Advanced Python expression. Set variable "result" to True/False. Use CONTRACT and USER keywords.',
                                 'result = CONTRACT.type == "purchase"  (only for purchase contracts)'],
        ],
        col_widths=[3.5, 6.5, 6.4]
    )

    add_note(doc,
             'IMPORTANT: The sequence order of approvers matters. Odoo processes approvals '
             'from the lowest sequence number to the highest. Drag rows to reorder. '
             'Approver 1 must approve before Approver 2 receives their notification.',
             label='SEQUENCE ORDER', bg='FFF2CC')

    add_body(doc, 'Custom Condition Code Examples:', bold=True, size=11, color=DARK_BLUE)
    add_styled_table(doc,
        headers=['Use Case', 'Condition Code'],
        rows=[
            ['Only for Purchase contracts',            'result = CONTRACT.type == \'purchase\''],
            ['Only for contracts above R1 million',    'result = CONTRACT.amount >= 1000000'],
            ['Only for a specific vendor',             'result = CONTRACT.partner_id.name == \'ABC Suppliers\''],
            ['Only for contracts in Gauteng region',   'result = CONTRACT.region_id.name == \'Gauteng\''],
            ['Only for a specific department user',    'result = USER.department_id.name == \'Finance\''],
        ],
        col_widths=[7, 9.4]
    )

    add_screenshot_placeholder(doc, 'Approval Team Form – Approvers Tab with Amount Thresholds Set')
    add_screenshot_placeholder(doc, 'Approval Team Form – Help Tab Showing Condition Code Examples')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 9 – USER GUIDE: MANAGER / ADMINISTRATOR
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '9.  User Guide – Manager / Administrator', level=1)
    add_body(doc,
        'Managers have full control over the module, including system-wide settings, '
        'visibility of all contracts, and the ability to cancel or close any contract.',
        size=11, color=GREY_TEXT)

    # ── 9.1 Module Settings ───────────────────────────────────────────────────
    add_heading(doc, '9.1  Module Settings', level=2, color=MID_BLUE)
    add_body(doc,
        'Refer to Section 4 for detailed configuration steps. As a Manager, you '
        'also see the "Settings" option under the Configuration menu.',
        size=11, color=GREY_TEXT)

    add_styled_table(doc,
        headers=['Setting', 'Location', 'Purpose'],
        rows=[
            ['Contract Approval Mode',
             'Contract Management → Configuration → Settings',
             'Set to No Approval / Optional / Required.'],
            ['Use Contract for Invoicing',
             'Contract Management → Configuration → Settings',
             'Enable/disable using contracts to generate customer invoices and vendor bills.'],
            ['Company Abbreviation',
             'Settings → Companies → [Your Company]',
             'Used in auto-generated contract reference numbers.'],
            ['User Role Assignment',
             'Settings → Users & Companies → Users',
             'Assign User / Team Leader / Manager roles to staff.'],
        ],
        col_widths=[4.5, 5.5, 6.4]
    )

    # ── 9.2 Managing Contracts in Bulk ────────────────────────────────────────
    add_heading(doc, '9.2  Managing Contracts in Bulk (List View)', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Select multiple contracts',
        ['In the Contracts list view, tick the checkboxes on the left of each row.',
         'Or tick the top checkbox to select all.'])

    add_step_box(doc, 2, 'Use the Action menu',
        ['With contracts selected, click the "Action" dropdown button that appears.',
         'Available bulk actions: Archive, Unarchive, Delete (caution: cannot be undone).'])

    add_note(doc,
             'You cannot archive a contract that is in "Running" or "Approval" state. '
             'You must Close or Cancel it first.',
             label='RESTRICTION', bg='FFE5E5')

    # ── 9.3 Cancelling or Closing Contracts ───────────────────────────────────
    add_heading(doc, '9.3  Cancelling or Closing Contracts', level=2, color=MID_BLUE)
    add_body(doc, 'Cancellation and Closure are permanent actions. Choose carefully:', size=11, color=GREY_TEXT)

    add_styled_table(doc,
        headers=['Action', 'When to Use', 'How to Do It', 'Result'],
        rows=[
            ['Cancel',
             'Contract is no longer needed; was in Draft or Approval stage.',
             'Open contract → Click "Cancel" button in header → Confirm dialog.',
             'Contract state = Cancelled. No further actions possible. Remains visible for audit.'],
            ['Close',
             'Contract has been fully executed or is being formally ended.',
             'Open contract (Running/Expired/To Renew) → Click "Close" → Confirm dialog.',
             'Contract state = Closed. Invoicing disabled. Remains visible for audit.'],
            ['Reset to Draft',
             'Contract needs to be renegotiated from scratch.',
             'Open contract (To Renew or Cancelled) → Click "Reset to Draft" → Confirm dialog.',
             'Contract returns to Draft state. Can be fully edited and re-submitted.'],
        ],
        col_widths=[2.5, 4, 4.5, 5.4]
    )

    add_screenshot_placeholder(doc, 'Contract Form Header Buttons – Cancel, Close, Reset to Draft')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 10 – INVOICE & BILLING WORKFLOW
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '10.  Invoice & Billing Workflow', level=1)
    add_body(doc,
        'Once a contract is in Running state, you can generate accounting documents '
        '(invoices for Sale contracts, vendor bills for Purchase contracts) directly '
        'from the contract record.',
        size=11, color=GREY_TEXT)

    add_heading(doc, '10.1  Creating a Customer Invoice (Sale Contracts)', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Open the Running contract',
        ['Navigate to Contract Management → Contracts.',
         'Click on a contract that is in "Running" state with Contract Type = "Sale".'])

    add_step_box(doc, 2, 'Click "Create Customer Invoice"',
        ['In the header area, click the blue "Create Customer Invoice" button.',
         'This button is only visible on Sale contracts in Running state.'])

    add_step_box(doc, 3, 'Review the auto-generated invoice',
        ['Odoo opens a new Customer Invoice draft form.',
         'The invoice is pre-filled with: Customer name (from contract), Invoice Lines (from contract lines), Payment Terms (from contract or partner default).',
         'Review all fields carefully before confirming.'])

    add_step_box(doc, 4, 'Confirm the invoice',
        ['Click the "Confirm" button on the invoice form to post it.',
         'The invoice number is generated and the invoice is locked for editing.',
         'Navigate back to the contract (use the breadcrumb at the top) to see the invoice counter has increased.'])

    add_screenshot_placeholder(doc, 'Contract Form – "Create Customer Invoice" Button in Header')
    add_screenshot_placeholder(doc, 'Auto-Generated Invoice – Pre-Filled from Contract Lines')

    add_heading(doc, '10.2  Creating a Vendor Bill (Purchase Contracts)', level=2, color=MID_BLUE)
    add_body(doc, 'The process is identical to creating a customer invoice, with one difference:', size=11, color=GREY_TEXT)
    add_bullet(doc, 'The button is labelled "Create Vendor Bill" and is only visible on contracts with Contract Type = "Purchase" in Running state.')
    add_bullet(doc, 'The resulting document is a Vendor Bill (not a Customer Invoice) and appears in Accounting → Vendors → Bills.')

    add_heading(doc, '10.3  Viewing All Invoices/Bills for a Contract', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Use the Invoices stat button',
        ['On any contract form, look at the top-right area for the stat button showing the number of invoices.',
         'Click the button to open a filtered list of all invoices/bills linked to this contract.'])
    add_step_box(doc, 2, 'Use the "List of Invoices Raised" tab',
        ['Scroll down to the notebook area on the contract form.',
         'Click the "List of Invoices Raised" tab to see all invoices listed inline.'])

    add_note(doc,
             'Invoices/bills generated from a contract are automatically linked back to '
             'the contract record. Deleting the invoice does NOT delete the contract.',
             label='NOTE', bg='FFF2CC')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 11 – CONTRACT RENEWAL WORKFLOW
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '11.  Contract Renewal Workflow', level=1)
    add_body(doc,
        'Contracts with a defined End Date will automatically transition to their '
        'configured Expiring State when the end date passes. Here is how to manage renewals.',
        size=11, color=GREY_TEXT)

    add_heading(doc, '11.1  How Expiry Works', level=2, color=MID_BLUE)
    add_body(doc,
        'A scheduled system task runs daily and checks all contracts for expiry. '
        'When the End Date is reached:',
        size=11, color=GREY_TEXT)
    add_bullet(doc, 'If Expiring State = "Expired": contract moves to Expired state (red ribbon).')
    add_bullet(doc, 'If Expiring State = "Closed": contract moves directly to Closed.')
    add_bullet(doc, 'If Expiring State = "To Renew": contract moves to To Renew (blue ribbon) – a flag for the team to process renewal.')

    add_heading(doc, '11.2  Processing a Renewal', level=2, color=MID_BLUE)
    add_step_box(doc, 1, 'Find contracts needing renewal',
        ['In the Contracts list, use the Filter → Group by State.',
         'Look for contracts in "To Renew" or "Expired" state.',
         'Click on the contract to open it.'])

    add_step_box(doc, 2, 'Click "To Renew" (if not already in that state)',
        ['For expired or closed contracts, click "To Renew" button in the header.',
         'Confirm the dialog: "Please confirm that you want to move this contract to the renewal stage."'])

    add_step_box(doc, 3, 'Edit the contract details',
        ['The contract is now editable.',
         'Update: End Date (new contract period), Contract Amount (if renegotiated), Variation Order fields, Extension Period (months), Revised End Date.',
         'Upload any new documents (renewal letters, updated SLAs, etc.).'])

    add_step_box(doc, 4, 'Re-confirm and re-approve',
        ['Click "Confirm" to re-submit the renewed contract.',
         'If an approval team is assigned, the contract goes through the full approval workflow again.',
         'Once approved (or if no approval needed), the contract moves back to Running state.'])

    add_screenshot_placeholder(doc, 'Contract Form in "To Renew" State – "To Renew" and "Close" Buttons Visible')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 12 – EMAIL NOTIFICATIONS
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '12.  Email Notifications Reference', level=1)
    add_body(doc,
        'The system sends automated email notifications at key points in the '
        'contract workflow. All emails are sent from the configured Odoo outgoing mail server.',
        size=11, color=GREY_TEXT)

    add_styled_table(doc,
        headers=['Trigger Event', 'Email Recipient', 'Email Content'],
        rows=[
            ['Contract submitted for approval (Confirm clicked with Approval Team set)',
             'Current Approver (first in sequence)',
             '"Dear [Approver Name], You have been requested to approve the contract [Title]. [View Contract link]"'],
            ['An approver approves (and there is a next approver)',
             'Next Approver in sequence',
             '"Dear [Next Approver], You have been requested to approve the contract [Title]. [View Contract link]"'],
            ['All approvers have approved (fully approved)',
             'Responsible User (contract creator)',
             '"Dear [Responsible User], The contract [Title] was approved. [View Contract link]"'],
            ['Contract returned for correction',
             'Responsible User (contract creator)',
             '"Dear [Responsible User], The contract [Title] was returned for correction. Comments: [approver comments]. [View Contract link]"'],
        ],
        col_widths=[5, 4, 7.4]
    )

    add_note(doc,
             'Emails include a direct hyperlink to the contract in Odoo. Recipients can '
             'click "View Contract" to navigate directly to the record without having to '
             'search for it manually.',
             label='TIP', bg='E2EFD9')

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 13 – TROUBLESHOOTING & FAQs
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '13.  Troubleshooting & Frequently Asked Questions', level=1)

    faqs = [
        ('I cannot see the "Confirm" button on my contract.',
         'The Confirm button is only visible when: (1) The contract is in Draft state. '
         '(2) You are the Responsible User of the contract. If another person created '
         'the contract, they must confirm it, or the Manager can reassign the Responsible User.'),
        ('I cannot see the "Approve" button even though I am in the approval team.',
         'The Approve button is only visible to the CURRENT approver in the sequence. '
         'If another approver before you has not yet approved, you must wait for them to '
         'complete their step first. Check the Approval tab to see the current status.'),
        ('The Contract Number still shows "000" after saving.',
         'The Company Abbreviation has not been set on the company record. Ask your '
         'administrator to go to Settings → Companies and set the Company Abbreviation field.'),
        ('I uploaded a document but cannot find it.',
         'Go to the contract form and click the "Documents" tab. All uploaded documents '
         'appear there. If the Documents tab is not visible, ensure you have the Contract '
         'User role or higher.'),
        ('The contract moved to "Expired" but we want to renew it.',
         'Open the expired contract and click the "To Renew" button. This will allow you '
         'to edit the contract dates and re-confirm it through the approval workflow.'),
        ('How do I see all contracts, not just mine?',
         'By default all internal users can see all contracts with Visibility = "All '
         'Internal Users". If a contract is set to "Invited Internal Users", you must be '
         'a follower to see it. Managers can always see all contracts.'),
        ('I need to edit a contract that is already Running.',
         'Running contracts cannot be edited directly. You have two options: (1) If you '
         'have Team Leader or Manager access and the approver has "Can Edit" enabled, the '
         'current approver can edit during review. (2) Click "Return for Correction" to '
         'send the contract back to Draft – then edit and re-confirm.'),
        ('How do I archive an old contract?',
         'Only Managers can archive contracts. From the contract list, select the contract(s) '
         'and use Action → Archive. Note: Running contracts cannot be archived; close them first.'),
        ('The "Create Customer Invoice" button is not visible.',
         'Check that: (1) The contract type is "Sale". (2) The contract is in "Running" state. '
         'Both conditions must be true for the button to appear.'),
        ('An approver left the organisation. How do I change the approval team?',
         'A Team Leader or Manager can open the Approval Team (Configuration → Contract '
         'Approval Teams), edit the team, and replace the approver. Changes affect future '
         'contracts; in-progress approvals may need to be manually managed.'),
    ]

    for q, a in faqs:
        add_body(doc, f'Q: {q}', bold=True, size=10.5, color=DARK_BLUE)
        add_body(doc, f'A: {a}', size=10.5, color=GREY_TEXT, indent=0.5)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_page_break(doc)

    # ════════════════════════════════════════════════════════════════════════
    #  SECTION 14 – GLOSSARY
    # ════════════════════════════════════════════════════════════════════════
    add_heading(doc, '14.  Glossary', level=1)

    glossary = [
        ('Approval Team',       'A configured group of users who sequentially approve contracts. Managed under Configuration → Contract Approval Teams.'),
        ('Approver',            'A user assigned to an Approval Team who is required to review and approve contracts.'),
        ('Bill of Quantities',  'A structured list of items/deliverables in the contract, each with quantity, unit price, and tax information. Also called "Lines".'),
        ('Chatter',             'The messaging and audit log area at the bottom of every Odoo form. Records all state changes, approvals, and manual notes.'),
        ('Confirmation',        'The action of clicking "Confirm" to submit a Draft contract for approval (or to Running if no approval is required).'),
        ('Contract Amount',     'The total monetary value of the contract.'),
        ('Contract Duration',   'The length of the contract expressed in months.'),
        ('Draft',               'The initial state of a contract. It can be fully edited.'),
        ('Expiring State',      'The state a contract moves to automatically when its End Date passes (Expired, Closed, or To Renew).'),
        ('Kanban State',        'A visual indicator on the contract form showing Draft, Running, or Expired status using a coloured circle.'),
        ('MOU',                 'Memorandum of Understanding – a non-binding agreement of intent between parties.'),
        ('Raised Contract Amount', 'The total contract value after adding variation orders: Initial Amount + Variation Order Amount.'),
        ('Responsible User',    'The Odoo user who created or is assigned to manage a specific contract. Has editing and action rights on that contract.'),
        ('Running',             'The active state of a contract. Invoices/bills can be generated. Cannot be edited without a formal process.'),
        ('SCMU',                'Supply Chain Management Unit reference code.'),
        ('SLA',                 'Service Level Agreement – a contract defining service delivery standards.'),
        ('Tender Number',       'The procurement tender or bid reference number associated with the contract.'),
        ('To Renew',            'A state indicating the contract has expired and is being processed for renewal.'),
        ('Variation Order',     'A formal amendment to the original contract scope or value. Must not exceed 20% of the Contract Award Amount.'),
        ('Vendor Bill',         'An accounting document created for Purchase contracts representing an amount owed to a vendor.'),
        ('Visibility',          'A contract setting controlling who can see it: "All Internal Users" or "Invited Internal Users" (followers only).'),
    ]

    add_styled_table(doc,
        headers=['Term', 'Definition'],
        rows=[[t, d] for t, d in glossary],
        col_widths=[5, 11.4]
    )

    # ════════════════════════════════════════════════════════════════════════
    #  END MATTER
    # ════════════════════════════════════════════════════════════════════════
    add_page_break(doc)
    add_body(doc, '\n\n', size=11)
    end_p = doc.add_paragraph()
    end_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    er = end_p.add_run('— End of Document —')
    style_run(er, bold=True, size=12, color=DARK_BLUE)

    ep2 = doc.add_paragraph()
    ep2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_border_bottom(ep2)
    er2 = ep2.add_run('Contract Management System User Guide  |  ECDHS  |  March 2026')
    style_run(er2, italic=True, size=9.5, color=GREY_TEXT)

    return doc


# ── Entry point ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    out_path = os.path.join(
        os.path.dirname(__file__),
        'Contract_Management_User_Guide.docx'
    )
    print('Building document …')
    document = build_document()
    document.save(out_path)
    print(f'Saved: {out_path}')
