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
from reportlab.lib.colors import black, white, gray, HexColor
import qrcode
from PIL import Image
from reportlab.lib.utils import ImageReader


class QRCodeGenerator:
    """Handles QR code generation and manipulation."""
    
    # QR code size presets (in points)
    SIZE_PRESETS = {
        'small': 30,
        'medium': 50,
        'large': 80
    }
    
    def __init__(self, size: str = 'small', border: int = 2):
        """
        Initialize QR code generator.
        
        Args:
            size: Size preset ('small', 'medium', 'large') or custom size in points
            border: Border width around the QR code
        """
        if size in self.SIZE_PRESETS:
            self.size = self.SIZE_PRESETS[size]
        else:
            try:
                self.size = int(size)
            except ValueError:
                raise ValueError(f"Invalid size: {size}. Use 'small', 'medium', 'large', or a number.")
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
        
        # Always use dark black for QR codes, regardless of watermark opacity
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


class WatermarkConfig:
    """Configuration for watermark generation."""
    
    def __init__(self, text: str, font_size: int = 24, opacity: float = 0.4, 
                 angle: int = 45, spacing_x: float = 200, spacing_y: float = 150, 
                 color: str = "#CCCCCC"):
        """
        Initialize watermark configuration.
        
        Args:
            text: Text to display as watermark
            font_size: Font size for watermark text (8-72, default: 24)
            opacity: Opacity of watermark (0.1-1.0, default: 0.2)
            angle: Rotation angle in degrees (-90 to 90, default: 45)
            spacing_x: Horizontal spacing between watermarks (50-500, default: 200)
            spacing_y: Vertical spacing between watermarks (50-500, default: 150)
            color: Color of watermark text in hex format (default: #CCCCCC)
        """
        self.text = text
        self.font_size = max(8, min(72, font_size))
        self.opacity = max(0.1, min(1.0, opacity))
        self.angle = max(-90, min(90, angle))
        self.spacing_x = max(50, min(500, spacing_x))
        self.spacing_y = max(50, min(500, spacing_y))
        self.color = color


class PDFHeaderFooter:
    """Handles adding headers and footers to PDF pages."""
    
    def __init__(self, page_width: float, page_height: float, qr_size: str = 'medium'):
        """
        Initialize PDF header/footer handler.
        
        Args:
            page_width: Width of the PDF page in points
            page_height: Height of the PDF page in points
            qr_size: Size of QR code ('small', 'medium', 'large', or custom number)
        """
        self.page_width = page_width
        self.page_height = page_height
        self.qr_generator = QRCodeGenerator(size=qr_size)
    
    def create_header_footer_overlay(self, qr_data: str, footer_message: str, watermark_config: Optional[WatermarkConfig] = None) -> BytesIO:
        """
        Create a PDF overlay with header (QR code), footer (message), and optional watermark.
        
        Args:
            qr_data: Data to encode in QR code
            footer_message: Message to display in footer
            watermark_config: Optional watermark configuration
            
        Returns:
            BytesIO object containing the overlay PDF
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(self.page_width, self.page_height))
        
        # Add watermark first (so it appears behind other elements)
        if watermark_config:
            self._add_watermark_to_canvas(c, watermark_config)
        
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
        qr_size = self.qr_generator.size  # Use the configured size
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
    
    def _add_watermark_to_canvas(self, canvas_obj: canvas.Canvas, watermark_config: WatermarkConfig) -> None:
        """
        Add watermark text across the entire canvas in a repeating pattern.
        
        Args:
            canvas_obj: ReportLab canvas object
            watermark_config: WatermarkConfig object containing watermark settings
        """
        # Set font and size
        canvas_obj.setFont("Helvetica-Bold", watermark_config.font_size)
        
        # Set color and opacity
        try:
            color = HexColor(watermark_config.color)
            # Apply opacity by adjusting alpha
            color.alpha = watermark_config.opacity
            canvas_obj.setFillColor(color)
        except:
            # Fallback to gray if color parsing fails
            canvas_obj.setFillColor(gray)
        
        # Calculate text width for spacing
        text_width = canvas_obj.stringWidth(watermark_config.text, "Helvetica-Bold", watermark_config.font_size)
        
        # Calculate spacing to ensure watermarks cover the entire page
        spacing_x = max(watermark_config.spacing_x, text_width + 50)
        spacing_y = max(watermark_config.spacing_y, watermark_config.font_size + 50)
        
        # Calculate how many watermarks we need in each direction
        num_cols = int(self.page_width / spacing_x) + 2  # Add extra for overlap
        num_rows = int(self.page_height / spacing_y) + 2  # Add extra for overlap
        
        # Draw watermarks in a grid pattern
        for row in range(num_rows):
            for col in range(num_cols):
                # Calculate position
                x = col * spacing_x
                y = self.page_height - (row * spacing_y)
                
                # Save current state
                canvas_obj.saveState()
                
                # Move to position and rotate
                canvas_obj.translate(x, y)
                canvas_obj.rotate(watermark_config.angle)
                
                # Draw the watermark text
                canvas_obj.drawString(0, 0, watermark_config.text)
                
                # Restore state
                canvas_obj.restoreState()


class PDFProcessor:
    """Main class for processing PDF files and adding headers/footers."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.header_footer_handler = None
    
    def process_pdf(self, input_path: str, output_path: str, 
                   qr_data: str, footer_message: str, qr_size: str = 'medium',
                   watermark_config: Optional[WatermarkConfig] = None) -> None:
        """
        Process the input PDF and add headers/footers to each page.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path for output PDF file
            qr_data: Data to encode in QR code
            footer_message: Message to display in footer
            qr_size: Size of QR code ('small', 'medium', 'large', or custom number)
            watermark_config: Optional watermark configuration
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
                    self.header_footer_handler = PDFHeaderFooter(page_width, page_height, qr_size)
                    
                    # Create overlay with header, footer, and optional watermark
                    overlay_buffer = self.header_footer_handler.create_header_footer_overlay(
                        qr_data, footer_message, watermark_config
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
        "--qr-size", "-s",
        default="small",
        choices=["small", "medium", "large"],
        help="QR code size: small (30pt), medium (50pt), or large (80pt) (default: small)"
    )
    parser.add_argument(
        "--watermark-text", "-w",
        help="Text to display as watermark across the document"
    )
    parser.add_argument(
        "--watermark-font-size",
        type=int,
        default=24,
        help="Font size for watermark text (default: 24)"
    )
    parser.add_argument(
        "--watermark-opacity",
        type=float,
        default=0.4,
        help="Opacity of watermark (0.1 to 1.0, default: 0.2)"
    )
    parser.add_argument(
        "--watermark-angle",
        type=int,
        default=45,
        help="Rotation angle of watermark in degrees (default: 45)"
    )
    parser.add_argument(
        "--watermark-color",
        default="#CCCCCC",
        help="Color of watermark text in hex format (default: #000000)"
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
    
    # Create watermark config if watermark text is provided
    watermark_config = None
    if args.watermark_text:
        watermark_config = WatermarkConfig(
            text=args.watermark_text,
            font_size=args.watermark_font_size,
            opacity=args.watermark_opacity,
            angle=args.watermark_angle,
            color=args.watermark_color
        )
    
    # Process PDF
    try:
        processor.process_pdf(
            args.input_pdf,
            output_path,
            args.qr_data,
            args.footer_message,
            args.qr_size,
            watermark_config
        )
    except Exception as e:
        print(f"Failed to process PDF: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 