"""
FastAPI Server - Leader
Backend API for story generation
Architecture: Sequential Reasoning → Parallel Media Generation → Result Formatter
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import asyncio
import time
import json
from datetime import datetime

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
    """Story generation request from Streamlit Frontend"""
    prompt: str
    style: Optional[str] = "fantasy"
    voice: Optional[str] = "default"
    num_images: Optional[int] = 4


class StoryResponse(BaseModel):
    """Story generation response to Streamlit Frontend"""
    story_text: str
    image_urls: List[str]
    audio_url: str
    metadata: dict


@app.get("/")
async def root():
    """Health check"""
    return {
        "message": "Vivid Story API is running",
        "architecture": "K2 Think → Parallel(Image+Audio) → Result Formatter",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "k2_think": "ready",
            "image_generation": "ready",
            "audio_generation": "ready"
        }
    }


@app.post("/api/generate-story", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    """
    Core Orchestration: Story Generation Pipeline
    
    Architecture Flow:
    1. Step 1: Sequential Reasoning (K2 Think)
       - Generate story text from keyword/theme
       - Create scene prompts for images
    
    2. Logic Controller: Decide parallel execution
    
    3. Step 2: Parallel Media Generation
       - Image Generation (Dedalus Labs / DALL-E 3) - 4 scenes
       - Audio Synthesis (ElevenLabs API)
    
    4. Result Formatter: Aggregate and return
    """
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"📚 Story Generation Request")
        print(f"{'='*60}")
        print(f"Prompt: {request.prompt}")
        print(f"Style: {request.style}")
        print(f"Voice: {request.voice}")
        print(f"Images: {request.num_images}")
        print(f"{'='*60}\n")
        
        # ================================================================
        # STEP 1: Sequential Reasoning (K2 Think)
        # ================================================================
        print("🧠 [STEP 1] Sequential Reasoning - K2 Think")
        print("-" * 60)
        
        from app.ai_logic import generate_story_text
        
        step1_start = time.time()
        story_text = await generate_story_text(request.prompt, request.style)
        step1_duration = time.time() - step1_start
        
        if not story_text:
            raise HTTPException(
                status_code=500,
                detail="Story generation failed - no content returned"
            )
        
        print(f"✅ Story generated ({len(story_text)} chars)")
        print(f"⏱️  Duration: {step1_duration:.2f}s")
        print(f"📖 Preview: {story_text[:150]}...\n")
        
        # ================================================================
        # LOGIC CONTROLLER: Parallel Execution Decision
        # ================================================================
        print("🎯 [LOGIC CONTROLLER] Starting parallel media generation")
        print("-" * 60)
        
        # ================================================================
        # STEP 2: Parallel Media Generation
        # ================================================================
        step2_start = time.time()
        
        # Import both modules
        from app.image_gen import generate_images
        from app.media_gen import generate_audio
        
        # Execute in parallel using asyncio.gather
        print("🚀 Launching parallel tasks:")
        print("   → Image Generation (Dedalus/DALL-E)")
        print("   → Audio Synthesis (ElevenLabs)\n")
        
        results = await asyncio.gather(
            # Parallel Task 1: Image Generation
            generate_images(story_text, num_images=request.num_images),
            
            # Parallel Task 2: Audio Generation
            generate_audio(story_text, voice=request.voice),
            
            # Return exceptions instead of raising them
            return_exceptions=True
        )
        
        step2_duration = time.time() - step2_start
        
        # Extract results
        image_urls = results[0] if not isinstance(results[0], Exception) else []
        audio_url = results[1] if not isinstance(results[1], Exception) else ""
        
        # Handle partial failures
        if isinstance(results[0], Exception):
            print(f"⚠️  Image generation error: {results[0]}")
            image_urls = []
        else:
            print(f"✅ Images generated: {len(image_urls)} files")
        
        if isinstance(results[1], Exception):
            print(f"⚠️  Audio generation error: {results[1]}")
            audio_url = ""
        else:
            print(f"✅ Audio generated: {audio_url}")
        
        print(f"⏱️  Parallel duration: {step2_duration:.2f}s\n")
        
        # ================================================================
        # RESULT FORMATTER: Aggregate all results
        # ================================================================
        print("📦 [RESULT FORMATTER] Aggregating results")
        print("-" * 60)
        
        total_duration = time.time() - start_time
        
        # Build metadata
        metadata = {
            "total_duration": round(total_duration, 2),
            "step1_duration": round(step1_duration, 2),
            "step2_duration": round(step2_duration, 2),
            "story_length": len(story_text),
            "images_generated": len(image_urls),
            "audio_generated": bool(audio_url),
            "timestamp": datetime.now().isoformat(),
            "request": {
                "prompt": request.prompt,
                "style": request.style,
                "voice": request.voice,
                "num_images": request.num_images
            }
        }
        
        response = StoryResponse(
            story_text=story_text,
            image_urls=image_urls,
            audio_url=audio_url,
            metadata=metadata
        )
        
        print(f"✅ Final response ready")
        print(f"⏱️  Total time: {total_duration:.2f}s")
        print(f"📊 Story: {len(story_text)} chars")
        print(f"🖼️  Images: {len(image_urls)}")
        print(f"🔊 Audio: {'Yes' if audio_url else 'No'}")
        print(f"{'='*60}\n")
        
        return response
        
    except Exception as e:
        print(f"\n❌ Error in story generation pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stream-story")
async def stream_story(prompt: str, style: str = "fantasy", voice: str = "default", num_images: int = 4):
    """
    SSE Streaming endpoint - yields each scene immediately as it's generated
    
    Event types:
    - story: Full story text
    - scene: Individual scene with image + audio
    - complete: Generation finished
    - error: Error occurred
    """
    
    async def event_generator():
        try:
            print(f"\n{'='*60}")
            print(f"📡 SSE Stream Started")
            print(f"{'='*60}")
            print(f"Prompt: {prompt}")
            print(f"Style: {style}")
            print(f"Voice: {voice}")
            print(f"Images: {num_images}")
            print(f"{'='*60}\n")
            
            # ========================================================
            # STEP 1: Generate story text with K2 Think
            # ========================================================
            print("🧠 [STEP 1] Generating story with K2 Think...")
            
            from app.ai_logic import generate_story_text
            
            story_text = await generate_story_text(prompt, style)
            
            if not story_text:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Story generation failed'})}\n\n"
                return
            
            print(f"✅ Story generated: {len(story_text)} chars")
            
            # Send story text immediately
            yield f"data: {json.dumps({'type': 'story', 'text': story_text})}\n\n"
            
            # ========================================================
            # STEP 2: Generate scenes in parallel and yield instantly
            # ========================================================
            print(f"🎨 [STEP 2] Generating {num_images} scenes in parallel...")
            
            from app.image_gen import generate_single_scene_with_audio
            
            # Create tasks for all scenes
            tasks = []
            for scene_idx in range(num_images):
                task = generate_single_scene_with_audio(
                    story_text=story_text,
                    scene_index=scene_idx,
                    total_scenes=num_images,
                    voice=voice
                )
                tasks.append(task)
            
            # Use asyncio.as_completed to yield results as they finish
            for completed_task in asyncio.as_completed(tasks):
                try:
                    scene_result = await completed_task
                    
                    if scene_result:
                        print(f"✅ Scene {scene_result['scene_index']} ready - sending to client")
                        
                        # Send scene immediately when ready
                        yield f"data: {json.dumps({'type': 'scene', **scene_result})}\n\n"
                    
                except Exception as e:
                    print(f"⚠️ Scene generation error: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
            # ========================================================
            # STEP 3: Send completion signal
            # ========================================================
            print("✅ All scenes completed - sending finish signal")
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
            print(f"{'='*60}")
            print(f"📡 SSE Stream Completed")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
