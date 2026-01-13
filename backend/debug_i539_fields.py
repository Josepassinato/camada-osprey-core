#!/usr/bin/env python3
"""
Debug I-539 PDF Fields
Discover the actual field names in the I-539 template
"""

import logging
import pypdf
import os

logger = logging.getLogger(__name__)

def debug_i539_fields():
    """Debug the I-539 PDF template to see available fields"""
    
    template_path = "/app/official_forms/uscis_forms/I-539.pdf"
    
    if not os.path.exists(template_path):
        logger.error(f"❌ Template not found: {template_path}")
        return
    
    logger.info(f"🔍 Analyzing I-539 PDF template")
    logger.info("="*80)
    
    try:
        reader = pypdf.PdfReader(template_path)
        logger.info(f"📄 PDF Pages: {len(reader.pages)}")
        
        # Get all form fields
        text_fields = reader.get_form_text_fields()
        
        if text_fields:
            logger.info(f"\n📊 Total fields found: {len(text_fields)}")
            
            # Look for fields related to our data
            logger.info(f"\n🔍 SEARCHING FOR CRITICAL FIELDS:")
            
            search_terms = [
                ("Nome/Family", ["name", "family", "surname", "apellido", "line1"]),
                ("Dado/Given", ["given", "first", "nombre"]),
                ("Endereço/Address", ["address", "street", "direccion", "calle"]),
                ("Cidade/City", ["city", "ciudad", "town"]),
                ("Estado/State", ["state", "estado", "province"]),
                ("CEP/ZIP", ["zip", "postal", "codigo"]),
                ("Email", ["email", "correo", "mail"]),
                ("Telefone/Phone", ["phone", "telefono", "tel", "daytime"]),
                ("Passaporte/Passport", ["passport", "pasaporte", "travel"]),
                ("País/Country", ["country", "pais", "birth", "citizenship"])
            ]
            
            for label, terms in search_terms:
                logger.info(f"\n  {label}:")
                found = []
                for field_name in text_fields.keys():
                    field_lower = field_name.lower()
                    if any(term in field_lower for term in terms):
                        found.append(field_name)
                
                if found:
                    for field in found[:5]:  # Show first 5 matches
                        logger.info(f"    ✅ {field}")
                    if len(found) > 5:
                        logger.info(f"    ... and {len(found) - 5} more")
                else:
                    logger.error(f"    ❌ No matches found")
            
            # Show ALL field names (first 50)
            logger.info(f"\n📋 ALL FIELD NAMES (first 50):")
            for i, field_name in enumerate(list(text_fields.keys())[:50]):
                logger.info(f"  {i+1:2d}. {field_name}")
            
            if len(text_fields) > 50:
                logger.info(f"  ... and {len(text_fields) - 50} more fields")
                
        else:
            logger.error("❌ No fields found")
            
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_i539_fields()
