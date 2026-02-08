"""
Streamlit UI - SSE Streaming Version
Real-time story generation with Server-Sent Events (SSE)

Work Guide:
- Core SSE logic is already implemented
- Only improve UI/styles in sections marked with TODO
- Complete the UI while testing with Mock mode
"""
import streamlit as st
import requests
import json
import time
import asyncio
from typing import Optional, Dict, Any, Generator
import os
from pathlib import Path


# API server URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Mock mode toggle
USE_MOCK_DATA = True  # Set to False when backend is ready


# ============================================================================
# SSE STREAMING FUNCTIONS (Core logic - Do not modify)
# ============================================================================

def simulate_sse_streaming(prompt: str, style: str, voice: str, num_images: int) -> Generator[Dict[str, Any], None, None]:
    """
    Mock SSE streaming simulation
    Generates same events as actual backend SSE
    
    🔒 Do not modify this function
    """
    import random
    
    # 1. Send story text
    story_text = """Once upon a time, in a magical forest filled with glowing mushrooms and whispering trees, there lived a brave little robot named Bolt. Unlike other robots, Bolt had a curious heart and dreamed of adventures beyond the factory walls.

One sunny morning, Bolt ventured into the Enchanted Grove, where flowers sang melodies and butterflies sparkled like diamonds. As Bolt walked deeper into the forest, the trees began to glow with a soft, golden light, guiding the way to an ancient secret.

Hidden behind a magnificent waterfall, Bolt discovered a mysterious temple covered in vines and ancient symbols. The temple doors slowly opened, revealing a grand hall filled with treasures from forgotten times. Bolt's sensors detected something extraordinary within.

At the center of the temple, Bolt found a magical treasure chest radiating with pure energy. Inside were glowing crystals that held the power to grant wishes. Bolt carefully took one crystal, wishing for all creatures, both robot and organic, to live together in harmony. The crystal glowed brighter, and Bolt knew the wish would come true."""
    
    time.sleep(1)  # Simulate story generation time
    yield {
        "type": "story",
        "text": story_text
    }
    
    # 2. Scene data (actually generated in parallel, so order is shuffled)
    scenes = [
        {
            "scene_index": 0,
            "scene_text": "In a magical forest, a brave little robot named Bolt dreams of adventures beyond the factory walls.",
            "image_url": "data/image_20260207_165814_a188efc3_0.webp",
            "audio_url": "data/file_example_MP3_700KB.mp3"
        },
        {
            "scene_index": 1,
            "scene_text": "Bolt ventures into the Enchanted Grove where flowers sing and butterflies sparkle like diamonds.",
            "image_url": "data/image_20260207_165829_f4c83e36_1.webp",
            "audio_url": "data/file_example_MP3_700KB.mp3"
        },
        {
            "scene_index": 2,
            "scene_text": "Behind a waterfall, Bolt discovers a mysterious temple covered in ancient symbols.",
            "image_url": "data/image_20260207_165842_95969ca7_2.webp",
            "audio_url": "data/file_example_MP3_700KB.mp3"
        },
        {
            "scene_index": 3,
            "scene_text": "Inside the temple, Bolt finds magical crystals that hold the power to grant wishes.",
            "image_url": "data/image_20260207_164812_0bf65e74.webp",
            "audio_url": "data/file_example_MP3_700KB.mp3"
        }
    ]
    
    
    # 3. Send scenes one by one (actually sent as soon as completed)
    for scene in scenes[:num_images]:
        delay = random.uniform(1.5, 3.0)  # Random delay 1.5~3s
        time.sleep(delay)
        yield {
            "type": "scene",
            **scene
        }
    
    # 4. Completion signal
    time.sleep(0.5)
    yield {
        "type": "complete"
    }


def stream_from_backend(prompt: str, style: str, voice: str, num_images: int) -> Generator[Dict[str, Any], None, None]:
    """
    Receive actual backend SSE stream
    
    🔒 Do not modify this function
    """
    url = f"{API_URL}/api/stream-story"
    params = {
        "prompt": prompt,
        "style": style,
        "voice": voice,
        "num_images": num_images
    }
    
    try:
        response = requests.get(url, params=params, stream=True, timeout=120)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                if line_str.startswith('data: '):
                    data = json.loads(line_str[6:])  # Remove 'data: '
                    yield data
                    
    except requests.exceptions.ConnectionError:
        yield {
            "type": "error",
            "message": "Cannot connect to backend server. Please start the server first."
        }
    except Exception as e:
        yield {
            "type": "error",
            "message": str(e)
        }


