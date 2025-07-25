#!/usr/bin/env python3
"""
Run this script to start the Taiyaki AI MCP server.
Make sure FreeCAD is running with the Taiyaki AI workbench active.
"""
import os
import sys
import importlib.util
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TaiyakiAI_Runner")

def main():
    """Run the MCP server with the updated code"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Starting Taiyaki AI MCP server from {current_dir}")
    
    # Add src directory to Python path so imports work
    src_dir = os.path.join(current_dir, "src")
    sys.path.insert(0, src_dir)
    
    # Try to import the server module
    try:
        from src.freecad_mcp.server import main as server_main
        
        # Verify prompts are loaded
        try:
            from src.freecad_mcp.prompts.printing_guidelines import printing_guidelines
            prompt_content = printing_guidelines()
            if "SLA" in prompt_content:
                logger.info("3D Printing guidelines prompt loaded successfully")
            else:
                logger.warning("3D Printing guidelines prompt loaded but content may be incorrect")
        except ImportError:
            logger.warning("Could not verify 3D Printing guidelines prompt")
            
        logger.info("Found freecad_mcp module, starting server")
        server_main()
    except ImportError as e:
        logger.error(f"Error importing server module: {e}")
        logger.info("Trying alternative approach...")
        
        # If that fails, try running the module directly
        server_path = os.path.join(current_dir, "src", "freecad_mcp", "server.py")
        if os.path.exists(server_path):
            logger.info(f"Found server.py at {server_path}")
            
            # Load the module directly
            spec = importlib.util.spec_from_file_location("server", server_path)
            server = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(server)
            
            # Run the main function
            logger.info("Starting server directly")
            server.main()
        else:
            logger.error(f"Server module not found at {server_path}")
            return 1
    
    return 0

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)