#!/usr/bin/env python3
"""
Debug I-539 PDF Fields using PyMuPDF
"""

import logging

import fitz

logger = logging.getLogger(__name__)


def debug_fields():
    template_path = "/app/official_forms/uscis_forms/I-539.pdf"

    logger.info("🔍 Analyzing I-539 with PyMuPDF")
    logger.info("=" * 80)

    doc = fitz.open(template_path)
    logger.info(f"📄 PDF Pages: {len(doc)}")

    all_fields = []

    for page_num, page in enumerate(doc):
        widgets = list(page.widgets())
        if widgets:
            logger.info(f"\n📄 Page {page_num + 1}: {len(widgets)} widgets")
            for widget in widgets:
                field_name = widget.field_name
                field_type = widget.field_type
                field_value = widget.field_value
                all_fields.append((field_name, field_type, field_value))

    logger.info(f"\n📊 Total widgets found: {len(all_fields)}")

    # Search for critical fields
    logger.info(f"\n🔍 SEARCHING FOR CRITICAL FIELDS:")

    search_terms = [
        ("Name/Family", ["name", "family", "surname"]),
        ("Given", ["given", "first"]),
        ("Address/Street", ["address", "street"]),
        ("City", ["city", "town"]),
        ("State", ["state", "province"]),
        ("ZIP", ["zip", "postal"]),
        ("Email", ["email", "mail"]),
        ("Phone", ["phone", "tel", "daytime"]),
        ("Passport", ["passport", "travel"]),
        ("Country", ["country", "birth", "citizenship"]),
    ]

    for label, terms in search_terms:
        logger.info(f"\n  {label}:")
        found = []
        for field_name, field_type, field_value in all_fields:
            if field_name:
                field_lower = field_name.lower()
                if any(term in field_lower for term in terms):
                    found.append(field_name)

        if found:
            for field in found[:5]:
                logger.info(f"    ✅ {field}")
            if len(found) > 5:
                logger.info(f"    ... and {len(found) - 5} more")
        else:
            logger.error(f"    ❌ No matches found")

    # Show first 30 field names
    logger.info(f"\n📋 FIRST 30 FIELD NAMES:")
    for i, (field_name, field_type, field_value) in enumerate(all_fields[:30]):
        type_name = {0: "unknown", 1: "button", 2: "text", 3: "choice", 4: "signature"}.get(
            field_type, str(field_type)
        )
        logger.info(f"  {i+1:2d}. [{type_name:9s}] {field_name}")

    if len(all_fields) > 30:
        logger.info(f"  ... and {len(all_fields) - 30} more fields")

    doc.close()


if __name__ == "__main__":
    debug_fields()
