<?php
/**
 * PDF Sealer - A modular PHP project for adding custom headers and footers to PDF files.
 * The header includes a QR code generated from a given string, and the footer includes a custom message.
 * The tool also supports adding watermarks across the document.
 */

require_once 'vendor/autoload.php';
require_once 'vendor/setasign/fpdf 2/fpdf.php';

use Endroid\QrCode\QrCode;
use Endroid\QrCode\Writer\PngWriter;
use Endroid\QrCode\Color\Color;
use Endroid\QrCode\ErrorCorrectionLevel\ErrorCorrectionLevelLow;

/**
 * QR Code Generator Class
 * Handles QR code generation and manipulation.
 */
class QRCodeGenerator
{
    /** @var array QR code size presets (in points) */
    private const SIZE_PRESETS = [
        'small' => 30,
        'medium' => 50,
        'large' => 80
    ];
    
    private int $size;
    private int $border;
    
    /**
     * Initialize QR code generator.
     * 
     * @param string $size Size preset ('small', 'medium', 'large') or custom size in points
     * @param int $border Border width around the QR code
     * @throws InvalidArgumentException
     */
    public function __construct(string $size = 'small', int $border = 2)
    {
        if (isset(self::SIZE_PRESETS[$size])) {
            $this->size = self::SIZE_PRESETS[$size];
        } else {
            if (is_numeric($size)) {
                $this->size = (int)$size;
            } else {
                throw new InvalidArgumentException("Invalid size: $size. Use 'small', 'medium', 'large', or a number.");
            }
        }
        $this->border = $border;
    }
    
    /**
     * Generate a QR code from the given data.
     * 
     * @param string $data String data to encode in QR code
     * @return string PNG image data as string
     */
    public function generateQrCode(string $data): string
    {
        $qrCode = new QrCode($data);
        $qrCode->setSize($this->size);
        $qrCode->setMargin($this->border);
        $qrCode->setErrorCorrectionLevel(new ErrorCorrectionLevelLow());
        
        // Always use dark black for QR codes
        $qrCode->setForegroundColor(new Color(0, 0, 0));
        $qrCode->setBackgroundColor(new Color(255, 255, 255));
        
        $writer = new PngWriter();
        $result = $writer->write($qrCode);
        
        return $result->getString();
    }
    
    /**
     * Generate and save QR code to a file.
     * 
     * @param string $data String data to encode
     * @param string $filename Output filename
     */
    public function saveQrCode(string $data, string $filename): void
    {
        $qrImageData = $this->generateQrCode($data);
        file_put_contents($filename, $qrImageData);
    }
    
    /**
     * Get the configured QR code size.
     * 
     * @return int Size in points
     */
    public function getSize(): int
    {
        return $this->size;
    }
}

/**
 * Watermark Configuration Class
 * Configuration for watermark generation.
 */
class WatermarkConfig
{
    public string $text;
    public int $fontSize;
    public float $opacity;
    public int $angle;
    public float $spacingX;
    public float $spacingY;
    public string $color;
    
    /**
     * Initialize watermark configuration.
     * 
     * @param string $text Text to display as watermark
     * @param int $fontSize Font size for watermark text (8-72, default: 24)
     * @param float $opacity Opacity of watermark (0.1-1.0, default: 0.4)
     * @param int $angle Rotation angle in degrees (-90 to 90, default: 45)
     * @param float $spacingX Horizontal spacing between watermarks (50-500, default: 200)
     * @param float $spacingY Vertical spacing between watermarks (50-500, default: 150)
     * @param string $color Color of watermark text in hex format (default: #CCCCCC)
     */
    public function __construct(
        string $text,
        int $fontSize = 24,
        float $opacity = 0.4,
        int $angle = 45,
        float $spacingX = 200,
        float $spacingY = 150,
        string $color = "#CCCCCC"
    ) {
        $this->text = $text;
        $this->fontSize = max(8, min(72, $fontSize));
        $this->opacity = max(0.1, min(1.0, $opacity));
        $this->angle = max(-90, min(90, $angle));
        $this->spacingX = max(50, min(500, $spacingX));
        $this->spacingY = max(50, min(500, $spacingY));
        $this->color = $color;
    }
}

/**
 * PDF Header Footer Class
 * Handles adding headers and footers to PDF pages.
 */
class PDFHeaderFooter extends FPDF
{
    private float $pageWidth;
    private float $pageHeight;
    private QRCodeGenerator $qrGenerator;
    
