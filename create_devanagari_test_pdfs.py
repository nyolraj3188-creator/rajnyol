#!/usr/bin/env python3
"""
Create test PDFs with REAL Devanagari Unicode text for Edit PDF font embedding test.
This is different from Kruti Dev ASCII - these PDFs have actual Unicode Devanagari.
"""
from fpdf import FPDF
import os

# Path to the Devanagari font
FONT_PATH = "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf"

def create_hindi_unicode_pdf():
    """Create a PDF with REAL Hindi Devanagari Unicode text."""
    pdf = FPDF()
    pdf.add_page()
    
    # Register the Devanagari font with a normal name (not legacy)
    pdf.add_font('Lohit-Devanagari', '', FONT_PATH, uni=True)
    pdf.set_font('Lohit-Devanagari', size=20)
    
    # Add Hindi text lines with REAL Devanagari Unicode
    pdf.set_xy(20, 30)
    pdf.cell(0, 10, 'नमस्ते दुनिया यह एक परीक्षण है', ln=True)
    
    pdf.set_xy(20, 50)
    pdf.cell(0, 10, 'चरित्र प्रमाण पत्र', ln=True)
    
    pdf.set_xy(20, 70)
    pdf.cell(0, 10, 'प्रमाणित किया जाता है कि श्री', ln=True)
    
    pdf.set_xy(20, 90)
    pdf.cell(0, 10, 'इनका नैतिक चरित्र उत्तम है', ln=True)
    
    output_path = '/tmp/hindi_edit_test.pdf'
    pdf.output(output_path)
    print(f"✅ Created Hindi Unicode test PDF: {output_path}")
    return output_path

def create_english_pdf():
    """Create a PDF with English text."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', size=16)
    
    pdf.set_xy(20, 30)
    pdf.cell(0, 10, 'Hello world this is a test document', ln=True)
    
    pdf.set_xy(20, 50)
    pdf.cell(0, 10, 'This is a simple English PDF', ln=True)
    
    pdf.set_xy(20, 70)
    pdf.cell(0, 10, 'for regression testing purposes', ln=True)
    
    output_path = '/tmp/english_edit_test.pdf'
    pdf.output(output_path)
    print(f"✅ Created English test PDF: {output_path}")
    return output_path

if __name__ == '__main__':
    # Check if font exists
    if not os.path.exists(FONT_PATH):
        print(f"❌ Font not found: {FONT_PATH}")
        exit(1)
    
    print("Creating test PDFs with REAL Devanagari Unicode text...")
    hindi_pdf = create_hindi_unicode_pdf()
    english_pdf = create_english_pdf()
    print("\n✅ All test PDFs created successfully!")
    print(f"Hindi Unicode PDF: {hindi_pdf}")
    print(f"English PDF: {english_pdf}")
