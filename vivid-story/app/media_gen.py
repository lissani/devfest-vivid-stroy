"""
Audio generation for story pages (ElevenLabs TTS).
Used by main.py for parallel media generation per page.
"""
import os
import uuid
from typing import Dict
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# 1. Load your secret key from the .env file
load_dotenv()

# 2. Initialize the ElevenLabs client
client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# Voice name → ElevenLabs voice_id (for pipeline compatibility)
VOICE_IDS = {
    "default": "XJ2fW4ybq7HouelYYGcL",
}


async def generate_story_audio(text_to_speak: str, voice_id: str = "XJ2fW4ybq7HouelYYGcL"):
    """
    Turns story text into a kid-friendly mp3 file and returns the file path.
    Updated with your specific Kid Voice ID.
    """
    try:
        # Make sure the 'data' folder exists
        os.makedirs("data", exist_ok=True)
        
        # Create a unique filename for this specific story
        file_path = f"data/story_{uuid.uuid4().hex[:8]}.mp3"

        print(f"🎙️ Generating kid-friendly audio for: {text_to_speak[:40]}...")

        # 3. Generate the audio using the Multilingual v2 model for best emotion
        audio_stream = client.text_to_speech.convert(
            text=text_to_speak,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.4,       # Lower stability = more expressive for storytelling
                "similarity_boost": 0.7, # Keeps the voice sounding clear
                "style": 0.45            # Adds narrative "flair"
            }
        )

        # 4. Save the stream to a file
        with open(file_path, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)

        print(f"✅ Success! Saved to: {file_path}")
        return file_path

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def generate_audio_for_page(page: Dict, voice: str = "default") -> str:
    """
    Generate audio for a story page (pipeline API for main.py).
    Uses generate_story_audio under the hood. Returns file path or "" on failure.
    """
    page_text = page.get("text", "")
    if not page_text:
        return ""
    voice_id = VOICE_IDS.get(voice, VOICE_IDS["default"])
    path = await generate_story_audio(page_text, voice_id)
    return path or ""


# --- THIS PART RUNS THE CODE ---
# if __name__ == "__main__":
#     import asyncio
    
#     # This is the text the new kid-friendly voice will read
#     test_text = "Once upon a time, in a forest made of candy, there lived a tiny dragon who loved to bake cupcakes!"
    
#     # We use asyncio.run to start the async engine
#     asyncio.run(generate_story_audio(test_text))
    