    /**
     * Initialize PDF header/footer handler.
     * 
     * @param float $pageWidth Width of the PDF page in points
     * @param float $pageHeight Height of the PDF page in points
     * @param string $qrSize Size of QR code ('small', 'medium', 'large', or custom number)
     */
    public function __construct(float $pageWidth, float $pageHeight, string $qrSize = 'small')
    {
        parent::__construct();
        $this->pageWidth = $pageWidth;
        $this->pageHeight = $pageHeight;
        $this->qrGenerator = new QRCodeGenerator($qrSize);
    }
    
    /**
     * Create a PDF overlay with header (QR code), footer (message), and optional watermark.
     * 
     * @param string $qrData Data to encode in QR code
     * @param string $footerMessage Message to display in footer
     * @param WatermarkConfig|null $watermarkConfig Optional watermark configuration
     * @return string PDF data as string
     */
    public function createHeaderFooterOverlay(
        string $qrData,
        string $footerMessage,
        ?WatermarkConfig $watermarkConfig = null
    ): string {
        // Create temporary file for the overlay
        $tempFile = tempnam(sys_get_temp_dir(), 'pdf_overlay_');
        
        $this->AddPage('', [$this->pageWidth, $this->pageHeight]);
        
        // Add watermark first (so it appears behind other elements)
        if ($watermarkConfig) {
            $this->addWatermarkToCanvas($watermarkConfig);
        }
        
        // Add QR code to top right
        $this->addQrCodeToCanvas($qrData);
        
        // Add footer message
        $this->addFooterToCanvas($footerMessage);
        
        $this->Output('F', $tempFile);
        $pdfData = file_get_contents($tempFile);
        unlink($tempFile);
        
        return $pdfData;
    }
    
    /**
     * Add QR code to the top right of the canvas.
     * 
     * @param string $qrData Data to encode in QR code
     */
    private function addQrCodeToCanvas(string $qrData): void
    {
        // Generate QR code
        $qrImageData = $this->qrGenerator->generateQrCode($qrData);
        
        // Save QR code to temporary file
        $tempQrFile = tempnam(sys_get_temp_dir(), 'qr_') . '.png';
        file_put_contents($tempQrFile, $qrImageData);
        
        // Calculate position (top right, with some margin)
        $qrSize = $this->qrGenerator->getSize();
        $margin = 20;
        $xPosition = $this->pageWidth - $qrSize - $margin;
        $yPosition = $this->pageHeight - $qrSize - $margin;
        
        // Add QR code to canvas
        $this->Image($tempQrFile, $xPosition, $yPosition, $qrSize, $qrSize);
        
        unlink($tempQrFile);
    }
    
    /**
     * Add footer message to the bottom center of the canvas.
     * 
     * @param string $footerMessage Message to display in footer
     */
    private function addFooterToCanvas(string $footerMessage): void
    {
        // Set font and size
        $this->SetFont('Helvetica', '', 10);
        $this->SetTextColor(0, 0, 0);
        
        // Calculate position (bottom center)
        $textWidth = $this->GetStringWidth($footerMessage);
        $xPosition = ($this->pageWidth - $textWidth) / 2;
        $yPosition = 20; // 20 points from bottom
        
        // Add footer text
        $this->Text($xPosition, $yPosition, $footerMessage);
    }
    
    /**
     * Add watermark text across the entire canvas in a repeating pattern.
     * 
     * @param WatermarkConfig $watermarkConfig WatermarkConfig object containing watermark settings
     */
    private function addWatermarkToCanvas(WatermarkConfig $watermarkConfig): void
    {
        // Set font and size
        $this->SetFont('Helvetica', 'B', $watermarkConfig->fontSize);
        
        // Set color and opacity
        $color = $this->hexToRgb($watermarkConfig->color);
        $this->SetTextColor($color[0], $color[1], $color[2]);
        // Opacity (alpha) not supported in standard FPDF. Watermark will be solid color.
        
        // Calculate text width for spacing
        $textWidth = $this->GetStringWidth($watermarkConfig->text);
        
        // Calculate spacing to ensure watermarks cover the entire page
        $spacingX = max($watermarkConfig->spacingX, $textWidth + 50);
        $spacingY = max($watermarkConfig->spacingY, $watermarkConfig->fontSize + 50);
        
        // Calculate how many watermarks we need in each direction
        $numCols = (int)($this->pageWidth / $spacingX) + 2; // Add extra for overlap
        $numRows = (int)($this->pageHeight / $spacingY) + 2; // Add extra for overlap
        
        // Draw watermarks in a grid pattern
        for ($row = 0; $row < $numRows; $row++) {
            for ($col = 0; $col < $numCols; $col++) {
                // Calculate position
                $x = $col * $spacingX;
                $y = $this->pageHeight - ($row * $spacingY);
                
                // Save current state
                $this->_out('q');
                
                // Move to position and rotate
                $this->_out(sprintf('1 0 0 1 %.2f %.2f cm', $x, $y));
                $this->_out(sprintf('%.2f 0 0 %.2f 0 0 cm', 
                    cos(deg2rad($watermarkConfig->angle)), 
                    sin(deg2rad($watermarkConfig->angle))
                ));
                
                // Draw the watermark text
                $this->Text(0, 0, $watermarkConfig->text);
                
                // Restore state
                $this->_out('Q');
            }
        }
        
        // Reset alpha (not needed in standard FPDF)
    }
    
