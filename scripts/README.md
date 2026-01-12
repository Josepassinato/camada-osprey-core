# Scripts

This directory contains utility scripts and package generators.

## Structure

### generators/
Scripts that generate complete visa application packages (PDFs) for testing and demonstration.

**Package Generators:**
- `generate_b2_complete_package.py` - Complete B-2 visa extension package
- `generate_b2_extension_complete_package.py` - B-2 extension with all documents
- `generate_f1_complete_package.py` - F-1 student visa package
- `generate_final_perfect_package.py` - Production-ready package generator
- `generate_filled_forms.py` - USCIS form filling

**Usage:**
```bash
python3 scripts/generators/generate_b2_complete_package.py
python3 scripts/generators/generate_f1_complete_package.py
```

These scripts generate PDF packages and save them to `samples/` directories.

### utilities/
Helper scripts for various tasks including image generation and document processing.

**Utility Scripts:**
- `b2_image_generator.py` - Generate images for B-2 applications
- `f1_image_generator.py` - Generate images for F-1 applications
- `document_image_generator.py` - General document image generation

**Usage:**
```bash
python3 scripts/utilities/b2_image_generator.py
python3 scripts/utilities/document_image_generator.py
```

## Notes

- All scripts should be run from the repository root
- Generated PDFs are saved to the `samples/` directory
- Scripts may require environment variables (see backend/.env)
