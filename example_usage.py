#!/usr/bin/env python3
"""
Example usage of PDF Sealer programmatically.
This script demonstrates how to use the PDF Sealer classes directly in Python code.
"""

import os
from pdf_sealer import PDFProcessor, QRCodeGenerator


def example_basic_usage():
    """Example of basic PDF sealing usage."""
    print("=== Basic Usage Example ===")
    
    # Initialize the processor
    processor = PDFProcessor()
    
    # Example parameters
    input_pdf = "sample.pdf"  # You would need a real PDF file here
    output_pdf = "sample_sealed.pdf"
    qr_data = "https://example.com/document/123"
    footer_message = "Confidential Document - Company Name"
    
    # Check if input file exists (for demonstration)
    if not os.path.exists(input_pdf):
        print(f"Note: {input_pdf} doesn't exist. This is just a demonstration.")
        print("To test with a real file, create a PDF file or use the test script.")
        return
    
    try:
        # Process the PDF
        processor.process_pdf(input_pdf, output_pdf, qr_data, footer_message)
        print(f"✓ Successfully sealed PDF: {output_pdf}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def example_qr_code_only():
    """Example of generating QR codes without PDF processing."""
    print("\n=== QR Code Generation Example ===")
    
    # Initialize QR code generator
    qr_gen = QRCodeGenerator(size=200, border=4)
    
    # Generate different types of QR codes
    qr_examples = [
        ("https://www.google.com", "google_qr.png"),
        ("mailto:contact@company.com", "email_qr.png"),
        ("tel:+1234567890", "phone_qr.png"),
        ("This is a text message", "text_qr.png")
    ]
    
    for data, filename in qr_examples:
        try:
            qr_gen.save_qr_code(data, filename)
            print(f"✓ Generated QR code: {filename} (data: {data[:30]}...)")
        except Exception as e:
            print(f"✗ Error generating {filename}: {str(e)}")


def example_custom_processing():
    """Example of custom PDF processing workflow."""
    print("\n=== Custom Processing Example ===")
    
    processor = PDFProcessor()
    
    # Example: Process multiple PDFs with different settings
    pdf_configs = [
        {
            "input": "document1.pdf",
            "output": "document1_sealed.pdf",
            "qr_data": "https://company.com/doc1",
            "footer": "Internal Document - Version 1.0"
        },
        {
            "input": "document2.pdf", 
            "output": "document2_sealed.pdf",
            "qr_data": "https://company.com/doc2",
            "footer": "Confidential - Do Not Distribute"
        }
    ]
    
    for config in pdf_configs:
        if os.path.exists(config["input"]):
            try:
                processor.process_pdf(
                    config["input"],
                    config["output"], 
                    config["qr_data"],
                    config["footer"]
                )
                print(f"✓ Processed: {config['input']} → {config['output']}")
            except Exception as e:
                print(f"✗ Error processing {config['input']}: {str(e)}")
        else:
            print(f"⚠ Skipping {config['input']} (file not found)")


def example_validation():
    """Example of file validation usage."""
    print("\n=== File Validation Example ===")
    
    processor = PDFProcessor()
    
    # Test various file scenarios
    test_files = [
        "nonexistent.pdf",
        "document.txt",  # Wrong extension
        "sample.pdf"     # Would be valid if it exists
    ]
    
    for test_file in test_files:
        is_valid = processor.validate_input_file(test_file)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"{status}: {test_file}")


def main():
    """Main example function."""
    print("PDF Sealer - Example Usage")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_qr_code_only()
    example_custom_processing()
    example_validation()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo run the actual PDF sealer:")
    print("python pdf_sealer.py input.pdf --qr-data 'your-data' --footer-message 'your-message'")


if __name__ == "__main__":
    main() 