import os
import requests
import random
import urllib.parse
import time
import threading
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# GLOBAL LOCK (Pollinations still prefers serialized access)
# ============================================================

pollinations_lock = threading.Lock()

# ============================================================
# PROMPT ENGINE
# ============================================================

STYLE_PRESET = (
    "cinematic lighting, ultra realistic, shallow depth of field, "
    "35mm film still, dramatic contrast, professional photography, "
    "global illumination, sharp focus"
)

NEGATIVE_PRESET = (
    "blurry, low quality, watermark, distorted, bad anatomy, "
    "oversaturated, cartoon, illustration"
)

def build_prompt(scene_prompt, style_seed):
    return (
        f"{scene_prompt}, {STYLE_PRESET}, same visual style, style seed {style_seed}. "
        f"Negative: {NEGATIVE_PRESET}"
    )

# ============================================================
# FALLBACK PLACEHOLDER
# ============================================================

def generate_placeholder(output_path):
    try:
        img = Image.new("RGB", (1280, 720), color=(15, 20, 40))
        img.save(output_path)
        return True
    except:
        return False

# ============================================================
# IMAGE GENERATORS
# ============================================================

def generate_with_huggingface(prompt, output_path, hf_token):
    print("      🟣 HuggingFace (SDXL)")
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"         ❌ HF error: {e}")

    return False


def generate_with_cloudflare(prompt, output_path, cf_account_id, cf_api_token):
    print("      🟠 Cloudflare Workers AI")

    url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account_id}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {cf_api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "width": 1024,
        "height": 576
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            image_bytes = response.json()["result"]["image"]
            with open(output_path, "wb") as f:
                f.write(bytes(image_bytes))
            return True
    except Exception as e:
        print(f"         ❌ CF error: {e}")

    return False


def generate_with_pollinations(prompt, output_path, seed, pollinations_api_key):
    print("      🔵 Pollinations AI (Keyed)")

    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1280&height=720&seed={seed}&model=turbo"
    )

    headers = {
        "Authorization": f"Bearer {pollinations_api_key}"
    }

    # 🔒 Still serialized, but faster & safer
    with pollinations_lock:
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=60)
                if response.status_code == 200 and len(response.content) > 5000:
                    with open(output_path, "wb") as f:
                        f.write(response.content)

                    time.sleep(0.6)  # smaller cooldown with key
                    return True
            except:
                time.sleep(1.5)

        return False

# ============================================================
# AUTO-SWITCH ENGINE
# ============================================================

def generate_image(
    prompt,
    output_path,
    seed,
    hf_token=None,
    cf_account_id=None,
    cf_api_token=None,
    pollinations_api_key=None
):
    if hf_token:
        if generate_with_huggingface(prompt, output_path, hf_token):
            return "HuggingFace"

    if cf_account_id and cf_api_token:
        if generate_with_cloudflare(prompt, output_path, cf_account_id, cf_api_token):
            return "Cloudflare"

    if pollinations_api_key:
        if generate_with_pollinations(prompt, output_path, seed, pollinations_api_key):
            return "Pollinations"

    generate_placeholder(output_path)
    return "Placeholder"

# ============================================================
# MAIN ENTRY POINT
# ============================================================

def generate_images(
    script_data,
    output_folder="assets/images",
    hf_token=None,
    cf_account_id=None,
    cf_api_token=None,
    pollinations_api_key=None
):
    os.makedirs(output_folder, exist_ok=True)
    image_paths = [None] * len(script_data["scenes"])

    print("🎨 Generating Images (Key-Aware Stable Mode)")

    style_seed = random.randint(10000, 99999)

    # Threading logic
    if hf_token or cf_api_token:
        max_workers = 4
    else:
        max_workers = 2 if pollinations_api_key else 1

    def process_scene(index, scene):
        filename = os.path.join(output_folder, f"scene_{index}.jpg")
        prompt = build_prompt(scene["image_prompt"], style_seed)

        print(f"   🎬 Scene {index + 1}")
        engine = generate_image(
            prompt,
            filename,
            seed=style_seed + index,
            hf_token=hf_token,
            cf_account_id=cf_account_id,
            cf_api_token=cf_api_token,
            pollinations_api_key=pollinations_api_key
        )

        print(f"      ✅ Generated via {engine}")
        return index, filename

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_scene, i, scene)
            for i, scene in enumerate(script_data["scenes"])
        ]

        for future in as_completed(futures):
            idx, path = future.result()
            image_paths[idx] = path

    return image_paths
