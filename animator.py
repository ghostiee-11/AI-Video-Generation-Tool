import os
import shutil
from gradio_client import Client

# We connect to a public Space that hosts the model
SPACE_ID = "multimodalart/stable-video-diffusion" 

def animate_image(image_path, hf_token=None, output_folder="assets/videos"):
    """
    Generates video using Gradio Client (Connects to HF Spaces).
    Robustly handles client version differences.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    filename = os.path.basename(image_path).replace(".jpg", ".mp4")
    output_path = os.path.join(output_folder, filename)
    
    # Check cache
    if os.path.exists(output_path):
        return output_path

    print(f"   🎞️ Animating {os.path.basename(image_path)} via HF Spaces...")
    
    # 1. Initialize Client (Try/Except for version compatibility)
    try:
        # Try with token (Newer versions)
        client = Client(SPACE_ID, hf_token=hf_token)
    except TypeError:
        try:
            # Try without token (Older versions or Public access)
            print("      ⚠️ Token auth not supported by this client version. Connecting anonymously...")
            client = Client(SPACE_ID)
        except Exception as e:
            print(f"      ❌ Client Init Failed: {e}")
            return None

    # 2. Generate Video
    try:
        # Predict: Send image to the Space
        result = client.predict(
            image_path, # Input Image
            0.0,        # Motion bucket id
            10,         # Frames per second
            "0",        # Seed
            api_name="/video" # The endpoint name
        )
        
        # Handle result (path vs list)
        temp_video_path = result[0] if isinstance(result, (list, tuple)) else result
        
        # Copy to assets
        shutil.copy(temp_video_path, output_path)
        print(f"      ✅ Animation Success!")
        return output_path
        
    except Exception as e:
        print(f"      ⚠️ SVD Error: {e}")
        # Detailed fallback attempt
        try:
            print("      🔄 Trying fallback space...")
            # Fallback to StabilityAI official space
            try:
                client = Client("stabilityai/stable-video-diffusion-img2img-xt", hf_token=hf_token)
            except:
                client = Client("stabilityai/stable-video-diffusion-img2img-xt")
                
            result = client.predict(image_path, "25", "25", "10", "14", api_name="/predict")
            
            temp_path = result['video'] if isinstance(result, dict) else result
            shutil.copy(temp_path, output_path)
            print("      ✅ Animation Success (Fallback)!")
            return output_path
        except:
            print("      👉 (Falling back to static zoom for this scene)")
            
    return None