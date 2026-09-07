---
name: connxio-flow-documentation
description: Create customer/IT-facing Word (docx) technical documentation for a Connxio integration flow (one integration, or several integrations chained via redirect actions). Use when the user asks to document, write up, or produce a Word doc for a Connxio flow, or asks for a flow diagram of an integration.
argument-hint: "integration id(s) that make up the flow, and the target audience (customer overview vs. IT technical)"
---

# Connxio Flow Documentation

Produces a branded, customer/IT-readable Word document describing a Connxio
integration flow, plus a matching flow diagram (PNG) with proper decision
shapes for branching logic. Use this whenever the user wants a flow
documented — this skill is the standard/template for all such documents.

## What counts as "a flow"

- A single integration can be a complete, self-contained flow.
- Some integrations have an outbound/redirect action that hands off to
  **another** integration. In that case, all connected integrations together
  form one flow and must be documented as such (trace every redirect before
  writing anything).
- **How to detect a redirect (concrete steps):** in the JSON returned by
  `get_integration`, check every subintegration's `outboundConnections`
  array. An entry with `"adapterType": "Redirect"` hands the message off to
  another integration. Its `connectionProperties` is a JSON *string* — parse
  it to find `"IntegrationId"` (the target integration's id) and note
  `"PreserveInterchangeId"` if present. Call `get_integration` on that
  target id next, and repeat the same check on *its* `outboundConnections`
  — redirects can chain more than one hop deep. Stop once an integration's
  outbound connections are all non-Redirect (e.g. `REST`, `Dataverse`,
  none) — that is the end of the chain.
- Also check `inboundConnection.adapterType` on each integration you find.
  Note it in section 3, but **do not assume a relationship between inbound
  type and redirects**:
  - An `"Api"` inbound does **not** imply the integration is only reachable
    via a redirect — it may also be called directly by an external system
    or another platform. Say only what you can confirm (e.g. "this
    integration is invoked via API" / "this integration is also invoked by
    a redirect from &lt;name&gt;"), don't assume exclusivity either way.
  - A `Redirect` outbound can target an integration with **any** inbound
    type, not just `Api` (e.g. it could redirect into another
    `TimeTrigger`-inbound integration). Don't use inbound type as a shortcut
    for detecting redirects — always check `outboundConnections` directly
    as described above.
- Build the full chain of integration ids/names before writing any content,
  and list all of them (with their ids) in the title-page metadata and in
  section 2 or a short "Integrations in this flow" note, so the reader can
  see at a glance how many Connxio integrations implement the one
  documented flow.
- Always read and fully understand every integration in the flow (via
  `get_integration`, and `get_security_config` / `list_security_configs` for
  any referenced security configs) before drafting content. Confirm your
  understanding of the flow with the user first if this is the first time
  documenting it, unless they've already confirmed it in the conversation.

## Hard rules

- **Never expose real secrets** — passwords, client secrets, tokens, API
  keys, connection strings. Always write "stored securely, not shown"
  instead. This applies even in the most technical IT-facing sections.
- Don't invent endpoints, fields, or behavior — only document what is
  actually configured in the integration(s).
- **Each flow document must be self-contained.** Do not reference other
  flows by name for comparison (e.g. "unlike the account sync flow..."),
  even if they were documented earlier in the same session. The reader of
  one flow's documentation may never see another flow's document. State
  limitations/behavior in terms of the flow itself (e.g. "there is no logic
  to detect an already-transferred record and update it instead") without
  naming or contrasting against a separate flow.
- Ask the user before creating a *new* skill for something not already
  covered; this skill already covers flow documentation end-to-end.

## Document structure (standard template)

1. Title page — logo, title, subtitle (flow name / systems), metadata
   (customer, environment, integration name(s), document version, date).
2. **1. Overview** — plain-language summary of what the flow does.
3. **2. Systems Involved** — table of each system and its role.
4. **3. How the Flow is Started** — trigger type/schedule; note any
   dev-time placeholders (e.g. a disabled-looking CRON kept enabled because
   the editor requires it, with manual triggering as the workaround).
5. **4. Flow Description** — ordered table of steps in plain language,
   followed immediately by the embedded **flow diagram** (see below).
6. **5. Field Mapping** — source field → destination field → notes table.
7. **6. Create vs. Update Logic** (or equivalent decision logic) — bullet
   explanation of branching business rules.
8. **7. Technical Details** (IT-facing sections; include when audience is IT
   or "more technical" was requested):
   - **7.1 Trigger** — adapter type, schedule.
   - **7.2 Step-by-Step Technical Reference** — one block per step: bold
     step title + a 2-column key/value table (Type, Endpoint/Target, Method,
     Authentication, Condition). Do **not** use one wide table for all steps
     — it becomes cramped and hard to read. One mini-table per step is the
     standard.
   - **7.3 Security Configurations Referenced** — table of each security
     config used, its type, which steps use it, and non-secret details
     (env URL, client ID) — never the secret/password itself.
9. **8. Notes and Current Limitations** — bullet list of test-only
   restrictions, known caveats, planned changes before go-live.
10. "End of document" footer.

## Brand style guide

- Colors: brand green `ACCENT = RGBColor(0x00, 0xAE, 0x79)`, dark teal
  `DARK = RGBColor(0x1C, 0x4E, 0x50)`, grey `GREY = RGBColor(0x59, 0x59, 0x59)`,
  light green tint for zebra striping `LIGHT_TINT = "E6F7EF"`.
- Level-1 headings use `DARK`, level-2 (and deeper) headings use `ACCENT`.
- **Set colors on the named styles themselves** (`doc.styles["Title"]`,
  `Heading 1`, `Heading 2`, `Heading 3`) in addition to per-run overrides.
  Some renderers show named-style colors instead of run overrides, so
  relying on run-level color alone can make headings appear to render as
  Word's default theme blue even though the "correct" color is in the XML.
- Table headers: dark teal fill, white bold text. Data rows: alternate
  white / light-green tint, computed per row so **every** cell (not just
  odd rows) has an explicit `w:shd` fill — never leave a cell to fall back
  to the table style's own conditional formatting.
- Table borders: explicit dark-teal `w:tblBorders`, and disable the table
  style's banding entirely (`w:tblLook` with `firstRow=0`, `lastRow=0`,
  `firstColumn=0`, `lastColumn=0`, `noHBand=1`, `noVBand=1`, `val=0000`) so
  no built-in blue banding can show through unshaded cells.
- **Header cells need their own white borders** (`w:tcBorders`), not just
  the table-level dark ones — dark-on-dark borders are invisible against a
  dark teal header fill, which otherwise makes the header row look like it
  has no dividing lines.
- Logo: a Connxio logo with transparent background (`connxio-logo.png`) is
  bundled in this skill's own folder, alongside `SKILL.md`. Use it by
  default so the skill works out of the box for anyone running it —
  resolve the path relative to the skill folder (see template below) rather
  than a hardcoded personal path. Only fall back to asking the user for a
  logo file if this bundled one is missing or they explicitly want a
  different logo.
- Base font: Calibri, 10.5pt body text.

## Reusable python-docx helpers (canonical template)

Use this as the starting point for every new flow document. Copy it into a
working folder (e.g. `C:\temp\cx\docs\`), then customize the `build()`
content (sections 1–8) and the `steps` list for the specific flow. Keep the
helper functions as-is — they encode the styling fixes above.

**Setup:** before running the template, copy the bundled `connxio-logo.png`
(next to this `SKILL.md`, in the skill's own folder) into the working
folder so `LOGO_PATH` below resolves correctly. This makes the skill work
out of the box for anyone running it, without depending on a
previously-provided logo file.

```python
# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ACCENT = RGBColor(0x00, 0xAE, 0x79)   # Connxio brand green
DARK = RGBColor(0x1C, 0x4E, 0x50)     # Connxio dark teal
GREY = RGBColor(0x59, 0x59, 0x59)
LOGO_PATH = r"C:\temp\cx\docs\connxio-logo.png"       # copied in from the skill folder, see setup note below
FLOWCHART_PATH = r"C:\temp\cx\docs\flow-diagram.png"  # replace per project
LIGHT_TINT = "E6F7EF"


def set_cell_shading(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def set_cell_borders(cell, color_hex):
    """Give a cell its own borders. Needed for header cells: table-level
    grid lines drawn in a dark color are invisible against a dark header
    fill, so header cells get explicit (white) borders instead."""
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color_hex)
        borders.append(el)
    tc_pr.append(borders)


def set_table_borders(table, color_hex="1C4E50"):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color_hex)
        borders.append(el)
    tbl_pr.append(borders)

    # Disable style-based banding so no built-in blue conditional formatting
    # can show through on cells we don't explicitly shade ourselves.
    look = tbl_pr.find(qn("w:tblLook"))
    if look is None:
        look = OxmlElement("w:tblLook")
        tbl_pr.append(look)
    look.set(qn("w:val"), "0000")
    look.set(qn("w:firstRow"), "0")
    look.set(qn("w:lastRow"), "0")
    look.set(qn("w:firstColumn"), "0")
    look.set(qn("w:lastColumn"), "0")
    look.set(qn("w:noHBand"), "1")
    look.set(qn("w:noVBand"), "1")


def style_headings(doc):
    """Force named Heading/Title styles (not just per-run overrides) to use
    brand colors, so the right color shows regardless of renderer."""
    for style_name, color in (
        ("Title", DARK),
        ("Heading 1", DARK),
        ("Heading 2", ACCENT),
        ("Heading 3", ACCENT),
    ):
        try:
            doc.styles[style_name].font.color.rgb = color
        except KeyError:
            pass


def add_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    color = DARK if level == 1 else ACCENT
    for run in h.runs:
        run.font.color.rgb = color
    return h


def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    set_table_borders(table)
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.bold = True
        set_cell_shading(hdr_cells[i], "1C4E50")
        set_cell_borders(hdr_cells[i], "FFFFFF")
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            fill = LIGHT_TINT if row_index % 2 == 1 else "FFFFFF"
            set_cell_shading(cells[i], fill)
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
    doc.add_paragraph()
    return table


def add_step_reference_block(doc, title, fields):
    """Section 7.2 pattern: bold step title + a 2-column key/value table.
    `fields` is an ordered list of (label, value) pairs, e.g.
    [("Type", "REST"), ("Endpoint / Target", "..."), ("Method", "POST"),
     ("Authentication", "..."), ("Condition", "isUpdate == false")]."""
    p = doc.add_paragraph()
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(11.5)
    run.font.color.rgb = ACCENT

    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    set_table_borders(table)
    for row_index, (label, value) in enumerate(fields):
        row_cells = table.add_row().cells
        row_cells[0].text = label
        for para in row_cells[0].paragraphs:
            for r in para.runs:
                r.bold = True
        set_cell_shading(row_cells[0], "1C4E50")
        set_cell_borders(row_cells[0], "FFFFFF")
        for para in row_cells[0].paragraphs:
            for r in para.runs:
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        row_cells[1].text = value
        fill = LIGHT_TINT if row_index % 2 == 1 else "FFFFFF"
        set_cell_shading(row_cells[1], fill)
    table.columns[0].width = Inches(1.6)
    table.columns[1].width = Inches(5.2)
    for row in table.rows:
        row.cells[0].width = Inches(1.6)
        row.cells[1].width = Inches(5.2)
    doc.add_paragraph()


def build():
    doc = Document()
    style_headings(doc)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    # --- Title page ---
    doc.add_paragraph()
    logo_p = doc.add_paragraph()
    logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo_p.add_run().add_picture(LOGO_PATH, width=Inches(2.4))

    doc.add_paragraph()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Integration Documentation")
    run.bold = True
    run.font.size = Pt(28)
    run.font.color.rgb = DARK

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("<Flow name / systems involved>")
    run.font.size = Pt(16)
    run.font.color.rgb = ACCENT

    doc.add_paragraph()
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_run = meta.add_run(
        "Customer: <customer>\n"
        "Environment: <Test/Prod>\n"
        "Integration name(s): <name(s)>\n"
        "Document version: 1.0\n"
        "Date: <yyyy-mm-dd>"
    )
    meta_run.font.size = Pt(11)
    meta_run.font.color.rgb = GREY

    doc.add_page_break()

    # --- Fill in sections 1-8 here, following the standard structure above ---
    # add_heading(doc, "1. Overview", level=1)
    # ...
    # After section 4's step table, embed the flow diagram:
    # diagram_p = doc.add_paragraph()
    # diagram_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # diagram_p.add_run().add_picture(FLOWCHART_PATH, width=Inches(5.7))
    # caption = doc.add_paragraph()
    # caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # cap_run = caption.add_run("Figure 1: <Flow name> flow diagram")
    # cap_run.italic = True
    # cap_run.font.size = Pt(9.5)
    # cap_run.font.color.rgb = GREY

    doc.save(r"C:\temp\cx\docs\<Flow Name> - Integration Documentation v1.docx")


if __name__ == "__main__":
    build()
```

## Flow diagram (matplotlib) — decision shapes and branching legs

Do **not** draw a single straight vertical chain when the flow has
branching logic (e.g. create vs. update, success vs. error). Use a real
decision diamond and separate the branches into visually distinct legs
(side-by-side columns) that reconverge at a shared "End" box. This is the
standard — a flat list of boxes with a text label describing the branch is
not sufficient.

```python
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

ACCENT = "#00AE79"
DARK = "#1C4E50"
GREY = "#F2F2F2"
WHITE = "#FFFFFF"


def draw_box(ax, x, y, w, h, label, facecolor, textcolor=WHITE, fontsize=10):
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                          boxstyle="round,pad=0.15,rounding_size=0.22",
                          linewidth=1.4, edgecolor=DARK, facecolor=facecolor)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize,
            color=textcolor, fontweight="bold", linespacing=1.35)
    return (x, y, w, h)


