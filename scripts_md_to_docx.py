"""
Chuyển bao_cao_luan_van.md sang bao_cao_luan_van.docx.
Parser markdown thu gọn, chỉ hỗ trợ đúng tập cú pháp dùng trong file nguồn:
#, ##, ###, ####, - bullet, 1. numbered, **bold**, *italic*, $...$/$$...$$ (giữ nguyên
dạng LaTeX, hiển thị nghiêng), bảng |...|, code fence ```, blockquote '>', '---' (ngắt trang).
"""
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = "bao_cao_luan_van.md"
OUT = "bao_cao_luan_van.docx"

BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def add_runs(paragraph, text, base_italic=False, mono=False):
    """Thêm text vào paragraph, xử lý **bold** và $...$ (in nghiêng) trong cùng 1 dòng."""
    # Tách theo bold trước, giữ lại phần còn lại xử lý math/italic đơn giản.
    tokens = []
    pos = 0
    for m in BOLD_RE.finditer(text):
        if m.start() > pos:
            tokens.append(("plain", text[pos:m.start()]))
        tokens.append(("bold", m.group(1)))
        pos = m.end()
    if pos < len(text):
        tokens.append(("plain", text[pos:]))

    for kind, chunk in tokens:
        # Trong phần plain, tách tiếp theo $...$ để in nghiêng (biểu diễn công thức).
        sub_pos = 0
        for dm in re.finditer(r"\$(.+?)\$", chunk):
            if dm.start() > sub_pos:
                r = paragraph.add_run(chunk[sub_pos:dm.start()])
                r.italic = base_italic
                if mono:
                    r.font.name = "Consolas"
            r = paragraph.add_run(dm.group(1))
            r.italic = True
            r.font.name = "Cambria Math"
            sub_pos = dm.end()
        remainder = chunk[sub_pos:]
        if remainder:
            r = paragraph.add_run(remainder)
            r.bold = (kind == "bold")
            r.italic = base_italic or r.italic
            if mono:
                r.font.name = "Consolas"


def set_col_widths(table, widths_cm):
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            cell.width = Cm(widths_cm[idx])


def shade_cell(cell, color="D9D9D9"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def parse_table(lines, start):
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        row = lines[i].strip()
        if not re.match(r"^\|[\s:\-|]+\|$", row):
            cells = [c.strip() for c in row.strip("|").split("|")]
            rows.append(cells)
        i += 1
    return rows, i


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    for i in range(1, 10):
        try:
            h = doc.styles[f"Heading {i}"]
            h.font.name = "Times New Roman"
            h.font.color.rgb = None
        except KeyError:
            pass

    i = 0
    n = len(lines)
    in_code = False
    code_buf = []

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_buf = []
            else:
                in_code = False
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.5)
                for j, cl in enumerate(code_buf):
                    r = p.add_run(cl if j == 0 else "\n" + cl)
                    r.font.name = "Consolas"
                    r.font.size = Pt(9.5)
            i += 1
            continue
        if in_code:
            code_buf.append(raw)
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            doc.add_page_break()
            i += 1
            continue

        if stripped.startswith("|"):
            table_rows, i = parse_table(lines, i)
            if table_rows:
                ncols = len(table_rows[0])
                table = doc.add_table(rows=0, cols=ncols)
                table.style = "Light Grid Accent 1"
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                for r_idx, row_cells in enumerate(table_rows):
                    row = table.add_row()
                    for c_idx in range(ncols):
                        text = row_cells[c_idx] if c_idx < len(row_cells) else ""
                        cell = row.cells[c_idx]
                        cell.paragraphs[0].clear() if cell.paragraphs[0].runs else None
                        p = cell.paragraphs[0]
                        add_runs(p, text)
                        for run in p.runs:
                            run.font.size = Pt(10)
                        if r_idx == 0:
                            for run in p.runs:
                                run.bold = True
                            shade_cell(cell, "D9E2F3")
                doc.add_paragraph()
            continue

        if stripped.startswith("#### "):
            p = doc.add_heading(level=4)
            add_runs(p, stripped[5:])
            i += 1
            continue
        if stripped.startswith("### "):
            p = doc.add_heading(level=3)
            add_runs(p, stripped[4:])
            i += 1
            continue
        if stripped.startswith("## "):
            p = doc.add_heading(level=2)
            add_runs(p, stripped[3:])
            i += 1
            continue
        if stripped.startswith("# "):
            p = doc.add_heading(level=1)
            add_runs(p, stripped[2:])
            i += 1
            continue

        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(stripped.strip("$"))
            r.italic = True
            r.font.name = "Cambria Math"
            i += 1
            continue

        if stripped.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            add_runs(p, stripped[2:])
            i += 1
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            p = doc.add_paragraph(style="List Number")
            add_runs(p, m.group(2))
            i += 1
            continue

        if stripped.startswith("> "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(1.0)
            add_runs(p, stripped[2:], base_italic=True)
            i += 1
            continue

        if stripped.startswith("**"):
            p = doc.add_paragraph()
            add_runs(p, stripped)
            i += 1
            continue

        p = doc.add_paragraph()
        add_runs(p, stripped)
        i += 1

    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
