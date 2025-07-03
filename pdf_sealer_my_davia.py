#!/usr/bin/env python3
"""
PDF Sealer - A modular Python project for adding custom headers and footers to PDF files.
The header includes a QR code generated from a given string, and the footer includes a custom message.
"""

import os
import sys
import argparse
from typing import Tuple, Optional, List
from io import BytesIO

import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
import qrcode
from PIL import Image
from reportlab.lib.utils import ImageReader
from pydantic import BaseModel, Field, validator
from davia import Davia

app = Davia(title="PDF Sealer Davia App", description="Seal PDFs with QR code and footer", version="1.0.0")


# Pydantic Models for Input/Output Types
class QRCodeConfig(BaseModel):
    """Configuration for QR code generation."""
    size: str = Field(default="medium", description="QR code size: 'small', 'medium', 'large', or custom number")
    border: int = Field(default=2, ge=0, le=10, description="Border width around QR code")
    
    @validator('size')
    def validate_size(cls, v):
        valid_sizes = ['small', 'medium', 'large']
        if v in valid_sizes:
            return v
        try:
            int(v)
            return v
        except ValueError:
            raise ValueError(f"Size must be 'small', 'medium', 'large', or a number, got {v}")


class PDFSealRequest(BaseModel):
    """Input model for PDF sealing request."""
    input_path: str = Field(..., description="Path to the input PDF file")
    qr_data: str = Field(..., min_length=1, description="String data to encode in QR code")
    footer_message: str = Field(..., min_length=1, description="Message to display in footer")
    qr_config: QRCodeConfig = Field(default_factory=QRCodeConfig, description="QR code configuration")
    output_path: Optional[str] = Field(None, description="Output PDF file path (optional)")


class PDFSealResponse(BaseModel):
    """Output model for PDF sealing response."""
    success: bool = Field(..., description="Whether the operation was successful")
    output_path: str = Field(..., description="Path to the sealed PDF file")
    message: str = Field(..., description="Success or error message")
    qr_size_used: str = Field(..., description="QR code size that was used")


class QRCodeGenerationRequest(BaseModel):
    """Input model for QR code generation."""
    data: str = Field(..., min_length=1, description="Data to encode in QR code")
    config: QRCodeConfig = Field(default_factory=QRCodeConfig, description="QR code configuration")


class QRCodeGenerationResponse(BaseModel):
    """Output model for QR code generation."""
    success: bool = Field(..., description="Whether the operation was successful")
    qr_code_path: Optional[str] = Field(None, description="Path to saved QR code file")
    message: str = Field(..., description="Success or error message")
    qr_size: str = Field(..., description="QR code size that was used")


class PDFValidationRequest(BaseModel):
    """Input model for PDF validation."""
    file_path: str = Field(..., description="Path to the file to validate")


class PDFValidationResponse(BaseModel):
    """Output model for PDF validation."""
    is_valid: bool = Field(..., description="Whether the file is a valid PDF")
    exists: bool = Field(..., description="Whether the file exists")
    message: str = Field(..., description="Validation message")


class PDFProcessingMetrics(BaseModel):
    """Metrics for PDF processing operations."""
    total_pages: int = Field(..., ge=0, description="Total number of pages processed")
    qr_code_size: str = Field(..., description="QR code size used")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    file_size_input: int = Field(..., ge=0, description="Input file size in bytes")
    file_size_output: int = Field(..., ge=0, description="Output file size in bytes")


