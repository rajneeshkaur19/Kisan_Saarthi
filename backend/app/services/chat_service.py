import json
import os
import time
from typing import List, Optional, Tuple

try:
    from google import genai
except Exception:
    genai = None

from app.config import settings
from app.schemas import ChatRequest, ChatData, RetrievedPassage

MODEL_NAME = settings.GEMINI_MODEL or os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


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


FAQ_KB: List[dict] = [
    {
        "keys": ["kcc", "kisan credit", "credit card", "केसीसी", "किसान क्रेडिट", "ਕ੍ਰੈਡਿਟ ਕਾਰਡ", "ਕੇਸੀਸੀ"],
        "title": "Kisan Credit Card",
        "section": "Credit",
        "source": "NABARD / Bank KCC guidelines",
        "answers": {
            "en": (
                "Kisan Credit Card (KCC) gives short-term crop credit, often with interest "
                "subvention so effective rate can be around 4% for prompt repayment.\n\n"
                "What to do:\n"
                "1. Visit your bank branch or PACS with Aadhaar, land records, passbook and photos.\n"
                "2. Fill the KCC form and complete KYC.\n"
                "3. After sanction, activate the RuPay KCC card.\n\n"
                "Use Loan & Schemes in this app for a readiness score and printable checklist."
            ),
            "hi": (
                "किसान क्रेडिट कार्ड (केसीसी) अल्पकालिक फसल ऋण देता है; समय पर चुकाने पर "
                "ब्याज अनुदान से प्रभावी दर लगभग 4% हो सकती है।\n\n"
                "क्या करें:\n"
                "1. बैंक/PACS जाएँ — आधार, भूमि रिकॉर्ड, पासबुक, फोटो लेकर।\n"
                "2. केसीसी फॉर्म भरें और KYC पूरा करें।\n"
                "3. मंज़ूरी के बाद रुपे केसीसी कार्ड सक्रिय करें।\n\n"
                "इस ऐप में ऋण व योजनाएँ से स्कोर और चेकलिस्ट लें।"
            ),
            "pa": (
                "ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ (KCC) ਥੋੜ੍ਹੇ ਸਮੇਂ ਦੀ ਫਸਲ ਲੋਨ ਦਿੰਦਾ ਹੈ; ਸਮੇਂ ਸਿਰ ਵਾਪਸੀ ਤੇ "
                "ਵਿਆਜ ਰਾਹਤ ਨਾਲ ਪ੍ਰਭਾਵੀ ਦਰ ਲਗਭਗ 4% ਹੋ ਸਕਦੀ ਹੈ।\n\n"
                "ਕੀ ਕਰੋ:\n"
                "1. ਬੈਂਕ/PACS ਜਾਓ — ਆਧਾਰ, ਜ਼ਮੀਨ ਰਿਕਾਰਡ, ਪਾਸਬੁੱਕ, ਫੋਟੋ ਲੈ ਕੇ।\n"
                "2. KCC ਫਾਰਮ ਭਰੋ ਅਤੇ KYC ਪੂਰਾ ਕਰੋ।\n"
                "3. ਮਨਜ਼ੂਰੀ ਤੋਂ ਬਾਅਦ ਰੁਪੇ KCC ਕਾਰਡ ਚਾਲੂ ਕਰੋ।\n\n"
                "ਇਸ ਐਪ ਵਿੱਚ ਲੋਨ ਅਤੇ ਯੋਜਨਾਵਾਂ ਤੋਂ ਸਕੋਰ ਅਤੇ ਚੈਕਲਿਸਟ ਲਓ।"
            ),
        },
    },
    {
        "keys": ["pm-kisan", "pmkisan", "pm kisan", "सम्मान निधि", "ਸਨਮਾਨ ਨਿਧੀ", "6000"],
        "title": "PM-KISAN",
        "section": "Income Support",
        "source": "pmkisan.gov.in",
        "answers": {
            "en": (
                "PM-KISAN pays ₹6,000/year in three instalments to eligible land-owning farmer families "
                "via DBT.\n\n"
                "Usually needed: Aadhaar, land ownership records, Aadhaar-seeded bank account.\n"
                "Register/update on pmkisan.gov.in or at CSC / agriculture office, then complete e-KYC.\n\n"
                "Actual eligibility is decided by official records — this app only guides."
            ),
            "hi": (
                "पीएम-किसान पात्र भूमि-स्वामी किसान परिवारों को DBT से ₹6,000/वर्ष तीन किस्तों में देता है।\n\n"
                "आमतौर पर चाहिए: आधार, भूमि स्वामित्व, आधार-सीडेड बैंक खाता।\n"
                "pmkisan.gov.in या CSC/कृषि कार्यालय पर पंजीकरण/अपडेट कर e-KYC पूरा करें।\n\n"
                "अंतिम पात्रता सरकारी रिकॉर्ड से तय होती है — ऐप केवल मार्गदर्शन करता है।"
            ),
            "pa": (
                "ਪੀਐਮ-ਕਿਸਾਨ ਯੋਗ ਜ਼ਮੀਨ-ਮਾਲਕ ਕਿਸਾਨ ਪਰਿਵਾਰਾਂ ਨੂੰ DBT ਰਾਹੀਂ ₹6,000/ਸਾਲ ਤਿੰਨ ਕਿਸ਼ਤਾਂ ਵਿੱਚ ਦਿੰਦਾ ਹੈ।\n\n"
                "ਆਮ ਤੌਰ ਤੇ ਚਾਹੀਦਾ: ਆਧਾਰ, ਜ਼ਮੀਨ ਮਾਲਕੀ, ਆਧਾਰ-ਸੀਡਡ ਬੈਂਕ ਖਾਤਾ।\n"
                "pmkisan.gov.in ਜਾਂ CSC/ਖੇਤੀ ਦਫ਼ਤਰ ਤੇ ਰਜਿਸਟਰ/ਅੱਪਡੇਟ ਕਰਕੇ e-KYC ਪੂਰਾ ਕਰੋ।\n\n"
                "ਅਸਲ ਯੋਗਤਾ ਅਧਿਕਾਰੀ ਰਿਕਾਰਡ ਤੋਂ ਨਿਸ਼ਚਿਤ ਹੁੰਦੀ ਹੈ — ਐਪ ਸਿਰਫ਼ ਮਾਰਗਦਰਸ਼ਨ ਕਰਦੀ ਹੈ।"
            ),
        },
    },
    {
        "keys": ["pmfby", "fasal bima", "crop insurance", "बीमा", "ਬੀਮਾ", "insurance"],
        "title": "PMFBY",
        "section": "Insurance",
        "source": "pmfby.gov.in",
        "answers": {
            "en": (
                "PMFBY is crop insurance. Farmer premium is typically a small share "
                "(often ~1.5–5% depending on crop/season); rest is subsidised.\n\n"
                "Enrol before the cut-off via bank, CSC or pmfby.gov.in with Aadhaar, "
                "land/tenancy proof and bank details.\n"
                "Report crop loss within the notified window for survey."
            ),
            "hi": (
                "पीएमएफबीवाई फसल बीमा है। किसान प्रीमियम आमतौर पर छोटा हिस्सा होता है "
                "(फसल/सीजन पर ~1.5–5%); बाकी सब्सिडी।\n\n"
                "कट-ऑफ से पहले बैंक/CSC/pmfby.gov.in पर आधार, भूमि/पट्टा व बैंक विवरण से नामांकन करें।\n"
                "नुकसान की सूचना अधिसूचित समय में दें।"
            ),
            "pa": (
                "ਪੀਐਮਐਫਬੀਵਾਈ ਫਸਲ ਬੀਮਾ ਹੈ। ਕਿਸਾਨ ਪ੍ਰੀਮੀਅਮ ਆਮ ਤੌਰ ਤੇ ਛੋਟਾ ਹਿੱਸਾ ਹੁੰਦਾ ਹੈ "
                "(ਫਸਲ/ਸੀਜ਼ਨ ਤੇ ~1.5–5%); ਬਾਕੀ ਸਬਸਿਡੀ।\n\n"
                "ਕੱਟ-ਆਫ ਤੋਂ ਪਹਿਲਾਂ ਬੈਂਕ/CSC/pmfby.gov.in ਤੇ ਆਧਾਰ, ਜ਼ਮੀਨ/ਪੱਟਾ ਤੇ ਬੈਂਕ ਵੇਰਵਿਆਂ ਨਾਲ ਨਾਮਜ਼ਦਗੀ ਕਰੋ।\n"
                "ਨੁਕਸਾਨ ਦੀ ਸੂਚਨਾ ਨਿਰਧਾਰਤ ਸਮੇਂ ਵਿੱਚ ਦਿਓ।"
            ),
        },
    },
    {
        "keys": ["yellow", "rust", "disease", "leaf", "पीली", "पत्ती", "ਰੋਗ", "ਪੱਤੇ", "ਪੀਲੇ", "blight", "blast"],
        "title": "Crop leaf symptoms",
        "section": "Crop Doctor",
        "source": "KisanSaarthi Crop Doctor guidance",
        "answers": {
            "en": (
                "Yellow or spotted leaves can mean disease, nutrient stress, or water issue.\n\n"
                "Practical steps:\n"
                "1. Open Crop Doctor and upload a clear daylight photo of one leaf.\n"
                "2. Follow treatment only after a clear diagnosis — do not spray randomly.\n"
                "3. Check Weather for spray window (wind/rain).\n"
                "4. For widespread field damage, visit KVK / agri officer with a sample."
            ),
            "hi": (
                "पीली/धब्बेदार पत्तियाँ रोग, पोषक तत्व या पानी की समस्या हो सकती हैं।\n\n"
                "क्या करें:\n"
                "1. क्रॉप डॉक्टर में एक पत्ती की साफ दिन की फ़ोटो अपलोड करें।\n"
                "2. साफ निदान के बाद ही उपचार करें — अंधाधुंध छिड़काव न करें।\n"
                "3. मौसम में स्प्रे विंडो देखें।\n"
                "4. बड़े नुकसान पर नमूना लेकर KVK/कृषि अधिकारी से मिलें।"
            ),
            "pa": (
                "ਪੀਲੇ/ਧੱਬੇਦਾਰ ਪੱਤੇ ਰੋਗ, ਪੋਸ਼ਕ ਤੱਤ ਜਾਂ ਪਾਣੀ ਦੀ ਸਮੱਸਿਆ ਹੋ ਸਕਦੇ ਹਨ।\n\n"
                "ਕੀ ਕਰੋ:\n"
                "1. ਕ੍ਰੌਪ ਡਾਕਟਰ ਵਿੱਚ ਇੱਕ ਪੱਤੇ ਦੀ ਸਾਫ਼ ਦਿਨ ਦੀ ਫੋਟੋ ਅਪਲੋਡ ਕਰੋ।\n"
                "2. ਸਾਫ਼ ਨਿਦਾਨ ਤੋਂ ਬਾਅਦ ਹੀ ਇਲਾਜ ਕਰੋ — ਬਿਨਾਂ ਸੋਚੇ ਛਿੜਕਾਅ ਨਾ ਕਰੋ।\n"
                "3. ਮੌਸਮ ਵਿੱਚ ਸਪਰੇ ਵਿੰਡੋ ਵੇਖੋ।\n"
                "4. ਵੱਡੇ ਨੁਕਸਾਨ ਤੇ ਨਮੂਨਾ ਲੈ ਕੇ KVK/ਖੇਤੀ ਅਧਿਕਾਰੀ ਨੂੰ ਮਿਲੋ।"
            ),
        },
    },
    {
        "keys": ["mandi", "price", "bhav", "भाव", "ਮੰਡੀ", "ਭਾਅ", "rate", "sell", "hold"],
        "title": "Mandi prices",
        "section": "Markets",
        "source": "Agmarknet cached guidance in app",
        "answers": {
            "en": (
                "Open Mandi Prices in this app, pick your mandi and crop, then review "
                "today's modal price, MSP benchmark, trend chart and Sell/Hold hint.\n\n"
                "Prices here are guidance from cached APMC records — always confirm at the "
                "mandi before selling."
            ),
            "hi": (
                "ऐप में मंडी भाव खोलें, अपनी मंडी और फसल चुनें, फिर आज का भाव, MSP, ट्रेंड "
                "और बेचें/रुकें संकेत देखें।\n\n"
                "ये कैश किए APMC आँकड़े मार्गदर्शन हैं — बेचने से पहले मंडी में पुष्टि करें।"
            ),
            "pa": (
                "ਐਪ ਵਿੱਚ ਮੰਡੀ ਭਾਅ ਖੋਲ੍ਹੋ, ਆਪਣੀ ਮੰਡੀ ਤੇ ਫਸਲ ਚੁਣੋ, ਫਿਰ ਅੱਜ ਦਾ ਭਾਅ, MSP, ਰੁਝਾਨ "
                "ਅਤੇ ਵੇਚੋ/ਰੁਕੋ ਸੰਕੇਤ ਵੇਖੋ।\n\n"
                "ਇਹ ਕੈਸ਼ APMC ਰਿਕਾਰਡ ਮਾਰਗਦਰਸ਼ਨ ਹਨ — ਵੇਚਣ ਤੋਂ ਪਹਿਲਾਂ ਮੰਡੀ ਵਿੱਚ ਪੁਸ਼ਟੀ ਕਰੋ।"
            ),
        },
    },
    {
        "keys": ["spray", "weather", "rain", "wind", "मौसम", "ਮੌਸਮ", "ਛਿੜਕਾਅ", "छिड़काव"],
        "title": "Spray weather",
        "section": "Agromet",
        "source": "Home weather advisory",
        "answers": {
            "en": (
                "Check Home → Agromet Spray Advisory before spraying.\n"
                "Prefer calm wind, dry canopy, and no rain soon after spray. "
                "Avoid spraying in strong wind (drift) or just before heavy rain (wash-off)."
            ),
            "hi": (
                "छिड़काव से पहले होम → एग्रोमेट स्प्रे सलाह देखें।\n"
                "हल्की हवा, सूखी पत्तियाँ और छिड़काव के बाद जल्दी बारिश न हो — यही अच्छा समय है।"
            ),
            "pa": (
                "ਛਿੜਕਾਅ ਤੋਂ ਪਹਿਲਾਂ ਹੋਮ → ਐਗਰੋਮੈਟ ਸਪਰੇ ਸਲਾਹ ਵੇਖੋ।\n"
                "ਹੌਲੀ ਹਵਾ, ਸੁੱਕੇ ਪੱਤੇ ਅਤੇ ਛਿੜਕਾਅ ਤੋਂ ਤੁਰੰਤ ਬਾਅਦ ਮੀਂਹ ਨਾ ਹੋਵੇ — ਇਹ ਵਧੀਆ ਸਮਾਂ ਹੈ।"
            ),
        },
    },
]


