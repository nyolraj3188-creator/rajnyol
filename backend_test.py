#!/usr/bin/env python3
"""
Test suite for POST /api/pdf/inspect endpoint enhancements:
- Content-based legacy-Hindi auto-detection
- English safeguard (looks_english heuristic)
"""
import requests
import io
from fpdf import FPDF

# Backend URL from frontend/.env
BACKEND_URL = "https://9b2e52ba-3227-4606-8314-c9a510e3eef8.preview.emergentagent.com/api"

def create_english_pdf() -> bytes:
    """Create a plain English text PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    # Use many common English words to trigger looks_english heuristic
    text = """This is a plain English document for testing purposes and it has many common words on the page.
The document contains text that should be recognized as English prose with the words like the, and, of, to, in, is, a, for, that, on, with, as, are, be, this, by, or, at, it, from, an, was, not, which, have, has, had, will, would, can, could, all, you, your, we, our, their, they, he, she, his, her, but, if, so, do, does, been, were, more, one, also, may, such, its, into, than, when, who, what, how, about, page, document, name, date, total, no, yes, there, these, some, other, only, over, then, them, out."""
    pdf.multi_cell(0, 10, text)
    output = pdf.output()
    return bytes(output) if isinstance(output, bytearray) else output

def create_kruti_ascii_pdf_non_legacy_font() -> bytes:
    """Create a PDF with genuine Kruti Dev ASCII encoding but using a NON-legacy font name.
    This tests content-based detection independent of font name."""
    pdf = FPDF()
    pdf.add_page()
    # Use built-in font (Helvetica/Arial) - NOT a legacy font name
    pdf.set_font("Helvetica", size=14)
    # Write EXACT Kruti Dev ASCII encoding lines as specified in the review request
    kruti_lines = [
        "pfj= izek.k i=",
        "izekf.kr fd;k tkrk gS fd Jh@dqekjh@Jherh",
        "O;fkxr :i ls ekg@o\"kksZa ls tkurk@tkurh gwi",
        "budk uSfrd pfj= mmke gSA"
    ]
    for line in kruti_lines:
        pdf.cell(0, 10, line, ln=True)
    output = pdf.output()
    return bytes(output) if isinstance(output, bytearray) else output

def create_empty_pdf() -> bytes:
    """Create a PDF with a blank page (no text)."""
    pdf = FPDF()
    pdf.add_page()
    # Don't add any text
    output = pdf.output()
    return bytes(output) if isinstance(output, bytearray) else output

def test_inspect_endpoint(pdf_bytes: bytes, test_name: str) -> dict:
    """POST a PDF to /api/pdf/inspect and return the JSON response."""
    url = f"{BACKEND_URL}/pdf/inspect"
    files = {'file': ('test.pdf', io.BytesIO(pdf_bytes), 'application/pdf')}
    response = requests.post(url, files=files, timeout=60)
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response JSON: {result}")
        return result
    else:
        print(f"ERROR: {response.text}")
        return None

def test_pdf_to_word(pdf_bytes: bytes, test_name: str) -> bool:
    """POST a PDF to /api/pdf/pdf-to-word and verify it returns a valid .docx."""
    url = f"{BACKEND_URL}/pdf/pdf-to-word"
    files = {'file': ('test.pdf', io.BytesIO(pdf_bytes), 'application/pdf')}
    response = requests.post(url, files=files, timeout=120)
    print(f"\n{'='*80}")
    print(f"REGRESSION TEST: {test_name} -> pdf-to-word")
    print(f"{'='*80}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        docx_bytes = response.content
        print(f"Response size: {len(docx_bytes)} bytes")
        # Check if it's a valid .docx (starts with PK zip signature)
        is_valid = docx_bytes[:2] == b'PK' and len(docx_bytes) > 1000
        print(f"Valid .docx: {is_valid}")
        return is_valid
    else:
        print(f"ERROR: {response.text}")
        return False

def main():
    print("="*80)
    print("TESTING POST /api/pdf/inspect - Content-based legacy-Hindi detection")
    print("="*80)
    
    # Test 1: Plain English PDF
    print("\n\n### TEST CASE 1: PLAIN ENGLISH PDF ###")
    english_pdf = create_english_pdf()
    result1 = test_inspect_endpoint(english_pdf, "Plain English PDF")
    if result1:
        assert result1['has_text'] == True, f"Expected has_text=True, got {result1['has_text']}"
        assert result1['devanagari_ratio'] <= 0.05, f"Expected devanagari_ratio ~0.0, got {result1['devanagari_ratio']}"
        assert result1['looks_english'] == True, f"Expected looks_english=True, got {result1['looks_english']}"
        assert result1['legacy_hindi'] == False, f"Expected legacy_hindi=False, got {result1['legacy_hindi']}"
        print("✅ PASS: Plain English PDF correctly identified")
    else:
        print("❌ FAIL: Plain English PDF test failed")
    
    # Test 2: Simulated Kruti Dev ASCII PDF with NON-legacy font name
    print("\n\n### TEST CASE 2: KRUTI DEV ASCII PDF (NON-LEGACY FONT NAME) ###")
    kruti_pdf = create_kruti_ascii_pdf_non_legacy_font()
    result2 = test_inspect_endpoint(kruti_pdf, "Kruti Dev ASCII (Helvetica font)")
    if result2:
        assert result2['has_text'] == True, f"Expected has_text=True, got {result2['has_text']}"
        assert result2['devanagari_ratio'] < 0.15, f"Expected devanagari_ratio<0.15, got {result2['devanagari_ratio']}"
        assert result2['looks_english'] == False, f"Expected looks_english=False, got {result2['looks_english']}"
        assert result2['legacy_hindi'] == False, f"Expected legacy_hindi=False (non-legacy font), got {result2['legacy_hindi']}"
        print("✅ PASS: Kruti Dev ASCII PDF correctly identified (content-based, font name NOT legacy)")
        print("   This proves content signal (has_text && ratio<0.15 && !looks_english) works independent of font name")
    else:
        print("❌ FAIL: Kruti Dev ASCII PDF test failed")
    
    # Test 3: Empty/no-text PDF
    print("\n\n### TEST CASE 3: EMPTY / NO-TEXT PDF ###")
    empty_pdf = create_empty_pdf()
    result3 = test_inspect_endpoint(empty_pdf, "Empty PDF (no text)")
    if result3:
        assert result3['has_text'] == False, f"Expected has_text=False, got {result3['has_text']}"
        assert result3['looks_english'] == False, f"Expected looks_english=False, got {result3['looks_english']}"
        assert result3['devanagari_ratio'] == 0.0, f"Expected devanagari_ratio=0.0, got {result3['devanagari_ratio']}"
        print("✅ PASS: Empty PDF correctly identified")
    else:
        print("❌ FAIL: Empty PDF test failed")
    
    # Test 4: Regression - pdf-to-word with English PDF
    print("\n\n### TEST CASE 4: REGRESSION - English PDF to Word ###")
    success1 = test_pdf_to_word(english_pdf, "English PDF")
    if success1:
        print("✅ PASS: English PDF to Word conversion working")
    else:
        print("❌ FAIL: English PDF to Word conversion failed")
    
    # Test 5: Regression - pdf-to-word with Kruti PDF
    print("\n\n### TEST CASE 5: REGRESSION - Kruti ASCII PDF to Word ###")
    success2 = test_pdf_to_word(kruti_pdf, "Kruti ASCII PDF")
    if success2:
        print("✅ PASS: Kruti ASCII PDF to Word conversion working")
    else:
        print("❌ FAIL: Kruti ASCII PDF to Word conversion failed")
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    all_passed = (
        result1 and result1['has_text'] and result1['looks_english'] and not result1['legacy_hindi'] and
        result2 and result2['has_text'] and not result2['looks_english'] and not result2['legacy_hindi'] and result2['devanagari_ratio'] < 0.15 and
        result3 and not result3['has_text'] and
        success1 and success2
    )
    if all_passed:
        print("✅ ALL TESTS PASSED (5/5)")
        print("\nKEY FINDINGS:")
        print("1. Plain English PDF: has_text=true, devanagari_ratio~0, looks_english=true, legacy_hindi=false")
        print("2. Kruti ASCII PDF (NON-legacy font): has_text=true, devanagari_ratio<0.15, looks_english=false, legacy_hindi=false")
        print("   → Content-based detection working INDEPENDENT of font name")
        print("3. Empty PDF: has_text=false, looks_english=false, devanagari_ratio=0.0")
        print("4. English PDF to Word: HTTP 200, valid .docx")
        print("5. Kruti ASCII PDF to Word: HTTP 200, valid .docx")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nFailed tests:")
        if not (result1 and result1['has_text'] and result1['looks_english'] and not result1['legacy_hindi']):
            print("  - Plain English PDF test")
        if not (result2 and result2['has_text'] and not result2['looks_english'] and not result2['legacy_hindi'] and result2['devanagari_ratio'] < 0.15):
            print("  - Kruti ASCII PDF test")
        if not (result3 and not result3['has_text']):
            print("  - Empty PDF test")
        if not success1:
            print("  - English PDF to Word regression")
        if not success2:
            print("  - Kruti ASCII PDF to Word regression")

if __name__ == "__main__":
    main()
