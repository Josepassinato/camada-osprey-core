#!/usr/bin/env python3
"""
Check if the data is actually in the PDF text (even if not in form fields)
"""

import pypdf
import sys

def check_pdf_text(pdf_path):
    """Check if data is in PDF text"""
    print(f"🔍 Checking PDF text content: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            print(f"📄 PDF Pages: {len(pdf_reader.pages)}")
            
            # Extract text from all pages
            all_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                all_text += page_text
                print(f"📄 Page {page_num + 1} text length: {len(page_text)} characters")
            
            print(f"📄 Total text length: {len(all_text)} characters")
            
            # Look for our test data
            test_data = {
                "Roberto": "Roberto",
                "Silva": "Silva", 
                "Carlos": "Carlos",
                "Mendes": "Mendes",
                "Orlando": "Orlando",
                "FL": "FL",
                "32801": "32801",
                "BR111222333": "BR111222333",
                "roberto.mendes@testqa.com": "roberto.mendes@testqa.com",
                "+1-407-555-1234": "+1-407-555-1234",
                "Brazil": "Brazil",
                "2580 Ocean Drive": "2580 Ocean Drive"
            }
            
            found_data = {}
            for key, value in test_data.items():
                if value in all_text:
                    found_data[key] = "✅ FOUND"
                else:
                    found_data[key] = "❌ NOT FOUND"
            
            print(f"\n🎯 TEST DATA IN PDF TEXT:")
            found_count = 0
            for key, status in found_data.items():
                print(f"  {status} {key}")
                if "✅" in status:
                    found_count += 1
            
            print(f"\n📊 DATA FOUND: {found_count}/{len(test_data)} ({found_count/len(test_data)*100:.1f}%)")
            
            # Show sample text from each page
            print(f"\n📄 SAMPLE TEXT FROM EACH PAGE:")
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if len(page_text) > 100:
                    print(f"\nPage {page_num + 1} (first 200 chars):")
                    print(repr(page_text[:200]))
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_pdf_text.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    check_pdf_text(pdf_path)