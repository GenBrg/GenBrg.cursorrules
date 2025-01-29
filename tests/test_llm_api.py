import pytest
import os
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path
import base64
from tools.llm_api import query_llm, encode_image_to_base64

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test data
TEST_PROMPT = "What is the capital of France?"
TEST_RESPONSE = "The capital of France is Paris."
TEST_IMAGE_CONTENT = b"fake_image_data"
TEST_IMAGE_BASE64 = base64.b64encode(TEST_IMAGE_CONTENT).decode('utf-8')

@pytest.fixture
def mock_image(tmp_path):
    """Create a temporary test image file."""
    image_path = tmp_path / "test_image.jpg"
    with open(image_path, "wb") as f:
        f.write(TEST_IMAGE_CONTENT)
    logger.info(f"Created mock image file at: {image_path}")
    return str(image_path)

def test_encode_image_to_base64(mock_image):
    """Test image encoding to base64."""
    logger.info("Testing image encoding to base64")
    encoded = encode_image_to_base64(mock_image)
    logger.info(f"Encoded image length: {len(encoded)}")
    assert encoded == TEST_IMAGE_BASE64
    logger.info("Image encoding test passed")

@patch('g4f.ChatCompletion.create')
def test_query_llm_basic(mock_create):
    """Test basic LLM query without image."""
    logger.info("\nTesting basic LLM query")
    mock_create.return_value = TEST_RESPONSE
    
    logger.info(f"Sending prompt: {TEST_PROMPT}")
    response = query_llm(TEST_PROMPT)
    
    logger.info(f"Received response: {response}")
    assert response == TEST_RESPONSE
    
    mock_create.assert_called_once()
    call_args = mock_create.call_args[1]
    logger.info(f"Call arguments: {call_args}")
    assert call_args['messages'][0]['content'] == TEST_PROMPT
    assert call_args['model'] == "gpt-4o"
    logger.info("Basic LLM query test passed")

@patch('g4f.ChatCompletion.create')
def test_query_llm_with_image(mock_create, mock_image):
    """Test LLM query with image input."""
    logger.info("\nTesting LLM query with image")
    mock_create.return_value = TEST_RESPONSE
    
    logger.info(f"Sending prompt with image: {TEST_PROMPT}")
    logger.info(f"Image path: {mock_image}")
    response = query_llm(TEST_PROMPT, image_path=mock_image)
    
    logger.info(f"Received response: {response}")
    assert response == TEST_RESPONSE
    
    mock_create.assert_called_once()
    call_args = mock_create.call_args[1]
    logger.info(f"Call arguments: {call_args}")
    assert TEST_IMAGE_BASE64 in call_args['messages'][0]['content']
    assert TEST_PROMPT in call_args['messages'][0]['content']
    assert call_args['model'] == "gpt-4o"
    logger.info("Image query test passed")

@patch('g4f.ChatCompletion.create')
def test_query_llm_with_custom_model(mock_create):
    """Test LLM query with custom model."""
    logger.info("\nTesting LLM query with custom model")
    mock_create.return_value = TEST_RESPONSE
    custom_model = "gpt-3.5-turbo"
    
    logger.info(f"Sending prompt with custom model: {custom_model}")
    response = query_llm(TEST_PROMPT, model=custom_model)
    
    logger.info(f"Received response: {response}")
    assert response == TEST_RESPONSE
    
    mock_create.assert_called_once()
    call_args = mock_create.call_args[1]
    logger.info(f"Call arguments: {call_args}")
    assert call_args['model'] == custom_model
    logger.info("Custom model test passed")

def test_query_llm_with_nonexistent_image():
    """Test LLM query with non-existent image file."""
    logger.info("\nTesting LLM query with non-existent image")
    nonexistent_path = "nonexistent.jpg"
    logger.info(f"Attempting to use non-existent image: {nonexistent_path}")
    
    with pytest.raises(FileNotFoundError) as exc_info:
        query_llm(TEST_PROMPT, image_path=nonexistent_path)
    
    logger.info(f"Caught expected FileNotFoundError: {str(exc_info.value)}")
    logger.info("Non-existent image test passed")

@patch('g4f.ChatCompletion.create')
def test_query_llm_error_handling(mock_create):
    """Test error handling in LLM query."""
    logger.info("\nTesting LLM query error handling")
    test_error = "Test error message"
    mock_create.side_effect = Exception(test_error)
    
    logger.info("Attempting query that should raise an exception")
    with pytest.raises(Exception) as exc_info:
        query_llm(TEST_PROMPT)
    
    logger.info(f"Caught expected exception: {str(exc_info.value)}")
    assert test_error in str(exc_info.value)
    logger.info("Error handling test passed")
