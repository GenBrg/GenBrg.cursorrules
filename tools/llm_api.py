#!/usr/bin/env python3
import argparse
import logging
import sys
from typing import Optional, Dict, Any
import g4f
from pathlib import Path
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 string."""
    logger.info(f"Encoding image: {image_path}")
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
    logger.info(f"Successfully encoded image (length: {len(encoded)} chars)")
    return encoded

def query_llm(
    prompt: str,
    model: str = "gpt-4o",
    image_path: Optional[str] = None,
    **kwargs
) -> str:
    """
    Query LLM using g4f with automatic provider selection.
    
    Args:
        prompt: The prompt to send to the LLM
        model: The model to use (defaults to "gpt-4o")
        image_path: Path to an image file to include in the prompt (optional)
        **kwargs: Additional arguments to pass to the provider
    
    Returns:
        str: The response from the LLM
    """
    try:
        logger.info(f"Starting LLM query with model: {model}")
        logger.info(f"Original prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Original prompt: {prompt}")
        
        # Handle image input
        if image_path:
            if not Path(image_path).exists():
                logger.error(f"Image file not found: {image_path}")
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Note: Not all g4f providers support image input
            # This is a basic implementation that may need to be adapted
            image_base64 = encode_image_to_base64(image_path)
            prompt = f"[Image: {image_base64}]\n\n{prompt}"
            logger.info("Added image to prompt")

        # Create completion with auto provider selection
        logger.info(f"Sending request to g4f with model: {model}")
        logger.info(f"Additional kwargs: {kwargs}")
        
        response = g4f.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        logger.info(f"Received response (length: {len(response)} chars)")
        logger.info(f"Response preview: {response[:100]}..." if len(response) > 100 else f"Response: {response}")
        
        return response

    except Exception as e:
        logger.error(f"Error querying LLM: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Query LLM using g4f")
    parser.add_argument("--prompt", required=True, help="The prompt to send to the LLM")
    parser.add_argument("--model", default="gpt-4o", help="The model to use (default: gpt-4o)")
    parser.add_argument("--image", help="Path to an image file to include in the prompt")
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting LLM API with arguments:")
        logger.info(f"  Prompt: {args.prompt}")
        logger.info(f"  Model: {args.model}")
        logger.info(f"  Image: {args.image if args.image else 'None'}")
        
        response = query_llm(
            prompt=args.prompt,
            model=args.model,
            image_path=args.image
        )
        
        logger.info("Query completed successfully")
        print("\nLLM Response:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
