#!/usr/bin/env python3
"""
Debug PDF Fields - Check what fields exist in the I-539 template
"""

import pypdf
import os

def debug_pdf_fields():
    """Debug the I-539 PDF template to see available fields"""
    
    template_path = "/app/official_forms/uscis_forms/I-539.pdf"
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return
    
    print(f"🔍 Analyzing PDF template: {template_path}")
    
    try:
        reader = pypdf.PdfReader(template_path)
        print(f"📄 PDF Pages: {len(reader.pages)}")
        
        # Method 1: get_form_text_fields()
        try:
            text_fields = reader.get_form_text_fields()
            if text_fields:
                print(f"📊 Text fields found: {len(text_fields)}")
                print("\n🎯 CRITICAL FIELDS WE'RE LOOKING FOR:")
                critical_fields = [
                    "Pt1Line1a_FamilyName",
                    "Pt1Line1b_GivenName", 
                    "Pt1Line7a_StreetNumberName",
                    "Pt1Line7c_CityOrTown",
                    "Pt1Line7d_State",
                    "Pt1Line7e_ZipCode",
                    "Pt1Line8_Email",
                    "Pt1Line9_DaytimeTelephone"
                ]
                
                for field in critical_fields:
                    if field in text_fields:
                        print(f"  ✅ {field}: EXISTS")
                    else:
                        print(f"  ❌ {field}: NOT FOUND")
                
                print(f"\n📋 ALL AVAILABLE FIELDS (first 20):")
                for i, (field_name, field_value) in enumerate(list(text_fields.items())[:20]):
                    print(f"  {i+1:2d}. {field_name}: '{field_value}'")
                
                if len(text_fields) > 20:
                    print(f"  ... and {len(text_fields) - 20} more fields")
                    
            else:
                print("❌ No text fields found via get_form_text_fields()")
        except Exception as e:
            print(f"❌ get_form_text_fields() failed: {str(e)}")
        
        # Method 2: get_fields()
        try:
            if hasattr(reader, 'get_fields'):
                fields = reader.get_fields()
                if fields:
                    print(f"\n📊 Fields via get_fields(): {len(fields)}")
                    
                    print(f"\n🔍 FIELD NAMES CONTAINING 'Pt1Line':")
                    pt1_fields = [name for name in fields.keys() if 'Pt1Line' in name]
                    for field in sorted(pt1_fields)[:10]:
                        print(f"  - {field}")
                    
                    if len(pt1_fields) > 10:
                        print(f"  ... and {len(pt1_fields) - 10} more Pt1Line fields")
                        
                else:
                    print("❌ No fields found via get_fields()")
        except Exception as e:
            print(f"❌ get_fields() failed: {str(e)}")
        
        # Method 3: Manual annotation inspection
        try:
            print(f"\n🔍 MANUAL ANNOTATION INSPECTION:")
            total_annotations = 0
            for page_num, page in enumerate(reader.pages):
                if '/Annots' in page:
                    annotations = page['/Annots']
                    if annotations:
                        page_annots = len(annotations)
                        total_annotations += page_annots
                        print(f"  Page {page_num + 1}: {page_annots} annotations")
                        
                        # Check first few annotations
                        for i, annot_ref in enumerate(annotations[:3]):
                            try:
                                annot = annot_ref.get_object()
                                if annot and '/T' in annot:
                                    field_name = str(annot['/T'])
                                    field_value = str(annot.get('/V', '')) if '/V' in annot else 'No value'
                                    print(f"    Annotation {i+1}: {field_name} = '{field_value}'")
                            except Exception:
                                continue
            
            print(f"📊 Total annotations found: {total_annotations}")
            
        except Exception as e:
            print(f"❌ Manual inspection failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error reading PDF: {str(e)}")

if __name__ == "__main__":
    debug_pdf_fields()