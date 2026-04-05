import base64
import os
from PIL import Image
import io

def _prepare_base64_image(image_path, max_size=(1024, 768)):
    """Compress and resize image if necessary for extreme speed."""
    with Image.open(image_path) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.NEAREST) # Fast scaling
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=75)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

def process_image_gemini(api_key, image_path, prompt):
    """Processes an image using the new Google GenAI SDK."""
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=api_key)
    # Gemini handles larger images better, but we still compress for speed
    b64 = _prepare_base64_image(image_path)
    image_bytes = base64.b64decode(b64)
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
            ]
        )
        return response.text
    except Exception as e:
        return f"Error processing with Gemini: {e}"

def process_image_openai(api_key, image_path, prompt, base_url=None, model="gpt-4o"):
    """Processes an image using OpenAI SDK (works for OpenAI, OpenRouter, NVIDIA)."""
    import openai
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    base64_image = _prepare_base64_image(image_path)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                    ],
                }
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing with OpenAI ({model} at {base_url}): {e}"

def process_image_anthropic(api_key, image_path, prompt):
    """Processes an image using Claude (Anthropic)."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    base64_image = _prepare_base64_image(image_path)
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        return message.content[0].text
    except Exception as e:
        return f"Error processing with Claude: {e}"
