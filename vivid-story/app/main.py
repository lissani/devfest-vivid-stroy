"""
FastAPI Server - Leader
Backend API for story generation
Architecture: Sequential Reasoning → Parallel Media Generation → Result Formatter
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import asyncio
import time
import json
from datetime import datetime

app = FastAPI(title="Vivid Story API")

# Base URL of this API (for building public URLs to images/audio). Required when frontend is on another host (e.g. Streamlit Cloud).
# Render: set API_BASE_URL to your Render service URL, e.g. https://vivid-story-api.onrender.com
API_BASE_URL = (os.getenv("API_BASE_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")

# Serve generated media so the frontend (Streamlit Cloud) can load images/audio by URL
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
if os.path.isdir(DATA_DIR):
    app.mount("/api/files", StaticFiles(directory=DATA_DIR), name="files")


def _to_public_media_url(relative_path: str) -> str:
    """Convert backend-relative path (e.g. data/image_xxx.webp) to a public URL the frontend can fetch."""
    if not (relative_path or "").strip():
        return ""
    if relative_path.startswith("http://") or relative_path.startswith("https://"):
        return relative_path
    if API_BASE_URL:
        # path like "data/image_xxx.webp" -> URL path "/api/files/image_xxx.webp"
        path = relative_path.replace("data/", "", 1) if relative_path.startswith("data/") else relative_path
        return f"{API_BASE_URL}/api/files/{path}"
    return relative_path

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
    story_pages: List[Dict]  # Changed from story_text to story_pages
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


# @app.post("/api/generate-story", response_model=StoryResponse)
# async def generate_story(request: StoryRequest):
#     """
#     Core Orchestration: Story Generation Pipeline
    
#     Architecture Flow:
#     1. Step 1: Sequential Reasoning (K2 Think)
#        - Generate story pages from keyword/theme
#        - Returns list of pages: [{"page": 1, "text": "..."}, ...]
    
#     2. Logic Controller: Decide parallel execution
    
#     3. Step 2: Parallel Media Generation (per page)
#        - Image Generation (Dedalus Labs / DALL-E 3)
#        - Audio Synthesis (ElevenLabs API)
    
#     4. Result Formatter: Aggregate and return
#     """
#     start_time = time.time()
    
#     try:
#         print(f"\n{'='*60}")
#         print(f"📚 Story Generation Request")
#         print(f"{'='*60}")
#         print(f"Prompt: {request.prompt}")
#         print(f"Style: {request.style}")
#         print(f"Voice: {request.voice}")
#         print(f"Images: {request.num_images}")
#         print(f"{'='*60}\n")
        
#         # ================================================================
#         # STEP 1: Sequential Reasoning (K2 Think)
#         # ================================================================
#         print("🧠 [STEP 1] Sequential Reasoning - K2 Think")
#         print("-" * 60)
        
#         from app.ai_logic import generate_story_pages, get_full_story_text
        
#         step1_start = time.time()
#         story_pages = await generate_story_pages(request.prompt, request.style)
#         step1_duration = time.time() - step1_start
        
#         if not story_pages:
#             raise HTTPException(
#                 status_code=500,
#                 detail="Story generation failed - no pages returned"
#             )
        
#         print(f"✅ Story generated: {len(story_pages)} pages")
#         print(f"⏱️  Duration: {step1_duration:.2f}s")
#         print(f"📖 Page 1 preview: {story_pages[0].get('text', '')[:100]}...\n")
        
#         # ================================================================
#         # LOGIC CONTROLLER: Parallel Execution Decision
#         # ================================================================
#         print("🎯 [LOGIC CONTROLLER] Starting parallel media generation per page")
#         print("-" * 60)
        
#         # ================================================================
#         # STEP 2: Parallel Media Generation (per page)
#         # ================================================================
#         step2_start = time.time()
        
#         # Import both modules
#         from app.image_gen import generate_image_for_page
#         from app.media_gen import generate_audio_for_page
        
#         # Limit to requested number of images
#         pages_to_process = story_pages[:request.num_images]
        
#         print(f"🚀 Processing {len(pages_to_process)} pages in parallel...")
#         print("   Each page: [Image Gen] + [Audio Gen]\n")
        
#         # Create tasks for each page
#         async def process_page(page: Dict) -> Dict:
#             """Process single page: generate image and audio"""
#             page_num = page.get("page", 0)
#             page_text = page.get("text", "")
            
#             try:
#                 # Generate image and audio in parallel
#                 image_url, audio_url = await asyncio.gather(
#                     generate_image_for_page(page),
#                     generate_audio_for_page(page, request.voice),
#                     return_exceptions=True
#                 )
                
#                 # Handle exceptions
#                 if isinstance(image_url, Exception):
#                     print(f"⚠️  Page {page_num} image error: {image_url}")
#                     image_url = ""
                
#                 if isinstance(audio_url, Exception):
#                     print(f"⚠️  Page {page_num} audio error: {audio_url}")
#                     audio_url = ""
                
#                 return {
#                     "page": page_num,
#                     "text": page_text,
#                     "image_url": image_url,
#                     "audio_url": audio_url
#                 }
#             except Exception as e:
#                 print(f"⚠️  Page {page_num} processing error: {e}")
#                 return {
#                     "page": page_num,
#                     "text": page_text,
#                     "image_url": "",
#                     "audio_url": ""
#                 }
        
