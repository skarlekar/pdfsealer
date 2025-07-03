# PDF Sealer

A modular Python project that adds custom headers and footers to PDF files. The header includes a QR code generated from a given string, and the footer includes a custom message. The tool preserves the original content and layout of each page while adding the new elements.

## Features

- **QR Code Header**: Generates QR codes from custom strings and places them in the top-right corner of each page
- **Custom Footer**: Adds centered footer messages at the bottom of each page
- **Modular Design**: Well-structured classes for QR code generation, PDF manipulation, and header/footer handling
- **Preserves Original Content**: Maintains the original PDF content and layout
- **Command Line Interface**: Easy-to-use CLI with flexible options
- **Error Handling**: Comprehensive validation and error handling

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdfsealer
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

- **PyPDF2**: PDF manipulation and merging
- **reportlab**: PDF generation and drawing
- **qrcode**: QR code generation
- **Pillow**: Image processing for QR codes

## Usage

### Basic Usage

```bash
python pdf_sealer.py input.pdf --qr-data "https://example.com" --footer-message "Confidential Document"
```

### Advanced Usage

```bash
python pdf_sealer.py input.pdf \
    --qr-data "https://example.com/document/123" \
    --footer-message "Company Name - Page {page}" \
    --output custom_output.pdf
```

### Command Line Arguments

- `input_pdf`: Path to the input PDF file (required)
- `--qr-data, -q`: String data to encode in QR code (required)
- `--footer-message, -f`: Message to display in footer (required)
- `--output, -o`: Output PDF file path (optional, defaults to `input_sealed.pdf`)

### Examples

1. **Simple document sealing**:
```bash
python pdf_sealer.py document.pdf --qr-data "https://company.com/doc/123" --footer-message "Confidential"
```

2. **Custom output filename**:
```bash
python pdf_sealer.py report.pdf --qr-data "scan.me/report" --footer-message "Internal Use Only" --output sealed_report.pdf
```

3. **QR code with contact information**:
```bash
python pdf_sealer.py contact.pdf --qr-data "mailto:contact@company.com" --footer-message "Contact: contact@company.com"
```

## Project Structure

```
pdfsealer/
├── pdf_sealer.py      # Main application file
├── requirements.txt   # Python dependencies
├── README.md         # This file
└── LICENSE           # License information
```

## Code Architecture

The project is organized into three main classes:

### QRCodeGenerator
- Handles QR code generation and manipulation
- Configurable size and border settings
- Supports saving QR codes to files

### PDFHeaderFooter
- Manages header and footer overlay creation
- Positions QR codes in top-right corner
- Centers footer messages at bottom
- Handles page dimension calculations

### PDFProcessor
- Main processing class
- Validates input files
- Coordinates the PDF processing workflow
- Handles file I/O operations

## How It Works

1. **Input Validation**: Checks if the input file exists and is a valid PDF
2. **Page Processing**: Iterates through each page of the input PDF
3. **Overlay Creation**: Creates a new PDF overlay with QR code and footer
4. **Page Merging**: Merges the overlay with the original page content
5. **Output Generation**: Writes the modified PDF to the output file

## QR Code Positioning

- **Location**: Top-right corner of each page
- **Size**: 50 points (approximately 0.7 inches)
- **Margin**: 20 points from page edges
- **Content**: Custom string data provided via command line

## Footer Positioning

- **Location**: Bottom center of each page
- **Font**: Helvetica, 10pt
- **Margin**: 20 points from bottom edge
- **Content**: Custom message provided via command line

## Error Handling

The application includes comprehensive error handling for:
- Missing or invalid input files
- PDF processing errors
- QR code generation issues
- File I/O problems

## Limitations

- QR code size is fixed at 50 points
- Footer font and size are predefined
- Only supports standard PDF formats
- QR code positioning is fixed to top-right corner

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **File Not Found**: Ensure the input PDF file exists and the path is correct

3. **Permission Errors**: Check file permissions for read/write access

4. **Large QR Codes**: If QR code data is too long, consider using a URL shortener

### Getting Help

If you encounter issues:
1. Check the error messages for specific details
2. Verify all dependencies are installed correctly
3. Ensure input file is a valid PDF
4. Check file permissions and paths
