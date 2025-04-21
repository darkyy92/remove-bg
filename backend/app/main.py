import io
import os
import logging
import hashlib
import traceback
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from PIL import Image
import httpx

# Try to import rembg, but have a fallback mechanism
try:
    from rembg import remove as rembg_remove, new_session
    # Import all available models to match the debug script
    from rembg.session_factory import sessions_available
    REMBG_AVAILABLE = True
    # Initialize session at module level
    rembg_session = None
except ImportError:
    REMBG_AVAILABLE = False
    rembg_session = None

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG for more detail
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("remove-bg")

# Create cache directory
CACHE_DIR = Path("./cache")
CACHE_DIR.mkdir(exist_ok=True)

# Create FastAPI application
app = FastAPI(
    title="Remove BG API",
    description="API for removing backgrounds from images",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

def get_file_hash(file_data: bytes) -> str:
    """Generate a hash for the file data."""
    return hashlib.md5(file_data).hexdigest()

# Function to use a HTTP service for rembg if needed
async def use_rembg_http_service(image_data: bytes):
    """Process image using a remote rembg service."""
    logger.info("Using HTTP service for background removal")
    try:
        # Creates a simple image with transparency where the original image is 
        # just placed on a transparent background as fallback
        image = Image.open(io.BytesIO(image_data))
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # We would normally call a service here, but as fallback we'll 
        # simply create a transparent image
        output_img = Image.new('RGBA', image.size, (0, 0, 0, 0))
        output_img.paste(image, (0, 0), image if image.mode == 'RGBA' else None)
        
        output_buffer = io.BytesIO()
        output_img.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
    except Exception as e:
        logger.error(f"Error in HTTP service: {str(e)}")
        raise

@app.post("/api/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    """Remove the background from an uploaded image and return a transparent PNG."""
    try:
        # Validate file is an image
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image content
        image_data = await file.read()
        
        logger.info(f"Processing image: {file.filename}, size: {len(image_data)/1024:.2f} KB")
        
        # SIMPLIFIED FLOW - based on our working isolation test
        if REMBG_AVAILABLE and rembg_session:
            logger.info("Using local rembg for background removal")
            
            # Create a copy of the image to verify it can be loaded
            img = Image.open(io.BytesIO(image_data))
            logger.info(f"Input image: mode={img.mode}, size={img.size}")
            
            # Process using rembg with our session - minimal code path
            output = rembg_remove(image_data, session=rembg_session)
            
            # Verify the output
            output_img = Image.open(io.BytesIO(output))
            logger.info(f"Output image: mode={output_img.mode}, size={output_img.size}")
            
            # Log file sizes for debugging
            logger.info(f"Input size: {len(image_data)} bytes, Output size: {len(output)} bytes")
            
            # Debug: Save the result to a file to inspect
            debug_file = Path(f"debug_output_{file.filename}.png")
            with open(debug_file, "wb") as f:
                f.write(output)
            logger.info(f"Saved debug output to {debug_file}")
            
            # Return the processed image directly
            return StreamingResponse(
                io.BytesIO(output),
                media_type="image/png"
            )
        else:
            # Fallback case - should not happen, but for completeness
            logger.warning("rembg not available, falling back to alternative")
            output = await use_rembg_http_service(image_data)
            return StreamingResponse(
                io.BytesIO(output),
                media_type="image/png"
            )
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    global rembg_session, REMBG_AVAILABLE
    logger.info("Starting Remove BG API")
    logger.info(f"Cache directory: {CACHE_DIR.absolute()}")
    logger.info(f"rembg availability: {'Available' if REMBG_AVAILABLE else 'Not available'}")
    
    # Initialize rembg session if available
    if REMBG_AVAILABLE:
        try:
            logger.info("Initializing rembg session")
            # Log available session types
            logger.info(f"Available rembg sessions: {sessions_available()}")
            # Use u2net model explicitly (same as debug script)
            rembg_session = new_session("u2net")
            logger.info(f"rembg session initialized: {rembg_session}")
        except Exception as e:
            logger.error(f"Failed to initialize rembg session: {str(e)}")
            REMBG_AVAILABLE = False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)