#         # Process all pages in parallel
#         processed_pages = await asyncio.gather(
#             *[process_page(page) for page in pages_to_process],
#             return_exceptions=True
#         )
        
#         # Filter out exceptions
#         processed_pages = [p for p in processed_pages if not isinstance(p, Exception)]
        
#         step2_duration = time.time() - step2_start
        
#         print(f"✅ Media generation completed")
#         print(f"⏱️  Parallel duration: {step2_duration:.2f}s\n")
        
#         # ================================================================
#         # RESULT FORMATTER: Aggregate all results
#         # ================================================================
#         print("📦 [RESULT FORMATTER] Aggregating results")
#         print("-" * 60)
        
#         total_duration = time.time() - start_time
        
#         # Build metadata
#         metadata = {
#             "total_duration": round(total_duration, 2),
#             "step1_duration": round(step1_duration, 2),
#             "step2_duration": round(step2_duration, 2),
#             "total_pages": len(story_pages),
#             "processed_pages": len(processed_pages),
#             "timestamp": datetime.now().isoformat(),
#             "request": {
#                 "prompt": request.prompt,
#                 "style": request.style,
#                 "voice": request.voice,
#                 "num_images": request.num_images
#             }
#         }
        
#         response = StoryResponse(
#             story_pages=processed_pages,
#             metadata=metadata
#         )
        
#         print(f"✅ Final response ready")
#         print(f"⏱️  Total time: {total_duration:.2f}s")
#         print(f"📊 Pages: {len(processed_pages)}")
#         print(f"{'='*60}\n")
        
#         return response
        
#     except Exception as e:
#         print(f"\n❌ Error in story generation pipeline: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stream-story")
async def stream_story(
    prompt: str,
    style: str = "fantasy",
    voice: str = "default",
    num_images: int = 4,
    use_style_consistency: bool = False,
):
    """
    SSE Streaming endpoint - yields story pages and media immediately.
    use_style_consistency=True: GPT Image 1로 마스터 스타일 프롬프트 추출 후, DALL-E 2로 페이지별 이미지 생성 (스타일 통일).
    
    Event types:
    - story: Full story pages (JSON list)
    - scene: Individual page with image + audio
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
            print(f"Use style consistency: {use_style_consistency}")
            print(f"{'='*60}\n")
            
            # ========================================================
            # STEP 1: Generate story pages with K2 Think
            # ========================================================
            print("🧠 [STEP 1] Generating story pages with K2 Think...")
            
            from app.ai_logic import generate_story_pages
            
            story_pages = await generate_story_pages(prompt, style)
            
            if not story_pages:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Story generation failed'})}\n\n"
                return
            
            print(f"✅ Story generated: {len(story_pages)} pages")
            
            # Send all story pages immediately
            yield f"data: {json.dumps({'type': 'story', 'pages': story_pages})}\n\n"
            
            # ========================================================
            # STEP 1.5 (optional): 마스터 스타일 프롬프트 추출 (GPT-Image-1 revised_prompt)
            # ========================================================
            master_prompt = None
            if use_style_consistency:
                from app.image_gen import generate_master_prompt
                print("🎨 [STEP 1.5] Establishing master style prompt (GPT Image 1)...")
                master_input = prompt
                if story_pages and story_pages[0].get("text"):
                    master_input = f"{prompt}. First scene: {story_pages[0]['text'][:200]}"
                master_prompt = await generate_master_prompt(master_input)
                if master_prompt:
                    print("✅ Master style prompt ready")
                else:
                    print("⚠️ Master prompt failed, falling back to per-page generations")
                    master_prompt = None
            
            # ========================================================
            # STEP 2: 큐 형식 — 페이지 1부터 순서대로 이미지+음성 완료 시마다 즉시 프론트로 전송
            # ========================================================
            print(f"🎨 [STEP 2] Generating media for {num_images} pages (queue: page1 → send → page2 → send ...)")
            
            from app.image_gen import generate_image_for_page
            from app.media_gen import generate_audio_for_page
            
            pages_to_process = story_pages[:num_images]
            
            for page in pages_to_process:
                page_num = page.get("page", 0)
                page_text = page.get("text", "")
                try:
                    print(f"🎬 Processing page {page_num} (image + audio)...")
                    image_url, audio_url = await asyncio.gather(
                        generate_image_for_page(page, master_prompt=master_prompt),
                        generate_audio_for_page(page, voice),
                        return_exceptions=True
                    )
                    if isinstance(image_url, Exception):
                        print(f"⚠️  Page {page_num} image error: {image_url}")
                        image_url = ""
                    if isinstance(audio_url, Exception):
                        print(f"⚠️  Page {page_num} audio error: {audio_url}")
                        audio_url = ""
                    scene_result = {
                        "scene_index": page_num - 1,
                        "page": page_num,
                        "scene_text": page_text,
                        "image_url": _to_public_media_url(image_url or ""),
                        "audio_url": _to_public_media_url(audio_url or "")
                    }
                    print(f"✅ Page {page_num} ready - sending to client")
                    yield f"data: {json.dumps({'type': 'scene', **scene_result})}\n\n"
                except Exception as e:
                    print(f"⚠️ Page {page_num} processing error: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
            # ========================================================
            # STEP 3: Send completion signal
            # ========================================================
            print("✅ All pages completed - sending finish signal")
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
