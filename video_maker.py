from moviepy import AudioFileClip, ImageClip, VideoFileClip, CompositeVideoClip, concatenate_videoclips, vfx, CompositeAudioClip, afx
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap
import os
import requests
import re

def download_file(url, filepath):
    try:
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
            print(f"⬇️ Downloading: {os.path.basename(filepath)}...")
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
    except Exception as e:
        print(f"⚠️ Error downloading {filepath}: {e}")

def ensure_assets_exist():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    fonts_dir = os.path.join(assets_dir, "fonts")
    music_dir = os.path.join(assets_dir, "music")
    
    os.makedirs(fonts_dir, exist_ok=True)
    os.makedirs(music_dir, exist_ok=True)
    
    font_en_path = os.path.join(fonts_dir, "NotoSans-Bold.ttf")
    download_file("https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf", font_en_path)
    
    font_hi_path = os.path.join(fonts_dir, "NotoSansDevanagari-Bold.ttf")
    download_file("https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf", font_hi_path)

    music_path = os.path.join(music_dir, "news_bgm.mp3")
    if not os.path.exists(music_path):
        download_file("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", music_path)
            
    return font_en_path, font_hi_path, music_path

def is_hindi(text):
    return bool(re.search(r'[\u0900-\u097F]', text))

def create_text_image(text, font_en, font_hi, size=(720, 560)):
    """
    Creates text overlay with strict safety margins.
    """
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Choose Font
    if is_hindi(text):
        selected_font_path = font_hi
        font_size = 25 # Slightly larger for Hindi legibility
    else:
        selected_font_path = font_en
        font_size = 25

    try:
        font = ImageFont.truetype(selected_font_path, font_size)
    except:
        font = ImageFont.load_default()

    # 2. SAFER WRAPPING (Crucial Fix)
    # Wrap at 30 chars to ensure it fits 1280px width with margins
    lines = textwrap.wrap(text, width=30)
    
    # 3. Calculate Box Dimensions
    line_height = font_size + 20
    padding_vertical = 30
    text_block_height = len(lines) * line_height
    box_height = text_block_height + (padding_vertical * 2)
    
    # 4. Position at Bottom with Safety Margin
    # Leave 50px gap from the absolute bottom of video
    box_y1 = size[1] - box_height - 50 
    box_y2 = size[1] - 50
    
    # Draw Semi-Transparent Box (Full width - 80px margins)
    # x1=40, x2=1240 ensures 40px safety margin on left/right
    draw.rectangle((40, box_y1, 1240, box_y2), fill=(0, 0, 0, 160))
    
    # 5. Draw Text Centered
    current_y = box_y1 + padding_vertical
    
    for line in lines:
        # Get width of this specific line
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        
        # Center X calculation
        x_pos = (size[0] - text_w) / 2
        
        # Draw text
        draw.text((x_pos, current_y), line, font=font, fill="white")
        current_y += line_height

    return np.array(img)

def create_video(media_paths, audio_paths, script_data, output_file="output/final_video.mp4"):
    output_file = os.path.abspath(output_file)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    font_en, font_hi, music_path = ensure_assets_exist()
    
    clips = []
    print(f"🎬 Assembling Video (Safe Text)...")

    for media_path, audio_path, scene in zip(media_paths, audio_paths, script_data['scenes']):
        if media_path is None or not os.path.exists(media_path): continue
            
        voice = AudioFileClip(audio_path)
        duration = voice.duration + 0.5
        
        # Video/Image Handling
        if media_path.endswith(".mp4"):
            visual = VideoFileClip(media_path)
            if visual.duration < duration: visual = vfx.Loop(visual, duration=duration)
            else: visual = visual.with_duration(duration)
            visual = visual.resized(height=720)
        else:
            visual = ImageClip(media_path).with_duration(duration)
            visual = visual.resized(height=800).cropped(width=1280, height=720, x_center=640, y_center=360)
            visual = visual.with_effects([vfx.Resize(lambda t: 1 + 0.04 * t)])

        # Create Text Overlay
        txt_img = create_text_image(scene['text_overlay'], font_en, font_hi, size=(1280, 720))
        txt_clip = ImageClip(txt_img).with_duration(duration)
        
        # Composite
        final_scene = CompositeVideoClip([visual, txt_clip]).with_audio(voice)
        final_scene = final_scene.with_effects([vfx.CrossFadeIn(0.5)])
        clips.append(final_scene)
        
    if not clips: return None

    final_clip = concatenate_videoclips(clips, method="compose")
    
    if os.path.exists(music_path):
        try:
            bgm = AudioFileClip(music_path)
            if bgm.duration < final_clip.duration: bgm = afx.AudioLoop(bgm, duration=final_clip.duration)
            bgm = bgm.subclipped(0, final_clip.duration).with_volume_multiplier(0.15)
            final_clip = final_clip.with_audio(CompositeAudioClip([final_clip.audio, bgm]))
        except: pass

    try:
        final_clip.write_videofile(
            output_file, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac", 
            threads=1, 
            preset="ultrafast", 
            ffmpeg_params=["-pix_fmt", "yuv420p"]
        )
        return output_file
    except Exception as e:
        print(f"❌ Write Error: {e}")
        return None