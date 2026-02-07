# 📚 Vivid Story Generator

AI-powered Interactive Story Generator with Images and Audio

## 🎯 Project Structure

```
vivid-story/
├── app/
│   ├── main.py          # FastAPI Server (Leader)
│   ├── ai_logic.py      # K2 Think & Gemini (Member B)
│   ├── media_gen.py     # Imagen & ElevenLabs (Member C)
├── frontend/
│   └── streamlit_app.py # UI (Leader & Team)
├── data/                # Generated audio/images temporary storage
├── .env                 # API Keys
└── requirements.txt
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Open `.env` file and configure your API keys:

- `GEMINI_API_KEY`: Google Gemini API key
- `GOOGLE_CLOUD_PROJECT`: Google Cloud project ID
- `ELEVENLABS_API_KEY`: ElevenLabs API key
- `K2_THINK_API_KEY`: K2 Think API key (optional)

### 3. Run Backend Server

```bash
cd app
python main.py
```

Server will run at `http://localhost:8000`.

### 4. Run Frontend

In a new terminal:

```bash
cd frontend
streamlit run streamlit_app.py
```

Web browser will open automatically.

## 🎨 Features

1. **Story Generation**
   - Generate creative story drafts with K2 Think
   - Enhance and refine stories with Gemini

2. **Image Generation**
   - Create beautiful illustrations with Google Imagen
   - 4 scene-based images per story

3. **Audio Generation**
   - Generate realistic narration with ElevenLabs
   - Multiple voice options available

## 📋 Team Roles

- **Leader**: FastAPI server setup, integration, UI planning
- **Member B**: AI Logic (K2 Think & Gemini)
- **Member C**: Media Generation (Imagen & ElevenLabs)

## 🔧 Development Guide

### API Endpoints

- `GET /`: Health check
- `POST /api/generate-story`: Generate story

### Request Example

```json
{
  "prompt": "A brave rabbit exploring a magical forest",
  "style": "fantasy",
  "voice": "narrator"
}
```

### Response Example

```json
{
  "story_text": "Once upon a time...",
  "image_urls": ["/data/image_1.png", "/data/image_2.png"],
  "audio_url": "/data/audio_1.mp3"
}
```

## 📝 TODO

- [ ] Complete K2 Think API integration
- [ ] Integrate Google Cloud Imagen API
- [ ] Complete ElevenLabs API integration
- [ ] Implement image storage and serving logic
- [ ] Add audio file streaming
- [ ] User history storage
- [ ] Multi-language support

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **Frontend**: Streamlit
- **AI**: K2 Think, Google Gemini, Imagen, ElevenLabs
- **Deployment**: TBD

## 📄 License

MIT License
