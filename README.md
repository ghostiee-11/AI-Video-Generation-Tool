# 🎬 AI News Video Generator

An automated AI pipeline that transforms trending news topics or URLs into engaging, professional short-form videos. Built for speed, cost-efficiency, and robustness.

## 🚀 Key Features

*   **🔥 Live Trending Topics:** Automatically fetches top news from India, USA, and the World using direct RSS feeds.
*   **#️⃣ Social Pulse:** Tracks trending Twitter/X hashtags and auto-discovers relevant news articles.
*   **🧠 Intelligent Scripting:** Uses **Groq (Llama 3)** to generate viral-style video scripts (JSON structured).
*   **🗣️ Neural Voiceover:** Implements **Edge-TTS** for ultra-realistic male/female voices in English and Hindi.
*   **🎨 Cinematic Visuals:** Generates high-quality images using **Flux.1 (via Hugging Face)** with automatic fallback to Pollinations AI.
*   **🎞️ AI Motion (Beta):** Animates static images into video clips using **Stable Video Diffusion (SVD)**.
*   **🛠️ Robust Engineering:**
    *   **Smart Scraper:** Handles Google News redirects and anti-bot headers automatically.
    *   **Universal Rendering:** Auto-downloads fonts (Noto Sans) to support Hindi/English text on any server (Vercel/Linux).
    *   **Fail-Safe Pipeline:** If one AI model fails (timeout/quota), the system auto-switches to backup models or placeholders.

## 🧰 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Framework** | Streamlit (Python) |
| **LLM (Script)** | Groq API (Llama 3.3 70B) |
| **Image Gen** | Flux.1-Schnell (Hugging Face Spaces) |
| **Video Gen** | Stable Video Diffusion (SVD) |
| **Audio** | Edge-TTS (Neural) |
| **Scraping** | BeautifulSoup4 + Requests |
| **Video Editing** | MoviePy |

## 📦 Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/ai-news-video-generator.git
    cd ai-news-video-generator
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App:**
    ```bash
    python -m streamlit run app.py
    ```

## 🔑 API Keys (Free Tier Compatible)

You will need to enter these keys in the app sidebar:
1.  **Groq API Key:** [Get here](https://console.groq.com/keys)
2.  **Hugging Face Token:** [Get here](https://huggingface.co/settings/tokens)

## 📂 Project Structure

```text
.
├── app.py                  # Main UI Application
├── scraper.py              # Robust News Scraper
├── script_generator.py     # LLM Logic (Groq)
├── audio_generator.py      # TTS Logic (Edge)
├── image_generator.py      # Flux + Pollinations Fallback
├── video_maker.py          # Video Assembly & Font Management
├── animator.py             # SVD Video Generation
├── topic_picker.py         # RSS & Hashtag Fetcher
└── assets/
    ├── audio/             
    └── fonts/             
    └── images/
    └── music/
    └── video/



