<?php
/**
 * Simple test suite for PDF Sealer PHP version
 */

require_once 'vendor/autoload.php';
require_once 'pdf_sealer.php';

class PDFSealerTest
{
    private int $passed = 0;
    private int $failed = 0;
    
    public function runTests(): void
    {
        echo "PDF Sealer PHP - Test Suite\n";
        echo "===========================\n\n";
        
        $this->testQRCodeGenerator();
        $this->testWatermarkConfig();
        $this->testPDFHeaderFooter();
        $this->testPDFProcessor();
        $this->testErrorHandling();
        
        $this->printResults();
    }
    
    private function testQRCodeGenerator(): void
    {
        echo "Testing QRCodeGenerator...\n";
        
        // Test valid sizes
        $sizes = ['small', 'medium', 'large'];
        foreach ($sizes as $size) {
            try {
                $qr = new QRCodeGenerator($size);
                $this->assert($qr->getSize() > 0, "QR size for '$size' should be positive");
                echo "  ✓ QRCodeGenerator with size '$size' created successfully\n";
            } catch (Exception $e) {
                $this->fail("QRCodeGenerator with size '$size' should not throw exception: " . $e->getMessage());
            }
        }
        
        // Test custom numeric size
        try {
            $qr = new QRCodeGenerator('40');
            $this->assert($qr->getSize() === 40, "Custom QR size should be 40");
            echo "  ✓ QRCodeGenerator with custom size '40' created successfully\n";
        } catch (Exception $e) {
            $this->fail("QRCodeGenerator with custom size should not throw exception: " . $e->getMessage());
        }
        
        // Test QR code generation
        try {
            $qr = new QRCodeGenerator('small');
            $qrData = $qr->generateQrCode('test data');
            $this->assert(!empty($qrData), "Generated QR code should not be empty");
            echo "  ✓ QR code generation successful\n";
        } catch (Exception $e) {
            $this->fail("QR code generation should not throw exception: " . $e->getMessage());
        }
        
        // Test invalid size
        try {
            new QRCodeGenerator('invalid');
            $this->fail("QRCodeGenerator with invalid size should throw exception");
        } catch (InvalidArgumentException $e) {
            $this->assert(true, "Correctly caught invalid size exception");
            echo "  ✓ Invalid size correctly rejected\n";
        }
        
        echo "\n";
    }
    
    private function testWatermarkConfig(): void
    {
        echo "Testing WatermarkConfig...\n";
        
        // Test valid configuration
        try {
            $watermark = new WatermarkConfig(
                'TEST',
                24,
                0.5,
                45,
                200,
                150,
                '#CCCCCC'
            );
            
            $this->assert($watermark->text === 'TEST', "Watermark text should be 'TEST'");
            $this->assert($watermark->fontSize === 24, "Font size should be 24");
            $this->assert($watermark->opacity === 0.5, "Opacity should be 0.5");
            $this->assert($watermark->angle === 45, "Angle should be 45");
            $this->assert($watermark->color === '#CCCCCC', "Color should be #CCCCCC");
            
            echo "  ✓ WatermarkConfig created successfully\n";
        } catch (Exception $e) {
            $this->fail("WatermarkConfig creation should not throw exception: " . $e->getMessage());
        }
        
        // Test parameter validation (font size)
        try {
            $watermark = new WatermarkConfig('TEST', 100); // Too large
            $this->assert($watermark->fontSize === 72, "Font size should be clamped to 72");
            echo "  ✓ Font size validation working\n";
        } catch (Exception $e) {
            $this->fail("Font size validation should not throw exception: " . $e->getMessage());
        }
        
        // Test parameter validation (opacity)
        try {
            $watermark = new WatermarkConfig('TEST', 24, 2.0); // Too high
            $this->assert($watermark->opacity === 1.0, "Opacity should be clamped to 1.0");
            echo "  ✓ Opacity validation working\n";
        } catch (Exception $e) {
            $this->fail("Opacity validation should not throw exception: " . $e->getMessage());
        }
        
        // Test parameter validation (angle)
        try {
            $watermark = new WatermarkConfig('TEST', 24, 0.5, 100); // Too high
            $this->assert($watermark->angle === 90, "Angle should be clamped to 90");
            echo "  ✓ Angle validation working\n";
        } catch (Exception $e) {
            $this->fail("Angle validation should not throw exception: " . $e->getMessage());
        }
        
        echo "\n";
    }
    
