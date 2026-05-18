
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.style import WD_STYLE_TYPE
import copy

# ─────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────
COL_DARK_BLUE   = RGBColor(0x00, 0x27, 0x5A)   # headers / cover
COL_MID_BLUE    = RGBColor(0x00, 0x5A, 0xA8)   # sub-headers
COL_ACCENT      = RGBColor(0xF0, 0x84, 0x00)   # callouts / step numbers
COL_LIGHT_BG    = RGBColor(0xE8, 0xF0, 0xFB)   # table header fill
COL_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
COL_TEXT        = RGBColor(0x1A, 0x1A, 0x2E)
COL_BORDER      = RGBColor(0xCC, 0xCC, 0xCC)
COL_GREEN       = RGBColor(0x1A, 0x7A, 0x3C)
COL_RED         = RGBColor(0xC0, 0x39, 0x2B)
COL_YELLOW_BG   = RGBColor(0xFF, 0xF9, 0xC4)
COL_STEP_BG     = RGBColor(0xEA, 0xF4, 0xFF)


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def set_cell_bg(cell, rgb: RGBColor):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    hex_color = '{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_border(cell, top=None, bottom=None, left=None, right=None):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        if val:
            el = OxmlElement(f'w:{side}')
            el.set(qn('w:val'), val.get('val', 'single'))
            el.set(qn('w:sz'), str(val.get('sz', 6)))
            el.set(qn('w:space'), '0')
            el.set(qn('w:color'), val.get('color', '000000'))
            tcBorders.append(el)
    tcPr.append(tcBorders)

def add_run_with_color(para, text, bold=False, size=11, color=None, italic=False):
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    return run

def add_heading(doc, text, level=1, color=None):
    style_map = {1: 'Heading 1', 2: 'Heading 2', 3: 'Heading 3', 4: 'Heading 4'}
    p = doc.add_paragraph(style=style_map.get(level, 'Heading 1'))
    run = p.add_run(text)
    run.bold = True
    if level == 1:
        run.font.size = Pt(18)
        run.font.color.rgb = color or COL_DARK_BLUE
    elif level == 2:
        run.font.size = Pt(14)
        run.font.color.rgb = color or COL_MID_BLUE
    elif level == 3:
        run.font.size = Pt(12)
        run.font.color.rgb = color or COL_DARK_BLUE
    elif level == 4:
        run.font.size = Pt(11)
        run.font.color.rgb = color or COL_MID_BLUE
    return p

def add_body(doc, text, indent=0, space_after=6, bold=False, color=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(2)
    if indent:
        p.paragraph_format.left_indent = Inches(indent)
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    run.bold = bold
    if color:
        run.font.color.rgb = color
    return p

def add_bullet(doc, text, level=0, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.left_indent = Inches(0.25 + level * 0.25)
    if bold_prefix:
        r1 = p.add_run(bold_prefix)
        r1.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = COL_DARK_BLUE
    r2 = p.add_run(text)
    r2.font.size = Pt(10.5)
    return p

def add_numbered(doc, text, level=0):
    p = doc.add_paragraph(style='List Number')
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Inches(0.25 + level * 0.25)
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    return p

def add_note_box(doc, text, title="NOTE", bg_color=None, border_color=None):
    bg = bg_color or COL_YELLOW_BG
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    cell = tbl.cell(0, 0)
    set_cell_bg(cell, bg)
    border_hex = '{:02X}{:02X}{:02X}'.format(
        (border_color or COL_ACCENT)[0],
        (border_color or COL_ACCENT)[1],
        (border_color or COL_ACCENT)[2]
    )
    for side in ['top', 'bottom', 'left', 'right']:
        set_cell_border(cell, **{side: {'val': 'single', 'sz': 8, 'color': border_hex}})
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Inches(0.1)
    r1 = p.add_run(f"  {title}:  ")
    r1.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = COL_DARK_BLUE
    r2 = p.add_run(text)
    r2.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_screenshot_placeholder(doc, label, description=""):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_bg(cell, RGBColor(0xF2, 0xF2, 0xF2))
    set_cell_border(cell,
        top={'val': 'dashed', 'sz': 6, 'color': '888888'},
        bottom={'val': 'dashed', 'sz': 6, 'color': '888888'},
        left={'val': 'dashed', 'sz': 6, 'color': '888888'},
        right={'val': 'dashed', 'sz': 6, 'color': '888888'})
    cell._tc.get_or_add_tcPr()
    # Set minimum height
    trPr = tbl.rows[0]._tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), '900')
    trHeight.set(qn('w:hRule'), 'atLeast')
    trPr.append(trHeight)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    icon_run = p.add_run("[ SCREENSHOT ]")
    icon_run.bold = True
    icon_run.font.size = Pt(12)
    icon_run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    if label:
        p2 = cell.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(4)
        lr = p2.add_run(label)
        lr.bold = True
        lr.font.size = Pt(9)
        lr.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    if description:
        p3 = cell.add_paragraph()
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.space_after = Pt(8)
        dr = p3.add_run(description)
        dr.font.size = Pt(8.5)
        dr.italic = True
        dr.font.color.rgb = RGBColor(0x77, 0x77, 0x77)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_step_box(doc, step_num, title, actions, note=None):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    # Number cell
    num_cell = tbl.cell(0, 0)
    num_cell.width = Inches(0.5)
    set_cell_bg(num_cell, COL_ACCENT)
    np = num_cell.paragraphs[0]
    np.alignment = WD_ALIGN_PARAGRAPH.CENTER
    np.paragraph_format.space_before = Pt(6)
    np.paragraph_format.space_after = Pt(4)
    nr = np.add_run(str(step_num))
    nr.bold = True
    nr.font.size = Pt(14)
    nr.font.color.rgb = COL_WHITE
    # Content cell
    content_cell = tbl.cell(0, 1)
    set_cell_bg(content_cell, COL_STEP_BG)
    for side in ['top', 'bottom', 'left', 'right']:
        set_cell_border(content_cell, **{side: {'val': 'single', 'sz': 4, 'color': '005AA8'}})
    tp = content_cell.paragraphs[0]
    tp.paragraph_format.left_indent = Inches(0.1)
    tp.paragraph_format.space_before = Pt(4)
    tr = tp.add_run(title)
    tr.bold = True
    tr.font.size = Pt(11)
    tr.font.color.rgb = COL_DARK_BLUE
    for action in actions:
        ap = content_cell.add_paragraph()
        ap.paragraph_format.left_indent = Inches(0.15)
        ap.paragraph_format.space_before = Pt(1)
        ap.paragraph_format.space_after = Pt(1)
        ar = ap.add_run(f"▸  {action}")
        ar.font.size = Pt(10)
    if note:
        np2 = content_cell.add_paragraph()
        np2.paragraph_format.left_indent = Inches(0.1)
        np2.paragraph_format.space_before = Pt(3)
        np2.paragraph_format.space_after = Pt(4)
        nr2 = np2.add_run(f"⚠  {note}")
        nr2.italic = True
        nr2.font.size = Pt(9.5)
        nr2.font.color.rgb = RGBColor(0x8B, 0x45, 0x13)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_bpmn_flow(doc, title, steps):
    """Draw a linear BPMN-style flow as a horizontal table with arrows."""
    add_heading(doc, title, level=3)
    cols = len(steps)
    tbl = doc.add_table(rows=3, cols=cols * 2 - 1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_idx = 0
    for i, step in enumerate(steps):
        # Step box
        c = tbl.cell(0, col_idx)
        c2 = tbl.cell(2, col_idx)
        # Merge rows 0-2 for the step cell
        merged = c.merge(c2)
        bg = step.get('bg', COL_STEP_BG)
        set_cell_bg(merged, bg)
        border_col = step.get('border', '005AA8')
        for side in ['top','bottom','left','right']:
            set_cell_border(merged, **{side: {'val':'single','sz':8,'color':border_col}})
        p = merged.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        icon = step.get('icon', '')
        if icon:
            ir = p.add_run(icon + "\n")
            ir.font.size = Pt(14)
        r = p.add_run(step['label'])
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = step.get('color', COL_DARK_BLUE)
        if step.get('sub'):
            sp = merged.add_paragraph()
            sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            sp.paragraph_format.space_after = Pt(6)
            sr = sp.add_run(step['sub'])
            sr.font.size = Pt(8)
            sr.italic = True
        col_idx += 1
        # Arrow cell
        if i < len(steps) - 1:
            ac = tbl.cell(0, col_idx)
            ac2 = tbl.cell(2, col_idx)
            am = ac.merge(ac2)
            ap = am.paragraphs[0]
            ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ap.paragraph_format.space_before = Pt(16)
            ar = ap.add_run("→")
            ar.bold = True
            ar.font.size = Pt(16)
            ar.font.color.rgb = COL_ACCENT
            col_idx += 1
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_decision_flow(doc, title, flow_lines):
    """Add a BPMN-style process flow as structured text table."""
    add_heading(doc, title, level=3)
    for line in flow_lines:
        indent = line.get('indent', 0)
        shape = line.get('shape', 'step')
        text = line.get('text', '')
        sub = line.get('sub', '')
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(indent * 0.3)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        if shape == 'start':
            r = p.add_run(f"  ◉  START  ◉")
            r.bold = True; r.font.size = Pt(10); r.font.color.rgb = COL_GREEN
        elif shape == 'end':
            r = p.add_run(f"  ◉  END  ◉")
            r.bold = True; r.font.size = Pt(10); r.font.color.rgb = COL_RED
        elif shape == 'process':
            r = p.add_run(f"  ▣  {text}")
            r.bold = True; r.font.size = Pt(10); r.font.color.rgb = COL_DARK_BLUE
            if sub:
                r2 = p.add_run(f"  —  {sub}")
                r2.font.size = Pt(9); r2.italic = True
        elif shape == 'decision':
            r = p.add_run(f"  ◇  {text}")
            r.bold = True; r.font.size = Pt(10); r.font.color.rgb = COL_ACCENT
        elif shape == 'arrow':
            r = p.add_run(f"        ↓")
            r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x66,0x66,0x66)
        elif shape == 'branch_yes':
            r = p.add_run(f"  ✔  YES  →  {text}")
            r.font.size = Pt(9.5); r.font.color.rgb = COL_GREEN
        elif shape == 'branch_no':
            r = p.add_run(f"  ✖  NO   →  {text}")
            r.font.size = Pt(9.5); r.font.color.rgb = COL_RED
        elif shape == 'note':
            r = p.add_run(f"  ℹ  {text}")
            r.font.size = Pt(9); r.italic = True; r.font.color.rgb = RGBColor(0x55,0x55,0x88)
        elif shape == 'swimlane':
            p2 = doc.add_paragraph()
            tbl = doc.add_table(rows=1, cols=1)
            c = tbl.cell(0,0)
            set_cell_bg(c, COL_DARK_BLUE)
            sp = c.paragraphs[0]
            sp.paragraph_format.space_before = Pt(3)
            sp.paragraph_format.space_after = Pt(3)
            sp.paragraph_format.left_indent = Inches(0.1)
            sr = sp.add_run(f"  LANE:  {text}")
            sr.bold = True; sr.font.size = Pt(10); sr.font.color.rgb = COL_WHITE
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def add_role_badge(doc, role_name, description, permissions):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    # Left: role icon+name
    lc = tbl.cell(0, 0)
    lc.width = Inches(1.8)
    set_cell_bg(lc, COL_DARK_BLUE)
    lp = lc.paragraphs[0]
    lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lp.paragraph_format.space_before = Pt(8)
    lp.paragraph_format.space_after = Pt(4)
    lr = lp.add_run(role_name)
    lr.bold = True; lr.font.size = Pt(11); lr.font.color.rgb = COL_WHITE
    # Right: description
    rc = tbl.cell(0, 1)
    set_cell_bg(rc, COL_LIGHT_BG)
    rp = rc.paragraphs[0]
    rp.paragraph_format.left_indent = Inches(0.1)
    rp.paragraph_format.space_before = Pt(4)
    rr = rp.add_run(description + "\n")
    rr.font.size = Pt(10)
    for perm in permissions:
        pp = rc.add_paragraph()
        pp.paragraph_format.left_indent = Inches(0.15)
        pr = pp.add_run(f"✔  {perm}")
        pr.font.size = Pt(9.5)
        pr.font.color.rgb = COL_GREEN
    rp2 = rc.add_paragraph()
    rp2.paragraph_format.space_after = Pt(6)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_nav_path(doc, path_parts):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Inches(0.15)
    nr = p.add_run("  Navigation:  ")
    nr.bold = True; nr.font.size = Pt(9.5); nr.font.color.rgb = COL_MID_BLUE
    for i, part in enumerate(path_parts):
        pr = p.add_run(part)
        pr.bold = True; pr.font.size = Pt(9.5); pr.font.color.rgb = COL_DARK_BLUE
        if i < len(path_parts) - 1:
            ar = p.add_run("  ›  ")
            ar.font.size = Pt(9.5); ar.font.color.rgb = COL_ACCENT

def add_table_header_row(tbl, headers, bg=None):
    row = tbl.rows[0]
    for i, hdr in enumerate(headers):
        cell = row.cells[i]
        set_cell_bg(cell, bg or COL_DARK_BLUE)
        for side in ['top','bottom','left','right']:
            set_cell_border(cell, **{side: {'val':'single','sz':4,'color':'FFFFFF'}})
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(hdr)
        r.bold = True; r.font.size = Pt(10); r.font.color.rgb = COL_WHITE

def fill_table_row(tbl, row_idx, values, alt=False):
    bg = RGBColor(0xF5,0xF8,0xFF) if alt else COL_WHITE
    row = tbl.rows[row_idx]
    for i, val in enumerate(values):
        cell = row.cells[i]
        set_cell_bg(cell, bg)
        for side in ['top','bottom','left','right']:
            set_cell_border(cell, **{side: {'val':'single','sz':4,'color':'CCCCCC'}})
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.left_indent = Inches(0.05)
        if isinstance(val, tuple):
            r = p.add_run(val[0])
            r.bold = val[1]; r.font.size = Pt(9.5)
            if len(val) > 2: r.font.color.rgb = val[2]
        else:
            r = p.add_run(str(val))
            r.font.size = Pt(9.5)

