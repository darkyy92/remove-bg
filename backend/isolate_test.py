"""
Complete isolation test for rembg functionality
This script tests each step in isolation to identify exactly where the issue occurs
"""
import io
import sys
import logging
from pathlib import Path
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("rembg-isolation-test")

def test_image_io():
    """Test basic image I/O operations"""
    logger.info("=== TESTING IMAGE I/O ===")
    
    # 1. Create a test image
    test_image_path = Path("test_image.jpg")
    if not test_image_path.exists():
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img.save(test_image_path)
        logger.info(f"Created test image: {test_image_path}")
    
    # 2. Read the image
    with open(test_image_path, "rb") as f:
        image_data = f.read()
    logger.info(f"Read image data: {len(image_data)} bytes")
    
    # 3. Convert to PIL Image
    img = Image.open(io.BytesIO(image_data))
    logger.info(f"Opened image: mode={img.mode}, size={img.size}")
    
    # 4. Save as PNG
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='PNG')
    output_buffer.seek(0)
    png_data = output_buffer.read()
    logger.info(f"Converted to PNG: {len(png_data)} bytes")
    
    # 5. Write test output
    output_path = Path("test_io.png")
    with open(output_path, "wb") as f:
        f.write(png_data)
    logger.info(f"Wrote test output to {output_path}")
    
    return True, "Image I/O operations successful"

def test_rembg_import():
    """Test rembg import and initialization"""
    logger.info("=== TESTING REMBG IMPORT ===")
    
    try:
        from rembg import remove, new_session
        logger.info("Successfully imported rembg")
        
        # Check session creation
        session = new_session()
        logger.info(f"Created session: {session}")
        
        # Check alternate session creation
        alt_session = new_session("u2net")
        logger.info(f"Created alternate session: {alt_session}")
        
        from rembg.session_factory import sessions_available
        logger.info(f"Available sessions: {sessions_available()}")
        
        return True, "rembg import successful"
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False, f"rembg import failed: {e}"
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return False, f"rembg initialization failed: {e}"

def test_rembg_functionality():
    """Test core rembg functionality"""
    logger.info("=== TESTING REMBG CORE FUNCTIONALITY ===")
    
    try:
        from rembg import remove, new_session
        
        # 1. Create session
        session = new_session("u2net")
        logger.info(f"Created session: {session}")
        
        # 2. Read test image
        test_image_path = Path("test_image.jpg")
        with open(test_image_path, "rb") as f:
            input_data = f.read()
        logger.info(f"Read input data: {len(input_data)} bytes")
        
        # 3. Process with default params
        logger.info("Processing with default parameters...")
        output_data = remove(input_data, session=session)
        logger.info(f"Output data size: {len(output_data)} bytes")
        
        # 4. Save and check result
        output_path = Path("test_default.png")
        with open(output_path, "wb") as f:
            f.write(output_data)
        logger.info(f"Saved output to {output_path}")
        
        # 5. Open output to verify
        output_img = Image.open(output_path)
        logger.info(f"Output image: mode={output_img.mode}, size={output_img.size}")
        
        # 6. Try alternative parameters
        logger.info("Processing with alternative parameters...")
        alt_output = remove(
            input_data,
            session=session,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10
        )
        
        # 7. Save alternative result
        alt_output_path = Path("test_alt.png")
        with open(alt_output_path, "wb") as f:
            f.write(alt_output)
        logger.info(f"Saved alternative output to {alt_output_path}")
        
        return True, "rembg functionality tests successful"
    except Exception as e:
        logger.error(f"rembg functionality error: {e}")
        return False, f"rembg functionality failed: {e}"

def test_api_flow():
    """Test the API flow similar to the FastAPI endpoint"""
    logger.info("=== TESTING API FLOW ===")
    
    try:
        from rembg import remove, new_session
        
        # 1. Create session (done at startup)
        session = new_session("u2net")
        logger.info(f"Created session: {session}")
        
        # 2. Read test image (similar to file upload)
        test_image_path = Path("test_image.jpg")
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        logger.info(f"Read input data: {len(image_data)} bytes")
        
        # 3. Process image (API endpoint logic)
        # 3.1 Validate image
        img = Image.open(io.BytesIO(image_data))
        logger.info(f"Validated image: mode={img.mode}, size={img.size}")
        
        # 3.2 Process with rembg
        output = remove(
            image_data,
            session=session,
            alpha_matting=False,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )
        logger.info(f"Processed output: {len(output)} bytes")
        
        # 3.3 Validate output
        output_img = Image.open(io.BytesIO(output))
        logger.info(f"Output image: mode={output_img.mode}, size={output_img.size}")
        has_transparency = 'A' in output_img.mode or output_img.mode == 'P' and 'transparency' in output_img.info
        logger.info(f"Has transparency: {has_transparency}")
        
        # 3.4 Save output (for inspection)
        output_path = Path("test_api_flow.png")
        with open(output_path, "wb") as f:
            f.write(output)
        logger.info(f"Saved output to {output_path}")
        
        return True, "API flow test successful"
    except Exception as e:
        logger.error(f"API flow error: {e}")
        return False, f"API flow test failed: {e}"

def run_all_tests():
    """Run all tests in sequence"""
    tests = [
        ("Image I/O", test_image_io),
        ("rembg Import", test_rembg_import),
        ("rembg Functionality", test_rembg_functionality),
        ("API Flow", test_api_flow)
    ]
    
    results = []
    for name, test_fn in tests:
        logger.info(f"\n\n=== STARTING TEST: {name} ===")
        try:
            success, message = test_fn()
            results.append((name, success, message))
        except Exception as e:
            logger.error(f"Test error: {e}")
            results.append((name, False, f"Test error: {e}"))
    
    logger.info("\n\n=== TEST RESULTS SUMMARY ===")
    for name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {name}: {message}")
    
    # Return overall success (all tests passed)
    return all(success for _, success, _ in results)

if __name__ == "__main__":
    logger.info("Starting comprehensive isolation tests")
    success = run_all_tests()
    exit_code = 0 if success else 1
    logger.info(f"Tests completed with exit code {exit_code}")
    sys.exit(exit_code)