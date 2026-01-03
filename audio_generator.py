import edge_tts
import asyncio
import os

# Voice Database
VOICE_MAP = {
    "English": {
        "Male": "en-US-BrianNeural",
        "Female": "en-US-AriaNeural"
    },
    "Hindi": {
        "Male": "hi-IN-MadhurNeural", 
        "Female": "hi-IN-SwaraNeural"
    }
}

async def generate_single_voice(text, filename, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def generate_voiceover(script_data, language, gender, output_folder="assets/audio"):
    """
    Generates voiceovers based on Language AND Gender.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    audio_paths = []
    
    # Select Voice
    try:
        selected_voice = VOICE_MAP[language][gender]
    except:
        selected_voice = "en-US-BrianNeural" # Fallback
    
    # Create loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    print(f"🎙️ Generating Audio: {language} | {gender} ({selected_voice})...")
    
    for index, scene in enumerate(script_data['scenes']):
        text = scene['narration']
        filename = os.path.join(output_folder, f"voice_{index}.mp3")
        
        try:
            loop.run_until_complete(generate_single_voice(text, filename, selected_voice))
            audio_paths.append(filename)
        except Exception as e:
            print(f"   ❌ Audio Error: {e}")
            audio_paths.append(None)
            
    loop.close()
    return audio_paths