def get_file_path(filepath: str) -> str:
    """Find file path"""
    paths_to_check = [
        filepath,
        os.path.join("..", filepath),
        os.path.join("vivid-story", filepath)
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            return path
    return filepath


# ============================================================================
# UI COMPONENTS (Feel free to modify this section!)
# ============================================================================

def render_page_header():
    """
    Render page header
    
    TODO: Design improvements
    - Change title font/color
    - Add background gradient
    - Add logo image
    """
    st.title("📚 Vivid Story Generator")
    st.markdown("### AI-powered Interactive Storybooks with Real-time Streaming")
    
    if USE_MOCK_DATA:
        st.info("🎭 **Mock Mode**: SSE streaming simulation mode")


def render_sidebar():
    """
    Render sidebar
    
    TODO: Design improvements
    - Add icons
    - Group settings
    - Style help section
    """
    with st.sidebar:
        st.header("⚙️ Settings")
        
        style = st.selectbox(
            "Story Style",
            ["fantasy", "adventure", "educational", "bedtime"],
            index=0
        )
        
        voice = st.selectbox(
            "Voice Selection",
            ["default", "child", "narrator", "storyteller"],
            index=0
        )
        
        num_images = st.slider(
            "Number of Scenes",
            min_value=2,
            max_value=4,
            value=4,
            step=1
        )
        
        st.markdown("---")
        st.markdown("#### 💡 How it Works")
        st.markdown("""
        **Real-time Streaming:**
        1. 📖 Story appears first (~8s)
        2. 🎨 Scenes appear as ready (parallel)
        3. ⚡ No waiting for all to finish!
        """)
        
        st.markdown("---")
        st.markdown("#### 🏗️ Architecture")
        st.markdown("""
        **Step 1**: K2 Think
        - Story generation
        
        **Step 2**: Parallel (SSE)
        - 🎨 Images (Dedalus)
        - 🔊 Audio (ElevenLabs)
        """)
    
    return style, voice, num_images


def render_story_input():
    """
    Render story input area
    
    TODO: Design improvements
    - Change input box style
    - Add example prompt buttons
    - Show character count limit
    """
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📝 Create Your Story")
        prompt = st.text_area(
            "What story would you like to create?",
            placeholder="Example: A brave robot exploring a magical forest",
            height=150,
            help="Enter a theme or idea for your story"
        )
        
        generate_button = st.button(
            "🎨 Generate Story",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        st.subheader("ℹ️ About")
        st.info("""
        **Real-time Generation:**
        
        Stories and scenes appear as they're created, not all at once!
        
        Powered by:
        - 🧠 K2 Think
        - 🎨 Dedalus Labs
        - 🔊 ElevenLabs
        """)
    
    return prompt, generate_button


def render_loading_placeholders(num_scenes: int):
    """
    Render loading placeholders (empty cards)
    
    TODO: Design improvements
    - Add skeleton loading animation
    - Style cards (border, shadow)
    - Improve loading text
    """
    st.markdown("### 🎨 Story Scenes")
    st.caption("Scenes will appear here as they're generated...")
    
    cols = st.columns(min(num_scenes, 4))
    placeholders = []
    
    for i in range(num_scenes):
        with cols[i % 4]:
            placeholder = st.empty()
            with placeholder.container():
                # TODO: Add skeleton loading UI here
                st.markdown(f"""
                <div style='
                    border: 2px dashed #ccc;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    min-height: 200px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                '>
                    <p style='color: #999;'>⏳ Scene {i+1}<br/>Waiting...</p>
                </div>
                """, unsafe_allow_html=True)
            placeholders.append(placeholder)
    
    return placeholders


def render_story_text(story_text: str):
    """
    Render story text
    
    TODO: Design improvements
    - Apply storybook-style font
    - Add background image/pattern
    - Adjust paragraph spacing
    - Add drop cap style for first letter
    """
    st.markdown("---")
    st.markdown("### 📖 Your Story")
    
    # TODO: Add custom styling here
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #fef3c7 0%, #fff 100%);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    '>
        <p style='
            font-size: 1.1em;
            line-height: 1.8;
            text-align: justify;
            color: #333;
        '>{story_text.replace(chr(10), '<br/><br/>')}</p>
    </div>
    """, unsafe_allow_html=True)


def render_scene_card(scene_data: Dict[str, Any], placeholder):
    """
    Render scene card
    
    TODO: Design improvements
    - Add card animation (fade-in)
    - Add image hover effect
    - Style caption
    - Customize audio player
    """
    with placeholder.container():
        # TODO: Add card design here
        
        # Image
        img_path = get_file_path(scene_data['image_url'])
        if os.path.exists(img_path):
            st.image(img_path, use_column_width=True)  # use_column_width for compatibility
        else:
            st.warning(f"Image not found: {scene_data['image_url']}")
        
        # Scene description
        st.caption(f"**Scene {scene_data['scene_index'] + 1}**")
        st.caption(scene_data['scene_text'])
        
        # Audio
        audio_path = get_file_path(scene_data['audio_url'])
        if os.path.exists(audio_path):
            with open(audio_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')


def render_progress_info(scenes_received: int, total_scenes: int, elapsed_time: float):
    """
    Display progress information
    
    TODO: Design improvements
    - Change progress bar color
    - Add animation effects
    - Style timer
    """
    progress = scenes_received / total_scenes
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("⏱️ Elapsed", f"{elapsed_time:.1f}s")
    
    with col2:
        st.metric("🎨 Scenes", f"{scenes_received}/{total_scenes}")
    
    with col3:
        status = "Complete!" if scenes_received == total_scenes else "Generating..."
        st.metric("📊 Status", status)
    
    st.progress(progress)


def render_completion_message():
    """
    Render completion message
    
    TODO: Design improvements
    - Add confetti animation
    - Group download buttons
    - Add share button
    """
    st.success("✨ Story generation complete!")
    st.balloons()  # TODO: Can change to confetti
    
    # TODO: Improve download section
    st.markdown("---")
    st.markdown("### 💾 Download")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'final_story' in st.session_state:
            st.download_button(
                label="📄 Download Story (TXT)",
                data=st.session_state.final_story,
                file_name="vivid_story.txt",
                mime="text/plain"
            )
    
    with col2:
        st.button("🔗 Share Story", disabled=True, help="Coming soon!")


# ============================================================================
# MAIN APPLICATION (Core logic - Modify carefully)
# ============================================================================

def main():
    st.set_page_config(
        page_title="Vivid Story Generator",
        page_icon="📚",
        layout="wide"
    )
    
    # TODO: Add custom CSS here
    st.markdown("""
    <style>
        /* Add global styles here */
        .stApp {
            /* background: linear-gradient(135deg, #fef3c7 0%, #fce7f3 100%); */
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Rendering
    render_page_header()
    
    # Default settings (sidebar removed)
    style = "fantasy"
    voice = "default"
    num_images = 4
    
    # TODO: Add settings to main screen if needed
    # style, voice, num_images = render_sidebar()  # Sidebar version
    
    prompt, generate_button = render_story_input()
    
    # Generate button clicked
    if generate_button:
        if not prompt:
            st.error("Please enter a story theme!")
            return
        
        # Initialize
        start_time = time.time()
        
        # Story container
        story_container = st.empty()
        
        st.markdown("---")
        
        # Progress container
        progress_container = st.empty()
        
        # Create scene placeholders
        scene_placeholders = render_loading_placeholders(num_images)
        
        # Receive SSE stream
        stream_generator = (
            simulate_sse_streaming(prompt, style, voice, num_images)
            if USE_MOCK_DATA
            else stream_from_backend(prompt, style, voice, num_images)
        )
        
        # Track state
        scenes_dict = {}
        story_text = ""
        scenes_received = 0
        
        # Process events
        for event in stream_generator:
            event_type = event.get('type')
            
            # 1. Receive story text
            if event_type == 'story':
                story_text = event['text']
                st.session_state.final_story = story_text
                
                with story_container:
                    render_story_text(story_text)
            
            # 2. Receive scene
            elif event_type == 'scene':
                scene_idx = event['scene_index']
                scenes_dict[scene_idx] = event
                scenes_received += 1
                
                # Render scene card
                render_scene_card(event, scene_placeholders[scene_idx])
                
                # Update progress
                elapsed = time.time() - start_time
                with progress_container:
                    render_progress_info(scenes_received, num_images, elapsed)
            
            # 3. Complete
            elif event_type == 'complete':
                progress_container.empty()
                render_completion_message()
                break
            
            # 4. Error
            elif event_type == 'error':
                st.error(f"❌ Error: {event['message']}")
                
                if USE_MOCK_DATA:
                    st.info("""
                    💡 Backend server is not running, using Mock mode.
                    
                    To test with real API:
                    1. `cd vivid-story`
                    2. `python app/main.py`
                    3. Set `USE_MOCK_DATA = False`
                    """)
                break
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Powered by K2 Think, Dedalus Labs, ElevenLabs | Built with FastAPI & Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