def _normalize_lang(lang: str) -> str:
    code = (lang or "en")[:2].lower()
    return code if code in ("en", "hi", "pa") else "en"


def _match_faq(message: str) -> Optional[Tuple[dict, float]]:
    text = (message or "").lower()
    best = None
    best_score = 0.0
    for item in FAQ_KB:
        hits = sum(1 for k in item["keys"] if k.lower() in text)
        if hits == 0:
            continue
        score = min(0.95, 0.45 + 0.15 * hits)
        if score > best_score:
            best_score = score
            best = item
    return (best, best_score) if best else None


def _default_offline_answer(lang: str) -> str:
    if lang == "hi":
        return (
            "मैं किसानसारथी हूँ — फसल रोग, मंडी भाव, ऋण/योजनाएँ और स्प्रे मौसम पर मदद करता हूँ।\n\n"
            "स्पष्ट प्रश्न पूछें, जैसे केसीसी आवेदन, पीएम-किसान पात्रता, या पीली पत्तियाँ।\n"
            "लाइव AI के लिए बैकएंड `.env` में GEMINI_API_KEY जोड़ें।"
        )
    if lang == "pa":
        return (
            "ਮੈਂ ਕਿਸਾਨਸਾਰਥੀ ਹਾਂ — ਫਸਲ ਰੋਗ, ਮੰਡੀ ਭਾਅ, ਲੋਨ/ਯੋਜਨਾਵਾਂ ਅਤੇ ਸਪਰੇ ਮੌਸਮ ਬਾਰੇ ਮਦਦ ਕਰਦਾ ਹਾਂ।\n\n"
            "ਸਾਫ਼ ਸਵਾਲ ਪੁੱਛੋ, ਜਿਵੇਂ KCC ਅਰਜ਼ੀ, ਪੀਐਮ-ਕਿਸਾਨ ਯੋਗਤਾ, ਜਾਂ ਪੀਲੇ ਪੱਤੇ।\n"
            "ਲਾਈਵ AI ਲਈ ਬੈਕਐਂਡ `.env` ਵਿੱਚ GEMINI_API_KEY ਜੋੜੋ।"
        )
    return (
        "I am KisanSaarthi — I can help with crop disease, mandi prices, loans/schemes, "
        "and spray weather.\n\n"
        "Ask a clear question like KCC application, PM-KISAN eligibility, or yellow leaves.\n"
        "Add GEMINI_API_KEY in the backend `.env` for live AI answers."
    )


