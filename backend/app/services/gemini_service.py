import os
import json
import time
from typing import List, Optional, Dict, Any

# Attempt to import the real Google Gemini SDK. If unavailable, provide minimal stubs.
try:
    from google import genai
except ImportError:  # pragma: no cover
    class _DummyClient:
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "Google Gemini SDK not installed. Install 'google-generativeai' to enable Gemini features."
            )
    class _DummyGenAI:
        Client = _DummyClient
    genai = _DummyGenAI()

try:
    from google.genai import types
except ImportError:  # pragma: no cover
    # Minimal stubs for the parts we use.
    class _DummyPart:
        @staticmethod
        def from_bytes(data: bytes, mime_type: str):
            raise RuntimeError("Google Gemini SDK not installed. Cannot create Part.")

    class _DummyGenerateContentConfig:
        def __init__(self, *args, **kwargs):
            # Accept all args in demo mode.
            pass

    class types:  # type: ignore
        Part = _DummyPart
        GenerateContentConfig = _DummyGenerateContentConfig

from pydantic import BaseModel, Field

from backend.app.config import settings

MODEL_NAME = settings.GEMINI_MODEL or os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

class GeminiRequest(BaseModel):
    prompt: str
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_output_tokens: int = Field(default=1024, ge=1)
    stop_sequences: Optional[List[str]] = None

class GeminiResponse(BaseModel):
    text: str
    usage: dict = Field(default_factory=dict)
    model_version: str

    class Config:
        protected_namespaces = ()


