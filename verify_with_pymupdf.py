#!/usr/bin/env python3
"""
Verify PDFs using pymupdf (fitz) as a second verification method.
"""
import fitz  # pymupdf
import os

def analyze_with_pymupdf(pdf_path, test_name):
    """Analyze PDF using pymupdf."""
    print("\n" + "=" * 80)
    print(f"PYMUPDF ANALYSIS: {test_name}")
    print(f"File: {pdf_path}")
    print("=" * 80)
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: File not found: {pdf_path}")
        return
    
    try:
        doc = fitz.open(pdf_path)
        print(f"Number of pages: {len(doc)}")
        
        all_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            all_text += page_text
            print(f"\nPage {page_num + 1} text length: {len(page_text)} characters")
        
        print(f"\n📄 EXTRACTED TEXT (pymupdf):")
        print(f"Total length: {len(all_text)} characters")
        print(f"Text preview (first 300 chars):")
        print(all_text[:300])
        print("\n" + "-" * 80)
        
        # Check for Devanagari
        devanagari_chars = [c for c in all_text if '\u0900' <= c <= '\u097F']
        devanagari_count = len(devanagari_chars)
        
        print(f"\n🔍 DEVANAGARI ANALYSIS:")
        print(f"Devanagari characters: {devanagari_count}")
        if devanagari_count > 0:
            print(f"Sample: {''.join(devanagari_chars[:50])}")
        
        # Check for '?'
        question_marks = all_text.count('?')
        print(f"\n❓ Question marks: {question_marks}")
        
        # Check for specific words
        print(f"\n🔎 CONTENT CHECK:")
        if "संपादित" in all_text:
            print("✅ Found 'संपादित'")
        if "परीक्षण" in all_text:
            print("✅ Found 'परीक्षण'")
        if "Hello" in all_text or "hello" in all_text.lower():
            print("✅ Found 'Hello'")
        if "edited" in all_text.lower():
            print("✅ Found 'edited'")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 80)
    print("PYMUPDF (FITZ) VERIFICATION")
    print("=" * 80)
    
    analyze_with_pymupdf('/tmp/hindi_edited_out.pdf', 'Hindi Edited PDF')
    analyze_with_pymupdf('/tmp/english_edited_out.pdf', 'English Edited PDF')

if __name__ == '__main__':
    main()