    private function testPDFHeaderFooter(): void
    {
        echo "Testing PDFHeaderFooter...\n";
        
        try {
            $headerFooter = new PDFHeaderFooter(595.28, 841.89, 'small');
            $this->assert($headerFooter instanceof PDFHeaderFooter, "PDFHeaderFooter should be instantiated");
            echo "  ✓ PDFHeaderFooter created successfully\n";
            
            // Test overlay creation
            $overlayData = $headerFooter->createHeaderFooterOverlay(
                'https://example.com',
                'Test Footer',
                new WatermarkConfig('TEST', 24, 0.3)
            );
            
            $this->assert(!empty($overlayData), "Overlay data should not be empty");
            echo "  ✓ PDF overlay creation successful\n";
            
        } catch (Exception $e) {
            $this->fail("PDFHeaderFooter should not throw exception: " . $e->getMessage());
        }
        
        echo "\n";
    }
    
    private function testPDFProcessor(): void
    {
        echo "Testing PDFProcessor...\n";
        
        try {
            $processor = new PDFProcessor();
            $this->assert($processor instanceof PDFProcessor, "PDFProcessor should be instantiated");
            echo "  ✓ PDFProcessor created successfully\n";
            
            // Test file validation
            $result = $processor->validateInputFile('non_existent.pdf');
            $this->assert($result === false, "Non-existent file should fail validation");
            echo "  ✓ File validation working (non-existent file)\n";
            
            // Test output path generation
            $outputPath = $processor->generateOutputPath('test.pdf');
            $this->assert($outputPath === 'test_sealed.pdf', "Output path should be 'test_sealed.pdf'");
            echo "  ✓ Output path generation working\n";
            
        } catch (Exception $e) {
            $this->fail("PDFProcessor should not throw exception: " . $e->getMessage());
        }
        
        echo "\n";
    }
    
    private function testErrorHandling(): void
    {
        echo "Testing Error Handling...\n";
        
        // Test invalid QR size
        try {
            new QRCodeGenerator('invalid_size');
            $this->fail("Should have thrown exception for invalid QR size");
        } catch (InvalidArgumentException $e) {
            $this->assert(true, "Correctly caught invalid QR size exception");
            echo "  ✓ Invalid QR size exception handling working\n";
        }
        
        // Test file operations with non-existent file
        try {
            $processor = new PDFProcessor();
            $processor->processPdf(
                'non_existent.pdf',
                'output.pdf',
                'test',
                'test',
                'small'
            );
            $this->fail("Should have thrown exception for non-existent file");
        } catch (Exception $e) {
            $this->assert(true, "Correctly caught file operation exception");
            echo "  ✓ File operation exception handling working\n";
        }
        
        echo "\n";
    }
    
    private function assert(bool $condition, string $message): void
    {
        if ($condition) {
            $this->passed++;
        } else {
            $this->failed++;
            echo "  ✗ FAIL: $message\n";
        }
    }
    
    private function fail(string $message): void
    {
        $this->failed++;
        echo "  ✗ FAIL: $message\n";
    }
    
    private function printResults(): void
    {
        echo "Test Results\n";
        echo "============\n";
        echo "Passed: {$this->passed}\n";
        echo "Failed: {$this->failed}\n";
        echo "Total: " . ($this->passed + $this->failed) . "\n\n";
        
        if ($this->failed === 0) {
            echo "🎉 All tests passed!\n";
        } else {
            echo "❌ Some tests failed. Please check the output above.\n";
        }
    }
}

// Run tests if script is executed directly
if (basename(__FILE__) === basename($_SERVER['SCRIPT_NAME'])) {
    $test = new PDFSealerTest();
    $test->runTests();
} 