def page_break(doc):
    doc.add_page_break()

# ─────────────────────────────────────────────
# DOCUMENT SETUP
# ─────────────────────────────────────────────

doc = Document()

# Margins
for section in doc.sections:
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.0)

# ─────────────────────────────────────────────
# COVER PAGE
# ─────────────────────────────────────────────

# Top colour bar
tbl_cover = doc.add_table(rows=1, cols=1)
tbl_cover.alignment = WD_TABLE_ALIGNMENT.CENTER
cc = tbl_cover.cell(0, 0)
set_cell_bg(cc, COL_DARK_BLUE)
trPr = tbl_cover.rows[0]._tr.get_or_add_trPr()
trH = OxmlElement('w:trHeight')
trH.set(qn('w:val'), '1800')
trH.set(qn('w:hRule'), 'exact')
trPr.append(trH)
cp = cc.paragraphs[0]
cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
cp.paragraph_format.space_before = Pt(28)
cr = cp.add_run("RECRUITMENT MANAGEMENT SYSTEM")
cr.bold = True; cr.font.size = Pt(22); cr.font.color.rgb = COL_WHITE
cp2 = cc.add_paragraph()
cp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
cp2r = cp2.add_run("Powered by Odoo 17")
cp2r.font.size = Pt(13); cp2r.italic = True; cp2r.font.color.rgb = RGBColor(0xAA, 0xCC, 0xFF)

doc.add_paragraph().paragraph_format.space_after = Pt(12)

p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
rt = p_title.add_run("COMPREHENSIVE USER GUIDE")
rt.bold = True; rt.font.size = Pt(28); rt.font.color.rgb = COL_DARK_BLUE

doc.add_paragraph().paragraph_format.space_after = Pt(6)

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
rs = p_sub.add_run("Step-by-Step Instructions for All User Roles\nwith BPMN Process Flowcharts")
rs.font.size = Pt(14); rs.font.color.rgb = COL_MID_BLUE; rs.italic = True

doc.add_paragraph().paragraph_format.space_after = Pt(24)

# Accent divider
tbl_div = doc.add_table(rows=1, cols=1)
dc = tbl_div.cell(0, 0)
set_cell_bg(dc, COL_ACCENT)
trPr2 = tbl_div.rows[0]._tr.get_or_add_trPr()
trH2 = OxmlElement('w:trHeight')
trH2.set(qn('w:val'), '120')
trH2.set(qn('w:hRule'), 'exact')
trPr2.append(trH2)
doc.add_paragraph().paragraph_format.space_after = Pt(18)

# Info block
info_data = [
    ("Document Version:", "1.0"),
    ("System:",           "Odoo 17 – Recruitment Enhancement Module"),
    ("Audience:",         "HR Coordinators, Line Managers, General Managers, CFO, HCM Managers, Interviewers, Applicants"),
    ("Classification:",   "Internal Use"),
]
for label, val in info_data:
    pi = doc.add_paragraph()
    pi.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ri1 = pi.add_run(f"{label}  ")
    ri1.bold = True; ri1.font.size = Pt(11); ri1.font.color.rgb = COL_DARK_BLUE
    ri2 = pi.add_run(val)
    ri2.font.size = Pt(11); ri2.font.color.rgb = COL_TEXT

page_break(doc)

# ─────────────────────────────────────────────
# TABLE OF CONTENTS (manual)
# ─────────────────────────────────────────────

add_heading(doc, "TABLE OF CONTENTS", level=1)
toc_entries = [
    ("1.", "Introduction to the Recruitment System", "3"),
    ("2.", "Understanding Odoo – First-Time User Orientation", "4"),
    ("3.", "System User Roles & Permissions", "5"),
    ("4.", "BPMN Process Flowcharts Overview", "7"),
    ("5.", "HR COORDINATOR – Complete User Guide", "10"),
    ("  5.1", "Creating a Recruitment Requisition", "10"),
    ("  5.2", "Managing the Approval Workflow", "16"),
    ("  5.3", "Publishing Job Adverts", "20"),
    ("  5.4", "Managing Applications & Pre-Screening", "22"),
    ("  5.5", "Running Shortlisting Sessions", "26"),
    ("  5.6", "Coordinating Background Checks", "30"),
    ("  5.7", "Processing Job Offers", "34"),
    ("6.", "LINE MANAGER – Complete User Guide", "38"),
    ("  6.1", "Reviewing & Approving a Requisition", "38"),
    ("  6.2", "Participating in Shortlisting", "42"),
    ("  6.3", "Conducting Interviews & Evaluations", "44"),
    ("7.", "GENERAL MANAGER – Complete User Guide", "48"),
    ("  7.1", "Reviewing & Approving a Requisition", "48"),
    ("  7.2", "Reviewing Shortlisting Recommendations", "51"),
    ("8.", "CFO – Complete User Guide", "53"),
    ("  8.1", "Reviewing Budget & Approving Requisition", "53"),
    ("  8.2", "Approving Job Offers", "56"),
    ("9.", "HCM MANAGER – Complete User Guide", "58"),
    ("  9.1", "Final Requisition Validation & HCM Checklist", "58"),
    ("  9.2", "Oversight of Recruitment Pipeline", "62"),
    ("10.", "INTERVIEWER / PANEL MEMBER – Complete User Guide", "64"),
    ("  10.1", "Signing Confidentiality Declaration", "64"),
    ("  10.2", "Conducting & Scoring Interviews", "66"),
    ("  10.3", "Submitting Interview Evaluations", "69"),
    ("11.", "BACKGROUND CHECK REVIEWER – Complete User Guide", "72"),
    ("12.", "APPLICANT (Portal User) – Complete User Guide", "76"),
    ("  12.1", "Finding & Applying for a Job", "76"),
    ("  12.2", "Completing the Pre-Screening Survey", "80"),
    ("  12.3", "Receiving Interview Notifications", "83"),
    ("  12.4", "Receiving & Accepting a Job Offer", "85"),
    ("13.", "System Administration & Configuration", "87"),
    ("14.", "Troubleshooting & FAQs", "90"),
    ("15.", "Glossary", "93"),
]

tbl_toc = doc.add_table(rows=len(toc_entries), cols=3)
tbl_toc.alignment = WD_TABLE_ALIGNMENT.LEFT
for i, (num, title, page) in enumerate(toc_entries):
    is_main = not num.startswith("  ")
    r0 = tbl_toc.rows[i].cells[0]
    r1 = tbl_toc.rows[i].cells[1]
    r2 = tbl_toc.rows[i].cells[2]
    r0.width = Inches(0.4)
    r2.width = Inches(0.5)
    p0 = r0.paragraphs[0]
    p0.paragraph_format.space_before = Pt(2 if is_main else 1)
    p0.paragraph_format.space_after = Pt(2 if is_main else 1)
    nr = p0.add_run(num.strip())
    nr.bold = is_main; nr.font.size = Pt(10.5 if is_main else 10)
    nr.font.color.rgb = COL_DARK_BLUE if is_main else COL_MID_BLUE
    p1 = r1.paragraphs[0]
    p1.paragraph_format.left_indent = Inches(0 if is_main else 0.15)
    tr = p1.add_run(title)
    tr.bold = is_main; tr.font.size = Pt(10.5 if is_main else 10)
    tr.font.color.rgb = COL_TEXT
    p2 = r2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pgr = p2.add_run(page)
    pgr.font.size = Pt(10); pgr.font.color.rgb = RGBColor(0x88,0x88,0x88)

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 1: INTRODUCTION
# ─────────────────────────────────────────────

add_heading(doc, "1.  Introduction to the Recruitment System", level=1)
add_body(doc, "This User Guide covers the Recruitment Enhancement Module built on the Odoo 17 platform. "
    "It is designed for first-time users across all roles and explains every step from creating a job "
    "requisition to onboarding a hired employee.", space_after=8)
add_body(doc, "The system enforces a structured, multi-stage, approval-driven recruitment process that "
    "ensures compliance, fairness, Employment Equity (EE) adherence, and full auditability.", space_after=8)

add_heading(doc, "What the System Does", level=2)
features = [
    ("Workforce Planning:", " Manage job requisitions with multi-level approval workflows."),
    ("Job Advertising:", " Publish job adverts internally and externally with configurable channels."),
    ("Online Applications:", " Applicants apply via a web portal; their data is captured automatically."),
    ("Pre-Screening:", " Automated surveys filter candidates before human review."),
    ("Shortlisting:", " Structured panel sessions to review and shortlist candidates."),
    ("Interviews:", " Schedule, run, and score interview sessions with panel members."),
    ("Background Checks:", " Verify candidate credentials with documented audit trails."),
    ("Offer Management:", " Create, approve, and send employment offers with digital tracking."),
    ("Compliance & EE:", " Track Employment Equity targets and compliance at every stage."),
]
for b, d in features:
    add_bullet(doc, d, bold_prefix=b)

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 2: ODOO ORIENTATION
# ─────────────────────────────────────────────

add_heading(doc, "2.  Understanding Odoo – First-Time User Orientation", level=1)
add_body(doc, "Odoo is a web-based business application. You access it through a web browser (Google Chrome "
    "or Microsoft Edge recommended). There is no software to install on your computer.", space_after=8)

add_heading(doc, "2.1  Logging In", level=2)
add_nav_path(doc, ["Open your web browser", "Enter the Odoo URL provided by your IT department", "Login page appears"])
add_screenshot_placeholder(doc, "Figure 2.1 – Odoo Login Screen",
    "Shows the Odoo login page with Email and Password fields, and a Log In button")
add_numbered(doc, "Open your web browser (Chrome or Edge).")
add_numbered(doc, "Type the Odoo URL in the address bar (e.g., https://yourcompany.odoo.com) and press Enter.")
add_numbered(doc, "On the Login page, enter your Email Address in the first field.")
add_numbered(doc, "Enter your Password in the second field.")
add_numbered(doc, "Click the blue Log In button.")
add_note_box(doc, "If you do not have login credentials, contact your IT Administrator or HR department to set up your account.")

add_heading(doc, "2.2  The Odoo Home Screen (Apps Menu)", level=2)
add_body(doc, "After logging in, you will see the main Home screen showing application icons (like a smartphone home screen). "
    "Each icon represents a module. You will primarily work in the Recruitment module.", space_after=6)
add_screenshot_placeholder(doc, "Figure 2.2 – Odoo Home Screen / Apps Menu",
    "Shows the grid of application icons. The Recruitment icon (person with magnifier) is highlighted")
add_note_box(doc, "Click the Recruitment icon to open the Recruitment module. If you cannot see it, use the Search bar at the top of the Home screen.")

add_heading(doc, "2.3  Navigating the Interface", level=2)
nav_items = [
    ("Top Menu Bar:", " The dark bar at the top of every page. Contains the main navigation links for the current module."),
    ("Left Sidebar (Menu):", " Below the top bar — shows sub-sections like Workforce Planning, Candidates, Interviews, etc."),
    ("Main Content Area:", " The large area in the centre — displays lists, forms, or kanban boards."),
    ("Breadcrumb Trail:", " Just above the content area — shows where you are (e.g., Recruitment › Requisitions › New Requisition)."),
    ("Action Buttons:", " Blue, orange, or grey buttons at the top-left of forms — perform actions like Save, Submit, Approve."),
    ("Search Bar:", " At the top of list/kanban views — type to filter records."),
    ("Filters & Group By:", " Dropdown arrows next to the Search bar — pre-defined filter options."),
]
for b, d in nav_items:
    add_bullet(doc, d, bold_prefix=b)
add_screenshot_placeholder(doc, "Figure 2.3 – Odoo Interface Layout",
    "Annotated screenshot showing: (A) Top Navigation Bar, (B) Left Menu, (C) Breadcrumb, (D) Search Bar, (E) Content Area, (F) Action Buttons")

add_heading(doc, "2.4  Saving Records", level=2)
add_body(doc, "Odoo auto-saves some fields, but always click the Save button (or the cloud icon) before "
    "navigating away from a form. If you leave without saving, a prompt will ask if you want to discard changes.", space_after=6)
add_note_box(doc, "The Save button appears in the top-left of a form when you are editing. It looks like a floppy disk icon or says 'Save manually'.", bg_color=COL_STEP_BG, border_color=COL_MID_BLUE)

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 3: USER ROLES & PERMISSIONS
# ─────────────────────────────────────────────

add_heading(doc, "3.  System User Roles & Permissions", level=1)
add_body(doc, "The Recruitment system has distinct user roles. Each role has specific permissions that control "
    "what menus, records, and actions are available. Your IT Administrator assigns your role when setting up "
    "your account.", space_after=8)

add_screenshot_placeholder(doc, "Figure 3.1 – User Roles Overview",
    "Diagram showing the 7 user roles as circles with connecting lines to their primary activities")

roles = [
    ("HR COORDINATOR\n(Recruitment Manager)",
     "The primary administrator of the recruitment process. Manages requisitions, applications, shortlisting, interviews, background checks, and offers.",
     ["Create & manage requisitions", "Publish job adverts", "Manage all applications", "Create shortlisting & interview sessions",
      "Process background checks", "Create & send job offers", "Full read/write access to all recruitment records"]),
    ("LINE MANAGER",
     "Approves requisitions at the first approval stage. Participates in shortlisting and interviews for their department.",
     ["Receive approval requests via email", "Review and sign requisitions", "Participate in shortlisting panels",
      "Conduct interviews and submit evaluations"]),
    ("GENERAL MANAGER",
     "Approves requisitions at the second approval stage. Reviews shortlisting outcomes.",
     ["Receive approval requests via email", "Review and sign requisitions at Stage 2",
      "Review shortlisting recommendations"]),
    ("CFO (Chief Finance Officer)",
     "Approves the financial justification at Stage 3 of the requisition approval.",
     ["Receive approval requests via email", "Review budget justification",
      "Sign and approve/reject at Stage 3", "Approve job offers requiring CFO sign-off"]),
    ("HCM MANAGER\n(Human Capital Management)",
     "Final approver of requisitions. Runs the HCM compliance checklist before formally approving.",
     ["Complete HCM checklist", "Final sign-off on requisitions",
      "Oversight of full recruitment pipeline", "Approve background check results"]),
    ("INTERVIEWER / PANEL MEMBER",
     "Invited to conduct interviews. Signs confidentiality declarations and scores candidates.",
     ["View assigned interview sessions", "Sign confidentiality declaration",
      "Score candidates during interviews", "Submit interview evaluations"]),
    ("APPLICANT (Portal User)",
     "External or internal candidate who applies for a job through the web portal.",
     ["Search and view job listings", "Submit an online application",
      "Complete pre-screening survey", "Receive email notifications about their application"]),
]

