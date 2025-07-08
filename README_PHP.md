# PDF Sealer - PHP Version

A PHP equivalent of the Python PDF Sealer project that adds custom headers and footers to PDF files. The header includes a QR code generated from a given string, and the footer includes a custom message. The tool also supports adding watermarks across the document.

## Features

- **QR Code Header**: Generates QR codes from custom strings and places them in the top-right corner of each page
- **Custom Footer**: Adds centered footer messages at the bottom of each page
- **Watermark Support**: Adds repeating watermark text across the document at customizable angles and opacity
- **Modular Design**: Well-structured classes for QR code generation, PDF manipulation, and header/footer handling
- **Preserves Original Content**: Maintains the original PDF content and layout
- **Command Line Interface**: Easy-to-use CLI with flexible options
- **Error Handling**: Comprehensive validation and error handling

## Requirements

- PHP 8.0 or higher
- Composer for dependency management

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdfsealer
```

2. Install the required dependencies:
```bash
composer install
```

## Dependencies

- **endroid/qr-code**: QR code generation
- **setasign/fpdf**: PDF generation and manipulation

## Usage

### Basic Usage

```bash
php pdf_sealer.php input.pdf --qr-data "https://example.com" --footer-message "Confidential Document"
```

### Advanced Usage with Watermark

```bash
php pdf_sealer.php input.pdf \
    --qr-data "https://example.com/document/123" \
    --footer-message "Company Name - Page {page}" \
    --watermark-text "CONFIDENTIAL" \
    --watermark-opacity 0.4 \
    --watermark-angle 45 \
    --output custom_output.pdf
```

### Command Line Arguments

- `input_pdf`: Path to the input PDF file (required)
- `--qr-data <data>`: String data to encode in QR code (required)
- `--footer-message <text>`: Message to display in footer (required)
- `--qr-size <size>`: QR code size: small, medium, or large (default: small)
- `--watermark-text <text>`: Text to display as watermark across the document (optional)
- `--watermark-font-size <size>`: Font size for watermark text (default: 24)
- `--watermark-opacity <opacity>`: Opacity of watermark (0.1-1.0, default: 0.4)
- `--watermark-angle <angle>`: Rotation angle of watermark in degrees (default: 45)
- `--watermark-color <color>`: Color of watermark text in hex format (default: #CCCCCC)
- `--output <file>`: Output PDF file path (optional, defaults to `input_sealed.pdf`)
- `--help`: Show help message

### Examples

1. **Simple document sealing**:
```bash
php pdf_sealer.php document.pdf --qr-data "https://company.com/doc/123" --footer-message "Confidential"
```

2. **Custom output filename**:
```bash
php pdf_sealer.php report.pdf --qr-data "scan.me/report" --footer-message "Internal Use Only" --output sealed_report.pdf
```

3. **QR code with contact information**:
```bash
php pdf_sealer.php contact.pdf --qr-data "mailto:contact@company.com" --footer-message "Contact: contact@company.com"
```

4. **Different QR code sizes**:
```bash
# Small QR code (default)
php pdf_sealer.php document.pdf --qr-data "https://example.com" --footer-message "Confidential" --qr-size small

# Large QR code
php pdf_sealer.php document.pdf --qr-data "https://example.com" --footer-message "Confidential" --qr-size large
```

5. **Document with watermark**:
```bash
php pdf_sealer.php document.pdf \
    --qr-data "https://example.com" \
    --footer-message "Confidential Document" \
    --watermark-text "DRAFT" \
    --watermark-opacity 0.6 \
    --watermark-angle 30
```

6. **Custom watermark color and size**:
```bash
php pdf_sealer.php document.pdf \
    --qr-data "https://example.com" \
    --footer-message "Company Internal" \
    --watermark-text "CONFIDENTIAL" \
    --watermark-color "#888888" \
    --watermark-font-size 36 \
    --watermark-opacity 0.7
