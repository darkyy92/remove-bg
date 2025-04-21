import io
import logging
import sys
from pathlib import Path
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("rembg-debug")

def test_rembg():
    try:
        from rembg import remove, new_session
        logger.info("Successfully imported rembg")
        
        # Check if models directory exists and what files are in it
        models_dir = Path.home() / ".u2net"
        logger.info(f"Models directory path: {models_dir}")
        logger.info(f"Models directory exists: {models_dir.exists()}")
        
        if models_dir.exists():
            logger.info(f"Files in models directory: {list(models_dir.glob('*'))}")
        
        # Test with a simple image
        test_image_path = Path("test_image.jpg")
        
        if not test_image_path.exists():
            # Create a simple test image if none exists
            logger.info("Creating test image")
            img = Image.new('RGB', (100, 100), color=(255, 0, 0))
            img.save(test_image_path)
        
        # Try to process the image
        logger.info(f"Loading image from {test_image_path}")
        with open(test_image_path, "rb") as input_file:
            input_data = input_file.read()
        
        # Create a session explicitly
        logger.info("Creating rembg session")
        session = new_session()
        logger.info(f"Session created: {session}")
        
        # Process the image with explicit session
        logger.info("Processing image with rembg")
        output_data = remove(input_data, session=session)
        logger.info(f"Output data size: {len(output_data)} bytes")
        
        # Save the result
        output_path = Path("test_output.png")
        with open(output_path, "wb") as output_file:
            output_file.write(output_data)
        logger.info(f"Saved output to {output_path}")
        
        # Success!
        logger.info("Test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting rembg debug test")
    result = test_rembg()
    logger.info(f"Test result: {'Success' if result else 'Failure'}")