<?php
/**
 * Example usage script for PDF Sealer PHP version
 * Demonstrates how to use the PDF Sealer classes programmatically
 */

require_once 'vendor/autoload.php';

use Endroid\QrCode\QrCode;
use Endroid\QrCode\Writer\PngWriter;
use Endroid\QrCode\Color\Color;
use Endroid\QrCode\ErrorCorrectionLevel\ErrorCorrectionLevelLow;
use FPDF\FPDF;

// Include the main PDF Sealer classes
require_once 'pdf_sealer.php';

echo "PDF Sealer PHP - Example Usage\n";
echo "==============================\n\n";

// Example 1: Basic QR Code Generation
echo "Example 1: Basic QR Code Generation\n";
echo "-----------------------------------\n";

try {
    $qrGenerator = new QRCodeGenerator('medium');
    $qrGenerator->saveQrCode('https://example.com/document/123', 'example_qr.png');
    echo "✓ QR code saved to 'example_qr.png'\n";
} catch (Exception $e) {
    echo "✗ Error generating QR code: " . $e->getMessage() . "\n";
}

echo "\n";

// Example 2: Watermark Configuration
echo "Example 2: Watermark Configuration\n";
echo "----------------------------------\n";

try {
    $watermarkConfig = new WatermarkConfig(
        'CONFIDENTIAL',
        36,    // font size
        0.6,   // opacity
        45,    // angle
        200,   // spacing_x
        150,   // spacing_y
        '#888888' // color
    );
    echo "✓ Watermark configuration created:\n";
    echo "  - Text: {$watermarkConfig->text}\n";
    echo "  - Font Size: {$watermarkConfig->fontSize}\n";
    echo "  - Opacity: {$watermarkConfig->opacity}\n";
    echo "  - Angle: {$watermarkConfig->angle}°\n";
    echo "  - Color: {$watermarkConfig->color}\n";
} catch (Exception $e) {
    echo "✗ Error creating watermark config: " . $e->getMessage() . "\n";
}

echo "\n";

// Example 3: PDF Header/Footer Creation
echo "Example 3: PDF Header/Footer Creation\n";
echo "-------------------------------------\n";

try {
    $headerFooter = new PDFHeaderFooter(595.28, 841.89, 'small'); // A4 size
    $overlayData = $headerFooter->createHeaderFooterOverlay(
        'https://company.com/doc/456',
        'Company Confidential - Page 1',
        $watermarkConfig
    );
    
    file_put_contents('example_overlay.pdf', $overlayData);
    echo "✓ PDF overlay created and saved to 'example_overlay.pdf'\n";
} catch (Exception $e) {
    echo "✗ Error creating PDF overlay: " . $e->getMessage() . "\n";
}

echo "\n";

// Example 4: Full PDF Processing
echo "Example 4: Full PDF Processing\n";
echo "------------------------------\n";

try {
    $processor = new PDFProcessor();
    
    // Check if we have a test PDF file
    $testPdfPath = 'docs/input.pdf';
    if (file_exists($testPdfPath)) {
        $outputPath = 'docs/output_php.pdf';
        
        $processor->processPdf(
            $testPdfPath,
            $outputPath,
            'https://example.com/processed-document',
            'Processed by PHP PDF Sealer',
            'medium',
            new WatermarkConfig('PROCESSED', 24, 0.4, 30)
        );
        
        echo "✓ PDF processed successfully!\n";
        echo "  - Input: $testPdfPath\n";
        echo "  - Output: $outputPath\n";
    } else {
        echo "ℹ No test PDF found at '$testPdfPath'\n";
        echo "  Create a test PDF file to see full processing in action.\n";
    }
} catch (Exception $e) {
    echo "✗ Error processing PDF: " . $e->getMessage() . "\n";
}

echo "\n";

// Example 5: Different QR Code Sizes
echo "Example 5: Different QR Code Sizes\n";
echo "----------------------------------\n";

