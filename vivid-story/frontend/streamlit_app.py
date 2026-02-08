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
import html
from typing import Dict, Any, Generator
import os
from pathlib import Path
import base64


# API server URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Mock mode toggle
# USE_MOCK_DATA = True  # Set to False when backend is ready
USE_MOCK_DATA = False

# Config constants
NUM_SCENES = 6
STREAM_TIMEOUT = 120


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
        },
        {
            "scene_index": 4,
            "scene_text": "Bolt shares the crystals with the forest creatures, and together they celebrate under the stars.",
            "image_url": "data/image_20260207_164812_0bf65e74.webp",
            "audio_url": "data/file_example_MP3_700KB.mp3"
        },
        {
            "scene_index": 5,
            "scene_text": "With the wish of harmony granted, Bolt returns home, knowing the forest will always be a friend.",
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
        response = requests.get(url, params=params, stream=True, timeout=STREAM_TIMEOUT)

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
    """Find file path. Returns path only if it points to an existing file (not a directory)."""
    if not (filepath or "").strip():
        return ""
    paths_to_check = [
        filepath,
        os.path.join("..", filepath),
        os.path.join("vivid-story", filepath),
    ]
    for path in paths_to_check:
        if path and os.path.isfile(path):
            return path
    return filepath

# Function to encode image to base64
def get_image_as_base64(path):
    if not os.path.exists(path):
        return "" # Return empty string if file does not exist
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def _image_mime(path_or_url: str) -> str:
    """Return MIME type from file extension."""
    ext = (path_or_url or "").lower().split("?")[0]
    if ext.endswith(".webp"):
        return "image/webp"
    if ext.endswith(".png"):
        return "image/png"
    if ext.endswith(".gif"):
        return "image/gif"
    return "image/jpeg"

# ============================================================================
# UI COMPONENTS (Feel free to modify this section!)
# ============================================================================

def render_loading_placeholders(num_scenes: int):
    """
    Render loading placeholders (empty cards).
    Layout: 2 scenes per row (bigger images & text for kids). 6 scenes → 3 rows × 2 cols.
    """
    st.markdown("### 🎨 Story Scenes")
    st.markdown(
        """
    <p class="scene-helper-text">
        Scenes will appear here as they're generated…
    </p>
    """,
        unsafe_allow_html=True,
    )

    placeholders = []
    cols_per_row = 2
    num_rows = (num_scenes + cols_per_row - 1) // cols_per_row

    for row in range(num_rows):
        start = row * cols_per_row
        end = min(start + cols_per_row, num_scenes)
        cols = st.columns(cols_per_row)

        for i in range(start, end):
            with cols[i - start]:
                placeholder = st.empty()
                with placeholder.container():
                    st.markdown(
                        f"""
                    <div class="scene-card-placeholder">
                        <p style='color: #333;'>⏳ Scene {i+1}<br/>Waiting...</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                placeholders.append(placeholder)

    return placeholders



def _render_scene_card_content(scene_data: Dict[str, Any]):
    """
    Render one scene's image, caption, and audio into the current layout.
    Shared by streaming updates and by re-render when story_complete (so story doesn’t disappear on rerun).
    """
    st.markdown("<div class='scene-card'>", unsafe_allow_html=True)
    image_url = (scene_data.get('image_url') or "").strip()
    img_src = None
    if image_url.startswith(("http://", "https://")):
        img_src = image_url
    elif image_url:
        img_path = get_file_path(image_url)
        if img_path and os.path.isfile(img_path):
            b64 = get_image_as_base64(img_path)
            if b64:
                mime = _image_mime(img_path)
                img_src = f"data:{mime};base64,{b64}"
    if img_src:
        st.markdown(
            f'<div class="scene-image-wrap"><img src="{img_src}" alt="Scene" /></div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("This scene image couldn't be loaded. You can still listen to the story.")

    scene_num = scene_data['scene_index'] + 1
    scene_text_escaped = html.escape(scene_data.get('scene_text') or "")
    st.markdown(
        f"""
    <p class="scene-caption">
        <b>Scene {scene_num}</b>: {scene_text_escaped}
    </p>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption("🔊 Listen to this page")
    audio_url = (scene_data.get('audio_url') or "").strip()
    if audio_url.startswith(("http://", "https://")):
        st.audio(audio_url, format='audio/mp3')
    elif audio_url:
        audio_path = get_file_path(audio_url)
        if audio_path and os.path.isfile(audio_path):
            with open(audio_path, 'rb') as audio_file:
                st.audio(audio_file.read(), format='audio/mp3')
        else:
            st.caption("Audio not available for this scene.")
    else:
        st.caption("Audio not available for this scene.")


def render_scene_card(scene_data: Dict[str, Any], placeholder):
    """Render scene card into a placeholder (used during streaming)."""
    with placeholder.container():
        _render_scene_card_content(scene_data)

def render_completion_message():
    """
    Render completion message (no balloons so it doesn't distract from reading).
    """
    st.success("✨ Your story is ready! Read and listen to each scene below.")
    st.markdown("---")
    st.markdown("### 💾 Download")

    if 'final_story' in st.session_state:
        st.download_button(
            label="📄 Get story as text (TXT)",
            data=st.session_state.final_story,
            file_name="vivid_story.txt",
            mime="text/plain"
        )

    st.markdown("---")


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
    about_us_bg_base64 = get_image_as_base64(about_us_bg_path)

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
        color: black !important;
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

    /* Focus for accessibility */
    div[data-testid="stButton"][data-key="generate_story_button_new"] button:focus-visible,
    button:focus-visible {
        outline: 2px solid #333;
        outline-offset: 2px;
    }
                
    /* ===============================
   Story Scenes Header
    ================================ */
    div[data-testid="stMarkdown"] h3 {
        color: #333 !important;
        font-family: 'Patrick Hand SC', cursive;
    }

    /* Scene cards: bigger for kids */
    .scene-card {
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }
    /* Match placeholder size to typical image area (3:2) so layout doesn’t jump when image loads */
    .scene-card-placeholder {
        border: 2px dashed #ccc;
        border-radius: 12px;
        padding: 28px;
        text-align: center;
        width: 100%;
        aspect-ratio: 3 / 2;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        background-color: #FAF4EA;
    }
    /* Same aspect ratio for loaded images so placeholder and image slot match */
    .scene-image-wrap {
        width: 100%;
        aspect-ratio: 3 / 2;
        overflow: hidden;
        border-radius: 12px;
        background-color: #FAF4EA;
    }
    .scene-image-wrap img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .scene-caption {
        color: #333;
        font-size: 1.25rem;
        line-height: 1.5;
        margin-top: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .scene-helper-text {
        color: #333;
        font-size: 1.05rem;
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
                placeholder="e.g. A brave robot in a magical forest",
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
                if st.session_state.get("story_complete"):
                    st.session_state["story_complete"] = False
                if "scenes" in st.session_state:
                    del st.session_state["scenes"]
                start_time = time.time()
                style, voice = "fantasy", "default"
                num_images = NUM_SCENES
                st.session_state["scenes"] = [None] * num_images
                # Single story-area container so new run draws a fresh block (reduces ghosting)
                story_container = st.container()
                with story_container:
                    scene_placeholders = render_loading_placeholders(num_images)
                stream_generator = (
                    simulate_sse_streaming(prompt, style, voice, num_images)
                    if USE_MOCK_DATA
                    else stream_from_backend(prompt, style, voice, num_images)
                )

                for event in stream_generator:
                    event_type = event.get('type')
                    if event_type == 'story':
                        # Backend sends 'pages' (list of {page, text}); mock sends 'text'
                        story_text = event.get('text')
                        if story_text is None and event.get('pages'):
                            story_text = "\n\n".join(
                                p.get("text", "").strip() for p in event["pages"] if p.get("text")
                            )
                        if story_text:
                            st.session_state.final_story = story_text
                    elif event_type == 'scene':
                        scene_idx = event['scene_index']
                        st.session_state["scenes"][scene_idx] = {k: v for k, v in event.items()}
                        render_scene_card(event, scene_placeholders[scene_idx])
                    elif event_type == 'complete':
                        st.session_state["story_complete"] = True
                        render_completion_message()
                        break
                    elif event_type == 'error':
                        msg = event.get("message", "Something went wrong.")
                        st.error(f"Something went wrong. Please try again. ({msg})")
                        break

        elif st.session_state.get("story_complete"):
            # Re-render stored scenes so the story stays visible after any rerun
            scenes = st.session_state.get("scenes") or []
            st.markdown("### 🎨 Story Scenes")
            st.markdown(
                """
            <p class="scene-helper-text">
                Your story is below. Read and listen to each scene.
            </p>
            """,
                unsafe_allow_html=True,
            )
            cols_per_row = 2
            num_scenes = len(scenes)
            if num_scenes > 0:
                num_rows = (num_scenes + cols_per_row - 1) // cols_per_row
                for row in range(num_rows):
                    start = row * cols_per_row
                    end = min(start + cols_per_row, num_scenes)
                    cols = st.columns(cols_per_row)
                    for i in range(start, end):
                        with cols[i - start]:
                            if scenes[i] is not None:
                                _render_scene_card_content(scenes[i])
            render_completion_message()

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