for role, desc, perms in roles:
    add_role_badge(doc, role, desc, perms)

add_heading(doc, "3.1  Role Assignment", level=2)
add_body(doc, "Roles are assigned by your IT Administrator in Odoo Settings. To check your current role:", space_after=4)
add_nav_path(doc, ["Settings", "Users & Companies", "Users", "Click your name"])
add_body(doc, "Your active groups (roles) are shown in the Access Rights tab of your user profile.", space_after=8)

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 4: BPMN PROCESS FLOWCHARTS
# ─────────────────────────────────────────────

add_heading(doc, "4.  BPMN Process Flowcharts Overview", level=1)
add_body(doc, "The following flowcharts illustrate the complete end-to-end recruitment process. "
    "Read these before using the system so you understand where each step fits in the overall workflow.", space_after=8)

# ── 4.1 MASTER END-TO-END FLOW ──
add_heading(doc, "4.1  Master End-to-End Recruitment Process", level=2)
add_bpmn_flow(doc, "", [
    {'label': 'PHASE 1\nRequisition\nCreation', 'icon': '📋', 'bg': RGBColor(0xE3,0xF2,0xFD), 'border': '005AA8'},
    {'label': 'PHASE 2\nApproval\nWorkflow', 'icon': '✍', 'bg': RGBColor(0xFFF3,0xE0,0x00)[:3] if False else RGBColor(0xFF,0xF3,0xE0), 'border': 'F08400'},
    {'label': 'PHASE 3\nJob\nAdvertising', 'icon': '📢', 'bg': RGBColor(0xE8,0xF5,0xE9), 'border': '1A7A3C'},
    {'label': 'PHASE 4\nApplications &\nPre-Screening', 'icon': '📝', 'bg': RGBColor(0xF3,0xE5,0xF5), 'border': '7B1FA2'},
    {'label': 'PHASE 5\nShortlisting', 'icon': '🎯', 'bg': RGBColor(0xE0,0xF7,0xFA), 'border': '0097A7'},
    {'label': 'PHASE 6\nInterviews', 'icon': '🤝', 'bg': RGBColor(0xFCE4,0xEC,0x00)[:3] if False else RGBColor(0xFC,0xE4,0xEC), 'border': 'C0392B'},
    {'label': 'PHASE 7\nBackground\nChecks', 'icon': '🔍', 'bg': RGBColor(0xF1,0xF8,0xE9), 'border': '558B2F'},
    {'label': 'PHASE 8\nOffer &\nOnboarding', 'icon': '🎉', 'bg': RGBColor(0xE8,0xEA,0xF6), 'border': '3949AB'},
])

# ── 4.2 REQUISITION APPROVAL ──
add_heading(doc, "4.2  Requisition Approval BPMN Flow", level=2)
add_body(doc, "SWIM LANES: Each coloured lane shows which user role performs that step.", space_after=4)
add_decision_flow(doc, "Requisition Approval Process", [
    {'shape': 'swimlane', 'text': 'HR COORDINATOR'},
    {'shape': 'process', 'text': 'Create Requisition', 'sub': 'Recruitment › Workforce Planning › Requisition Requests › New', 'indent': 0},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'process', 'text': 'Fill all tabs (Position, Business Justification, Job Details, Requirements, Screening, EE, Documents)', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'process', 'text': 'Click "Submit" button', 'sub': 'State changes: Draft → In Process', 'indent': 0},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'process', 'text': 'Click "Start Approval Process"', 'sub': 'State: In Process → Approval In Process', 'indent': 0},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'LINE MANAGER  (Stage 1 Approval)'},
    {'shape': 'process', 'text': 'Receives email notification with link to requisition', 'indent': 0},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'process', 'text': 'Opens requisition, reviews all tabs', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'decision', 'text': 'Approve or Reject?', 'indent': 0},
    {'shape': 'branch_yes', 'text': 'Clicks "Sign" → enters signature → Stage 1 APPROVED', 'indent': 1},
    {'shape': 'branch_no', 'text': 'Clicks "Reject" → enters reason → returns to HR Coordinator', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'GENERAL MANAGER  (Stage 2 Approval)'},
    {'shape': 'process', 'text': 'Receives email notification', 'indent': 0},
    {'shape': 'decision', 'text': 'Approve or Reject?', 'indent': 0},
    {'shape': 'branch_yes', 'text': 'Signs → Stage 2 APPROVED → advances to CFO', 'indent': 1},
    {'shape': 'branch_no', 'text': 'Rejects with reason → returns to HR Coordinator', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'CFO  (Stage 3 Approval)'},
    {'shape': 'process', 'text': 'Receives email notification', 'indent': 0},
    {'shape': 'decision', 'text': 'Approve budget & Approve or Reject?', 'indent': 0},
    {'shape': 'branch_yes', 'text': 'Signs → Stage 3 APPROVED → advances to HCM', 'indent': 1},
    {'shape': 'branch_no', 'text': 'Rejects → returns to HR Coordinator', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'HCM MANAGER  (Stage 4 – Final Validation)'},
    {'shape': 'process', 'text': 'Receives email notification', 'indent': 0},
    {'shape': 'process', 'text': 'Completes HCM Checklist (5 items)', 'indent': 1},
    {'shape': 'decision', 'text': 'All checklist items complete?', 'indent': 0},
    {'shape': 'branch_yes', 'text': 'Signs → Requisition FULLY APPROVED', 'indent': 1},
    {'shape': 'branch_no', 'text': 'Requests missing documents before signing', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'HR COORDINATOR  (Post-Approval)'},
    {'shape': 'process', 'text': 'Clicks "Recruitment In Process"', 'sub': 'State: Approved → Recruitment In Process', 'indent': 0},
    {'shape': 'process', 'text': 'Creates Job Position and publishes advert', 'indent': 1},
    {'shape': 'end'},
])

# ── 4.3 APPLICATION & SCREENING FLOW ──
add_heading(doc, "4.3  Application & Pre-Screening BPMN Flow", level=2)
add_decision_flow(doc, "Application Lifecycle", [
    {'shape': 'swimlane', 'text': 'APPLICANT (Portal)'},
    {'shape': 'process', 'text': 'Visits company website › Clicks Jobs/Careers', 'indent': 0},
    {'shape': 'process', 'text': 'Selects job listing and clicks "Apply Now"', 'indent': 0},
    {'shape': 'process', 'text': 'Fills application form (personal details, qualifications, CV upload, declarations)', 'indent': 1},
    {'shape': 'process', 'text': 'Submits application → receives acknowledgement email', 'indent': 0},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'SYSTEM (Automated)'},
    {'shape': 'process', 'text': 'Creates HR Applicant record in Odoo', 'indent': 0},
    {'shape': 'process', 'text': 'Sends pre-screening survey link to applicant (if enabled)', 'indent': 0},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'APPLICANT (Portal)'},
    {'shape': 'process', 'text': 'Completes pre-screening survey', 'indent': 0},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'SYSTEM (Automated)'},
    {'shape': 'decision', 'text': 'Elimination question failed OR score below threshold?', 'indent': 0},
    {'shape': 'branch_yes', 'text': 'Applicant auto-moved to Staging or Rejected stage', 'indent': 1},
    {'shape': 'branch_no', 'text': 'Applicant auto-moved to Qualification stage', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'HR COORDINATOR'},
    {'shape': 'process', 'text': 'Reviews applicants in Qualification stage', 'indent': 0},
    {'shape': 'process', 'text': 'Creates Shortlisting Session with panel members', 'indent': 0},
    {'shape': 'end'},
])

# ── 4.4 INTERVIEW & HIRING FLOW ──
add_heading(doc, "4.4  Interview, Background Check & Offer BPMN Flow", level=2)
add_decision_flow(doc, "Interview through to Hiring", [
    {'shape': 'swimlane', 'text': 'HR COORDINATOR'},
    {'shape': 'process', 'text': 'Creates Interview Session linked to Shortlisting', 'indent': 0},
    {'shape': 'process', 'text': 'Adds panel members and collects confidentiality declarations', 'indent': 1},
    {'shape': 'process', 'text': 'Clicks "Prepare" then "Start" to begin session', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'INTERVIEW PANEL MEMBERS'},
    {'shape': 'process', 'text': 'Score each candidate (Technical, Competency, Culture Fit)', 'indent': 0},
    {'shape': 'process', 'text': 'Collect candidate declarations and signatures', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'HR COORDINATOR / PANEL CHAIR'},
    {'shape': 'process', 'text': 'Select Recommended Candidate and Reserve candidates', 'indent': 0},
    {'shape': 'process', 'text': 'Click "Done" to finalise interview session', 'indent': 1},
    {'shape': 'process', 'text': 'Click "Create Background Checks" to auto-create 5 mandatory checks', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'BACKGROUND CHECK REVIEWER'},
    {'shape': 'process', 'text': 'For each check type: updates status (Clear / Concern / Failed)', 'indent': 0},
    {'shape': 'decision', 'text': 'All 5 mandatory checks Clear?', 'indent': 0},
    {'shape': 'branch_yes', 'text': 'Proceed to Offer creation', 'indent': 1},
    {'shape': 'branch_no', 'text': 'Escalate concern or reject candidate', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'HR COORDINATOR'},
    {'shape': 'process', 'text': 'Creates Recruitment Offer record', 'indent': 0},
    {'shape': 'process', 'text': 'Sets salary, contract type, start date, uploads offer letter', 'indent': 1},
    {'shape': 'process', 'text': 'Clicks "Submit for Approval"', 'indent': 1},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'CFO / FINAL APPROVER'},
    {'shape': 'process', 'text': 'Reviews offer and clicks "Approve"', 'indent': 0},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'HR COORDINATOR'},
    {'shape': 'process', 'text': 'Clicks "Send Offer" — email sent to candidate', 'indent': 0},
    {'shape': 'arrow', 'indent': 0},
    {'shape': 'swimlane', 'text': 'HR COORDINATOR (after candidate response)'},
    {'shape': 'decision', 'text': 'Candidate Accepts or Declines?', 'indent': 0},
    {'shape': 'branch_yes', 'text': 'Clicks "Mark Accepted" → applicant moves to Hired → Requisition Done', 'indent': 1},
    {'shape': 'branch_no', 'text': 'Clicks "Mark Rejected" → consider reserve candidate', 'indent': 1},
    {'shape': 'end'},
])

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 5: HR COORDINATOR GUIDE
# ─────────────────────────────────────────────

add_heading(doc, "5.  HR COORDINATOR – Complete User Guide", level=1)
add_body(doc, "This section covers every task performed by the HR Coordinator (Recruitment Manager). "
    "The HR Coordinator is the primary user of the system and manages the full recruitment lifecycle.", space_after=8)

# ── 5.1 CREATING A REQUISITION ──
add_heading(doc, "5.1  Creating a Recruitment Requisition", level=2)
add_body(doc, "A Recruitment Requisition is the formal request to fill a job position. It must be completed "
    "and approved before any recruitment activity begins.", space_after=6)
add_nav_path(doc, ["Recruitment", "Workforce Planning", "Requisition Requests", "New"])
add_screenshot_placeholder(doc, "Figure 5.1.1 – Requisition Requests List View",
    "Shows the list of all requisitions with columns: Reference, Job, Department, Status, Approval Status, Responsible. A blue 'New' button is visible at top-left.")

add_step_box(doc, 1, "Open the Recruitment Module",
    ["Click the main menu icon (☰) or navigate to the top bar.",
     "Click 'Recruitment' from the top navigation menu.",
     "The Recruitment dashboard opens."])

add_step_box(doc, 2, "Navigate to Requisition Requests",
    ["In the left sidebar, find the 'Workforce Planning' section.",
     "Click 'Requisition Requests'.",
     "A list of all existing requisitions appears."])

add_step_box(doc, 3, "Create a New Requisition",
    ["Click the blue 'New' button at the top-left of the list.",
     "A blank Requisition form opens.",
     "The system automatically generates a reference number (e.g., REQ/2024/001)."],
    note="The form has multiple tabs at the top. You must complete all required fields (marked with a red asterisk *) before submitting.")

add_screenshot_placeholder(doc, "Figure 5.1.2 – New Requisition Form – Position Overview Tab",
    "Shows the Requisition form with tabs: Position Overview, Business Justification, Job Details, Requirements & Competencies, Screening & Interview Setup, EE & Compliance, Documents. The Position Overview tab is active.")

add_heading(doc, "Tab 1: Position Overview", level=3)
add_body(doc, "This tab captures the basic details of the position being requested.", space_after=4)

fields_tab1 = [
    ("Job Position *", "Click the dropdown and select the job position, or type to search. If the position does not exist, type the name and click 'Create'."),
    ("Department *", "Select the department this position belongs to."),
    ("Company *", "Auto-filled from your company settings. Change if necessary."),
    ("Position Type *", "Select 'Existing Position' (replacing someone) or 'New Position' (brand new role)."),
    ("Number of Positions *", "Enter how many vacancies need to be filled."),
    ("Job Grade", "Enter the salary grade or band for this position."),
    ("Reports To (Title)", "Enter the job title this position reports to."),
    ("Previous Incumbent", "If replacing someone, enter their name here."),
    ("HR Coordinator *", "Select the HR Coordinator responsible for this requisition (usually yourself)."),
    ("Sourcing Method", "Select Internal, External, or Both."),
    ("Advert Days", "Number of days the advert will run (default: 10 days)."),
]

