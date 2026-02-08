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
import base64


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

# Function to encode image to base64
def get_image_as_base64(path):
    if not os.path.exists(path):
        return "" # Return empty string if file does not exist
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# ============================================================================
# UI COMPONENTS (Feel free to modify this section!)
# ============================================================================

def render_loading_placeholders(num_scenes: int):
    """
    Render loading placeholders (empty cards)
    """
    st.markdown("### 🎨 Story Scenes")
    st.markdown(
    """
    <p class="scene-helper-text">
        Scenes will appear here as they're generated…
    </p>
    """,
    unsafe_allow_html=True
)

    cols = st.columns(min(num_scenes, 4))
    placeholders = []

    for i in range(num_scenes):
        with cols[i % 4]:
            placeholder = st.empty()
            with placeholder.container():
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
                    <p style='color: #333;'>⏳ Scene {i+1}<br/>Waiting...</p>
                </div>
                """, unsafe_allow_html=True)
            placeholders.append(placeholder)

    return placeholders


def render_story_text(story_text: str):
    """
    Render story text
    """
    st.markdown("---")
    st.markdown("### 📖 Your Story")

    st.markdown(f"""
    <div style='
        background-color: rgba(203, 230, 255, 0.5);
        padding: 20px;
        border-radius: 10px;
    '>
        <p style='
            font-size: 1.1em;
            line-height: 1.6;
            color: #333;
        '>{story_text.replace(chr(10), '<br/><br/>')}</p>
    </div>
    """, unsafe_allow_html=True)


def render_scene_card(scene_data: Dict[str, Any], placeholder):
    """
    Render scene card
    """
    with placeholder.container():
        img_path = get_file_path(scene_data['image_url'])
        if os.path.exists(img_path):
            st.image(img_path, width='stretch') # Set width to 'stretch' to let the image adapt to the column width.
        else:
            st.warning(f"Image not found: {scene_data['image_url']}")

        st.markdown(
    f"""
    <p class="scene-caption">
        <b>Scene {scene_data['scene_index'] + 1}</b>: {scene_data['scene_text']}
    </p>
    """,
    unsafe_allow_html=True
)


        audio_path = get_file_path(scene_data['audio_url'])
        if os.path.exists(audio_path):
            with open(audio_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')

def render_completion_message():
    """
    Render completion message
    """
    st.success("✨ Story generation complete!")
    st.balloons()
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

    # --- Pre-load and encode images ---
    about_us_bg_path = get_file_path('data/AboutUsBackgroundImg.webp')
    create_story_bg_path = get_file_path('data/CreateYourStoryBackgroundImg.webp')

    about_us_bg_base64 = get_image_as_base64(about_us_bg_path)
    create_story_bg_base64 = get_image_as_base64(create_story_bg_path)

    # --- CUSTOM CSS ---
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Palette+Mosaic&family=Patrick+Hand+SC&display=swap');

    /* ===============================
    Global App Styling
    ================================ */
    .stApp {
        background-color: #FAF4EA;
        font-family: 'Patrick Hand SC', cursive;
    }

    /* ===============================
    Title
    ================================ */
    .title h1 {
        font-family: 'Palette Mosaic', cursive;
        font-size: 5rem;
        line-height: 1.1;
        text-align: left;
        color: #333;
    }

    /* ===============================
    Image + Text Overlay Sections
    ================================ */
    .image-container {
        position: relative;
        width: 100%;
        border-radius: 15px;
        overflow: hidden;
    }

    .image-container img {
        width: 100%;
        display: block;
    }

    .text-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 30%;
        bottom: 0;
        padding: 20px;
        margin-left: 30px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .about-us-text {
        font-size: 1.25rem;
        font-family: 'Patrick Hand SC', cursive;
        color: #333;
    }

    .create-story-text {
        font-family: 'Patrick Hand SC', cursive;
        font-size: 1.5rem;
        color: #333;
    }

    /* ===============================
    Text Area (ACTUAL INPUT)
    ================================ */
    div[data-testid="stTextArea"] textarea {
        color: white !important;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #ccc;
        font-family: 'Patrick Hand SC', cursive;
        font-size: 1.1rem;
    }

    /* Label (even though hidden, keeps consistency) */
    div[data-testid="stTextArea"] label {
        color: black !important;
    }

    /* ===============================
    Generate Story Button
    ================================ */
    div[data-testid="stButton"][data-key="generate_story_button_new"] button {
        background-color: rgba(203, 230, 255, 0.5) !important;
        color: black !important;
        border-radius: 8px;
        padding: 10px 22px;
        border: none;
        font-family: 'Patrick Hand SC', cursive;
        font-size: 1.1rem;
        float: right;
    }

    /* Hover */
    div[data-testid="stButton"][data-key="generate_story_button_new"] button:hover {
        background-color: rgba(180, 210, 245, 0.75) !important;
    }

    /* Click */
    div[data-testid="stButton"][data-key="generate_story_button_new"] button:active {
        transform: scale(0.97);
    }
                
    /* ===============================
   Story Scenes Header
    ================================ */
    div[data-testid="stMarkdown"] h3 {
        color: #333 !important;
        font-family: 'Patrick Hand SC', cursive;
    }

    .scene-caption {
    color: #333;
    font-size: 0.95rem;
    margin-top: 0.5rem;
}

    .scene-helper-text {
    color: #333;
    font-size: 0.95rem;
    margin-top: -0.25rem;
    margin-bottom: 1rem;
}

    </style>
    """, unsafe_allow_html=True)



    # --- LAYOUT ---
    left_col, right_col = st.columns([1, 2])

    with left_col:
        # --- TITLE ---
        st.markdown(
            "<div class='title'><h1>Vivid<br>Story<br>Generator</h1></div>",
            unsafe_allow_html=True
        )
        st.empty() # Spacer

        # --- ABOUT US ---
        st.markdown(f"""
        <div class="image-container">
            <img src="data:image/webp;base64,{about_us_bg_base64}">
            <div class="text-overlay about-us-text">
                <p>
                    <b>About Us:</b><br>
                    Create your own storybook with visual illustrations and audio features!<br><br>
                    Powered by K2 Think, Dedalus Labs, & ElevenLabs
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        # --- CREATE YOUR STORY IMAGE AND STATIC TEXT ---
        st.markdown(f"""
        <div class="create-story-text" style="justify-content: flex-start; align-items: flex-start;">
            <p style="margin-bottom: 0;">
                <b>Create Your Story:</b><br>
                What story would you like to create?
            </p>
        </div>
        """, unsafe_allow_html=True)

        # --- INPUT FORM (visually overlaid) ---
        # Use a Streamlit container for the input box and button, positioned with CSS
        with st.container():
            st.markdown(
                """
                <style>
                    .input-button-overlap {
                        border-radius: 10px;
                        position: relative;
                        z-index: 1;
                        background-color: transparent; /* Remove background color from this container itself */
                        margin-top: -1.5rem; /* Pull up to reduce space */
                    }
                </style>
                <div class="input-button-overlap">
                """,
                unsafe_allow_html=True
            )
            prompt = st.text_area(
                label="Your Story Prompt:",
                placeholder="Example: A brave robot exploring a magical forest",
                height=100,
                label_visibility="hidden",
                key="story_prompt_input_new"
            )
            generate_button = st.button(
                "Generate Story",
                key="generate_story_button_new"
            )
            st.markdown("</div>", unsafe_allow_html=True)
        
        # --- STORY GENERATION LOGIC ---
        if generate_button:
            if not prompt:
                st.error("Please enter a story theme!")
            else:
                start_time = time.time()
                style, voice, num_images = "fantasy", "default", 4
                story_container = st.empty()
                scene_placeholders = render_loading_placeholders(num_images)
                stream_generator = (
                    simulate_sse_streaming(prompt, style, voice, num_images)
                    if USE_MOCK_DATA
                    else stream_from_backend(prompt, style, voice, num_images)
                )

                for event in stream_generator:
                    event_type = event.get('type')
                    if event_type == 'story':
                        with story_container:
                            render_story_text(event['text'])
                        st.session_state.final_story = event['text']
                    elif event_type == 'scene':
                        scene_idx = event['scene_index']
                        render_scene_card(event, scene_placeholders[scene_idx])
                    elif event_type == 'complete':
                        render_completion_message()
                        break
                    elif event_type == 'error':
                        st.error(f"❌ Error: {event['message']}")
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
