import os
from typing import List

# Attempt to import Google Gemini SDK; fallback to None if unavailable
try:
    from google import genai
except Exception:
    genai = None

from backend.app.schemas import ChatRequest, ChatData, RetrievedPassage


MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def get_suggestions_for_language(lang: str) -> List[str]:
    if lang == "hi":
        return [
            "मेरी गेहूँ की पत्तियाँ पीली हो रही हैं, क्या करूँ?",
            "मंडी में फसल के सही भाव कैसे पता करें?",
            "किसान क्रेडिट कार्ड के लिए आवेदन कैसे करें?",
            "PM-KISAN योजना की पात्रता क्या है?",
        ]

    if lang == "pa":
        return [
            "ਕਣਕ ਦੇ ਪੱਤੇ ਪੀਲੇ ਹੋ ਰਹੇ ਹਨ, ਕੀ ਕਰਾਂ?",
            "ਮੰਡੀ ਵਿੱਚ ਫ਼ਸਲ ਦੇ ਅੱਜ ਦੇ ਭਾਅ ਕਿਵੇਂ ਪਤਾ ਕਰਨੇ ਹਨ?",
            "ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ ਲਈ ਅਰਜ਼ੀ ਕਿਵੇਂ ਦੇਣੀ ਹੈ?",
            "PM-KISAN ਯੋਜਨਾ ਲਈ ਯੋਗਤਾ ਕੀ ਹੈ?",
        ]

    return [
        "What should I do if my wheat leaves turn yellow?",
        "How can I check current mandi prices?",
        "How do I apply for a Kisan Credit Card?",
        "What are the PM-KISAN eligibility conditions?",
    ]


class ChatService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        if self.api_key:
            if genai:
                self.client = genai.Client(api_key=self.api_key)
            else:
                self.client = None

    def process_chat(self, req: ChatRequest) -> ChatData:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "Gemini API key is missing. "
                "Configure GEMINI_API_KEY in the backend .env file."
            )

        if self.client is None:
            if genai:
                self.client = genai.Client(api_key=api_key)
            else:
                self.client = None

        language_names = {
            "en": "English",
            "hi": "Hindi",
            "pa": "Punjabi",
        }
        language = language_names.get(req.language, "English")

        history = req.history or []
        recent_history = history[-8:]

        history_text = "\n".join(
            f"{item.get('role', 'user')}: "
            f"{str(item.get('content', item.get('message', '')))[:1500]}"
            for item in recent_history
            if isinstance(item, dict)
            and item.get("role") in ("user", "assistant", "model")
        )

        prompt = f"""
You are KisanSaarthi, a helpful agricultural assistant for farmers.

Answer the user's question in {language}.
Use simple, clear, practical language.

You can help with:
- Crop diseases, symptoms, prevention and safe treatment practices.
- Farming methods, irrigation, soil health and crop care.
- Indian agricultural schemes and Kisan Credit Card guidance.
- Mandi prices and farm financial planning.

Important accuracy and safety rules:
- Never invent current mandi prices, weather, scheme deadlines,
  eligibility decisions, or government announcements.
- You do not have verified live data unless it is explicitly
  provided in the conversation. Clearly say when current information
  needs to be checked through an official source.
- Do not claim you diagnosed a crop from an image when no image
  was provided.
- For pesticides, recommend following the product label and local
  agricultural expert guidance. Do not invent dosage instructions.
- For uncertain crop symptoms, explain that a clear image or local
  agricultural expert may be needed.
- Be respectful, concise, and useful to farmers.
- Do not claim that you searched a database or retrieved sources.

Recent conversation:
{history_text if history_text else "No previous conversation."}

Current user question:
{req.message}
"""

        # Ensure Gemini client is available; otherwise return demo response
        if not self.client:
            demo_answer = f"[Demo] Answer to your question: '{req.message}'. (Gemini integration not configured)"
            return ChatData(
                response=demo_answer,
                sources=[],
                retrieved_passages=[],
                confidence="low",
                language=req.language,
                is_fallback=True,
                suggestions=get_suggestions_for_language(req.language),
            )
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "temperature": 0.4,
                    "max_output_tokens": 1200,
                },
            )

            answer = response.text

            if not answer or not answer.strip():
                raise RuntimeError("Gemini returned an empty response.")

        except Exception as exc:
            print(f"[Gemini Chat Error] {type(exc).__name__}: {exc}")
            raise RuntimeError(
                "Gemini could not answer the question. "
                "Please check your API configuration and try again."
            ) from exc

        return ChatData(
            response=answer.strip(),
            sources=[],
            retrieved_passages=[],
            confidence="medium",
            language=req.language,
            is_fallback=False,
            suggestions=get_suggestions_for_language(req.language),
        )


_chat_service = None


def get_chat_service() -> ChatService:
    global _chat_service

    if _chat_service is None:
        _chat_service = ChatService()

    return _chat_service