from pathlib import Path
from fpdf import FPDF

txt_path = Path("inputs/sample.txt")
pdf_path = Path("inputs/sample.pdf")
pdf_path.parent.mkdir(parents=True, exist_ok=True)

text = txt_path.read_text(encoding="utf-8")

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

for line in text.split("\n"):
    pdf.multi_cell(0, 8, line)

pdf.output(str(pdf_path))
print("✅ Created:", pdf_path)
