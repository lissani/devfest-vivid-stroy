"""
FastAPI Server - Leader
Backend API for story generation
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Vivid Story API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StoryRequest(BaseModel):
    """Story generation request"""
    prompt: str
    style: Optional[str] = "fantasy"
    voice: Optional[str] = "default"


class StoryResponse(BaseModel):
    """Story generation response"""
    story_text: str
    image_urls: list[str]
    audio_url: str


@app.get("/")
async def root():
    """Health check"""
    return {"message": "Vivid Story API is running"}


@app.post("/api/generate-story", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    """
    Story generation endpoint
    1. Generate story with K2 Think
    2. Enhance story with Gemini
    3. Generate images with Imagen
    4. Generate audio with ElevenLabs
    """
    try:
        # TODO: Integrate AI logic and media generation
        from app.ai_logic import generate_story_text
        from app.media_gen import generate_images, generate_audio
        
        # Generate story
        story_text = await generate_story_text(request.prompt, request.style)
        
        # Generate images
        image_urls = await generate_images(story_text)
        
        # Generate audio
        audio_url = await generate_audio(story_text, request.voice)
        
        return StoryResponse(
            story_text=story_text,
            image_urls=image_urls,
            audio_url=audio_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
