"""
Streamlit UI - Leader & Team
Web interface for story generation
"""
import streamlit as st
import requests
from typing import Optional
import os


# API server URL
API_URL = os.getenv("API_URL", "http://localhost:8000")


def main():
    st.set_page_config(
        page_title="Vivid Story Generator",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Vivid Story Generator")
    st.markdown("### AI-powered Interactive Stories")
    
    # Sidebar - Settings
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
        
        st.markdown("---")
        st.markdown("#### 💡 How to Use")
        st.markdown("""
        1. Enter your story theme
        2. Select style and voice
        3. Click 'Generate Story'
        4. AI will create story, images, and audio
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Story Theme Input")
        prompt = st.text_area(
            "What story would you like to create?",
            placeholder="Example: A brave rabbit exploring a magical forest",
            height=150
        )
        
        generate_button = st.button("🎨 Generate Story", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("ℹ️ About")
        st.info("""
        **K2 Think** generates creative stories,
        **Gemini** enhances them with vivid details.
        
        **Imagen** creates beautiful illustrations,
        **ElevenLabs** narrates with realistic voices.
        """)
    
    # Story generation
    if generate_button:
        if not prompt:
            st.error("Please enter a story theme!")
            return
        
        with st.spinner("🎨 AI is creating your story..."):
            try:
                # API call
                response = requests.post(
                    f"{API_URL}/api/generate-story",
                    json={
                        "prompt": prompt,
                        "style": style,
                        "voice": voice
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✨ Story created successfully!")
                    
                    # Display results
                    st.markdown("---")
                    
                    # Story text
                    st.subheader("📖 Story")
                    st.write(result["story_text"])
                    
                    st.markdown("---")
                    
                    # Images
                    st.subheader("🎨 Illustrations")
                    if result["image_urls"]:
                        cols = st.columns(min(len(result["image_urls"]), 4))
                        for idx, img_url in enumerate(result["image_urls"]):
                            with cols[idx % 4]:
                                # TODO: Display actual images
                                st.image(f"https://via.placeholder.com/300x400?text=Scene+{idx+1}", 
                                        caption=f"Scene {idx+1}")
                    else:
                        st.info("Failed to generate images.")
                    
                    st.markdown("---")
                    
                    # Audio
                    st.subheader("🔊 Audio Narration")
                    if result["audio_url"]:
                        # TODO: Play actual audio file
                        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
                    else:
                        st.info("Failed to generate audio.")
                
                else:
                    st.error(f"An error occurred: {response.status_code}")
                    st.json(response.json())
            
            except requests.exceptions.ConnectionError:
                st.error("""
                ❌ Cannot connect to API server.
                
                Please make sure the backend server is running:
                ```bash
                cd app
                python main.py
                ```
                """)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Powered by K2 Think, Gemini, Imagen, ElevenLabs"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