tbl_fields = doc.add_table(rows=len(fields_tab1)+1, cols=2)
tbl_fields.alignment = WD_TABLE_ALIGNMENT.LEFT
add_table_header_row(tbl_fields, ["Field Name", "What to Enter / How to Use It"])
for i, (fname, fdesc) in enumerate(fields_tab1):
    fill_table_row(tbl_fields, i+1, [(fname, True, COL_DARK_BLUE), fdesc], alt=(i%2==0))

doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_heading(doc, "Tab 2: Business Justification", level=3)
add_body(doc, "Explain WHY this position is needed. This information is reviewed by Line Managers, General Managers, and the CFO.", space_after=4)
fields_tab2 = [
    ("Business Justification *", "Write a clear explanation of why this role is required."),
    ("Business Strategy Alignment", "Explain how this role supports the company's strategic goals."),
    ("Impact if Not Filled", "Describe the risk or impact to the business if the position is not filled."),
    ("Budget Availability", "Enter the confirmed budget amount for this position."),
]
tbl_f2 = doc.add_table(rows=len(fields_tab2)+1, cols=2)
add_table_header_row(tbl_f2, ["Field Name", "What to Enter"])
for i, (fn, fd) in enumerate(fields_tab2):
    fill_table_row(tbl_f2, i+1, [(fn, True, COL_DARK_BLUE), fd], alt=(i%2==0))
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_heading(doc, "Tab 3: Job Details", level=3)
add_body(doc, "Define the role itself — what the job entails and what qualifications are required.", space_after=4)
fields_tab3 = [
    ("Job Description *", "Write or paste the full job description. You can use formatting (bold, bullets) in this rich-text editor."),
    ("Job Summary", "A shorter summary shown in the public job advert."),
    ("Years of Experience", "Minimum years of experience required (numeric value)."),
    ("Minimum Qualifications", "e.g., 'National Diploma in Human Resources'."),
    ("Required Experience", "Describe the type of experience required."),
    ("Main Purpose of Job", "One-paragraph overview of the role's purpose."),
    ("Skills", "Click 'Add a line' to add required skills. Search from the skill library."),
    ("Certifications", "List any required professional certifications."),
    ("Qualification Level", "Select the required qualification (Grade 11 through Doctoral Degree)."),
    ("Work Level", "Select: Executive, Senior, Middle, Junior, Skilled, Semi-Skilled, or Unskilled."),
]
tbl_f3 = doc.add_table(rows=len(fields_tab3)+1, cols=2)
add_table_header_row(tbl_f3, ["Field Name", "What to Enter"])
for i, (fn, fd) in enumerate(fields_tab3):
    fill_table_row(tbl_f3, i+1, [(fn, True, COL_DARK_BLUE), fd], alt=(i%2==0))
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_heading(doc, "Tab 4: Requirements & Competencies", level=3)
add_body(doc, "List competencies, soft skills, and behavioural requirements for the role. "
    "Add skills using the 'Add a line' button. Each skill should have a type, name, and level.", space_after=6)
add_screenshot_placeholder(doc, "Figure 5.1.3 – Requirements & Competencies Tab",
    "Shows the skills table with columns: Skill Type, Skill, Skill Level, Progress. An 'Add a line' button is below the table.")

add_heading(doc, "Tab 5: Screening & Interview Setup", level=3)
add_body(doc, "Configure the pre-screening survey that candidates must complete after applying.", space_after=4)
fields_tab5 = [
    ("Pre-Screening Required", "Tick this checkbox to enable the pre-screening survey (ON by default)."),
    ("Survey / Pre-screening Form *", "Select an existing survey from the dropdown, or click 'New' to create one."),
    ("Interview Questions", "Add questions by clicking 'Add a line'. These become part of the survey."),
    ("Elimination Questions", "Tick 'Elimination' on any question that should automatically disqualify a candidate if answered incorrectly."),
    ("Advertising Channels", "Click 'Add a line' to select where the job will be advertised (e.g., LinkedIn, Indeed, Company Website)."),
    ("Internal Advert Required", "Tick if the job should be advertised internally first."),
    ("External Advert Required", "Tick if the job should be advertised on external platforms."),
    ("Website Published", "Tick to make the job visible on the company's public website."),
    ("Publish Date / Unpublish Date", "Set the start and end dates for the advert."),
]
tbl_f5 = doc.add_table(rows=len(fields_tab5)+1, cols=2)
add_table_header_row(tbl_f5, ["Field Name", "What to Enter"])
for i, (fn, fd) in enumerate(fields_tab5):
    fill_table_row(tbl_f5, i+1, [(fn, True, COL_DARK_BLUE), fd], alt=(i%2==0))
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_heading(doc, "Tab 6: EE & Compliance", level=3)
add_body(doc, "Set Employment Equity targets for this position.", space_after=4)
add_bullet(doc, "Tick 'Youth Target' if this position targets candidates aged 18–35.")
add_bullet(doc, "Tick 'Women Target' if this position targets women candidates.")
add_bullet(doc, "Tick 'PWD Target' if this position targets Persons with Disabilities.")
add_note_box(doc, "These EE targets are used during shortlisting to ensure compliance. They are visible to the shortlisting panel.")

add_heading(doc, "Tab 7: Documents", level=3)
add_body(doc, "Upload supporting documents required for the approval process.", space_after=4)
doc_fields = [
    ("Requisition Form File", "Upload the signed requisition form (PDF or Word)."),
    ("Job Description File", "Upload the formal job description document."),
    ("Organogram File", "Upload the organisational chart showing the position. (REQUIRED for HCM approval)"),
    ("Budget File", "Upload the finance/budget approval document."),
]
tbl_d = doc.add_table(rows=len(doc_fields)+1, cols=2)
add_table_header_row(tbl_d, ["Document", "Purpose"])
for i, (dn, dd) in enumerate(doc_fields):
    fill_table_row(tbl_d, i+1, [(dn, True, COL_DARK_BLUE), dd], alt=(i%2==0))
doc.add_paragraph().paragraph_format.space_after = Pt(6)
add_note_box(doc, "The Organogram file is MANDATORY for HCM approval. The HCM Manager will not be able to complete their checklist without it.")

add_heading(doc, "Saving and Submitting the Requisition", level=3)
add_step_box(doc, 4, "Save the Requisition",
    ["Click the Save button (cloud/floppy disk icon at top-left of the form).",
     "The form is saved as a Draft. You can return and edit it at any time while it is in Draft state."])

add_step_box(doc, 5, "Submit for Review",
    ["Once all required fields are complete, click the 'Submit' button.",
     "The state changes from 'Draft' to 'In Process'.",
     "You will see the status bar at the top change to reflect this."],
    note="After submitting, you cannot edit the main fields. To make changes, you must click 'Reset to Draft' first.")

add_screenshot_placeholder(doc, "Figure 5.1.4 – Submitted Requisition showing Status Bar",
    "Shows the requisition form with the status bar at the top: Draft > In Process > Approval In Process > Approved > Recruitment In Process > Done. 'In Process' is highlighted.")

page_break(doc)

# ── 5.2 MANAGING THE APPROVAL WORKFLOW ──
add_heading(doc, "5.2  Managing the Approval Workflow", level=2)
add_body(doc, "After submitting, you need to set up the approval team and start the approval process. "
    "The approval passes through four stages: Line Manager → General Manager → CFO → HCM Manager.", space_after=8)

add_heading(doc, "Setting Up Approval Lines", level=3)
add_body(doc, "Before starting the approval process, you must configure who will approve the requisition "
    "at each stage. This is done in the Approval section of the requisition form.", space_after=6)

add_step_box(doc, 1, "Scroll to the Approval Section",
    ["On the requisition form, scroll down below the tabs.",
     "You will see four sections: Line Manager, General Manager, CFO, and HCM Manager.",
     "Each section has a table where you can add approvers."])

add_step_box(doc, 2, "Add Line Manager Approvers",
    ["In the 'Line Manager' section, click 'Add a line'.",
     "In the User column, click the dropdown and search for the Line Manager's name.",
     "Set Sequence (1, 2, 3...) — this controls the order in which they are notified.",
     "Tick 'Required' if this approver MUST sign before moving to the next stage.",
     "Click 'Add a line' again to add more Line Manager approvers if needed."])

add_screenshot_placeholder(doc, "Figure 5.2.1 – Approval Lines Configuration",
    "Shows the approval section with four sub-tables. The Line Manager table has 2 rows: User='John Smith', Sequence=1, Status=Pending; User='Jane Doe', Sequence=2, Status=Pending.")

add_step_box(doc, 3, "Add General Manager, CFO, and HCM Manager Approvers",
    ["Repeat the same process for each of the remaining three approval stages.",
     "Each stage can have multiple approvers who sign in sequence.",
     "At minimum, each stage needs one approver."])

add_step_box(doc, 4, "Start the Approval Process",
    ["Click the 'Start Approval Process' button at the top of the form.",
     "The state changes to 'Approval In Process'.",
     "An email is automatically sent to the FIRST Line Manager approver (Sequence 1).",
     "The system will handle notifying subsequent approvers as each stage is completed."],
    note="The approval is TURN-BASED. Only the current active approver can sign. They receive an email with a direct link.")

add_heading(doc, "Monitoring Approval Progress", level=3)
add_body(doc, "You can track the approval status at any time by opening the requisition.", space_after=4)
add_bullet(doc, "The Approval Status field shows: Not Started, Partially Approved, Fully Approved, or Rejected.")
add_bullet(doc, "Each approval line shows the Status: Pending, Approved, or Rejected.")
add_bullet(doc, "The date and time of each signature is automatically recorded.")
add_bullet(doc, "The Current Approver field shows who needs to act next.")
add_screenshot_placeholder(doc, "Figure 5.2.2 – Approval Progress View",
    "Shows the requisition with approval lines. Line Manager row 1 shows Status='Approved', signed date. Line Manager row 2 shows Status='Pending', highlighted in orange.")

add_heading(doc, "Handling Rejections", level=3)
add_body(doc, "If an approver rejects the requisition, you will receive an email notification. "
    "To resubmit after addressing the rejection:", space_after=4)
add_numbered(doc, "Open the rejected requisition.")
add_numbered(doc, "Read the rejection reason in the approval line's Comment field or the Approval Log.")
add_numbered(doc, "Click 'Reset to Draft' button.")
add_numbered(doc, "Make the necessary changes (edit any tab).")
add_numbered(doc, "Click 'Submit' again, then 'Start Approval Process'.")
add_note_box(doc, "The Approval Log at the bottom of the form records every approval decision with timestamps for audit purposes.")

page_break(doc)

# ── 5.3 PUBLISHING JOB ADVERTS ──
add_heading(doc, "5.3  Publishing Job Adverts", level=2)
add_body(doc, "Once the requisition is approved, you can publish the job advert and begin accepting applications.", space_after=6)
add_nav_path(doc, ["Recruitment", "Workforce Planning", "Job Positions", "Select Job"])

add_step_box(doc, 1, "Create the Job Position (if not already created)",
    ["Open the approved requisition.",
     "Click the 'Create Job Position' button at the top.",
     "A new Job Position record is created, pre-filled with data from the requisition.",
     "The Job Position appears in Recruitment › Workforce Planning › Job Positions."])

add_step_box(doc, 2, "Generate the Job Advert PDF",
    ["On the job position form, click 'View Advert PDF' or 'Generate Advert PDF'.",
     "A PDF is generated containing the full job description, requirements, and application instructions.",
     "Download or save this PDF for distributing to advertising channels."])

add_step_box(doc, 3, "Publish on Website",
    ["On the requisition form, go to the Screening & Interview Setup tab.",
     "Tick the 'Website Published' checkbox.",
     "Set the 'Publish Date' (today's date or a future date).",
     "Set the 'Unpublish Date' (when applications close).",
     "Save the record. The job now appears on the company's careers page."])

add_screenshot_placeholder(doc, "Figure 5.3.1 – Job Position on Company Careers Page",
    "Shows the public-facing job listing on the company website with: Job Title, Department, Location, Summary, Requirements, and an 'Apply Now' button.")

add_note_box(doc, "To view what the job looks like to applicants, open a private/incognito browser window and visit your company's /jobs page.")

page_break(doc)

# ── 5.4 MANAGING APPLICATIONS ──
add_heading(doc, "5.4  Managing Applications & Pre-Screening", level=2)
add_body(doc, "As applications come in, they appear in the Applications view. This section explains how to "
    "review applications, monitor pre-screening scores, and move candidates to the next stage.", space_after=6)
add_nav_path(doc, ["Recruitment", "Candidates", "Applications"])

add_screenshot_placeholder(doc, "Figure 5.4.1 – Applications Kanban Board",
    "Shows the Kanban board with columns: New, Qualification, First Interview, Second Interview, Contract Proposal, Hired. Cards show candidate names and screening scores.")

add_step_box(doc, 1, "Access Applications",
    ["Click 'Candidates' in the left menu.",
     "Click 'Applications'.",
     "Applications appear in a Kanban (card) view by default.",
     "Switch to List view by clicking the list icon (top-right of the content area) for a tabular view."])

add_step_box(doc, 2, "Filter by Job / Requisition",
    ["In the Search bar at the top, type the job title or requisition number.",
     "Or click the 🔽 Filters dropdown and select 'My Requisition' or filter by 'Job Position'.",
     "Click 'Group By' › 'Job Position' to group candidates by job."])

add_step_box(doc, 3, "Open an Application",
    ["Click on any candidate card (Kanban) or row (List) to open their application form.",
     "The application form shows all personal details, qualifications, CV, and screening score."])

add_screenshot_placeholder(doc, "Figure 5.4.2 – Application Form",
    "Shows the applicant form with tabs: Candidate Info, Qualifications, Screening Results, Interview Notes. The screening score badge shows '72/100' in green.")

add_heading(doc, "Understanding the Pre-Screening Results", level=3)
add_body(doc, "If pre-screening is enabled, candidates complete a survey before their application is reviewed. "
    "The system automatically calculates their score.", space_after=4)
