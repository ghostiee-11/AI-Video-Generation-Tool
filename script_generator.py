import json
import os
from groq import Groq

def generate_script(article_data, api_key, language="English"):
    """
    Generates a video script in the selected language.
    """
    try:
        client = Groq(api_key=api_key)
        
        # specific instructions based on language
        if language == "Hindi":
            lang_instruction = """
            IMPORTANT: 
            1. Write the 'narration' strictly in HINDI (Devanagari script).
            2. Write the 'text_overlay' in HINDI (Devanagari script).
            3. Write the 'image_prompt' in ENGLISH (for the image generator).
            """
        else:
            lang_instruction = "Write everything in English."

        prompt = f"""
You are a senior video script writer and visual director for short-form news videos.

INPUT NEWS:
TITLE: {article_data['title']}
CONTENT: {article_data['text'][:2000]}

TASK:
Create a 30-second video script divided into exactly 4 scenes.

LANGUAGE MODE:
{language}

LANGUAGE RULES:
- If Language Mode = Hindi:
  1. Narration MUST be in pure, natural Hindi (Devanagari script).
  2. Avoid English words unless absolutely necessary.
  3. Tone should feel like a professional Hindi news explainer.
  4. Text overlay MUST be in Hindi (Devanagari).
- If Language Mode = English:
  1. Use fluent, conversational, professional English.
  2. Avoid slang.

IMPORTANT VISUAL GUIDELINES:
- image_prompt MUST ALWAYS be written in ENGLISH.
- Cinematic, ultra-realistic, high-detail visuals only.

CULTURAL & LOCATION EMPHASIS:
- India → Indian people, Indian locations, Indian environment
- Indian-Americans → Indian ethnicity + American locations
- USA / Europe → Western people & environments
- If unclear → neutral global visuals
DO NOT mix cultures incorrectly.

SCENE RULES:
- Exactly 4 scenes
- Each scene:
  - narration: 1 engaging sentence
  - image_prompt: detailed cinematic visual
  - text_overlay: 3–5 words only

JSON OUTPUT RULES (STRICT):
1. Output MUST be valid JSON only
2. Root key MUST be "scenes"
3. No markdown, no explanations, no extra text

EXPECTED JSON FORMAT:
{{
  "scenes": [
    {{
      "narration": "",
      "image_prompt": "",
      "text_overlay": ""
    }}
  ]
}}
"""



        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a JSON assistant."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            response_format={"type": "json_object"}, 
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return None