class QRCodeGenerator:
    """Handles QR code generation and manipulation."""
    
    # QR code size presets (in points)
    SIZE_PRESETS = {
        'small': 30,
        'medium': 50,
        'large': 80
    }
    
    def __init__(self, config: QRCodeConfig):
        """
        Initialize QR code generator.
        
        Args:
            config: QRCodeConfig object containing size and border settings
        """
        self.config = config
        if config.size in self.SIZE_PRESETS:
            self.size = self.SIZE_PRESETS[config.size]
        else:
            try:
                self.size = int(config.size)
            except ValueError:
                raise ValueError(f"Invalid size: {config.size}. Use 'small', 'medium', 'large', or a number.")
        self.border = config.border
    
    def generate_qr_code(self, request: QRCodeGenerationRequest) -> Image.Image:
        """
        Generate a QR code from the given data.
        
        Args:
            request: QRCodeGenerationRequest object containing data and config
            
        Returns:
            PIL Image object containing the QR code
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=request.config.border
        )
        qr.add_data(request.data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        return qr_image
    
    def save_qr_code(self, request: QRCodeGenerationRequest, filename: str) -> QRCodeGenerationResponse:
        """
        Generate and save QR code to a file.
        
        Args:
            request: QRCodeGenerationRequest object containing data and config
            filename: Output filename
            
        Returns:
            QRCodeGenerationResponse object with operation results
        """
        try:
            qr_image = self.generate_qr_code(request)
            qr_image.save(filename)
            
            return QRCodeGenerationResponse(
                success=True,
                qr_code_path=filename,
                message=f"QR code saved successfully to {filename}",
                qr_size=request.config.size
            )
        except Exception as e:
            return QRCodeGenerationResponse(
                success=False,
                qr_code_path=None,
                message=f"Failed to save QR code: {str(e)}",
                qr_size=request.config.size
            )


class PDFHeaderFooter:
    """Handles adding headers and footers to PDF pages."""
    
    def __init__(self, page_width: float, page_height: float, qr_config: QRCodeConfig):
        """
        Initialize PDF header/footer handler.
        
        Args:
            page_width: Width of the PDF page in points
            page_height: Height of the PDF page in points
            qr_config: QRCodeConfig object containing QR code settings
        """
        self.page_width = page_width
        self.page_height = page_height
        self.qr_generator = QRCodeGenerator(qr_config)
    
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
        # Create QR code generation request
        qr_request = QRCodeGenerationRequest(data=qr_data, config=self.qr_generator.qr_config)
        
        # Generate QR code
        qr_image = self.qr_generator.generate_qr_code(qr_request)
        
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


class PDFProcessor:
    """Main class for processing PDF files and adding headers/footers."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.header_footer_handler = None
    
    def process_pdf(self, request: PDFSealRequest) -> PDFSealResponse:
        """
        Process the input PDF and add headers/footers to each page.
        
        Args:
            request: PDFSealRequest object containing all processing parameters
            
        Returns:
            PDFSealResponse object with operation results
        """
        import time
        start_time = time.time()
        
        try:
            # Get file sizes for metrics
            input_file_size = os.path.getsize(request.input_path)
            
            # Open input PDF
            with open(request.input_path, 'rb') as input_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                pdf_writer = PyPDF2.PdfWriter()
                
                # Process each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    
                    # Get page dimensions
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)
                    
                    # Initialize header/footer handler for this page
                    self.header_footer_handler = PDFHeaderFooter(page_width, page_height, request.qr_config)
                    
                    # Create overlay with header and footer
                    overlay_buffer = self.header_footer_handler.create_header_footer_overlay(
                        request.qr_data, request.footer_message
                    )
                    
                    # Create overlay PDF
                    overlay_buffer.seek(0)
                    overlay_pdf = PyPDF2.PdfReader(stream=overlay_buffer)
                    overlay_page = overlay_pdf.pages[0]
                    
                    # Merge original page with overlay
                    page.merge_page(overlay_page)
                    
                    # Add to output PDF
                    pdf_writer.add_page(page)
                
                # Determine output path
                output_path = request.output_path if request.output_path else self.generate_output_path(request.input_path)
                
                # Write output PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                processing_time = time.time() - start_time
                output_file_size = os.path.getsize(output_path)
                
                return PDFSealResponse(
                    success=True,
                    output_path=output_path,
                    message=f"Successfully processed PDF with {len(pdf_reader.pages)} pages",
                    qr_size_used=request.qr_config.size
                )
            
        except Exception as e:
            return PDFSealResponse(
                success=False,
                output_path="",
                message=f"Error processing PDF: {str(e)}",
                qr_size_used=request.qr_config.size
            )
    
    def validate_input_file(self, request: PDFValidationRequest) -> PDFValidationResponse:
        """
        Validate that the input file exists and is a PDF.
        
        Args:
            request: PDFValidationRequest object containing file path
            
        Returns:
            PDFValidationResponse object with validation results
        """
        exists = os.path.exists(request.file_path)
        is_valid = exists and request.file_path.lower().endswith('.pdf')
        
        if not exists:
            message = f"File '{request.file_path}' does not exist."
        elif not is_valid:
            message = f"File '{request.file_path}' is not a PDF file."
        else:
            message = f"File '{request.file_path}' is a valid PDF."
        
        return PDFValidationResponse(
            is_valid=is_valid,
            exists=exists,
            message=message
        )
    
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