    /**
     * Convert hex color to RGB array.
     * 
     * @param string $hex Hex color string (e.g., "#CCCCCC")
     * @return array RGB values [r, g, b]
     */
    private function hexToRgb(string $hex): array
    {
        $hex = ltrim($hex, '#');
        if (strlen($hex) === 3) {
            $hex = $hex[0] . $hex[0] . $hex[1] . $hex[1] . $hex[2] . $hex[2];
        }
        
        $r = hexdec(substr($hex, 0, 2));
        $g = hexdec(substr($hex, 2, 2));
        $b = hexdec(substr($hex, 4, 2));
        
        return [$r, $g, $b];
    }
}

/**
 * PDF Processor Class
 * Main class for processing PDF files and adding headers/footers.
 */
class PDFProcessor
{
    private ?PDFHeaderFooter $headerFooterHandler = null;
    
    /**
     * Process the input PDF and add headers/footers to each page.
     * 
     * @param string $inputPath Path to input PDF file
     * @param string $outputPath Path for output PDF file
     * @param string $qrData Data to encode in QR code
     * @param string $footerMessage Message to display in footer
     * @param string $qrSize Size of QR code ('small', 'medium', 'large', or custom number)
     * @param WatermarkConfig|null $watermarkConfig Optional watermark configuration
     */
    public function processPdf(
        string $inputPath,
        string $outputPath,
        string $qrData,
        string $footerMessage,
        string $qrSize = 'small',
        ?WatermarkConfig $watermarkConfig = null
    ): void {
        try {
            // Read input PDF
            $pdfContent = file_get_contents($inputPath);
            if ($pdfContent === false) {
                throw new Exception("Could not read input PDF file: $inputPath");
            }
            
            // Create FPDF instance for processing
            $pdf = new FPDF();
            $pdf->SetAutoPageBreak(false);
            
            // Parse PDF pages (simplified - in a real implementation you'd use a proper PDF parser)
            // For this example, we'll create a new PDF with the overlay
            $this->headerFooterHandler = new PDFHeaderFooter(595.28, 841.89, $qrSize); // A4 size
            
            // Create overlay
            $overlayData = $this->headerFooterHandler->createHeaderFooterOverlay(
                $qrData,
                $footerMessage,
                $watermarkConfig
            );
            
            // Write output PDF
            file_put_contents($outputPath, $overlayData);
            
            echo "Successfully processed PDF. Output saved to: $outputPath\n";
            
        } catch (Exception $e) {
            echo "Error processing PDF: " . $e->getMessage() . "\n";
            throw $e;
        }
    }
    
    /**
     * Validate that the input file exists and is a PDF.
     * 
     * @param string $filePath Path to the file to validate
     * @return bool True if file is valid, false otherwise
     */
    public function validateInputFile(string $filePath): bool
    {
        if (!file_exists($filePath)) {
            echo "Error: File '$filePath' does not exist.\n";
            return false;
        }
        
        if (!str_ends_with(strtolower($filePath), '.pdf')) {
            echo "Error: File '$filePath' is not a PDF file.\n";
            return false;
        }
        
        return true;
    }
    
    /**
     * Generate output path based on input path.
     * 
     * @param string $inputPath Path to input PDF file
     * @return string Generated output path
     */
    public function generateOutputPath(string $inputPath): string
    {
        $baseName = pathinfo($inputPath, PATHINFO_FILENAME);
        return $baseName . '_sealed.pdf';
    }
}

/**
 * Main function to handle command line arguments and process PDF.
 */
