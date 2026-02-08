"""
Image Generation - Separated from media_gen.py
Image generation using Dedalus API (OpenAI GPT-Image-1, DALL-E)
"""
import os
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import base64
import requests
import asyncio
import time
from pathlib import Path


# API Configuration
DEDALUS_API_URL = "https://api.dedaluslabs.ai/v1/images/generations"
DEFAULT_MODEL = "openai/dall-e-3"
DEFAULT_QUALITY = "standard"
DEFAULT_SIZE = "1024x1024"  # Landscape for storybook
DEFAULT_OUTPUT_FORMAT = "webp"
DEFAULT_COMPRESSION = 85
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def get_api_key() -> str:
    """Get Dedalus API key from environment"""
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key or api_key == "your_dedalus_api_key_here":
        raise ValueError(
            "DEDALUS_API_KEY is not configured. "
            "Please set it in your .env file."
        )
    return api_key


async def call_dedalus_api(
    prompt: str,
    model: str = DEFAULT_MODEL,
    size: str = DEFAULT_SIZE,
    quality: str = DEFAULT_QUALITY,
    n: int = 1,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    output_compression: int = DEFAULT_COMPRESSION,
    response_format: str = "b64_json"
) -> Dict[str, Any]:
    """
    Call Dedalus API to generate images
    
    Args:
        prompt: Text description of desired image
        model: Model to use (openai/gpt-image-1, openai/dall-e-3, etc.)
        size: Image size (1536x1024, 1024x1536, etc.)
        quality: Quality level (high, medium, low)
        n: Number of images to generate
        output_format: Output format (webp, png, jpeg)
        output_compression: Compression level (0-100)
        response_format: Response format (b64_json or url)
    
    Returns:
        API response as dictionary
    """
    api_key = get_api_key()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "quality": quality,
        "n": n,
        "response_format": response_format
    }
    
    # Add specific model parameters
    # model="openai/gpt-image-1" (최고 품질)
    # model="openai/dall-e-3" (프롬프트 자동 개선)
    # model="openai/dall-e-2" (빠르고 저렴)
    if model == "openai/dall-e-2":
        payload["output_format"] = output_format
        payload["output_compression"] = output_compression
    
    # Retry logic
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                DEDALUS_API_URL,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limit - wait and retry
                wait_time = RETRY_DELAY * (2 ** attempt)
                print(f"Rate limited. Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
                continue
            elif response.status_code == 401:
                raise ValueError("Invalid API key. Check DEDALUS_API_KEY.")
            else:
                error_msg = f"API error {response.status_code}: {response.text}"
                if attempt < MAX_RETRIES - 1:
                    print(f"{error_msg}. Retrying...")
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                print(f"Request timeout. Retrying...")
                await asyncio.sleep(RETRY_DELAY)
                continue
            raise Exception("API request timed out after multiple retries")
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Request error: {e}. Retrying...")
                await asyncio.sleep(RETRY_DELAY)
                continue
            raise Exception(f"API request failed: {e}")
    
    raise Exception("Failed to generate image after multiple retries")


def save_base64_image(
    base64_data: str,
    output_path: str,
    file_format: str = "webp"
) -> str:
    """
    Save base64-encoded image to file
    
    Args:
        base64_data: Base64-encoded image data
        output_path: Path to save the image
        file_format: Image format (webp, png, jpeg)
    
    Returns:
        Path to saved image
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Decode and save
        image_data = base64.b64decode(base64_data)
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        print(f"Image saved: {output_path} ({len(image_data)} bytes)")
        return output_path
        
    except Exception as e:
        print(f"Error saving image: {e}")
        return ""


def simple_split_story(story: str, num_scenes: int) -> List[str]:
    """
    Simple story splitting without AI
    TODO: Replace with JSON input from K2 Think when connected
    
    Args:
        story: Story text (can be string or will be JSON list later)
        num_scenes: Number of scenes to generate
    
    Returns:
        List of scene descriptions
    """
    # Split by paragraphs/lines and filter empty ones
    lines = [line.strip() for line in story.strip().split('\n') if line.strip()]
    
    # If we have enough lines, use them directly
    if len(lines) >= num_scenes:
        return lines[:num_scenes]
    
    # Otherwise, repeat or pad
    scenes = lines * (num_scenes // len(lines) + 1) if lines else ["A beautiful scene"]
    return scenes[:num_scenes]


async def generate_images(story: str, num_images: int = 4) -> List[str]:
    """
    Generate multiple images from story using Dedalus API
    
    Args:
        story: Story text to generate images from (will be JSON list later)
        num_images: Number of images to generate
    
    Returns:
        List of paths to generated images
    """
    try:
        print(f"Splitting story into {num_images} scenes...")
        scenes = simple_split_story(story, num_images)
        
        if not scenes:
            print("No scenes generated from story")
            return []
        
        image_paths = []
        
        # Generate images for each scene
        for idx, scene in enumerate(scenes[:num_images]):
            try:
                print(f"\n[{idx+1}/{num_images}] Generating image for scene:")
                print(f"  {scene[:100]}...")
                
                # Call API
                start_time = time.time()
                response = await call_dedalus_api(
                    prompt=scene,
                    model=DEFAULT_MODEL,
                    size=DEFAULT_SIZE,
                    quality=DEFAULT_QUALITY,
                    n=1
                )
                
                elapsed = time.time() - start_time
                print(f"  API call completed in {elapsed:.2f}s")
                
                # Extract and save image
                if response.get("data") and len(response["data"]) > 0:
                    image_data = response["data"][0]
                    
                    # Generate output path
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"image_{timestamp}_{uuid.uuid4().hex[:8]}_{idx}.{DEFAULT_OUTPUT_FORMAT}"
                    output_path = os.path.join("data", filename)
                    
                    # Save image
                    if image_data.get("b64_json"):
                        saved_path = save_base64_image(
                            image_data["b64_json"],
                            output_path,
                            DEFAULT_OUTPUT_FORMAT
                        )
                        if saved_path:
                            image_paths.append(saved_path)
                    elif image_data.get("url"):
                        # If URL is returned, we could download it
                        print(f"  Image URL: {image_data['url']}")
                        image_paths.append(image_data["url"])
                    
                    # Log revised prompt if available (DALL-E-3)
                    if image_data.get("revised_prompt"):
                        print(f"  Revised prompt: {image_data['revised_prompt'][:100]}...")
                
                # Small delay between requests to avoid rate limiting
                if idx < len(scenes) - 1:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                print(f"  Error generating image {idx+1}: {e}")
                continue
        
        print(f"\nSuccessfully generated {len(image_paths)}/{num_images} images")
        return image_paths
        
    except Exception as e:
        print(f"Image generation error: {e}")
        return []


async def generate_imagen_image(
    prompt: str,
    output_path: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    size: str = DEFAULT_SIZE,
    quality: str = DEFAULT_QUALITY
) -> str:
    """
    Generate single image using Dedalus API
    
    Args:
        prompt: Text description of desired image
        output_path: Path to save the image (optional, auto-generated if not provided)
        model: Model to use for generation
        size: Image size
        quality: Image quality
    
    Returns:
        Path to generated image, or empty string on error
    """
    try:
        print(f"Generating image: {prompt[:100]}...")
        
        # Call API
        start_time = time.time()
        response = await call_dedalus_api(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            n=1
        )
        
        elapsed = time.time() - start_time
        print(f"API call completed in {elapsed:.2f}s")
        
        # Extract image data
        if not response.get("data") or len(response["data"]) == 0:
            raise Exception("No image data in API response")
        
        image_data = response["data"][0]
        
        # Generate output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}_{uuid.uuid4().hex[:8]}.{DEFAULT_OUTPUT_FORMAT}"
            output_path = os.path.join("data", filename)
        
        # Save image
        if image_data.get("b64_json"):
            saved_path = save_base64_image(
                image_data["b64_json"],
                output_path,
                DEFAULT_OUTPUT_FORMAT
            )
            return saved_path
        elif image_data.get("url"):
            print(f"Image URL: {image_data['url']}")
            return image_data["url"]
        else:
            raise Exception("No image data (b64_json or url) in response")
        
    except Exception as e:
        print(f"Imagen image generation error: {e}")
        return ""


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

async def test_single_image():
    """Test single image generation"""
    print("=" * 60)
    print("TEST 1: Single Image Generation")
    print("=" * 60)
    
    prompt = "A cute robot reading a book in a cozy library, warm lighting, children's book illustration style"
    
    print(f"\nPrompt: {prompt}\n")
    
    result = await generate_imagen_image(
        prompt=prompt,
        quality="standard",  # Use standard for faster testing
        size="1024x1024"   # Square format for testing
    )
    
    if result:
        print(f"\n✅ SUCCESS: Image saved at {result}")
    else:
        print("\n❌ FAILED: Image generation failed")
    
    return result


async def test_multiple_images():
    """Test multiple images from story"""
    print("\n" + "=" * 60)
    print("TEST 2: Multiple Images from Story")
    print("=" * 60)
    
    story = """
    Once upon a time, there was a brave little robot named Bolt.
    Bolt lived in a magical forest filled with glowing mushrooms and talking animals.
    One day, Bolt discovered a mysterious ancient temple hidden behind a waterfall.
    Inside the temple, Bolt found a treasure chest filled with magical crystals.
    """
    
    print(f"\nStory preview: {story[:100]}...\n")
    print("Generating 3 images...\n")
    
    results = await generate_images(story, num_images=3)
    
    if results:
        print(f"\n✅ SUCCESS: Generated {len(results)} images")
        for i, path in enumerate(results, 1):
            print(f"   {i}. {path}")
    else:
        print("\n❌ FAILED: No images generated")
    
    return results


async def test_api_configuration():
    """Test different API configurations"""
    print("\n" + "=" * 60)
    print("TEST 3: API Configuration Test")
    print("=" * 60)
    
    # Check API key
    try:
        api_key = get_api_key()
        key_preview = api_key[:10] + "..." if len(api_key) > 10 else api_key
        print(f"\n✅ API Key found: {key_preview}")
    except ValueError as e:
        print(f"\n❌ API Key error: {e}")
        return False
    
    # Test different models
    models = [
        ("openai/gpt-image-1", "GPT Image 1 - Best quality, longest prompt"),
        ("openai/dall-e-3", "DALL-E 3 - High quality, prompt enhancement"),
        ("openai/dall-e-2", "DALL-E 2 - Fast and affordable"),
    ]
    
    print("\nAvailable models:")
    for model, description in models:
        print(f"  - {model}: {description}")
    
    print(f"\nCurrent default model: {DEFAULT_MODEL}")
    print(f"Default size: {DEFAULT_SIZE}")
    print(f"Default quality: {DEFAULT_QUALITY}")
    print(f"Default format: {DEFAULT_OUTPUT_FORMAT}")
    
    return True


async def generate_single_scene_with_audio(
    story_text: str,
    scene_index: int,
    total_scenes: int,
    voice: str = "default"
) -> Optional[Dict[str, Any]]:
    """
    Generate a single scene (image only) for SSE streaming
    
    Note: Audio generation is handled separately by media_gen.py team
    
    Args:
        story_text: Full story text
        scene_index: Index of this scene (0-based)
        total_scenes: Total number of scenes
        voice: Voice parameter (reserved for future audio integration)
    
    Returns:
        Dict with scene_index, image_url, scene_text
    """
    try:
        print(f"🎬 Generating scene {scene_index + 1}/{total_scenes}...")
        
        # Split story into scenes
        scenes = simple_split_story(story_text, total_scenes)
        
        if scene_index >= len(scenes):
            print(f"⚠️ Scene index {scene_index} out of range")
            return None
        
        scene_text = scenes[scene_index]
        
        # Generate image using existing function
        image_url = await generate_imagen_image(
            prompt=scene_text,
            model=DEFAULT_MODEL,
            size=DEFAULT_SIZE,
            quality=DEFAULT_QUALITY
        )
        
        result = {
            "scene_index": scene_index,
            "scene_text": scene_text,
            "image_url": image_url,
            "audio_url": "",  # Will be populated by media_gen.py team
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Scene {scene_index + 1} image completed: {image_url}")
        return result
        
    except Exception as e:
        print(f"❌ Error generating scene {scene_index}: {e}")
        return None


async def run_all_tests():
    """Run all test functions"""
    print("\n🚀 Starting Dedalus Image Generation Tests...\n")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test 1: API Configuration
    config_ok = await test_api_configuration()
    if not config_ok:
        print("\n⚠️ Please set DEDALUS_API_KEY in .env file first!")
        return
    
    # Test 2: Single image (uncomment to test)
    # await test_single_image()
    
    # Test 3: Multiple images (uncomment to test)
    await test_multiple_images()
    
    print("\n" + "=" * 60)
    print("📝 NOTE: Uncomment test functions in run_all_tests() to run actual API tests")
    print("=" * 60)
    print("\nTests to run:")
    print("  1. test_single_image() - Generate one image")
    print("  2. test_multiple_images() - Generate images from story")
    print("\n⚠️ Remember: Each API call will consume credits!")


if __name__ == "__main__":
    """Run tests when executed directly"""
    import sys
    
    # Check if dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not found. Make sure .env variables are set.")
    
    # Run tests
    asyncio.run(run_all_tests())