def _load_scheme_passages() -> List[RetrievedPassage]:
    passages: List[RetrievedPassage] = []
    schemes_path = os.path.join(settings.DATA_DIR, "schemes.json")
    try:
        with open(schemes_path, "r", encoding="utf-8") as f:
            schemes = json.load(f)
        for s in schemes:
            passages.append(
                RetrievedPassage(
                    score=0.7,
                    title=s.get("name", s.get("code", "Scheme")),
                    section=s.get("category", "Scheme"),
                    content=s.get("financial_benefit", ""),
                    source=s.get("official_portal", "schemes.json"),
                )
            )
    except Exception:
        pass
    return passages


class ChatService:
    def __init__(self):
        self.api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()
        self.client = None
        if self.api_key and genai:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                print(f"[ChatService] Could not init Gemini client: {exc}")
                self.client = None

    def _offline_response(self, req: ChatRequest) -> ChatData:
        lang = _normalize_lang(req.language)
        match = _match_faq(req.message)
        passages: List[RetrievedPassage] = []
        sources: List[str] = []

        if match:
            item, score = match
            answer = item["answers"].get(lang) or item["answers"]["en"]
            passages.append(
                RetrievedPassage(
                    score=score,
                    title=item["title"],
                    section=item["section"],
                    content=answer[:280],
                    source=item["source"],
                )
            )
            sources.append(item["source"])
            confidence = "high" if score >= 0.7 else "medium"
        else:
            answer = _default_offline_answer(lang)
            # Attach light scheme context for discovery
            passages = _load_scheme_passages()[:3]
            sources = [p.source for p in passages if p.source]
            confidence = "low"

        return ChatData(
            response=answer,
            sources=sources,
            retrieved_passages=passages,
            confidence=confidence,
            language=lang,
            is_fallback=True,
            suggestions=get_suggestions_for_language(lang),
        )

    def process_chat(self, req: ChatRequest) -> ChatData:
        lang = _normalize_lang(req.language)
        api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()

        if not api_key or not genai:
            return self._offline_response(req)

        if self.client is None:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception:
                return self._offline_response(req)

        language_names = {"en": "English", "hi": "Hindi", "pa": "Punjabi"}
        language = language_names.get(lang, "English")

        history = req.history or []
        recent_history = history[-8:]
        history_text = "\n".join(
            f"{item.get('role', 'user')}: "
            f"{str(item.get('content', item.get('message', '')))[:1500]}"
            for item in recent_history
            if isinstance(item, dict) and item.get("role") in ("user", "assistant", "model")
        )

        # Ground with offline FAQ match when available
        faq_context = ""
        match = _match_faq(req.message)
        if match:
            item, _ = match
            faq_context = item["answers"].get("en", "")[:800]

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
- Be respectful, concise, and useful to farmers.

