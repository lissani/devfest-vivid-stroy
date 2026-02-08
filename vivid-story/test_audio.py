import os
import asyncio
from dotenv import load_dotenv
from elevenlabs.client import AsyncElevenLabs

# 1. This line tells Python to look in your .env file
load_dotenv()

async def test_my_key():
    # 2. Get the key from the vault
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("❌ Oh no! I can't find the ELEVENLABS_API_KEY in your .env file.")
        return

    # 3. Try to talk to ElevenLabs
    client = AsyncElevenLabs(api_key=api_key)
    
    try:
        # We ask for a list of voices just to see if they answer us
        voices = await client.voices.get_all()
        print(f"✅ Success! Your key works. I found {len(voices.voices)} voices in your account.")
        
        # Let's print the first voice's name as a prize
        print(f"The first voice available is: {voices.voices[0].name}")
        
    except Exception as e:
        print(f"❌ Something is wrong with the key or the connection: {e}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_my_key())
    
    