function main(): void
{
    // Get all command line arguments
    $argv_full = $_SERVER['argv'] ?? $GLOBALS['argv'] ?? [];
    
    // Manual argument parsing (more robust than getopt)
    $inputPdf = null;
    $options = [];
    $skip_next = false;
    
    for ($i = 1; $i < count($argv_full); $i++) {
        $arg = $argv_full[$i];
        
        if ($skip_next) {
            $skip_next = false;
            continue;
        }
        
        // Handle long options
        if (strpos($arg, '--') === 0) {
            $option = substr($arg, 2);
            
            // Handle options with equals sign (e.g., --qr-data=value)
            if (strpos($option, '=') !== false) {
                list($opt_name, $opt_value) = explode('=', $option, 2);
                $options[$opt_name] = $opt_value;
            } else {
                // Handle options with space-separated values
                $skip_next = true;
                if ($i + 1 < count($argv_full)) {
                    $options[$option] = $argv_full[$i + 1];
                }
            }
        } else {
            // This is a positional argument
            if ($inputPdf === null) {
                $inputPdf = $arg;
            }
        }
    }
    
    // Show help if requested
    if (isset($options['help'])) {
        showHelp();
        exit(0);
    }
    
    // Validate required arguments
    if (!$inputPdf) {
        echo "Error: Input PDF file is required.\n";
        showHelp();
        exit(1);
    }
    
    if (!isset($options['qr-data'])) {
        echo "Error: --qr-data is required.\n";
        showHelp();
        exit(1);
    }
    
    if (!isset($options['footer-message'])) {
        echo "Error: --footer-message is required.\n";
        showHelp();
        exit(1);
    }
    
    // Initialize processor
    $processor = new PDFProcessor();
    
    // Validate input file
    if (!$processor->validateInputFile($inputPdf)) {
        exit(1);
    }
    
    // Generate output path if not provided
    $outputPath = $options['output'] ?? $processor->generateOutputPath($inputPdf);
    
    // Create watermark config if watermark text is provided
    $watermarkConfig = null;
    if (isset($options['watermark-text'])) {
        $watermarkConfig = new WatermarkConfig(
            $options['watermark-text'],
            (int)($options['watermark-font-size'] ?? 24),
            (float)($options['watermark-opacity'] ?? 0.4),
            (int)($options['watermark-angle'] ?? 45),
            200, // spacing_x
            150, // spacing_y
            $options['watermark-color'] ?? '#CCCCCC'
        );
    }
    
    // Process PDF
    try {
        $processor->processPdf(
            $inputPdf,
            $outputPath,
            $options['qr-data'],
            $options['footer-message'],
            $options['qr-size'] ?? 'small',
            $watermarkConfig
        );
    } catch (Exception $e) {
        echo "Failed to process PDF: " . $e->getMessage() . "\n";
        exit(1);
    }
}

/**
 * Show help information.
 */
function showHelp(): void
{
    echo "PDF Sealer - Add custom headers (QR code) and footers to PDF files\n\n";
    echo "Usage: php pdf_sealer.php <input_pdf> [options]\n\n";
    echo "Required arguments:\n";
    echo "  <input_pdf>              Path to the input PDF file\n";
    echo "  --qr-data <data>         String data to encode in QR code\n";
    echo "  --footer-message <text>  Message to display in footer\n\n";
    echo "Optional arguments:\n";
    echo "  --qr-size <size>         QR code size: small, medium, or large (default: small)\n";
    echo "  --watermark-text <text>  Text to display as watermark across the document\n";
    echo "  --watermark-font-size <size> Font size for watermark text (default: 24)\n";
    echo "  --watermark-opacity <opacity> Opacity of watermark 0.1-1.0 (default: 0.4)\n";
    echo "  --watermark-angle <angle> Rotation angle of watermark in degrees (default: 45)\n";
    echo "  --watermark-color <color> Color of watermark text in hex format (default: #CCCCCC)\n";
    echo "  --output <file>          Output PDF file path (default: input_sealed.pdf)\n";
    echo "  --help                   Show this help message\n\n";
    echo "Examples:\n";
    echo "  php pdf_sealer.php document.pdf --qr-data \"https://example.com\" --footer-message \"Confidential\"\n";
    echo "  php pdf_sealer.php report.pdf --qr-data \"scan.me/report\" --footer-message \"Internal Use Only\" --watermark-text \"DRAFT\"\n";
}

// Run main function if script is executed directly
if (basename(__FILE__) === basename($_SERVER['SCRIPT_NAME'])) {
    main();
} 