Local reference notes (may help, verify if unsure):
{faq_context if faq_context else "None"}

Recent conversation:
{history_text if history_text else "No previous conversation."}

Current user question:
{req.message}
"""
        answer = ""
        last_error = None
        for attempt in range(1, 4):
            try:
                response = self.client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config={
                        "temperature": 0.4,
                        "max_output_tokens": 1200,
                    },
                )
                answer = (response.text or "").strip()
                if answer:
                    break
                last_error = RuntimeError("empty Gemini response")
            except Exception as exc:
                last_error = exc
                msg = str(exc)
                retryable = any(code in msg for code in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"))
                print(f"[Gemini Chat Error] attempt={attempt} {type(exc).__name__}: {exc}")
                if not retryable or attempt == 3:
                    break
                time.sleep(1.5 * attempt)
        if not answer:
            if last_error:
                print(f"[Gemini Chat] falling back offline after: {last_error}")
            return self._offline_response(req)

        passages: List[RetrievedPassage] = []
        sources: List[str] = []
        if match:
            item, score = match
            passages.append(
                RetrievedPassage(
                    score=score,
                    title=item["title"],
                    section=item["section"],
                    content=item["answers"].get("en", "")[:280],
                    source=item["source"],
                )
            )
            sources.append(item["source"])

        return ChatData(
            response=answer,
            sources=sources,
            retrieved_passages=passages,
            confidence="medium",
            language=lang,
            is_fallback=False,
            suggestions=get_suggestions_for_language(lang),
        )


_chat_service = None


def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