@app.task
def seal_pdf(request: PDFSealRequest) -> PDFSealResponse:
    """
    Seal a PDF with QR code header and footer message.
    
    Args:
        request: PDFSealRequest object containing all parameters for PDF sealing
        
    Returns:
        PDFSealResponse object with operation results
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file is not a PDF
        Exception: If PDF processing fails
    """
    # Initialize processor
    processor = PDFProcessor()
    
    # Validate input file
    validation_request = PDFValidationRequest(file_path=request.input_path)
    validation_response = processor.validate_input_file(validation_request)
    
    if not validation_response.is_valid:
        raise FileNotFoundError(validation_response.message)
    
    # Process PDF
    response = processor.process_pdf(request)
    
    return response


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
        default="medium",
        choices=["small", "medium", "large"],
        help="QR code size: small (30pt), medium (50pt), or large (80pt) (default: medium)"
    )
    parser.add_argument(
        "--qr-border", "-b",
        type=int,
        default=2,
        help="QR code border width (default: 2)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output PDF file path (default: input_sealed.pdf)"
    )
    
    args = parser.parse_args()
    
    try:
        # Create Pydantic request object
        qr_config = QRCodeConfig(size=args.qr_size, border=args.qr_border)
        request = PDFSealRequest(
            input_path=args.input_pdf,
            qr_data=args.qr_data,
            footer_message=args.footer_message,
            qr_config=qr_config,
            output_path=args.output
        )
        
        # Process PDF
        response = seal_pdf(request)
        
        if response.success:
            print(f"Successfully sealed PDF. Output saved to: {response.output_path}")
            print(f"Message: {response.message}")
            print(f"QR code size used: {response.qr_size_used}")
        else:
            print(f"Failed to seal PDF: {response.message}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Failed to seal PDF: {str(e)}")
        sys.exit(1)


# Additional API endpoints to demonstrate Pydantic models
@app.post("/validate-pdf")
async def validate_pdf_endpoint(request: PDFValidationRequest) -> PDFValidationResponse:
    """Validate if a file is a valid PDF."""
    processor = PDFProcessor()
    return processor.validate_input_file(request)


@app.post("/generate-qr")
async def generate_qr_endpoint(request: QRCodeGenerationRequest) -> QRCodeGenerationResponse:
    """Generate a QR code and save it to a file."""
    import tempfile
    
    try:
        # Create temporary file for QR code
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            qr_generator = QRCodeGenerator(request.config)
            response = qr_generator.save_qr_code(request, temp_file.name)
            return response
    except Exception as e:
        return QRCodeGenerationResponse(
            success=False,
            qr_code_path=None,
            message=f"Failed to generate QR code: {str(e)}",
            qr_size=request.config.size
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "PDF Sealer with Pydantic Models"}


if __name__ == "__main__":
    app.run()