screening_info = [
    ("Screening Point:", " The score out of 100 calculated from the survey responses."),
    ("Pre-Screening State:", " 'Not started yet', 'In Progress', or 'Completed'."),
    ("Elimination Questions:", " If a candidate fails an elimination question, they are auto-moved to Staging or Rejected."),
    ("View Survey Answers:", " Click 'View Pre-Screening Answers' button to see their exact responses."),
]
for b, d in screening_info:
    add_bullet(doc, d, bold_prefix=b)

add_step_box(doc, 4, "Manually Move a Candidate",
    ["To move a candidate to the next stage, open their application.",
     "Click the stage indicator in the status bar at the top of the form (e.g., click 'Qualification').",
     "Or drag-and-drop the card to a different column in Kanban view.",
     "To move to Qualification specifically, click the 'Move to Qualification' button."])

add_note_box(doc, "The system automatically moves candidates based on pre-screening scores. Manual movement is available for edge cases or special circumstances.", bg_color=COL_STEP_BG, border_color=COL_MID_BLUE)

add_heading(doc, "Candidate Profile vs Application", level=3)
add_body(doc, "The system stores an Applicant Profile (permanent record) separate from each Application. "
    "This means the same person can apply for multiple positions and their profile persists.", space_after=4)
add_bullet(doc, "To view a candidate's full profile: Recruitment › Workforce Planning › Applicant Profiles")
add_bullet(doc, "The profile shows all previous applications, skills, and qualifications in one place.")

page_break(doc)

# ── 5.5 SHORTLISTING ──
add_heading(doc, "5.5  Running Shortlisting Sessions", level=2)
add_body(doc, "After pre-screening, a formal shortlisting session is conducted where a panel reviews all "
    "qualifying candidates and selects those to be invited for interviews.", space_after=6)
add_nav_path(doc, ["Recruitment", "Workforce Planning", "Requisition Requests", "Open Requisition", "Open Shortlisting"])

add_step_box(doc, 1, "Open the Shortlisting List",
    ["Open the relevant requisition.",
     "Click the 'Open Shortlisting' smart button (shows count of shortlisting sessions).",
     "Or navigate to the Shortlisting Sessions view from the requisition."])

add_step_box(doc, 2, "Create a New Shortlisting Session",
    ["Click the 'New' button.",
     "The system auto-fills the Requisition and Job Position from context."])

add_screenshot_placeholder(doc, "Figure 5.5.1 – New Shortlisting Session Form",
    "Shows the shortlisting form with fields: Reference (auto), Requisition, Job, Meeting Date/Time, Venue. Below are two tabs: Panel Members and Candidates.")

add_step_box(doc, 3, "Fill Shortlisting Session Details",
    ["Reference: Auto-generated (e.g., SHORTLIST/2024/001).",
     "Meeting Date/Time *: Click the date field and select the date and time of the shortlisting meeting.",
     "Venue *: Type the meeting room or location (e.g., 'Boardroom A, 3rd Floor').",
     "Purpose: Optional — describe the purpose of this session.",
     "EE Compliance Notes: Add any notes about Employment Equity considerations."])

add_step_box(doc, 4, "Add Panel Members",
    ["Click the 'Panel Members' tab.",
     "Click 'Add a line' to add each panel member.",
     "Enter their Name, Surname, Department, and Contact Number.",
     "These can be internal employees or external observers.",
     "Add all relevant panel members before starting the session."])

add_step_box(doc, 5, "Add Candidates",
    ["Click the 'Candidates' tab.",
     "Click 'Add a line' and search for the applicant by name or reference.",
     "All qualifying applicants (in Qualification stage) will be searchable.",
     "Add all candidates to be reviewed in this session."])

add_step_box(doc, 6, "Start the Session",
    ["Click the 'Start' button (changes state from Draft to In Progress).",
     "Note: The system requires at least one panel member before you can Start."])

add_step_box(doc, 7, "Score and Shortlist Candidates",
    ["For each candidate in the Candidates tab, enter a Score (0–100).",
     "Add Notes about each candidate's suitability.",
     "Tick the 'Shortlisted' checkbox for candidates selected for interview.",
     "At least one candidate must be shortlisted to complete the session."])

add_screenshot_placeholder(doc, "Figure 5.5.2 – Shortlisting Candidates Table",
    "Shows the candidates table with columns: Candidate, Score, Shortlisted (checkbox), Notes. Three candidates visible: two with 'Shortlisted' ticked and one without.")

add_step_box(doc, 8, "Complete the Session",
    ["Once all candidates are reviewed and shortlisted ones are ticked, click 'Done'.",
     "The session state changes to Done.",
     "Shortlisted candidates are ready for interview scheduling.",
     "Click 'Open Interview Sessions' to create the interview session."])

page_break(doc)

# ── 5.6 BACKGROUND CHECKS ──
add_heading(doc, "5.6  Coordinating Background Checks", level=2)
add_body(doc, "After interviews, background checks must be completed for the recommended candidate "
    "before a job offer can be made.", space_after=6)
add_nav_path(doc, ["Recruitment", "Verification & Compliance", "Background Checks"])

add_step_box(doc, 1, "Create Background Checks Automatically",
    ["Open the completed Interview Session.",
     "Click the 'Create Background Checks' button.",
     "The system automatically creates FIVE mandatory background check records:",
     "  1. Credit Record Check",
     "  2. CV Validation",
     "  3. Employment Record Verification",
     "  4. Criminal Check",
     "  5. Identity Validation"])

add_screenshot_placeholder(doc, "Figure 5.6.1 – Background Checks List",
    "Shows 5 background check records for the same candidate. Columns: Reference, Check Type, Candidate, Status, State. All show Status='Pending', State='Draft'.")

add_step_box(doc, 2, "Open Each Background Check",
    ["Click on each background check record to open it.",
     "The form shows: Check Type, Candidate, Requested Date, Vendor Name, Status, Notes."])

add_step_box(doc, 3, "Update the Background Check Status",
    ["Enter the Vendor Name (who is conducting the check).",
     "Use the status buttons to update progress:",
     "  'Mark Pending' — check is being processed",
     "  'Mark Concern' — issue found, needs review",
     "  'Mark Failed' — check failed (candidate disqualified)",
     "When cleared: Click 'Start Approval Process' to route for approval."])

add_step_box(doc, 4, "Complete All 5 Checks",
    ["Repeat for all five mandatory check types.",
     "ALL FIVE must show Status = 'Clear' (Approved) before a job offer can be submitted.",
     "If any check shows 'Failed', the offer submission will be blocked."],
    note="The system validates background checks when you submit the offer. A red warning appears if any mandatory check is not cleared.")

page_break(doc)

# ── 5.7 PROCESSING JOB OFFERS ──
add_heading(doc, "5.7  Processing Job Offers", level=2)
add_body(doc, "Once all background checks are clear, create and process the employment offer.", space_after=6)
add_nav_path(doc, ["Recruitment", "Offers & Onboarding", "Offers"])

add_step_box(doc, 1, "Create a New Offer",
    ["Navigate to Offers & Onboarding › Offers.",
     "Click 'New'.",
     "A new offer form opens."])

add_screenshot_placeholder(doc, "Figure 5.7.1 – New Recruitment Offer Form",
    "Shows the offer form with fields: Reference (auto), Requisition, Applicant, Offer Date, Proposed Start Date, Contract Type (dropdown), Salary Offered. Status bar: Draft > To Approve > Approved > Sent to Candidate > Accepted.")

fields_offer = [
    ("Requisition *", "Link to the approved requisition this offer is for."),
    ("Applicant *", "Select the recommended candidate from the dropdown."),
    ("Offer Date", "Auto-filled to today. Change if needed."),
    ("Proposed Start Date", "Enter when the candidate is expected to start."),
    ("Contract Type *", "Select 'Permanent' or 'Fixed Term'."),
    ("Salary Offered", "Enter the agreed salary amount."),
    ("Requires CEO/CFO Approval", "Tick if the offer requires senior leadership approval."),
    ("Offer Letter File", "Upload the signed offer letter PDF."),
    ("Contract File", "Upload the employment contract."),
]
tbl_offer = doc.add_table(rows=len(fields_offer)+1, cols=2)
add_table_header_row(tbl_offer, ["Field", "Instructions"])
for i, (fn, fd) in enumerate(fields_offer):
    fill_table_row(tbl_offer, i+1, [(fn, True, COL_DARK_BLUE), fd], alt=(i%2==0))
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_step_box(doc, 2, "Complete the Onboarding Checklist",
    ["Scroll to the Onboarding section of the offer form.",
     "Tick each item as it is prepared:",
     "  ☐ IT Account — request created with IT department",
     "  ☐ Access Card — physical access card ordered",
     "  ☐ Workstation — desk/equipment allocated",
     "  ☐ Induction — induction date scheduled",
     "  ☐ Policy Acknowledgement Signed — HR policy signed by candidate",
     "  ☐ Confidentiality Agreement Signed — NDA signed by candidate"])

add_step_box(doc, 3, "Submit for Approval",
    ["Click 'Submit for Approval'.",
     "The system first validates that ALL 5 background checks are cleared.",
     "If checks are not clear, a warning message blocks the submission.",
     "If all checks are clear, the offer moves to 'To Approve' state.",
     "The designated Final Approver receives an email notification."])

add_step_box(doc, 4, "Send the Offer",
    ["Once approved (state = Approved), click 'Send Offer'.",
     "An email is automatically sent to the candidate with offer details.",
     "The state changes to 'Sent to Candidate'."])

add_step_box(doc, 5, "Record Candidate's Response",
    ["If candidate ACCEPTS: Click 'Mark Accepted'.",
     "  → The applicant is automatically moved to the 'Hired' stage.",
     "  → The requisition state changes to 'Done'.",
     "  → The hired employee and hire date are recorded on the requisition.",
     "If candidate DECLINES: Click 'Mark Rejected'.",
     "  → Consider contacting a reserve candidate from the interview session."])

add_screenshot_placeholder(doc, "Figure 5.7.2 – Offer Status: Accepted",
    "Shows the offer form with Status='Accepted', the Applicant stage showing 'Hired', and the Requisition showing 'Done'.")

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 6: LINE MANAGER GUIDE
# ─────────────────────────────────────────────

add_heading(doc, "6.  LINE MANAGER – Complete User Guide", level=1)
add_body(doc, "As a Line Manager, you are the first approver in the requisition workflow. You may also "
    "participate in shortlisting and interview panels.", space_after=8)

add_heading(doc, "6.1  Reviewing & Approving a Requisition", level=2)
add_body(doc, "You will receive an email notification when a requisition requires your approval.", space_after=6)

add_step_box(doc, 1, "Receive the Email Notification",
    ["Check your email inbox for a message from the Odoo system.",
     "Subject will be similar to: 'Action Required: Requisition REQ/2024/001 Awaiting Your Approval'.",
     "The email contains a direct link to the requisition.",
     "Click the link in the email — your browser opens Odoo."])

add_screenshot_placeholder(doc, "Figure 6.1.1 – Approval Request Email",
    "Shows the email notification with: Subject line, Sender (HR Coordinator name), body text describing the requisition, and a blue 'Review Requisition' button/link.")

add_step_box(doc, 2, "Log In to Odoo",
    ["If prompted, enter your email and password to log in.",
     "You are taken directly to the requisition form."])

add_step_box(doc, 3, "Review the Requisition",
    ["The requisition form opens showing all the details.",
     "Review each tab thoroughly:",
     "  • Position Overview: Is the position justified? Is it budgeted?",
     "  • Business Justification: Does the business case make sense?",
     "  • Job Details: Is the job description accurate and complete?",
     "  • Requirements & Competencies: Are the skills requirements correct?",
     "  • EE & Compliance: Are the EE targets appropriate?",
     "  • Documents: Has the organogram and job description been attached?"])

add_step_box(doc, 4, "Sign and Approve",
    ["Scroll to the Approval Lines section.",
     "Find the Line Manager approval table.",
     "Find your row (your name in the User column).",
     "Click the 'Sign' button on your row.",
     "A signature wizard opens."])

add_screenshot_placeholder(doc, "Figure 6.1.2 – Signature Wizard",
    "Shows a pop-up dialog with: 'Sign Requisition Approval' title, a checkbox 'Use my existing signature', a signature canvas area, and Confirm/Cancel buttons.")

add_step_box(doc, 5, "Complete the Signature",
    ["Option A – Use Existing Signature: Tick 'Use my existing signature' checkbox if you have a stored signature.",
     "Option B – Draw New Signature: Draw your signature in the signature canvas using your mouse or touchscreen.",
     "Enter your name in the 'Signature Name' field.",
     "Click 'Confirm'.",
     "Your approval is recorded with the date and time.",
     "If you are the last required approver in this stage, the system automatically sends a notification to the General Manager."],
    note="You can only sign if you are the CURRENT ACTIVE approver. If the sign button is greyed out, it means a previous approver in the sequence has not yet signed.")

add_step_box(doc, 6, "Reject a Requisition",
    ["If you believe the requisition should not proceed, click the 'Reject' button.",
     "A dialog box appears asking for a rejection reason.",
     "Type a clear explanation of why you are rejecting (this goes to the HR Coordinator).",
     "Click 'Confirm'.",
     "The HR Coordinator receives an email with your feedback.",
     "The requisition state changes to 'Rejected'."])

add_note_box(doc, "You can also access requisitions directly: Log in → Recruitment → Workforce Planning → Requisition Requests → Filter by 'Awaiting My Approval'.")

page_break(doc)

add_heading(doc, "6.2  Participating in Shortlisting", level=2)
add_body(doc, "If you are added to a shortlisting panel, you will receive a notification. "
    "Shortlisting is a meeting where the panel reviews all candidates and selects those for interview.", space_after=6)
add_nav_path(doc, ["Recruitment", "Workforce Planning", "Requisition Requests", "Open Shortlisting"])

add_step_box(doc, 1, "Access the Shortlisting Session",
    ["Log in to Odoo.",
     "Navigate to Recruitment › Workforce Planning › Requisition Requests.",
     "Open the relevant requisition.",
     "Click the 'Open Shortlisting' smart button.",
     "Open the relevant shortlisting session."])