class GeminiService:
    """Shared Gemini text and image analysis service with graceful fallbacks."""

    def __init__(self):
        self.api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip() or None
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                # SDK missing or mis-configured – we'll fall back later.
                print(f"[GeminiService] Could not initialise client: {exc}")
                self.client = None

    def _get_client(self, api_key: Optional[str] = None):
        key = (
            api_key
            or self.api_key
            or (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()
        )
        if not key:
            raise RuntimeError("GEMINI_API_KEY is missing. Configure it in backend .env.")
        # If a different key is supplied, create a fresh client.
        if api_key and api_key != self.api_key:
            return genai.Client(api_key=api_key)
        if self.client is None:
            # Attempt to create a client now; may raise if SDK is stubbed.
            self.client = genai.Client(api_key=key)
        return self.client

    def generate(self, request: GeminiRequest) -> GeminiResponse:
        """Generate a text response for the chatbot.

        Returns a deterministic demo response when the real SDK or API key is unavailable.
        """
        try:
            client = self._get_client()
        except RuntimeError as exc:
            dummy_text = "[Demo] Gemini SDK not available. This is a placeholder response."
            return GeminiResponse(text=dummy_text, usage={}, model_version=MODEL_NAME)
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=request.prompt,
                config=types.GenerateContentConfig(
                    temperature=request.temperature,
                    max_output_tokens=request.max_output_tokens,
                    stop_sequences=request.stop_sequences,
                ),
            )
            text = response.text
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            usage = {}
            metadata = getattr(response, "usage_metadata", None)
            if metadata is not None:
                usage = {
                    "prompt_token_count": getattr(metadata, "prompt_token_count", None),
                    "candidates_token_count": getattr(metadata, "candidates_token_count", None),
                    "total_token_count": getattr(metadata, "total_token_count", None),
                }
            return GeminiResponse(text=text, usage=usage, model_version=MODEL_NAME)
        except Exception as exc:
            raise RuntimeError(f"Gemini text generation failed: {exc}") from exc

    def analyze_leaf_image(
        self,
        image_bytes: bytes,
        language: str = "en",
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze a leaf photograph.

        Provides a demo fallback when the Gemini SDK or API key is missing.
        """
        if not image_bytes:
            raise ValueError("The uploaded image is empty.")
        try:
            client = self._get_client(api_key)
        except RuntimeError:
            # Caller (disease_service) supplies a richer offline demo catalog.
            raise
        mime_type = detect_image_mime(image_bytes)
        language_names = {"en": "English", "hi": "Hindi", "pa": "Punjabi"}
        output_language = language_names.get(language, "English")
        prompt = f"""
You are a cautious agricultural crop-health assistant.

Analyze the attached leaf photograph and return ONLY valid JSON.
Write all farmer-facing text in {output_language}.

Required JSON structure:
{{
  \"crop\": \"identified crop or Unknown\",
  \"disease_key\": \"short disease identifier or unknown\",
  \"disease_name\": \"possible disease or Unable to identify\",
  \"confidence_score\": 0.0,
  \"confidence_percent\": 0.0,
  \"severity\": \"low, moderate, high, or unknown\",
  \"is_inconclusive\": true,
  \"is_uncertain\": true,
  \"symptoms\": \"visible symptoms or explanation of uncertainty\",
  \"treatment_steps\": [\"practical cautious next step\"],
  \"prevention\": \"prevention guidance\",
  \"caution\": \"limitations and appropriate caution\",
  \"related_schemes\": [],
  \"mandi_crop\": \"\",
  \"top_candidates\": [
    {{\"class_key\": \"possible disease\", \"confidence\": 0.0}}
  ],
  \"model_version\": \"{MODEL_NAME}\",
  \"model_loaded\": true,
  \"source_attribution\": \"Gemini image analysis\"
}}

Rules:
- Examine only what is visible in the image.
- Do not invent symptoms, crop identity, or a disease.
- If the image is unclear, set is_inconclusive and is_uncertain to true.
- confidence_score must be between 0 and 1.
- confidence_percent = confidence_score * 100.
- Include every required JSON field.
"""
        last_error: Optional[Exception] = None
        for attempt in range(1, 4):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        prompt,
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                        max_output_tokens=1800,
                    ),
                )
                if not getattr(response, "text", None):
                    raise RuntimeError("Gemini returned no image analysis.")
                result = json.loads(response.text)
                required_fields = [
                    "crop",
                    "disease_key",
                    "disease_name",
                    "confidence_score",
                    "confidence_percent",
                    "severity",
                    "is_inconclusive",
                    "is_uncertain",
                    "symptoms",
                    "treatment_steps",
                    "caution",
                    "related_schemes",
                    "mandi_crop",
                    "top_candidates",
                    "model_version",
                    "model_loaded",
                    "source_attribution",
                ]
                missing = [f for f in required_fields if f not in result]
                if missing:
                    raise RuntimeError(f"Gemini response is missing fields: {missing}")
                score = float(result["confidence_score"])
                if not 0.0 <= score <= 1.0:
                    raise RuntimeError("Gemini returned an invalid confidence score.")
                result["confidence_score"] = score
                result["confidence_percent"] = round(score * 100, 2)
                result["model_version"] = MODEL_NAME
                result["model_loaded"] = True
                result["source_attribution"] = "Gemini image analysis"
                return result
            except (ValueError, TypeError, KeyError) as exc:
                raise RuntimeError(f"Could not parse Gemini image analysis: {exc}") from exc
            except Exception as exc:
                last_error = exc
                msg = str(exc)
                retryable = any(code in msg for code in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"))
                print(f"[Gemini Vision] attempt={attempt} {type(exc).__name__}: {exc}")
                if not retryable or attempt == 3:
                    break
                time.sleep(1.5 * attempt)
        raise RuntimeError(f"Gemini image analysis failed: {last_error}") from last_error

def detect_image_mime(image_bytes: bytes) -> str:
    """Identify supported image formats using their file signatures."""
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    raise ValueError("Unsupported or invalid image. Upload a valid JPG, PNG, or WebP file.")

_gemini_service = None

def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

def analyze_leaf_image(image_bytes: bytes, language: str = "en", api_key: Optional[str] = None) -> Dict[str, Any]:
    """Public helper used by disease_service."""
    return get_gemini_service().analyze_leaf_image(image_bytes=image_bytes, language=language, api_key=api_key)
