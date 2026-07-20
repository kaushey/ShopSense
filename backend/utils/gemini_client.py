import json
import re

from google import genai
from google.genai import types

from database.config import GEMINI_API_KEY

_client = genai.Client(api_key=GEMINI_API_KEY)

# gemini-2.5-flash handles both text and multimodal (image) prompts,
# so one model covers every search type (text/video/YouTube transcripts
# and image uploads) - no separate vision model needed. It's also the
# cheapest current-generation Gemini model, which matters on a free tier.
_MODEL_NAME = "gemini-2.5-flash"

_KEYWORD_INSTRUCTION = (
    '; extract keywords related to each product described here and '
    'respond with ONLY raw JSON (no markdown, no code fences, no extra '
    'text) in exactly this shape: '
    '{"Product name 1": ["feature 1", "feature 2", "feature 3"], '
    '"Product name 2": ["feature 1", "feature 2", "feature 3"]}'
)


def ask_gemini_text(prompt: str) -> str:
    """Send a plain text prompt to Gemini and return the raw text reply."""
    response = _client.models.generate_content(
        model=_MODEL_NAME,
        contents=prompt,
    )
    return response.text


def extract_keywords_json(source_text: str) -> dict | None:
    """
    Given free text (typed search, video transcript, etc), ask Gemini to
    turn it into {product_name: [features...]} JSON and parse it.
    """
    prompt = source_text + _KEYWORD_INSTRUCTION
    raw = ask_gemini_text(prompt)
    return extract_json(raw)


def identify_product_in_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Ask Gemini's vision-capable model what product is shown in an image."""
    prompt = (
        "Identify the product(s) shown in this image. Respond with only "
        "the product name(s), no extra commentary, no markdown."
    )
    response = _client.models.generate_content(
        model=_MODEL_NAME,
        contents=[
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ],
    )
    return response.text


def extract_json(input_string: str) -> dict | None:
    """
    Parse a JSON object out of a model response, tolerating the markdown
    code fences (```json ... ```) that Gemini sometimes wraps replies in.
    """
    if not input_string:
        return None

    cleaned = input_string.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw model output was: {input_string!r}")
        return None
