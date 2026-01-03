import streamlit as st
from scraper import scrape_article
from script_generator import generate_script
from image_generator import generate_images
from audio_generator import generate_voiceover
from video_maker import create_video
from animator import animate_image
from topic_picker import get_trending_news, get_social_trends, find_news_url_for_tag

st.set_page_config(page_title="AI Video Gen", page_icon="🎬", layout="wide")
st.title("🎬 AI News Video Generator (Pro)")

# --- SESSION STATE ---
if 'selected_url' not in st.session_state:
    st.session_state.selected_url = ""
if 'selected_title' not in st.session_state:
    st.session_state.selected_title = ""

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("⚙️ Configuration")

    groq_key = st.text_input("Groq API Key", type="password")
    hf_key = st.text_input("Hugging Face Token", type="password")
    pollinations_key = st.text_input("Pollinations API Key (Optional)", type="password")

    with st.expander("☁️ Advanced (Optional)"):
        cf_account_id = st.text_input("Cloudflare Account ID")
        cf_api_token = st.text_input("Cloudflare API Token", type="password")

    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("Language", ["English", "Hindi"])
    with col2:
        gender = st.selectbox("Voice", ["Male", "Female"])

    use_ai_video = st.toggle("Enable AI Motion (SVD)", value=False)

# ============================================================
# INPUT TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(["🔥 Top News", "#️⃣ Social Hashtags", "🔗 Paste URL"])

# --- NEWS TAB ---
with tab1:
    col_region, _ = st.columns([2, 4])
    with col_region:
        news_region = st.selectbox("News Region", ["India (IN)", "USA (US)", "World"])
        region_code = "IN" if "India" in news_region else "US" if "USA" in news_region else "WORLD"

    trends = get_trending_news(region_code)
    if trends:
        st.write("### 🗞️ Top Stories:")
        for i, item in enumerate(trends):
            if st.button(f"{i+1}. {item['title']}", key=f"news_{i}", use_container_width=True):
                st.session_state.selected_url = item['link']
                st.session_state.selected_title = item['title']
                st.rerun()

# --- HASHTAG TAB ---
with tab2:
    col_social, _ = st.columns([2, 4])
    with col_social:
        social_region = st.selectbox("Social Region", ["India (IN)", "USA (US)", "World"])
        social_code = "IN" if "India" in social_region else "US" if "USA" in social_region else "WORLD"

    hashtags = get_social_trends(social_code)

    if hashtags:
        st.write("### 🔥 Trending X/Twitter Hashtags")
        cols = st.columns(2)
        for i, tag in enumerate(hashtags):
            if cols[i % 2].button(f"#{tag}", key=f"tag_{i}", use_container_width=True):
                with st.spinner(f"🔍 Finding news for {tag}..."):
                    found_url = find_news_url_for_tag(tag)
                    if found_url:
                        st.session_state.selected_url = found_url
                        st.session_state.selected_title = f"Trend: {tag}"
                        st.rerun()
                    else:
                        st.error(f"No news articles found for {tag}.")
    else:
        st.warning("Could not fetch hashtags.")

# --- URL TAB ---
with tab3:
    url_input = st.text_input("Paste Article URL")
    if st.button("Set URL"):
        if url_input:
            st.session_state.selected_url = url_input
            st.session_state.selected_title = "Custom URL"
            st.rerun()

# ============================================================
# EXECUTION
# ============================================================

st.divider()

if st.session_state.selected_url:
    st.success(f"✅ Selected: **{st.session_state.selected_title}**")
    st.caption(f"Target URL: {st.session_state.selected_url}")

    if st.button("🚀 CREATE VIDEO NOW", type="primary", use_container_width=True):

        if not groq_key:
            st.error("Please provide Groq API Key.")
            st.stop()

        status = st.status("🚀 Processing...", expanded=True)

        try:
            # 1. Scrape
            status.write("🗞️ Scraping Content...")
            article_data = scrape_article(st.session_state.selected_url)

            if not article_data:
                status.update(label="❌ Scrape Failed", state="error")
                st.stop()

            # 2. Script
            status.write(f"⚡ Writing {language} Script...")
            script_data = generate_script(article_data, groq_key, language)
            with status.expander("📜 View Script"):
                st.json(script_data)

            # 3. Audio
            status.write(f"🎙️ Generating {gender} Voice...")
            audio_paths = generate_voiceover(script_data, language, gender)

            # 4. Images (UPDATED CALL)
            status.write("🎨 Generating Images...")
            image_paths = generate_images(
                script_data,
                hf_token=hf_key or None,
                cf_account_id=cf_account_id or None,
                cf_api_token=cf_api_token or None,
                pollinations_api_key=pollinations_key or None
            )

            # 5. Animation
            final_media = image_paths
            if use_ai_video:
                status.write("🎞️ Animating (SVD)...")
                videos = []
                for img in image_paths:
                    vid = animate_image(img, hf_key) if img else None
                    videos.append(vid if vid else img)
                final_media = videos

            # 6. Assemble
            status.write("🎬 Mixing Video...")
            output = create_video(final_media, audio_paths, script_data)

            status.update(label="✅ Video Ready!", state="complete", expanded=False)
            st.balloons()
            st.video(output)

        except Exception as e:
            status.update(label="❌ Error", state="error")
            st.error(f"Error: {e}")
