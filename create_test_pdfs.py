#!/usr/bin/env python3
"""
Create test PDFs for Edit PDF page testing:
1. /tmp/kruti_test.pdf - Kruti Dev ASCII encoding with normal font name (Helvetica)
2. /tmp/english_test.pdf - Plain English text
"""
from fpdf import FPDF

# Test 1: Kruti Dev ASCII PDF with normal font name (Helvetica)
# These are genuine Kruti Dev ASCII encodings that should convert to Devanagari
kruti_lines = [
    "pfj= izek.k i=",
    "izekf.kr fd;k tkrk gS fd Jh@dqekjh@Jherh",
    "budk uSfrd pfj= mmke gSA"
]

pdf1 = FPDF()
pdf1.add_page()
pdf1.set_font("Helvetica", size=20)  # Using normal font name, NOT a legacy name
y = 50
for line in kruti_lines:
    pdf1.set_xy(30, y)
    pdf1.cell(0, 10, line)
    y += 15

pdf1.output("/tmp/kruti_test.pdf")
print("✓ Created /tmp/kruti_test.pdf with Kruti Dev ASCII encoding (font: Helvetica)")

# Test 2: Plain English PDF
english_text = [
    "This is a plain English document for testing the edit pdf tool.",
    "It has many common words on the page.",
    "The text should remain readable and not be garbled.",
    "This verifies the English safeguard is working correctly."
]

pdf2 = FPDF()
pdf2.add_page()
pdf2.set_font("Helvetica", size=14)
y = 50
for line in english_text:
    pdf2.set_xy(30, y)
    pdf2.cell(0, 10, line)
    y += 12

pdf2.output("/tmp/english_test.pdf")
print("✓ Created /tmp/english_test.pdf with plain English text")

print("\nTest PDFs created successfully!")
print("- /tmp/kruti_test.pdf: Kruti Dev ASCII (should convert to Devanagari)")
print("- /tmp/english_test.pdf: Plain English (should remain English)")