add_step_box(doc, 2, "Review Candidates",
    ["In the Candidates tab, review each candidate's details.",
     "Click on a candidate's name to open their full application form.",
     "Review their: CV, qualifications, work experience, screening score.",
     "Return to the shortlisting session when done."])

add_step_box(doc, 3, "Score Candidates",
    ["In the Candidates table, enter a Score (0–100) for each candidate.",
     "Add Notes explaining your scoring rationale.",
     "Tick 'Shortlisted' for candidates the panel agrees should proceed to interview."])

add_heading(doc, "6.3  Conducting Interviews & Evaluations", level=2)
add_body(doc, "As a panel member in an interview session, you will score candidates during the interview "
    "and submit a formal evaluation afterwards.", space_after=6)
add_nav_path(doc, ["Recruitment", "Interview & Assessment", "Interview Sessions"])

add_step_box(doc, 1, "Open the Interview Session",
    ["Navigate to Recruitment › Interview & Assessment › Interview Sessions.",
     "Find and open your assigned session (you can filter by 'My Sessions')."])

add_step_box(doc, 2, "Sign Confidentiality Declaration",
    ["In the Panel Members tab, find your row.",
     "Tick the following declarations:",
     "  ☑ Confidentiality Signed — you agree to keep deliberations confidential.",
     "  ☑ No Personal Interest — you have no personal interest in any candidate.",
     "  ☑ No Relationship — you have no personal relationship with any candidate.",
     "  ☑ No Conflict of Interest — you have no conflict of interest.",
     "Enter your signature name and sign date."],
    note="The session cannot move to 'Prepared' state until ALL panel members have signed their confidentiality declarations.")

add_screenshot_placeholder(doc, "Figure 6.3.1 – Panel Confidentiality Declarations",
    "Shows the Panel Members table with columns: User, Role, Confidentiality Signed, No Personal Interest, No Relationship, No Conflict, Signed On. Row shows all checkboxes ticked.")

add_step_box(doc, 3, "Score Candidates During the Interview",
    ["In the Candidates tab, find each candidate.",
     "As the interview progresses, enter scores:",
     "  • Technical Score (0–100): Job knowledge and technical competency.",
     "  • Competency Score (0–100): Behavioural and leadership competencies.",
     "  • Culture Fit Score (0–100): Alignment with organisational values.",
     "The Total Score is calculated automatically.",
     "Tick 'Attended' if the candidate actually attended.",
     "Note their 'Arrival DateTime' for records."])

add_step_box(doc, 4, "Complete Interview Evaluation",
    ["Navigate to Recruitment › Interview & Assessment › Evaluations.",
     "Click 'New' to create an evaluation for each candidate you interviewed.",
     "Fill in:",
     "  • Applicant: Select the candidate",
     "  • Interviewer: Select yourself",
     "  • Technical Score, Communication Score, Experience Score, Cultural Fit Score",
     "  • Recommendation: Strong Hire / Hire / Hold / Reject",
     "  • Comments: Detailed narrative justification",
     "Click Save."])

add_screenshot_placeholder(doc, "Figure 6.3.2 – Interview Evaluation Form",
    "Shows the evaluation form with 4 score fields, a Recommendation dropdown showing 'Hire', and a Comments text area with narrative text.")

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 7: GENERAL MANAGER GUIDE
# ─────────────────────────────────────────────

add_heading(doc, "7.  GENERAL MANAGER – Complete User Guide", level=1)
add_body(doc, "As General Manager, you are the second approver in the requisition workflow. "
    "Your approval confirms the strategic and operational justification for the position.", space_after=8)

add_heading(doc, "7.1  Reviewing & Approving a Requisition (Stage 2)", level=2)
add_body(doc, "You receive an email notification only AFTER the Line Manager has fully approved. "
    "The process is the same as the Line Manager approval but at a different stage.", space_after=6)

add_step_box(doc, 1, "Receive Email & Open Requisition",
    ["Check your inbox for the approval email.",
     "Subject: 'Action Required: Requisition [REF] – General Manager Approval Needed'.",
     "Click the link in the email to open the requisition in Odoo.",
     "Log in if prompted."])

add_step_box(doc, 2, "Review Focus Areas for General Manager",
    ["As GM, focus your review on:",
     "  • Business Justification: Does the business case align with strategic direction?",
     "  • Budget Availability: Is the budget reasonable and confirmed by finance?",
     "  • Position Type: Is this a genuine new/replacement need?",
     "  • Impact if Not Filled: What is the operational risk?",
     "  • Line Manager Approval: Confirm that Stage 1 is already approved (check Line Manager table)."])

add_step_box(doc, 3, "Sign and Approve / Reject",
    ["Scroll to the Approval Lines section.",
     "Find the General Manager approval table.",
     "Find your row and click 'Sign'.",
     "Draw or use your existing signature, enter your name, and click Confirm.",
     "Or click Reject and provide a detailed reason."],
    note="If you reject, the HR Coordinator must address your concerns and restart the approval process from Stage 1.")

add_screenshot_placeholder(doc, "Figure 7.1.1 – General Manager Approval Section",
    "Shows the requisition with the Stage 1 (Line Manager) section showing 'Approved' status, and Stage 2 (General Manager) section showing the current user's row highlighted with a 'Sign' button.")

add_heading(doc, "7.2  Reviewing Shortlisting Recommendations", level=2)
add_body(doc, "The General Manager may review shortlisting outcomes to ensure they align with departmental "
    "needs. This is typically a read-only review.", space_after=6)
add_nav_path(doc, ["Recruitment", "Workforce Planning", "Requisition Requests", "Open Requisition", "Open Shortlisting"])
add_body(doc, "Open the completed shortlisting session and review the Candidates tab to see who was "
    "shortlisted and the scoring rationale in the Notes column.", space_after=6)

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 8: CFO GUIDE
# ─────────────────────────────────────────────

add_heading(doc, "8.  CFO – Complete User Guide", level=1)
add_body(doc, "As CFO (or acting CFO), you approve the financial aspects of the recruitment requisition "
    "at Stage 3, and may also approve employment offers.", space_after=8)

add_heading(doc, "8.1  Reviewing Budget & Approving Requisition (Stage 3)", level=2)

add_step_box(doc, 1, "Receive Email & Open Requisition",
    ["Receive the Stage 3 approval email (sent only after both Line Manager and GM have approved).",
     "Click the link in the email to open Odoo.",
     "Log in if prompted."])

add_step_box(doc, 2, "Financial Review Focus Areas",
    ["As CFO, concentrate on these fields:",
     "  • Budget Availability (Position Overview tab): Is the amount accurate?",
     "  • Business Justification tab: Does the business case justify the cost?",
     "  • Budget File (Documents tab): Is there a formal budget approval attached?",
     "  • Number of Positions: Does the headcount budget support this many positions?",
     "  • Salary / Job Grade: Is the proposed grade aligned with the salary band?"])

add_step_box(doc, 3, "Approve or Reject",
    ["Navigate to the CFO approval table in the Approval Lines section.",
     "Click 'Sign' on your row to approve.",
     "Or click 'Reject' if the financial justification is insufficient.",
     "Always add a comment when rejecting to guide the HR team."])

add_screenshot_placeholder(doc, "Figure 8.1.1 – CFO Approval with Budget Details",
    "Shows the requisition form with the Business Justification tab open, showing Budget Availability field = R450,000. The CFO approval section below shows 'Sign' button.")

add_heading(doc, "8.2  Approving Job Offers", level=2)
add_body(doc, "For offers that require CFO approval (high-value or executive roles), "
    "you will receive an approval request after the HR Coordinator submits the offer.", space_after=6)
add_nav_path(doc, ["Recruitment", "Offers & Onboarding", "Offers"])

add_step_box(doc, 1, "Access the Offer",
    ["Receive an email notification for the offer approval.",
     "Or navigate to: Recruitment › Offers & Onboarding › Offers.",
     "Filter by 'State = To Approve' to find pending offers."])

add_step_box(doc, 2, "Review the Offer Details",
    ["Open the offer record.",
     "Review: Candidate name, position, contract type, salary offered, proposed start date.",
     "Confirm: Background checks are all shown as 'Clear' (auto-validated).",
     "Verify: The salary is within the approved budget from the requisition."])

add_step_box(doc, 3, "Approve the Offer",
    ["Click the 'Approve' button at the top of the form.",
     "The offer state changes to 'Approved'.",
     "The HR Coordinator can now send the offer to the candidate."])

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 9: HCM MANAGER GUIDE
# ─────────────────────────────────────────────

add_heading(doc, "9.  HCM MANAGER – Complete User Guide", level=1)
add_body(doc, "As HCM Manager (General Manager: Human Capital Management), you are the FINAL approver "
    "of all recruitment requisitions. You also have oversight of the entire recruitment pipeline.", space_after=8)

add_heading(doc, "9.1  Final Requisition Validation & HCM Checklist", level=2)
add_body(doc, "You receive the approval request only AFTER Stages 1, 2, and 3 are complete. "
    "Your stage includes a mandatory compliance checklist.", space_after=6)

add_step_box(doc, 1, "Receive Email & Open Requisition",
    ["Receive the Stage 4 email: 'Final HCM Validation Required'.",
     "Click the link to open Odoo.",
     "Log in if prompted."])

add_step_box(doc, 2, "Review ALL Tabs",
    ["As the final approver, review the complete requisition:",
     "  • All previous approvals are confirmed (Stages 1–3 all show Approved).",
     "  • Job description is complete and appropriate.",
     "  • Skills requirements are reasonable.",
     "  • EE targets are set.",
     "  • All required documents are attached."])

add_step_box(doc, 3, "Complete the HCM Checklist",
    ["Find the HCM Checklist section on the requisition form.",
     "Tick each item to confirm compliance:",
     "  ☐ Job Description Received — formal JD document attached",
     "  ☐ Organogram Attached — org chart showing position uploaded",
     "  ☐ Finance Approved — CFO approval confirmed (Stage 3)",
     "  ☐ GM Approved — General Manager approval confirmed (Stage 2)",
     "  ☐ All Signatories Signed — all required approvers at each stage have signed",
     "The 'Completed By' and 'Check Date' fields are auto-filled when you save."],
    note="You CANNOT sign your approval line until all 5 checklist items are ticked. This enforces compliance.")

add_screenshot_placeholder(doc, "Figure 9.1.1 – HCM Checklist Section",
    "Shows the HCM Checklist with 5 boolean checkboxes: 'Job Description Received', 'Organogram Attached', 'Finance Approved', 'GM Approved', 'All Signatories Signed'. All ticked. Completed By = 'Sarah HCM', Check Date = today.")

add_step_box(doc, 4, "Sign the HCM Approval",
    ["After completing the checklist, scroll to the HCM Manager approval table.",
     "Click 'Sign' on your row.",
     "Draw or select your signature.",
     "Enter your signature name and click Confirm.",
     "The requisition state changes to APPROVED (shown in the status bar)."])

add_step_box(doc, 5, "Notify HR Coordinator",
    ["After your approval, the HR Coordinator receives an automatic email.",
     "They can now proceed with: Creating the job position, Publishing the advert, Beginning recruitment."])

add_heading(doc, "9.2  Oversight of the Recruitment Pipeline", level=2)
add_body(doc, "As HCM Manager, you have read access to all recruitment records. "
    "Use this to monitor progress across all open positions.", space_after=6)

add_bullet(doc, "Requisitions: Recruitment › Workforce Planning › Requisition Requests — view all active requisitions and their approval status.")
add_bullet(doc, "Applications: Recruitment › Candidates › Applications — view the pipeline of all candidates across all jobs.")
add_bullet(doc, "Background Checks: Recruitment › Verification & Compliance › Background Checks — monitor all checks in progress.")
add_bullet(doc, "Offers: Recruitment › Offers & Onboarding › Offers — track all pending and accepted offers.")

add_note_box(doc, "Use the Search bar Filters and Group By options to segment data by department, job, or state for management reporting.", bg_color=COL_STEP_BG, border_color=COL_MID_BLUE)

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 10: INTERVIEWER / PANEL MEMBER GUIDE
# ─────────────────────────────────────────────

add_heading(doc, "10.  INTERVIEWER / PANEL MEMBER – Complete User Guide", level=1)
add_body(doc, "As an Interviewer or Panel Member, your role is to conduct fair, structured interviews, "
    "score candidates objectively, and submit formal evaluations.", space_after=8)

add_heading(doc, "10.1  Signing the Confidentiality Declaration", level=2)
add_body(doc, "Before participating in any interview or shortlisting session, you MUST sign a "
    "confidentiality declaration. This is a legal requirement.", space_after=6)

add_step_box(doc, 1, "Receive Interview Invitation",
    ["The HR Coordinator adds you to a session. You receive a notification.",
     "Log in to Odoo.",
     "Navigate to: Recruitment › Interview & Assessment › Interview Sessions.",
     "Find and open the session you are assigned to."])

add_step_box(doc, 2, "Complete Declarations in Panel Tab",
    ["Click the 'Panel Members' tab.",
     "Find your row in the table.",
     "Tick the following checkboxes:",
     "  ☑ Confidentiality Signed",
     "  ☑ No Personal Interest (I confirm I have no personal interest in any candidate)",
     "  ☑ No Relationship (I have no personal relationship with any candidate)",
     "  ☑ No Conflict of Interest (I have no conflict of interest)",
     "Enter your full name in 'Signature Name'.",
     "The 'Signed On' date auto-fills to today.",
     "Click Save."])

add_note_box(doc, "If you DO have a conflict of interest with any candidate, you must NOT tick 'No Conflict of Interest'. Inform the HR Coordinator immediately so you can be removed from the panel.")

add_heading(doc, "10.2  Conducting & Scoring Interviews", level=2)
add_body(doc, "The HR Coordinator will start the session (state: In Progress). "
    "During the interview, record scores in real time.", space_after=6)

add_step_box(doc, 1, "Open the Interview Session",
    ["Navigate to Recruitment › Interview & Assessment › Interview Sessions.",
     "Open the session (should be In Progress state)."])