$sizes = ['small', 'medium', 'large'];
foreach ($sizes as $size) {
    try {
        $qrGenerator = new QRCodeGenerator($size);
        $filename = "example_qr_{$size}.png";
        $qrGenerator->saveQrCode("QR Code Size: $size", $filename);
        echo "✓ {$size} QR code saved to '$filename'\n";
    } catch (Exception $e) {
        echo "✗ Error generating {$size} QR code: " . $e->getMessage() . "\n";
    }
}

echo "\n";

// Example 6: Watermark Variations
echo "Example 6: Watermark Variations\n";
echo "-------------------------------\n";

$watermarkVariations = [
    ['DRAFT', 24, 0.3, 45, '#CCCCCC'],
    ['CONFIDENTIAL', 36, 0.6, 30, '#888888'],
    ['INTERNAL USE ONLY', 18, 0.5, 60, '#666666']
];

foreach ($watermarkVariations as $index => $variation) {
    try {
        $watermarkConfig = new WatermarkConfig(
            $variation[0], // text
            $variation[1], // font size
            $variation[2], // opacity
            $variation[3], // angle
            200,           // spacing_x
            150,           // spacing_y
            $variation[4]  // color
        );
        
        $headerFooter = new PDFHeaderFooter(595.28, 841.89, 'small');
        $overlayData = $headerFooter->createHeaderFooterOverlay(
            'https://example.com',
            'Watermark Example ' . ($index + 1),
            $watermarkConfig
        );
        
        $filename = "example_watermark_" . ($index + 1) . ".pdf";
        file_put_contents($filename, $overlayData);
        echo "✓ Watermark variation " . ($index + 1) . " saved to '$filename'\n";
        echo "  - Text: {$variation[0]}, Size: {$variation[1]}, Opacity: {$variation[2]}, Angle: {$variation[3]}°\n";
    } catch (Exception $e) {
        echo "✗ Error creating watermark variation " . ($index + 1) . ": " . $e->getMessage() . "\n";
    }
}

echo "\n";

// Example 7: Error Handling
echo "Example 7: Error Handling\n";
echo "-------------------------\n";

// Test invalid QR size
try {
    $qrGenerator = new QRCodeGenerator('invalid_size');
    echo "✗ Should have thrown an error for invalid size\n";
} catch (InvalidArgumentException $e) {
    echo "✓ Correctly caught invalid QR size error: " . $e->getMessage() . "\n";
}

// Test invalid watermark parameters
try {
    $watermarkConfig = new WatermarkConfig(
        'TEST',
        100,  // Invalid font size (too large)
        2.0,  // Invalid opacity (too high)
        100,  // Invalid angle (too high)
        1000, // Invalid spacing (too large)
        1000, // Invalid spacing (too large)
        '#INVALID' // Invalid color
    );
    echo "✗ Should have thrown an error for invalid watermark parameters\n";
} catch (Exception $e) {
    echo "✓ Correctly caught invalid watermark parameter error: " . $e->getMessage() . "\n";
}

echo "\n";

// Example 8: File Validation
echo "Example 8: File Validation\n";
echo "--------------------------\n";

$processor = new PDFProcessor();

// Test non-existent file
$result = $processor->validateInputFile('non_existent_file.pdf');
echo $result ? "✗ Should have failed validation" : "✓ Correctly failed validation for non-existent file\n";

// Test non-PDF file
$result = $processor->validateInputFile('example_usage_php.php');
echo $result ? "✗ Should have failed validation" : "✓ Correctly failed validation for non-PDF file\n";

echo "\n";

echo "Example usage completed!\n";
echo "Check the generated files to see the results.\n";
echo "\n";
echo "Generated files:\n";
echo "- example_qr.png (medium QR code)\n";
echo "- example_overlay.pdf (PDF with header/footer/watermark)\n";
echo "- example_qr_small.png, example_qr_medium.png, example_qr_large.png (different QR sizes)\n";
echo "- example_watermark_1.pdf, example_watermark_2.pdf, example_watermark_3.pdf (watermark variations)\n";
echo "- docs/output_php.pdf (if test PDF exists)\n"; 