```

## Project Structure

```
pdfsealer/
├── pdf_sealer.php     # Main PHP application file
├── composer.json      # PHP dependencies
├── README_PHP.md      # This file
├── requirements.txt   # Python dependencies (original version)
├── pdf_sealer.py      # Python version
└── LICENSE           # License information
```

## Code Architecture

The PHP project is organized into four main classes:

### QRCodeGenerator
- Handles QR code generation and manipulation using endroid/qr-code
- Configurable size and border settings
- Supports saving QR codes to files
- Always generates dark black QR codes for maximum readability

### WatermarkConfig
- Manages watermark configuration and validation
- Controls text, font size, opacity, angle, spacing, and color
- Validates parameters within acceptable ranges

### PDFHeaderFooter
- Extends FPDF for PDF generation
- Manages header and footer overlay creation
- Positions QR codes in top-right corner
- Centers footer messages at bottom
- Adds repeating watermark text across the page
- Handles page dimension calculations

### PDFProcessor
- Main processing class
- Validates input files
- Coordinates the PDF processing workflow
- Handles file I/O operations

## How It Works

1. **Input Validation**: Checks if the input file exists and is a valid PDF
2. **Page Processing**: Creates a new PDF with the overlay content
3. **Overlay Creation**: Creates a new PDF overlay with QR code, footer, and optional watermark
4. **Page Merging**: Combines the overlay with the original page content
5. **Output Generation**: Writes the modified PDF to the output file

## QR Code Positioning

- **Location**: Top-right corner of each page
- **Size Options**: 
  - Small: 30 points (approximately 0.4 inches) - **default**
  - Medium: 50 points (approximately 0.7 inches)
  - Large: 80 points (approximately 1.1 inches)
- **Margin**: 20 points from page edges
- **Content**: Custom string data provided via command line
- **Color**: Always dark black for maximum readability

## Footer Positioning

- **Location**: Bottom center of each page
- **Font**: Helvetica, 10pt
- **Margin**: 20 points from bottom edge
- **Content**: Custom message provided via command line

## Watermark Features

- **Text**: Custom text that repeats across the entire document
- **Positioning**: Grid pattern covering the full page with configurable spacing
- **Rotation**: Configurable angle (-90 to 90 degrees, default: 45°)
- **Opacity**: Adjustable transparency (0.1 to 1.0, default: 0.4)
- **Color**: Customizable hex color (default: #CCCCCC light gray)
- **Font Size**: Adjustable from 8 to 72 points (default: 24)
- **Spacing**: Automatic spacing based on text size and page dimensions
- **Layering**: Appears behind QR code and footer for proper visual hierarchy

## Error Handling

The application includes comprehensive error handling for:
- Missing or invalid input files
- PDF processing errors
- QR code generation issues
- Watermark configuration validation
- File I/O problems

## Limitations

- QR code size is limited to predefined options (small, medium, large)
- Footer font and size are predefined
- Only supports standard PDF formats
- QR code positioning is fixed to top-right corner
- Watermark text is limited to single line
- Current implementation creates a new PDF rather than modifying existing PDF pages

## Development

### Running Tests

```bash
composer test
```

### Code Coverage

```bash
composer test-coverage
```

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

1. **Composer Dependencies**: Make sure all dependencies are installed:
   ```bash
   composer install
   ```

2. **PHP Version**: Ensure you're using PHP 8.0 or higher:
   ```bash
   php --version
   ```

3. **File Not Found**: Ensure the input PDF file exists and the path is correct

4. **Permission Errors**: Check file permissions for read/write access

5. **Large QR Codes**: If QR code data is too long, consider using a URL shortener

6. **Watermark Too Light**: Increase opacity (0.6-0.7) or use darker color (#888888)

7. **Watermark Too Dark**: Decrease opacity (0.2-0.3) or use lighter color (#CCCCCC)

### Getting Help

If you encounter issues:
1. Check the error messages for specific details
2. Verify all dependencies are installed correctly
3. Ensure input file is a valid PDF
4. Check file permissions and paths
5. Test with different watermark settings for optimal visibility

## Comparison with Python Version

| Feature | Python Version | PHP Version |
|---------|----------------|-------------|
| QR Code Generation | qrcode + PIL | endroid/qr-code |
| PDF Manipulation | PyPDF2 + reportlab | FPDF |
| Watermark Support | ✅ | ✅ |
| CLI Interface | argparse | getopt |
| Error Handling | ✅ | ✅ |
| Modular Design | ✅ | ✅ |
| Type Hints | ✅ | ✅ (PHP 8.0+) |

Both versions provide the same core functionality with similar APIs and command-line interfaces. 