def draw_diamond(ax, x, y, w, h, label, facecolor=DARK, textcolor=WHITE, fontsize=10):
    pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
    ax.add_patch(Polygon(pts, closed=True, linewidth=1.4, edgecolor=DARK, facecolor=facecolor))
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize,
            color=textcolor, fontweight="bold", linespacing=1.3)
    return (x, y, w, h)


def arrow(ax, p0, p1, color=DARK, ls="solid", lw=1.6):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=17,
                                  linewidth=lw, color=color, linestyle=ls,
                                  shrinkA=0, shrinkB=0))


def edge_point(box, side):
    x, y, w, h = box
    return {"top": (x, y + h / 2), "bottom": (x, y - h / 2),
            "left": (x - w / 2, y), "right": (x + w / 2, y)}[side]


# Build a common trunk of boxes top-to-bottom, then a draw_diamond() for the
# decision point, then two (or more) parallel legs of draw_box() calls at
# different x positions that reconverge into a shared "End" box — see the
# Account.Trigger flow diagram in this session's history for a full worked
# example (trigger -> retrieve -> split -> map -> decision -> [create leg |
# update leg] -> End).
```

## Procedure

1. Identify every integration in the flow (trace redirect actions per the
   detection steps above). Call `get_integration` (and
   `get_security_config`/`list_security_configs` for referenced security
   configs) for each one.
2. Summarize your understanding of the flow back to the user and get
   confirmation before writing the document, unless already confirmed.
3. Ask (or infer from context) the target audience: customer-readable
   overview only, or IT-technical (include section 7).
4. Set up the working folder: create it if needed, and copy this skill's
   bundled `connxio-logo.png` into it so the document template's `LOGO_PATH`
   resolves.
5. Build the flow diagram PNG first (matplotlib template above), reflecting
   every real branch with a decision diamond and separate legs.
6. Build the Word document (python-docx template above), embedding the
   diagram after the section 4 step table.
7. Save output as `<Flow Name> - Integration Documentation v<N>.docx` in the
   working docs folder (e.g. `C:\temp\cx\docs\`), incrementing the version
   number on each revision so prior versions aren't overwritten.
8. Before presenting, verify there are no un-shaded table cells, no
   remaining theme-blue color codes, and no exposed secrets — e.g. by
   inspecting the generated `word/document.xml` for `w:color` values and
   confirming every `<w:tc>` contains a `<w:shd>`.
9. Present the result to the user and iterate based on feedback (colors,
   logo, layout, added detail) — this skill's template should be updated
   with any recurring style fixes so future documents don't repeat the same
   issues.