add_step_box(doc, 2, "Record Candidate Attendance",
    ["In the Candidates tab, confirm each candidate's attendance:",
     "  • 'Attended' checkbox — tick if the candidate arrived.",
     "  • 'Arrival DateTime' — record when they arrived."])

add_step_box(doc, 3, "Score During the Interview",
    ["For each candidate, enter scores (0–100) in these three dimensions:",
     "  • Technical Score: Knowledge, skills, and ability relevant to the role.",
     "  • Competency Score: Leadership, problem-solving, behavioural competencies.",
     "  • Culture Fit Score: Alignment with organisational values and team culture.",
     "The Total Score (sum of all three) is calculated automatically."])

add_screenshot_placeholder(doc, "Figure 10.2.1 – Interview Candidate Scoring",
    "Shows the Candidates tab with 3 candidates. Each row shows: Candidate Name, Attended (ticked), Technical Score=78, Competency Score=82, Culture Score=75, Total=235.")

add_step_box(doc, 4, "Collect Candidate Declarations",
    ["For each candidate in the session, collect their declarations:",
     "  ☑ Declaration: Information Accurate — candidate confirms their application is truthful.",
     "  ☑ Declaration: Conflict of Interest — candidate discloses any conflicts.",
     "  ☑ Candidate Signed — candidate has physically signed their declaration form.",
     "  • Role Impact: Candidate's statement on how they will impact the role.",
     "  • Availability to Join: Enter the date they can start.",
     "  • Declaration: Interview Fair — candidate confirms the interview was fair."])

add_heading(doc, "10.3  Submitting Interview Evaluations", level=2)
add_body(doc, "After the interview, submit a formal evaluation for each candidate you interviewed. "
    "This is separate from the session scoring.", space_after=6)
add_nav_path(doc, ["Recruitment", "Interview & Assessment", "Evaluations", "New"])

add_step_box(doc, 1, "Create an Evaluation",
    ["Navigate to Recruitment › Interview & Assessment › Evaluations.",
     "Click 'New'.",
     "An evaluation form opens."])

add_screenshot_placeholder(doc, "Figure 10.3.1 – Interview Evaluation Form",
    "Shows the full evaluation form: Applicant (linked), Interviewer (auto-filled to current user), four score fields, Recommendation dropdown, and a large Comments text area.")

eval_fields = [
    ("Applicant *", "Select the candidate you are evaluating from the dropdown."),
    ("Interviewer *", "Auto-filled to your name. Do not change unless evaluating on behalf of someone."),
    ("Technical Score", "Score 0–100 based on technical knowledge demonstrated in the interview."),
    ("Communication Score", "Score 0–100 based on verbal communication, clarity, and articulation."),
    ("Experience Score", "Score 0–100 based on relevant work experience and examples given."),
    ("Cultural Fit Score", "Score 0–100 based on values alignment, attitude, and fit with team."),
    ("Total Score", "Auto-calculated. Sum of the four scores above."),
    ("Recommendation", "Select: Strong Hire / Hire / Hold / Reject — your overall hiring recommendation."),
    ("Comments", "Write a detailed narrative (minimum 3–5 sentences) explaining your scores and recommendation. This is critical for the record."),
]
tbl_eval = doc.add_table(rows=len(eval_fields)+1, cols=2)
add_table_header_row(tbl_eval, ["Field", "Instructions"])
for i, (fn, fd) in enumerate(eval_fields):
    fill_table_row(tbl_eval, i+1, [(fn, True, COL_DARK_BLUE), fd], alt=(i%2==0))
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_step_box(doc, 2, "Save the Evaluation",
    ["Click Save.",
     "Your evaluation is now linked to the applicant's record.",
     "The HR Coordinator can view all evaluations from the applicant's form.",
     "The Final Score on the applicant's record is the average of all evaluations."])

add_note_box(doc, "Submit your evaluation AS SOON AS POSSIBLE after the interview — ideally the same day. This ensures the HR Coordinator can process results promptly.")

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 11: BACKGROUND CHECK REVIEWER GUIDE
# ─────────────────────────────────────────────

add_heading(doc, "11.  BACKGROUND CHECK REVIEWER – Complete User Guide", level=1)
add_body(doc, "The Background Check Reviewer is responsible for managing the verification of candidate "
    "credentials. This may be an internal HR compliance officer or an external vendor liaison.", space_after=8)
add_nav_path(doc, ["Recruitment", "Verification & Compliance", "Background Checks"])

add_step_box(doc, 1, "Access Background Checks",
    ["Navigate to Recruitment › Verification & Compliance › Background Checks.",
     "A list of all background checks appears.",
     "Filter by 'State = Draft' to find newly created checks awaiting action.",
     "Or filter by 'Applicant' to see all checks for a specific candidate."])

add_screenshot_placeholder(doc, "Figure 11.1 – Background Checks List View",
    "Shows the list with columns: Reference, Check Type, Candidate, Requisition, Status, State, Requested Date, Vendor. Filter 'Draft' is active showing 5 records for one candidate.")

add_step_box(doc, 2, "Open a Background Check Record",
    ["Click on a record to open it.",
     "The form shows the Check Type, Candidate name, Requested Date."])

check_types_info = [
    ("Credit Record Check", "Contact the credit bureau to verify the candidate's credit history. Note the vendor name and any reference number."),
    ("CV Validation", "Verify that the information on the CV (qualifications, dates of employment) is accurate and not fabricated."),
    ("Employment Record Verification", "Contact previous employers to verify employment dates, position, and reason for leaving."),
    ("Criminal Check", "Obtain a police clearance certificate from the candidate and submit to SAPS or accredited vendor for verification."),
    ("Identity Validation", "Verify the candidate's ID document or passport with Home Affairs or an accredited vendor."),
]
add_heading(doc, "Background Check Types & How to Process Each", level=3)
tbl_cht = doc.add_table(rows=len(check_types_info)+1, cols=2)
add_table_header_row(tbl_cht, ["Check Type", "How to Process"])
for i, (ct, cd) in enumerate(check_types_info):
    fill_table_row(tbl_cht, i+1, [(ct, True, COL_DARK_BLUE), cd], alt=(i%2==0))
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_step_box(doc, 3, "Update the Check Status",
    ["On the background check form:",
     "  • Vendor Name: Enter the name of the organisation conducting the check.",
     "  • Result Notes: Describe the findings.",
     "  • Completed Date: Enter when the check was completed.",
     "Use the status buttons to record the result:",
     "  'Mark Pending' → check is in progress with vendor",
     "  'Mark Concern' → an issue was found that needs HR review",
     "  'Mark Failed' → the candidate has failed this check"])

add_step_box(doc, 4, "Route for Approval (when cleared)",
    ["Once the vendor confirms the check is clear:",
     "  Click 'Start Approval Process'.",
     "  The approval workflow begins.",
     "  The designated approvers are notified.",
     "  Approvers review and click Approve or Reject.",
     "  When approved: the Status automatically changes to 'Clear'."])

add_step_box(doc, 5, "Handling Failed Checks",
    ["If a check fails:",
     "  Click 'Mark Failed'.",
     "  Enter a detailed explanation in Result Notes.",
     "  Inform the HR Coordinator immediately.",
     "  The HR Coordinator will decide whether to proceed with a reserve candidate.",
     "  The offer submission will be BLOCKED until this is resolved."])

add_note_box(doc, "ALL FIVE mandatory checks (Credit, CV, Employment, Criminal, Identity) must show Status='Clear' before the offer can be submitted. This is enforced by the system.")

add_screenshot_placeholder(doc, "Figure 11.2 – Completed Background Check Record",
    "Shows a background check form with: Check Type='Criminal Check', Status='Clear' (green badge), State='Approved', Vendor='SAPS Accredited Bureau', Result Notes='No criminal record found', Completed Date=today.")

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 12: APPLICANT (PORTAL USER) GUIDE
# ─────────────────────────────────────────────

add_heading(doc, "12.  APPLICANT (Portal User) – Complete User Guide", level=1)
add_body(doc, "This section is for candidates applying for a job. You interact with the system through "
    "the company's public website and do not need an Odoo login to apply.", space_after=8)

add_heading(doc, "12.1  Finding & Applying for a Job", level=2)
add_body(doc, "All open positions are published on the company's careers page on their website.", space_after=6)

add_step_box(doc, 1, "Visit the Careers Page",
    ["Open your web browser.",
     "Go to the company's website (e.g., https://www.yourcompany.co.za).",
     "Look for a 'Careers', 'Jobs', or 'Vacancies' link in the main menu or footer.",
     "Click to open the Jobs/Careers page."])

add_screenshot_placeholder(doc, "Figure 12.1.1 – Public Careers Page",
    "Shows the company's public careers page with job cards. Each card shows: Job Title, Department, Location, Brief Description, and an 'Apply Now' button. Search/filter options at the top.")

add_step_box(doc, 2, "Find the Right Job",
    ["Browse the list of available positions.",
     "Use the search bar to search by job title or department.",
     "Use the filter options to narrow by location or employment type.",
     "Click on a job title to read the full job description."])

add_screenshot_placeholder(doc, "Figure 12.1.2 – Full Job Description Page",
    "Shows the job detail page with: Job Title (large heading), Department, Location, Employment Type, Salary (if shown), full Description, Requirements, and an 'Apply Now' button.")

add_step_box(doc, 3, "Click Apply Now",
    ["On the job detail page, click the 'Apply Now' button.",
     "An application form opens in your browser.",
     "You do NOT need to create an account to apply."])

add_screenshot_placeholder(doc, "Figure 12.1.3 – Online Application Form",
    "Shows the multi-section application form with sections: Personal Information, Qualifications, Work Experience, CV Upload, Declarations, and a Submit button at the bottom.")

add_heading(doc, "Completing the Application Form", level=3)
app_sections = [
    ("SECTION 1: Personal Information", [
        "Title: Select from dropdown (Mr, Mrs, Ms, Dr, etc.)",
        "First Name / Initials: Enter your first name(s) or initials.",
        "Surname *: Enter your surname/last name.",
        "ID / Passport Number *: Enter your South African ID number or passport number.",
        "Date of Birth *: Click the calendar icon and select your date of birth.",
        "Gender *: Select Male, Female, or Other.",
        "Nationality: Defaults to South Africa. Change if needed.",
        "Race *: Select African, White, Coloured, Indian, or Other.",
        "Disability: Select Yes or No.",
        "Home Language: Select your home language.",
        "Email Address *: Enter a valid email — all correspondence will be sent here.",
        "Phone Number *: Enter your contact number.",
    ]),
    ("SECTION 2: Qualifications & Experience", [
        "Highest Qualification *: Select from dropdown (Grade 11 through Doctoral Degree).",
        "Do you have an Honours Degree?: Select Yes or No.",
        "Do you have a Master's Degree?: Select Yes or No.",
        "Years of Work Experience *: Select the range that applies to you.",
        "Last Role / Position Held: Enter your most recent job title.",
        "Experience by Role: Describe your experience briefly.",
        "Current Salary: Enter your current or last salary (optional).",
        "Notice Period *: Select how much notice you need to give (30 Days, 1 Month, Immediately, Other).",
        "Willing to Relocate?: Select Yes or No.",
        "Professional Body Membership: Select Yes if you are registered with a professional body.",
    ]),
    ("SECTION 3: Motivation Letter", [
        "Write a motivation letter explaining why you are the best candidate for this role.",
        "Be specific about how your experience matches the requirements.",
        "Minimum recommended length: 300 words.",
    ]),
    ("SECTION 4: Upload Documents", [
        "CV Upload *: Click 'Choose File' and select your CV (PDF or Word format, max 5MB).",
        "Qualifications Upload: Upload your highest qualification certificate (PDF).",
    ]),
    ("SECTION 5: Declarations", [
        "Declaration – Conflict of Interest: Tick if you have a conflict of interest with anyone in the organisation, then describe the relationship in the text box.",
        "Declaration – Information Accurate *: TICK THIS to confirm all information you provided is true and accurate. This is REQUIRED.",
        "Terms & Conditions *: TICK THIS to accept the application terms and conditions. This is REQUIRED.",
    ]),
]
for section_title, fields in app_sections:
    add_heading(doc, section_title, level=3)
    for f in fields:
        add_bullet(doc, f)

add_step_box(doc, 4, "Submit Your Application",
    ["Review all the information you have entered.",
     "Ensure all required fields (marked *) are filled.",
     "Tick both declaration checkboxes.",
     "Click the 'Submit Application' button at the bottom.",
     "A confirmation message appears: 'Your application has been submitted successfully!'"])

add_step_box(doc, 5, "Check Your Email",
    ["Within a few minutes, you will receive an acknowledgement email.",
     "Subject: 'Application Received – [Job Title] at [Company Name]'.",
     "The email confirms your application was received and provides a reference.",
     "Save this email for your records."])

add_note_box(doc, "Ensure you use a valid email address. All interview invitations, survey links, and offer notifications will be sent to this email.")

page_break(doc)

add_heading(doc, "12.2  Completing the Pre-Screening Survey", level=2)
add_body(doc, "After submitting your application, you may receive an email asking you to complete "
    "a pre-screening survey. This is MANDATORY and must be completed to advance your application.", space_after=6)

add_step_box(doc, 1, "Receive the Survey Email",
    ["Check your email for a message with subject similar to:",
     "'Pre-Screening Assessment – [Job Title] Application'.",
     "The email contains a unique link to YOUR survey.",
     "Click the link."])

add_step_box(doc, 2, "Complete the Survey",
    ["The survey opens in your browser.",
     "Answer ALL questions carefully and honestly.",
     "Some questions may be multiple choice; others may require text answers.",
     "Elimination Questions: These are critical — if you answer them incorrectly, your application may be automatically declined.",
     "Take your time — read each question carefully before answering.",
     "Click 'Next' to move between pages.",
     "Click 'Submit' when all questions are answered."])

add_screenshot_placeholder(doc, "Figure 12.2.1 – Pre-Screening Survey",
    "Shows the survey interface with: Job title at the top, question number/total (e.g., Question 3 of 10), a multiple-choice question about experience, answer options, and a Next button.")

