#!/usr/bin/env python3
"""
Debug the generated PDF to see if fields are actually filled
"""

import pypdf
import sys

def debug_generated_pdf(pdf_path):
    """Debug the generated PDF"""
    print(f"🔍 Debugging generated PDF: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            print(f"📄 PDF Pages: {len(pdf_reader.pages)}")
            
            # Method 1: get_form_text_fields()
            print("\n🔍 Method 1: get_form_text_fields()")
            try:
                text_fields = pdf_reader.get_form_text_fields()
                print(f"Type: {type(text_fields)}")
                if text_fields and isinstance(text_fields, dict):
                    print(f"📊 Text fields found: {len(text_fields)}")
                    
                    # Look for our critical fields
                    critical_fields = [
                        "P1Line1a_FamilyName[0]",
                        "P1_Line1b_GivenName[0]", 
                        "Part1_Item6_StreetName[0]",
                        "Part1_Item6_City[0]",
                        "P2_Line10_Province[0]",
                        "Part1_Item6_ZipCode[0]",
                        "P5_Line5_EmailAddress[0]",
                        "P5_Line3_DaytimePhoneNumber[0]",
                        "Part1_Item4_Number[0]",
                        "P1_Line6_CountryOfBirth[0]"
                    ]
                    
                    print(f"\n🎯 CRITICAL FIELDS CHECK:")
                    filled_count = 0
                    for field in critical_fields:
                        value = text_fields.get(field, "NOT FOUND")
                        if value and value != "NOT FOUND" and value.strip():
                            filled_count += 1
                            print(f"  ✅ {field}: '{value}'")
                        else:
                            print(f"  ❌ {field}: '{value}'")
                    
                    print(f"\n📊 CRITICAL FIELDS FILLED: {filled_count}/{len(critical_fields)}")
                    
                    # Show all non-empty fields
                    print(f"\n📋 ALL NON-EMPTY FIELDS:")
                    non_empty_count = 0
                    for field_name, field_value in text_fields.items():
                        if field_value and field_value.strip() and field_value != "None":
                            non_empty_count += 1
                            print(f"  {non_empty_count}. {field_name}: '{field_value}'")
                    
                    print(f"\n📊 TOTAL NON-EMPTY FIELDS: {non_empty_count}/{len(text_fields)}")
                    
                else:
                    print("❌ No text fields or wrong type")
            except Exception as e:
                print(f"❌ get_form_text_fields() failed: {str(e)}")
            
            # Method 2: Extract text to see if data is visible
            print("\n🔍 Method 2: Text extraction")
            try:
                first_page_text = pdf_reader.pages[0].extract_text()
                print(f"📄 First page text length: {len(first_page_text)} characters")
                
                # Look for our test data
                test_strings = ["Roberto", "Silva", "Orlando", "FL", "32801", "BR111222333", "roberto.mendes"]
                found_strings = []
                
                for test_str in test_strings:
                    if test_str in first_page_text:
                        found_strings.append(test_str)
                
                print(f"📊 Test data found in text: {len(found_strings)}/{len(test_strings)}")
                for found in found_strings:
                    print(f"  ✅ Found: {found}")
                
                # Show a sample of the text
                if len(first_page_text) > 200:
                    print(f"\n📄 Sample text (first 500 chars):")
                    print(repr(first_page_text[:500]))
                
            except Exception as e:
                print(f"❌ Text extraction failed: {str(e)}")
    
    except Exception as e:
        print(f"❌ Error opening PDF: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_generated_pdf.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    debug_generated_pdf(pdf_path)