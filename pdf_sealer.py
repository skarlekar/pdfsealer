#!/usr/bin/env python3
"""
PDF Sealer - A modular Python project for adding custom headers and footers to PDF files.
The header includes a QR code generated from a given string, and the footer includes a custom message.
"""

import os
import sys
import argparse
from typing import Tuple, Optional
from io import BytesIO

import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
import qrcode
from PIL import Image
from reportlab.lib.utils import ImageReader


class QRCodeGenerator:
    """Handles QR code generation and manipulation."""
    
    def __init__(self, size: int = 100, border: int = 2):
        """
        Initialize QR code generator.
        
        Args:
            size: Size of the QR code in pixels
            border: Border width around the QR code
        """
        self.size = size
        self.border = border
    
    def generate_qr_code(self, data: str) -> Image.Image:
        """
        Generate a QR code from the given data.
        
        Args:
            data: String data to encode in QR code
            
        Returns:
            PIL Image object containing the QR code
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=self.border
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        return qr_image
    
    def save_qr_code(self, data: str, filename: str) -> None:
        """
        Generate and save QR code to a file.
        
        Args:
            data: String data to encode
            filename: Output filename
        """
        qr_image = self.generate_qr_code(data)
        qr_image.save(filename)


class PDFHeaderFooter:
    """Handles adding headers and footers to PDF pages."""
    
    def __init__(self, page_width: float, page_height: float):
        """
        Initialize PDF header/footer handler.
        
        Args:
            page_width: Width of the PDF page in points
            page_height: Height of the PDF page in points
        """
        self.page_width = page_width
        self.page_height = page_height
        self.qr_generator = QRCodeGenerator()
    
    def create_header_footer_overlay(self, qr_data: str, footer_message: str) -> BytesIO:
        """
        Create a PDF overlay with header (QR code) and footer (message).
        
        Args:
            qr_data: Data to encode in QR code
            footer_message: Message to display in footer
            
        Returns:
            BytesIO object containing the overlay PDF
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(self.page_width, self.page_height))
        
        # Add QR code to top right
        self._add_qr_code_to_canvas(c, qr_data)
        
        # Add footer message
        self._add_footer_to_canvas(c, footer_message)
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def _add_qr_code_to_canvas(self, canvas_obj: canvas.Canvas, qr_data: str) -> None:
        """
        Add QR code to the top right of the canvas.
        
        Args:
            canvas_obj: ReportLab canvas object
            qr_data: Data to encode in QR code
        """
        # Generate QR code
        qr_image = self.qr_generator.generate_qr_code(qr_data)
        
        # Save QR code to temporary buffer
        qr_buffer = BytesIO()
        qr_image.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Use ImageReader to wrap the buffer
        qr_img_reader = ImageReader(qr_buffer)
        
        # Calculate position (top right, with some margin)
        qr_size = 50  # Size in points
        margin = 20
        x_position = self.page_width - qr_size - margin
        y_position = self.page_height - qr_size - margin
        
        # Add QR code to canvas
        canvas_obj.drawImage(qr_img_reader, x_position, y_position, 
                           width=qr_size, height=qr_size)
    
    def _add_footer_to_canvas(self, canvas_obj: canvas.Canvas, footer_message: str) -> None:
        """
        Add footer message to the bottom center of the canvas.
        
        Args:
            canvas_obj: ReportLab canvas object
            footer_message: Message to display in footer
        """
        # Set font and size
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.setFillColor(black)
        
        # Calculate position (bottom center)
        text_width = canvas_obj.stringWidth(footer_message, "Helvetica", 10)
        x_position = (self.page_width - text_width) / 2
        y_position = 20  # 20 points from bottom
        
        # Add footer text
        canvas_obj.drawString(x_position, y_position, footer_message)


class PDFProcessor:
    """Main class for processing PDF files and adding headers/footers."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.header_footer_handler = None
    
    def process_pdf(self, input_path: str, output_path: str, 
                   qr_data: str, footer_message: str) -> None:
        """
        Process the input PDF and add headers/footers to each page.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path for output PDF file
            qr_data: Data to encode in QR code
            footer_message: Message to display in footer
        """
        try:
            # Open input PDF
            with open(input_path, 'rb') as input_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                pdf_writer = PyPDF2.PdfWriter()
                
                # Process each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    
                    # Get page dimensions
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)
                    
                    # Initialize header/footer handler for this page
                    self.header_footer_handler = PDFHeaderFooter(page_width, page_height)
                    
                    # Create overlay with header and footer
                    overlay_buffer = self.header_footer_handler.create_header_footer_overlay(
                        qr_data, footer_message
                    )
                    
                    # Create overlay PDF
                    overlay_buffer.seek(0)
                    overlay_pdf = PyPDF2.PdfReader(stream=overlay_buffer)
                    overlay_page = overlay_pdf.pages[0]
                    
                    # Merge original page with overlay
                    page.merge_page(overlay_page)
                    
                    # Add to output PDF
                    pdf_writer.add_page(page)
                
                # Write output PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                    
            print(f"Successfully processed PDF. Output saved to: {output_path}")
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            raise
    
    def validate_input_file(self, file_path: str) -> bool:
        """
        Validate that the input file exists and is a PDF.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file is valid, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return False
        
        if not file_path.lower().endswith('.pdf'):
            print(f"Error: File '{file_path}' is not a PDF file.")
            return False
        
        return True
    
    def generate_output_path(self, input_path: str) -> str:
        """
        Generate output path based on input path.
        
        Args:
            input_path: Path to input PDF file
            
        Returns:
            Generated output path
        """
        base_name = os.path.splitext(input_path)[0]
        return f"{base_name}_sealed.pdf"


def main():
    """Main function to handle command line arguments and process PDF."""
    parser = argparse.ArgumentParser(
        description="Add custom headers (QR code) and footers to PDF files"
    )
    parser.add_argument(
        "input_pdf",
        help="Path to the input PDF file"
    )
    parser.add_argument(
        "--qr-data", "-q",
        required=True,
        help="String data to encode in QR code"
    )
    parser.add_argument(
        "--footer-message", "-f",
        required=True,
        help="Message to display in footer"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output PDF file path (default: input_sealed.pdf)"
    )
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = PDFProcessor()
    
    # Validate input file
    if not processor.validate_input_file(args.input_pdf):
        sys.exit(1)
    
    # Generate output path if not provided
    output_path = args.output if args.output else processor.generate_output_path(args.input_pdf)
    
    # Process PDF
    try:
        processor.process_pdf(
            args.input_pdf,
            output_path,
            args.qr_data,
            args.footer_message
        )
    except Exception as e:
        print(f"Failed to process PDF: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 