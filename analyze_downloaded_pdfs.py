#!/usr/bin/env python3
"""
Analyze the downloaded PDFs to verify Devanagari font embedding.
"""
import pdfplumber
import os

def analyze_pdf(pdf_path, test_name):
    """Analyze a PDF and check for Devanagari characters and '?' placeholders."""
    print("\n" + "=" * 80)
    print(f"ANALYZING: {test_name}")
    print(f"File: {pdf_path}")
    print("=" * 80)
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: File not found: {pdf_path}")
        return False
    
    file_size = os.path.getsize(pdf_path)
    print(f"File size: {file_size} bytes")
    
    try:
        with pdfplumber.open(pdf_path) as pdf_doc:
            print(f"Number of pages: {len(pdf_doc.pages)}")
            
            all_text = ""
            for i, page_obj in enumerate(pdf_doc.pages):
                page_text = page_obj.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                    print(f"\nPage {i+1} text length: {len(page_text)} characters")
            
            print(f"\n📄 EXTRACTED TEXT:")
            print(f"Total length: {len(all_text)} characters")
            print(f"Text preview (first 300 chars):")
            print(all_text[:300])
            print("\n" + "-" * 80)
            
            # Check for Devanagari Unicode characters (U+0900–U+097F)
            devanagari_chars = [c for c in all_text if '\u0900' <= c <= '\u097F']
            devanagari_count = len(devanagari_chars)
            
            print(f"\n🔍 DEVANAGARI UNICODE ANALYSIS:")
            print(f"Devanagari characters found: {devanagari_count}")
            if devanagari_count > 0:
                # Show unique Devanagari characters
                unique_deva = sorted(set(devanagari_chars))
                print(f"Unique Devanagari chars ({len(unique_deva)}): {''.join(unique_deva[:30])}")
                print(f"Sample Devanagari text: {''.join(devanagari_chars[:50])}")
            
            # Check for '?' characters
            question_marks = all_text.count('?')
            print(f"\n❓ QUESTION MARK ANALYSIS:")
            print(f"Question mark count: {question_marks}")
            
            # Check for specific edited words
            print(f"\n🔎 CONTENT VERIFICATION:")
            if "संपादित" in all_text:
                print("✅ Found edited word 'संपादित' (edited)")
            if "परीक्षण" in all_text:
                print("✅ Found word 'परीक्षण' (test)")
            if "नमस्ते" in all_text:
                print("✅ Found word 'नमस्ते' (hello)")
            if "दुनिया" in all_text:
                print("✅ Found word 'दुनिया' (world)")
            
            # ASSERTIONS
            print("\n" + "=" * 80)
            print("ASSERTIONS:")
            print("=" * 80)
            
            passed = True
            
            if devanagari_count > 0:
                print(f"✅ PASS: PDF contains {devanagari_count} Devanagari Unicode characters (U+0900–U+097F)")
            else:
                print("❌ FAIL: PDF does NOT contain Devanagari Unicode characters")
                passed = False
            
            if question_marks == 0:
                print("✅ PASS: PDF does NOT contain '?' placeholders")
            else:
                print(f"⚠️ WARNING: PDF contains {question_marks} '?' characters")
                # Check if these are legitimate question marks or placeholders
                if question_marks > 5:
                    print("❌ FAIL: Too many '?' characters - likely placeholders for missing glyphs")
                    passed = False
            
            return passed
            
    except Exception as e:
        print(f"❌ ERROR analyzing PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 80)
    print("PDF ANALYSIS: Devanagari Font Embedding Verification")
    print("=" * 80)
    
    # Test 1: Hindi edited PDF
    hindi_passed = analyze_pdf('/tmp/hindi_edited_out.pdf', 'TEST 1: Hindi Edited PDF')
    
    # Test 2: English edited PDF
    print("\n\n")
    english_passed = analyze_pdf('/tmp/english_edited_out.pdf', 'TEST 2: English Edited PDF (Regression)')
    
    # For English PDF, check that it contains English text
    print("\n" + "=" * 80)
    print("ENGLISH PDF SPECIFIC CHECKS:")
    print("=" * 80)
    
    try:
        with pdfplumber.open('/tmp/english_edited_out.pdf') as pdf_doc:
            all_text = ""
            for page_obj in pdf_doc.pages:
                page_text = page_obj.extract_text()
                if page_text:
                    all_text += page_text + "\n"
            
            if "Hello" in all_text or "hello" in all_text.lower():
                print("✅ PASS: English text 'Hello' found")
            else:
                print("⚠️ WARNING: 'Hello' not found in English PDF")
            
            if "edited" in all_text.lower():
                print("✅ PASS: Edited word 'edited' found")
            else:
                print("⚠️ WARNING: 'edited' not found in English PDF")
            
            # Check that English text is not garbled
            devanagari_in_english = len([c for c in all_text if '\u0900' <= c <= '\u097F'])
            if devanagari_in_english == 0:
                print("✅ PASS: English PDF does not contain Devanagari (not garbled)")
            else:
                print(f"⚠️ WARNING: English PDF contains {devanagari_in_english} Devanagari characters")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    if hindi_passed:
        print("✅ TEST 1 PASSED: Hindi PDF with Devanagari font embedding")
    else:
        print("❌ TEST 1 FAILED: Hindi PDF Devanagari verification failed")
    
    if english_passed:
        print("✅ TEST 2 PASSED: English PDF regression test")
    else:
        print("⚠️ TEST 2: English PDF - check warnings above")
    
    if hindi_passed and english_passed:
        print("\n🎉 ALL TESTS PASSED! Devanagari font embedding is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed or have warnings. Review the details above.")
        return 1

if __name__ == '__main__':
    exit(main())
