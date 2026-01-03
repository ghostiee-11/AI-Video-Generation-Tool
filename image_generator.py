import os
import shutil
import requests
import random
import urllib.parse
import time
from gradio_client import Client
from PIL import Image

def generate_placeholder(output_path):
    """Creates a dark cinematic background if AI fails."""
    try:
        img = Image.new('RGB', (1280, 720), color=(15, 20, 40)) # Dark Blue
        img.save(output_path)
        return True
    except:
        return False

def generate_with_gradio(prompt, output_path):
    """Public HF Spaces"""
    print(f"      🔹 Flux Space...")
    try:
        client = Client("black-forest-labs/FLUX.1-schnell")
        result = client.predict(prompt, 0, True, 1280, 720, 4, api_name="/infer")
        shutil.copy(result[0], output_path)
        return True
    except:
        return False

def generate_with_pollinations(prompt, output_path):
    """Pollinations AI with Short Timeout"""
    print(f"      🔸 Pollinations...")
    encoded = urllib.parse.quote(prompt)
    seed = random.randint(1, 99999)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&model=turbo&seed={seed}"
    
    try:
        # Reduced timeout to 25s to fail faster if server is slow
        response = requests.get(url, timeout=25) 
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"         ⚠️ Pollinations Timeout: {e}")
            
    return False

def generate_images(script_data, hf_token, output_folder="assets/images"):
    if not os.path.exists(output_folder): os.makedirs(output_folder)
    image_paths = []
    print("🎨 Generating Images...")

    for index, scene in enumerate(script_data['scenes']):
        prompt = f"{scene['image_prompt']}, cinematic, 8k"
        filename = os.path.join(output_folder, f"scene_{index}.jpg")
        
        print(f"   🎬 Scene {index+1}:")

        # 1. Try Gradio
        if generate_with_gradio(prompt, filename):
            image_paths.append(filename)
            print("      ✅ Success (Flux)")
            continue

        # 2. Try Pollinations
        if generate_with_pollinations(prompt, filename):
            image_paths.append(filename)
            print("      ✅ Success (Pollinations)")
            continue

        # 3. Fallback to Placeholder (Instant)
        print("      ❌ AI Busy. Using Placeholder.")
        generate_placeholder(filename)
        image_paths.append(filename)

    return image_paths