add_step_box(doc, 3, "After Submitting",
    ["A confirmation message confirms your survey is submitted.",
     "Your score is automatically calculated by the system.",
     "If your score meets the threshold and no elimination questions were failed:",
     "  → Your application moves to the Qualification stage (awaiting HR review).",
     "If your score is below threshold or you failed an elimination question:",
     "  → You may receive a regret email from the HR team."])

add_note_box(doc, "The survey link is unique to you and can only be used once. Complete it in one session if possible. If you experience technical issues, contact the HR Coordinator.")

add_heading(doc, "12.3  Receiving Interview Notifications", level=2)
add_body(doc, "If you are shortlisted for an interview, you will receive an email notification.", space_after=6)

add_step_box(doc, 1, "Interview Invitation Email",
    ["Subject: 'Interview Invitation – [Job Title] at [Company Name]'.",
     "The email contains:",
     "  • Interview date and time",
     "  • Interview type: ONSITE (you must come in person) or ONLINE (video call)",
     "  • For ONLINE: A meeting link (Teams/Zoom) is included",
     "  • For ONSITE: The physical address and reporting instructions",
     "  • Name of the recruiter and contact number",
     "  • What to bring (ID document, qualifications, etc.)"])

add_screenshot_placeholder(doc, "Figure 12.3.1 – Interview Invitation Email",
    "Shows the interview email with company logo, candidate name, job title, interview details (date/time/type/location), contact information, and preparation tips.")

add_step_box(doc, 2, "Prepare for the Interview",
    ["Confirm your attendance by contacting the HR Coordinator (details in the email).",
     "Prepare the required documents:",
     "  • Original ID document or passport",
     "  • Certified copies of your qualifications",
     "  • Updated CV",
     "  • Any other documents mentioned in the email.",
     "Research the company and the role.",
     "Arrive 15 minutes early for ONSITE interviews."])

add_heading(doc, "12.4  Receiving & Accepting a Job Offer", level=2)
add_body(doc, "If you are the successful candidate, you will receive a formal job offer by email.", space_after=6)

add_step_box(doc, 1, "Receive the Offer Email",
    ["Subject: 'Job Offer – [Job Title] at [Company Name]'.",
     "The email contains your offer letter as an attachment.",
     "The offer letter includes:",
     "  • Position title and department",
     "  • Proposed start date",
     "  • Salary and benefits",
     "  • Contract type (Permanent or Fixed Term)",
     "  • Instructions on how to accept or decline"])

add_step_box(doc, 2, "Review the Offer",
    ["Read the offer letter carefully.",
     "Clarify any questions with the HR Coordinator before accepting.",
     "Check: salary, start date, contract type, and any conditions."])

add_step_box(doc, 3, "Accept or Decline",
    ["To Accept: Follow the instructions in the email. You may be asked to:",
     "  • Sign and return the offer letter",
     "  • Complete additional onboarding forms",
     "  • Provide your banking details and tax number",
     "The HR Coordinator will confirm your acceptance in the system.",
     "To Decline: Contact the HR Coordinator by email or phone to inform them."])

add_note_box(doc, "Once you accept the offer, keep a copy of the signed offer letter for your records. It is a legally binding document.")

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 13: SYSTEM ADMINISTRATION
# ─────────────────────────────────────────────

add_heading(doc, "13.  System Administration & Configuration", level=1)
add_body(doc, "This section is for system administrators or senior HR users who need to configure "
    "the recruitment system.", space_after=8)

add_heading(doc, "13.1  Managing Approval Teams", level=2)
add_nav_path(doc, ["Recruitment", "Configuration", "Roles"])
add_body(doc, "Approval Teams define the default approvers for different departments or jobs.", space_after=4)
add_numbered(doc, "Navigate to Recruitment › Configuration › Roles.")
add_numbered(doc, "Click 'New' to create a new approval team.")
add_numbered(doc, "Enter a Team Name.")
add_numbered(doc, "Select the Department this team applies to.")
add_numbered(doc, "In the Lines tab, add users and their approver roles (Line Manager, GM, CFO, HCM).")
add_numbered(doc, "Set the Sequence for each approver to control signing order.")
add_numbered(doc, "Click Save.")

add_heading(doc, "13.2  Managing Media Channels", level=2)
add_nav_path(doc, ["Recruitment", "Configuration", "Media Channels"])
add_body(doc, "Media Channels are the platforms where jobs are advertised (e.g., LinkedIn, Indeed, Pnet).", space_after=4)
add_numbered(doc, "Navigate to Recruitment › Configuration › Media Channels.")
add_numbered(doc, "Click 'New'.")
add_numbered(doc, "Enter the channel name and any relevant details.")
add_numbered(doc, "Click Save. The channel is now available when configuring a requisition's advertising.")

add_heading(doc, "13.3  Managing Approver Roles", level=2)
add_nav_path(doc, ["Recruitment", "Configuration", "Approver Roles"])
add_body(doc, "Pre-defined roles: Line Manager, General Manager, Acting: Chief Finance Officer, "
    "General Manager: Human Capital Management.", space_after=4)
add_body(doc, "To add a custom role, click New, enter the role name, and Save.", space_after=6)

add_heading(doc, "13.4  Pre-Screening Survey Setup", level=2)
add_nav_path(doc, ["Recruitment", "Workforce Planning", "Requisition Requests", "Open Requisition", "Screening Tab"])
add_body(doc, "Surveys are linked to requisitions in the Screening & Interview Setup tab.", space_after=4)
add_numbered(doc, "Open a requisition.")
add_numbered(doc, "Click the Screening & Interview Setup tab.")
add_numbered(doc, "In the Survey field, select an existing survey or click 'New' to create one.")
add_numbered(doc, "To configure the survey: click 'Start Pre-Screening Survey' button to open the survey editor.")
add_numbered(doc, "Add questions by clicking 'Add a Question'.")
add_numbered(doc, "For elimination questions: tick the 'Elimination Question' checkbox on the question.")
add_numbered(doc, "Set the Required Score threshold for the survey.")
add_numbered(doc, "Click Save.")
add_note_box(doc, "Elimination questions override the score threshold. A candidate failing ANY elimination question is automatically disqualified regardless of total score.")

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 14: TROUBLESHOOTING & FAQs
# ─────────────────────────────────────────────

add_heading(doc, "14.  Troubleshooting & FAQs", level=1)

faqs = [
    ("I cannot log in to Odoo.",
     "Check your email address and password. Ensure Caps Lock is off. If you forgot your password, click 'Reset Password' on the login page. If the issue persists, contact your IT Administrator."),
    ("I received an approval email but the link does not work.",
     "Try copying the link and pasting it directly into your browser's address bar. Ensure you are logged into Odoo first, then try the link again. Contact HR if the link has expired."),
    ("The Sign button is greyed out on the approval line.",
     "This means it is not yet your turn to sign. A previous approver in the sequence must sign first. Check the Sequence column — the approver with the lowest sequence number who has not yet signed must go first."),
    ("I cannot submit the requisition — it shows an error.",
     "Required fields (marked with a red asterisk *) must all be completed. Common missing fields: Job Description, Survey/Pre-screening Form, HR Coordinator. Scroll through all tabs to find unfilled required fields."),
    ("The 'Submit for Approval' button on the offer is blocked.",
     "One or more mandatory background checks are not yet cleared. Navigate to the background checks list, filter by the candidate, and check that all 5 check types show Status = 'Clear'."),
    ("A candidate's application does not appear in the pipeline.",
     "The candidate may not have completed their pre-screening survey. Check their application record and look at the Pre-Screening State field. If 'Not started yet', the survey has not been submitted."),
    ("I accidentally rejected a requisition. Can I undo it?",
     "Yes. Open the rejected requisition and click 'Reset to Draft'. All approval signatures will be cleared and you will need to restart the approval process. Contact all previous approvers to re-sign."),
    ("The shortlisting session 'Done' button is greyed out.",
     "At least one candidate must have the 'Shortlisted' checkbox ticked in the Candidates table. Tick at least one candidate as shortlisted, then click Done."),
    ("I cannot find a candidate's application.",
     "Use the Search bar at the top of the Applications list. Type the candidate's name, email, or ID number. Or use the Filters dropdown to search across all stages including Rejected and Staging."),
    ("An applicant applied but did not receive the acknowledgement email.",
     "Check your company's email configuration in Odoo Settings. Verify the applicant's email address is correct on their application form. The HR Coordinator can manually send an email from the application's chatter (message area at the bottom of the form)."),
    ("How do I export a list of candidates to Excel?",
     "In any list view (Applications, Background Checks, etc.), tick the checkboxes for records you want to export. Click the Action button (⚙) › Export. Select the fields to export and click Export to Excel."),
    ("The interview session is stuck in 'Draft' state.",
     "The 'Prepare' button validates that all panel members have signed their confidentiality declarations. Check the Panel Members tab — find any rows where the declaration checkboxes are not all ticked and follow up with those panelists."),
]

for q, a in faqs:
    add_heading(doc, f"Q: {q}", level=3)
    add_body(doc, f"A:  {a}", space_after=8)

page_break(doc)

# ─────────────────────────────────────────────
# SECTION 15: GLOSSARY
# ─────────────────────────────────────────────

add_heading(doc, "15.  Glossary", level=1)
add_body(doc, "The following terms are used throughout this guide.", space_after=8)

glossary = [
    ("Applicant Profile", "A permanent record of a candidate in the system, separate from individual job applications. One profile can have multiple applications."),
    ("Approval Line", "A single row in an approval table representing one approver at a specific stage. Contains the approver's name, sequence, status, and signature."),
    ("Approval Team", "A pre-configured group of approvers assigned to a department or position type."),
    ("Background Check", "A formal verification of a candidate's credentials, identity, employment history, and criminal record."),
    ("BEE / EE", "Broad-Based Black Economic Empowerment / Employment Equity — South African legislation requiring representation of designated groups."),
    ("Breadcrumb", "The navigation trail at the top of a form in Odoo (e.g., Recruitment › Requisitions › REQ/2024/001) showing where you are."),
    ("Chatter", "The communication/logging panel at the bottom of every Odoo form. Shows all messages, emails, and system logs related to that record."),
    ("CFO", "Chief Finance Officer — responsible for financial approval of requisitions."),
    ("Elimination Question", "A survey question that, if answered incorrectly, automatically disqualifies a candidate regardless of their total score."),
    ("HCM", "Human Capital Management — refers to the HR function managing the full employee lifecycle."),
    ("HR Coordinator", "The primary HR user who creates and manages recruitment records. Also called Recruitment Manager."),
    ("Interview Session", "A formal group interview event with a panel of interviewers, linked to a shortlisting outcome."),
    ("Kanban View", "A visual card-based view in Odoo where records appear as cards organised in columns by stage."),
    ("KPE/KPI", "Key Performance Expectations / Key Performance Indicators — metrics used to evaluate job performance."),
    ("Mandatory Background Check", "One of the five required checks (Credit, CV, Employment, Criminal, Identity) that must be cleared before an offer can be made."),
    ("Odoo", "An open-source, web-based business application platform. The Recruitment Enhancement Module runs on Odoo 17."),
    ("Panel Member", "A person assigned to participate in a shortlisting or interview session to evaluate candidates."),
    ("Portal User", "An external user (such as a job applicant) who accesses the system through the public website, not the internal backend."),
    ("Pre-Screening", "An automated survey sent to applicants after they submit their application to initially screen their suitability."),
    ("PWD", "Persons with Disabilities — an Employment Equity designated group."),
    ("Recruiter", "The HR staff member responsible for managing the day-to-day recruitment activities for a specific position."),
    ("Recruitment Requisition", "The formal document requesting approval to fill a job vacancy. Must be approved by Line Manager, GM, CFO, and HCM before recruitment begins."),
    ("Screening Point", "A score out of 100 automatically calculated based on a candidate's pre-screening survey responses."),
    ("Shortlisting", "The process of reviewing all qualifying applicants and selecting a subset to invite for interviews."),
    ("Sourcing Method", "Whether a position is filled through Internal candidates, External candidates, or Both."),
    ("State", "The current stage of a record in its lifecycle (e.g., Draft, In Process, Approved, Done). Shown in the status bar."),
    ("Status Bar", "The bar at the top of a form in Odoo showing the current state and all possible states as clickable buttons."),
    ("Turn-Based Approval", "A sequential approval system where only the next designated approver can act at any given time."),
]

tbl_gloss = doc.add_table(rows=len(glossary)+1, cols=2)
add_table_header_row(tbl_gloss, ["Term", "Definition"])
for i, (term, defn) in enumerate(glossary):
    fill_table_row(tbl_gloss, i+1, [(term, True, COL_DARK_BLUE), defn], alt=(i%2==0))

doc.add_paragraph().paragraph_format.space_after = Pt(12)

# ─────────────────────────────────────────────
# FOOTER NOTE
# ─────────────────────────────────────────────

page_break(doc)
tbl_footer = doc.add_table(rows=1, cols=1)
fc = tbl_footer.cell(0, 0)
set_cell_bg(fc, COL_DARK_BLUE)
fp = fc.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp.paragraph_format.space_before = Pt(16)
fp.paragraph_format.space_after = Pt(16)
fr = fp.add_run("END OF RECRUITMENT MANAGEMENT SYSTEM USER GUIDE")
fr.bold = True; fr.font.size = Pt(13); fr.font.color.rgb = COL_WHITE

doc.add_paragraph().paragraph_format.space_after = Pt(8)
p_end = doc.add_paragraph()
p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_end = p_end.add_run(
    "This document is for internal use only.\n"
    "For support, contact your IT Administrator or HR Department.\n"
    "Recruitment Enhancement Module | Odoo 17 | Version 1.0"
)
r_end.font.size = Pt(9); r_end.font.color.rgb = RGBColor(0x77,0x77,0x77); r_end.italic = True

# ─────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────

output_path = "Recruitment_System_User_Guide.docx"
doc.save(output_path)
print(f"✅  User Guide saved: {output_path}")
