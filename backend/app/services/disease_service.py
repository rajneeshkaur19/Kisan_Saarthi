import hashlib
import os
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import DiagnosisAudit
from app.services.gemini_service import analyze_leaf_image


def _pick_lang(payload: Dict[str, Any], language: str) -> Any:
    if isinstance(payload, dict) and ("en" in payload or "hi" in payload or "pa" in payload):
        return payload.get(language) or payload.get("en") or next(iter(payload.values()), "")
    return payload


DEMO_CATALOG: List[Dict[str, Any]] = [
    {
        "disease_key": "tomato_early_blight",
        "crop": "Tomato",
        "disease_name": {
            "en": "Tomato Early Blight (Alternaria)",
            "hi": "टमाटर अर्ली ब्लाइट (अल्टरनेरिया)",
            "pa": "ਟਮਾਟਰ ਅਰਲੀ ਬਲਾਈਟ (ਅਲਟਰਨੇਰੀਆ)",
        },
        "confidence_score": 0.91,
        "severity": "moderate",
        "is_inconclusive": False,
        "is_uncertain": False,
        "symptoms": {
            "en": "Brown concentric target-spot lesions on older leaves, yellowing around spots, lower canopy drying first.",
            "hi": "पुरानी पत्तियों पर भूरे गोलाकार धब्बे, धब्बों के आसपास पीलापन, नीचे की पत्तियाँ पहले सूख रही हैं।",
            "pa": "ਪੁਰਾਣੇ ਪੱਤਿਆਂ ਉੱਤੇ ਭੂਰੇ ਗੋਲ ਧੱਬੇ, ਧੱਬਿਆਂ ਦੁਆਲੇ ਪੀਲਾਪਣ, ਹੇਠਲੇ ਪੱਤੇ ਪਹਿਲਾਂ ਸੁੱਕ ਰਹੇ ਹਨ।",
        },
        "treatment_steps": {
            "en": [
                "Remove and destroy heavily infected lower leaves; avoid composting them.",
                "Improve airflow — avoid overhead irrigation late evening.",
                "Spray a labelled copper or mancozeb fungicide as per local agri officer advice.",
                "Rotate tomato with non-solanaceous crops next season.",
            ],
            "hi": [
                "ज़्यादा संक्रमित नीचे की पत्तियाँ तोड़कर नष्ट करें; खाद में न डालें।",
                "हवा का संचार बढ़ाएँ — शाम को ऊपर से सिंचाई से बचें।",
                "स्थानीय कृषि अधिकारी की सलाह से कॉपर/मैंकोज़ेब कवकनाशी छिड़कें।",
                "अगले सीजन टमाटर के अलावा अन्य फसल उगाएँ।",
            ],
            "pa": [
                "ਜ਼ਿਆਦਾ ਸੰਕਰਮਿਤ ਹੇਠਲੇ ਪੱਤੇ ਤੋੜ ਕੇ ਨਸ਼ਟ ਕਰੋ; ਖਾਦ ਵਿੱਚ ਨਾ ਪਾਓ।",
                "ਹਵਾ ਦਾ ਵਹਾਅ ਵਧਾਓ — ਸ਼ਾਮ ਨੂੰ ਉੱਪਰੋਂ ਸਿੰਜਾਈ ਤੋਂ ਬਚੋ।",
                "ਸਥਾਨਕ ਖੇਤੀ ਅਧਿਕਾਰੀ ਦੀ ਸਲਾਹ ਨਾਲ ਕਾਪਰ/ਮੈਂਕੋਜ਼ੈਬ ਫੰਗੀਸਾਈਡ ਛਿੜਕੋ।",
                "ਅਗਲੇ ਸੀਜ਼ਨ ਟਮਾਟਰ ਤੋਂ ਇਲਾਵਾ ਹੋਰ ਫਸਲ ਲਗਾਓ।",
            ],
        },
        "prevention": {
            "en": "Use disease-free seedlings, mulch soil, and avoid working fields when foliage is wet.",
            "hi": "स्वस्थ पौध लगाएँ, मिट्टी पर मल्च बिछाएँ, भीगी पत्तियों पर काम न करें।",
            "pa": "ਸਿਹਤਮੰਦ ਪੌਦੇ ਲਗਾਓ, ਮਿੱਟੀ ਉੱਤੇ ਮਲਚ ਵਿਛਾਓ, ਗਿੱਲੇ ਪੱਤਿਆਂ ਉੱਤੇ ਕੰਮ ਨਾ ਕਰੋ।",
        },
        "caution": {
            "en": "Always follow pesticide label rates. Confirm with a local agriculture officer before spraying.",
            "hi": "कीटनाशक लेबल की मात्रा का पालन करें। छिड़काव से पहले स्थानीय कृषि अधिकारी से पुष्टि करें।",
            "pa": "ਕੀਟਨਾਸ਼ਕ ਲੇਬਲ ਦੀ ਮਾਤਰਾ ਮੰਨੋ। ਛਿੜਕਾਅ ਤੋਂ ਪਹਿਲਾਂ ਸਥਾਨਕ ਖੇਤੀ ਅਧਿਕਾਰੀ ਨਾਲ ਪੁਸ਼ਟੀ ਕਰੋ।",
        },
        "related_schemes": ["PMFBY", "KCC"],
        "mandi_crop": "Tomato",
        "top_candidates": [
            {"class_key": "Tomato Early Blight", "confidence": 91.0},
            {"class_key": "Tomato Late Blight", "confidence": 6.0},
            {"class_key": "Healthy", "confidence": 3.0},
        ],
    },
    {
        "disease_key": "wheat_yellow_rust",
        "crop": "Wheat",
        "disease_name": {
            "en": "Wheat Yellow Rust (Stripe Rust)",
            "hi": "गेहूँ येलो रस्ट (धारीदार रस्ट)",
            "pa": "ਕਣਕ ਯੈਲੋ ਰਸਟ (ਸਟ੍ਰਾਈਪ ਰਸਟ)",
        },
        "confidence_score": 0.88,
        "severity": "high",
        "is_inconclusive": False,
        "is_uncertain": False,
        "symptoms": {
            "en": "Yellow-orange powdery stripes along leaf veins; pustules rub off on fingers; rapid spread in cool humid weather.",
            "hi": "पत्ती की नसों के साथ पीले-नारंगी पाउडर जैसी धारियाँ; छूने पर रंग हाथ लगता है; ठंडे नम मौसम में तेज़ फैलाव।",
            "pa": "ਪੱਤੇ ਦੀਆਂ ਨਾੜੀਆਂ ਨਾਲ ਪੀਲੀਆਂ-ਸੰਤਰੀ ਧਾਰੀਆਂ; ਛੂਹਣ ਤੇ ਰੰਗ ਹੱਥ ਲੱਗਦਾ ਹੈ; ਠੰਡੇ ਨਮ ਮੌਸਮ ਵਿੱਚ ਤੇਜ਼ ਫੈਲਾਅ।",
        },
        "treatment_steps": {
            "en": [
                "Scout the whole field — yellow rust spreads fast in cool weather.",
                "If active pustules are present, consult agri officer for a labelled triazole fungicide spray.",
                "Prefer resistant wheat varieties next season (check PAU / HAU advisories).",
                "Avoid excess late nitrogen that keeps canopy too dense and humid.",
            ],
            "hi": [
                "पूरे खेत का निरीक्षण करें — ठंडे मौसम में येलो रस्ट तेज़ी से फैलता है।",
                "सक्रिय पस्ट्यूल हों तो कृषि अधिकारी से ट्रायज़ोल कवकनाशी की सलाह लें।",
                "अगले सीजन प्रतिरोधी किस्में लगाएँ (PAU/HAU सलाह देखें)।",
                "देर से ज़्यादा नाइट्रोजन न दें जिससे छतरी घनी और नम रहे।",
            ],
            "pa": [
                "ਪੂਰੇ ਖੇਤ ਦੀ ਜਾਂਚ ਕਰੋ — ਠੰਡੇ ਮੌਸਮ ਵਿੱਚ ਯੈਲੋ ਰਸਟ ਤੇਜ਼ੀ ਨਾਲ ਫੈਲਦਾ ਹੈ।",
                "ਸਰਗਰਮ ਪਸਟਿਊਲ ਹੋਣ ਤੇ ਖੇਤੀ ਅਧਿਕਾਰੀ ਤੋਂ ਟ੍ਰਾਇਜ਼ੋਲ ਫੰਗੀਸਾਈਡ ਦੀ ਸਲਾਹ ਲਓ।",
                "ਅਗਲੇ ਸੀਜ਼ਨ ਰੋਧਕ ਕਿਸਮਾਂ ਲਗਾਓ (PAU/HAU ਸਲਾਹ ਵੇਖੋ)।",
                "ਦੇਰ ਨਾਲ ਜ਼ਿਆਦਾ ਨਾਈਟ੍ਰੋਜਨ ਨਾ ਦਿਓ ਜਿਸ ਨਾਲ ਛੱਤਰੀ ਘਣੀ ਤੇ ਨਮ ਰਹੇ।",
            ],
        },
        "prevention": {
            "en": "Sow recommended rust-resistant varieties on time and monitor from tillering onward.",
            "hi": "समय पर अनुशंसित रस्ट-रोधी किस्में बोएँ और कल्ले फूटने से निगरानी रखें।",
            "pa": "ਸਮੇਂ ਸਿਰ ਰਸਟ-ਰੋਧਕ ਕਿਸਮਾਂ ਬੀਜੋ ਅਤੇ ਕੱਲੇ ਫੁੱਟਣ ਤੋਂ ਨਿਗਰਾਨੀ ਰੱਖੋ।",
        },
        "caution": {
            "en": "Do not spray during strong wind or rain. Follow PHI (pre-harvest interval) on the label.",
            "hi": "तेज़ हवा या बारिश में छिड़काव न करें। लेबल पर लिखा PHI मानें।",
            "pa": "ਤੇਜ਼ ਹਵਾ ਜਾਂ ਮੀਂਹ ਵਿੱਚ ਛਿੜਕਾਅ ਨਾ ਕਰੋ। ਲੇਬਲ ਉੱਤੇ ਲਿਖਿਆ PHI ਮੰਨੋ।",
        },
        "related_schemes": ["PMFBY", "KCC", "PM-KISAN"],
        "mandi_crop": "Wheat",
        "top_candidates": [
            {"class_key": "Wheat Yellow Rust", "confidence": 88.0},
            {"class_key": "Wheat Leaf Rust", "confidence": 8.0},
            {"class_key": "Nitrogen Deficiency", "confidence": 4.0},
        ],
    },
    {
        "disease_key": "rice_leaf_blast",
        "crop": "Rice",
        "disease_name": {
            "en": "Rice Leaf Blast",
            "hi": "धान लीफ ब्लास्ट",
            "pa": "ਝੋਨਾ ਲੀਫ ਬਲਾਸਟ",
        },
        "confidence_score": 0.86,
        "severity": "moderate",
        "is_inconclusive": False,
        "is_uncertain": False,
        "symptoms": {
            "en": "Diamond-shaped grey lesions with dark borders on leaves; tips may look scorched in humid weather.",
            "hi": "पत्तियों पर हीरे जैसे भूरे किनारे वाले धब्बे; नम मौसम में सिरे झुलसे दिख सकते हैं।",
            "pa": "ਪੱਤਿਆਂ ਉੱਤੇ ਹੀਰੇ ਵਰਗੇ ਸਲੇਟੀ ਧੱਬੇ ਕਾਲੇ ਕਿਨਾਰਿਆਂ ਨਾਲ; ਨਮ ਮੌਸਮ ਵਿੱਚ ਸਿਰੇ ਸੜੇ ਲੱਗ ਸਕਦੇ ਹਨ।",
        },
        "treatment_steps": {
            "en": [
                "Avoid excess nitrogen; keep balanced NPK.",
                "Drain standing water briefly if field is continuously flooded and blast is active.",
                "Ask agri officer about labelled tricyclazole / other blast fungicides for your district.",
                "Destroy infected stubbles after harvest.",
            ],
            "hi": [
                "नाइट्रोजन ज़्यादा न दें; संतुलित NPK रखें।",
                "खेत लगातार भरा हो और ब्लास्ट सक्रिय हो तो थोड़ी देर पानी निकालें।",
                "अपने जिले के लिए ट्राइसाइक्लाज़ोल आदि कवकनाशी की कृषि अधिकारी से पूछें।",
                "कटाई के बाद संक्रमित ठूंठ नष्ट करें।",
            ],
            "pa": [
                "ਨਾਈਟ੍ਰੋਜਨ ਜ਼ਿਆਦਾ ਨਾ ਦਿਓ; ਸੰਤੁਲਿਤ NPK ਰੱਖੋ।",
                "ਖੇਤ ਲਗਾਤਾਰ ਭਰਿਆ ਹੋਵੇ ਤੇ ਬਲਾਸਟ ਸਰਗਰਮ ਹੋਵੇ ਤਾਂ ਥੋੜ੍ਹੀ ਦੇਰ ਪਾਣੀ ਕੱਢੋ।",
                "ਆਪਣੇ ਜ਼ਿਲ੍ਹੇ ਲਈ ਟ੍ਰਾਈਸਾਈਕਲਾਜ਼ੋਲ ਆਦਿ ਫੰਗੀਸਾਈਡ ਬਾਰੇ ਖੇਤੀ ਅਧਿਕਾਰੀ ਤੋਂ ਪੁੱਛੋ।",
                "ਕਟਾਈ ਤੋਂ ਬਾਅਦ ਸੰਕਰਮਿਤ ਠੂਠ ਨਸ਼ਟ ਕਰੋ।",
            ],
        },
        "prevention": {
            "en": "Use resistant varieties, avoid dense planting, and follow seed treatment advisories.",
            "hi": "प्रतिरोधी किस्में लगाएँ, घनी बुवाई से बचें, बीज उपचार सलाह मानें।",
            "pa": "ਰੋਧਕ ਕਿਸਮਾਂ ਲਗਾਓ, ਘਣੀ ਬਿਜਾਈ ਤੋਂ ਬਚੋ, ਬੀਜ ਇਲਾਜ ਸਲਾਹ ਮੰਨੋ।",
        },
        "caution": {
            "en": "Blast can look similar to other leaf spots — confirm locally before repeated sprays.",
            "hi": "ब्लास्ट अन्य पत्ती धब्बों जैसा लग सकता है — बार-बार छिड़काव से पहले स्थानीय पुष्टि करें।",
            "pa": "ਬਲਾਸਟ ਹੋਰ ਪੱਤਾ ਧੱਬਿਆਂ ਵਰਗਾ ਲੱਗ ਸਕਦਾ ਹੈ — ਵਾਰ-ਵਾਰ ਛਿੜਕਾਅ ਤੋਂ ਪਹਿਲਾਂ ਸਥਾਨਕ ਪੁਸ਼ਟੀ ਕਰੋ।",
        },
        "related_schemes": ["PMFBY", "KCC"],
        "mandi_crop": "Paddy",
        "top_candidates": [
            {"class_key": "Rice Leaf Blast", "confidence": 86.0},
            {"class_key": "Brown Spot", "confidence": 9.0},
            {"class_key": "Healthy", "confidence": 5.0},
        ],
    },
    {
        "disease_key": "tomato_healthy",
        "crop": "Tomato",
        "disease_name": {
            "en": "Healthy Tomato Leaf",
            "hi": "स्वस्थ टमाटर पत्ती",
            "pa": "ਸਿਹਤਮੰਦ ਟਮਾਟਰ ਪੱਤਾ",
        },
        "confidence_score": 0.84,
        "severity": "low",
        "is_inconclusive": False,
        "is_uncertain": False,
        "symptoms": {
            "en": "No clear disease lesions visible. Leaf colour and edges look healthy.",
            "hi": "कोई स्पष्ट रोग धब्बा नहीं दिख रहा। पत्ती का रंग और किनारे स्वस्थ लगते हैं।",
            "pa": "ਕੋਈ ਸਪੱਸ਼ਟ ਰੋਗ ਧੱਬਾ ਨਹੀਂ ਦਿਖ ਰਿਹਾ। ਪੱਤੇ ਦਾ ਰੰਗ ਤੇ ਕਿਨਾਰੇ ਸਿਹਤਮੰਦ ਲੱਗਦੇ ਹਨ।",
        },
        "treatment_steps": {
            "en": [
                "Continue regular scouting once a week.",
                "Maintain balanced irrigation — avoid water stress and waterlogging.",
                "Keep field weed-free to reduce pest host plants.",
            ],
            "hi": [
                "सप्ताह में एक बार नियमित निरीक्षण जारी रखें।",
                "संतुलित सिंचाई रखें — सूखा और जलभराव दोनों से बचें।",
                "खरपतवार साफ रखें ताकि कीट आश्रय न मिलें।",
            ],
            "pa": [
                "ਹਫ਼ਤੇ ਵਿੱਚ ਇੱਕ ਵਾਰ ਨਿਯਮਿਤ ਜਾਂਚ ਜਾਰੀ ਰੱਖੋ।",
                "ਸੰਤੁਲਿਤ ਸਿੰਜਾਈ ਰੱਖੋ — ਸੁੱਕ ਅਤੇ ਪਾਣੀ ਭਰਨ ਤੋਂ ਬਚੋ।",
                "ਨਦੀਨ ਸਾਫ਼ ਰੱਖੋ ਤਾਂ ਜੋ ਕੀੜਿਆਂ ਨੂੰ ਆਸਰਾ ਨਾ ਮਿਲੇ।",
            ],
        },
        "prevention": {
            "en": "Follow crop calendar sprays only when pests/diseases are observed or advisory recommends.",
            "hi": "कीट/रोग दिखने या सलाह होने पर ही छिड़काव करें।",
            "pa": "ਕੀੜੇ/ਰੋਗ ਦਿਖਣ ਜਾਂ ਸਲਾਹ ਹੋਣ ਤੇ ਹੀ ਛਿੜਕਾਅ ਕਰੋ।",
        },
        "caution": {
            "en": "Healthy today does not mean risk-free — monitor after rain or dew nights.",
            "hi": "आज स्वस्थ होने का मतलब जोखिम खत्म नहीं — बारिश/ओस के बाद निगरानी रखें।",
            "pa": "ਅੱਜ ਸਿਹਤਮੰਦ ਹੋਣ ਦਾ ਮਤਲਬ ਖਤਰਾ ਖਤਮ ਨਹੀਂ — ਮੀਂਹ/ਔਸ ਤੋਂ ਬਾਅਦ ਨਿਗਰਾਨੀ ਰੱਖੋ।",
        },
        "related_schemes": ["PM-KISAN", "KCC"],
        "mandi_crop": "Tomato",
        "top_candidates": [
            {"class_key": "Healthy", "confidence": 84.0},
            {"class_key": "Early Nutrient Stress", "confidence": 10.0},
            {"class_key": "Early Blight", "confidence": 6.0},
        ],
    },
    {
        "disease_key": "unclear_sample",
        "crop": "Unknown",
        "disease_name": {
            "en": "Unable to identify confidently",
            "hi": "विश्वास के साथ पहचान संभव नहीं",
            "pa": "ਭਰੋਸੇ ਨਾਲ ਪਛਾਣ ਸੰਭਵ ਨਹੀਂ",
        },
        "confidence_score": 0.32,
        "severity": "unknown",
        "is_inconclusive": True,
        "is_uncertain": True,
        "symptoms": {
            "en": "Image is blurry, dark, or does not clearly show a single leaf surface. Guessing would be unsafe.",
            "hi": "फ़ोटो धुंधली/अँधेरी है या एक पत्ती साफ नहीं दिख रही। अनुमान लगाना सुरक्षित नहीं।",
            "pa": "ਫੋਟੋ ਧੁੰਦਲੀ/ਹਨੇਰੀ ਹੈ ਜਾਂ ਇੱਕ ਪੱਤਾ ਸਾਫ਼ ਨਹੀਂ ਦਿਖ ਰਿਹਾ। ਅਨੁਮਾਨ ਲਗਾਉਣਾ ਸੁਰੱਖਿਅਤ ਨਹੀਂ।",
        },
        "treatment_steps": {
            "en": [
                "Retake photo in daylight, leaf filling most of the frame.",
                "Wipe camera lens; avoid motion blur.",
                "If symptoms persist, visit nearest Krishi Vigyan Kendra / agri officer with a fresh sample.",
            ],
            "hi": [
                "दिन की रोशनी में दोबारा फ़ोटो लें, पत्ती फ्रेम का ज़्यादा हिस्सा भरे।",
                "कैमरा लेंस साफ करें; हिलाकर न खींचें।",
                "लक्षण बने रहें तो ताज़ा नमूना लेकर नज़दीकी कृषि विज्ञान केंद्र / अधिकारी से मिलें।",
            ],
            "pa": [
                "ਦਿਨ ਦੀ ਰੋਸ਼ਨੀ ਵਿੱਚ ਦੁਬਾਰਾ ਫੋਟੋ ਲਓ, ਪੱਤਾ ਫਰੇਮ ਦਾ ਜ਼ਿਆਦਾ ਹਿੱਸਾ ਭਰੇ।",
                "ਕੈਮਰਾ ਲੈਂਸ ਸਾਫ਼ ਕਰੋ; ਹਿਲਾ ਕੇ ਨਾ ਖਿੱਚੋ।",
                "ਲੱਛਣ ਰਹਿਣ ਤੇ ਤਾਜ਼ਾ ਨਮੂਨਾ ਲੈ ਕੇ ਨਜ਼ਦੀਕੀ ਕ੍ਰਿਸ਼ੀ ਵਿਗਿਆਨ ਕੇਂਦਰ / ਅਧਿਕਾਰੀ ਨੂੰ ਮਿਲੋ।",
            ],
        },
        "prevention": None,
        "caution": {
            "en": "KisanSaarthi will not invent a disease name from an unclear photo.",
            "hi": "अस्पष्ट फ़ोटो से किसानसारथी रोग का नाम नहीं गढ़ेगा।",
            "pa": "ਅਸਪਸ਼ਟ ਫੋਟੋ ਤੋਂ ਕਿਸਾਨਸਾਰਥੀ ਰੋਗ ਦਾ ਨਾਮ ਨਹੀਂ ਘੜੇਗਾ।",
        },
        "related_schemes": [],
        "mandi_crop": "",
        "top_candidates": [
            {"class_key": "Unclear / Low Confidence", "confidence": 70.0},
            {"class_key": "Possible Leaf Spot", "confidence": 20.0},
            {"class_key": "Healthy", "confidence": 10.0},
        ],
    },
]


def _localize_demo(entry: Dict[str, Any], language: str) -> Dict[str, Any]:
    lang = (language or "en")[:2].lower()
    if lang not in ("en", "hi", "pa"):
        lang = "en"

    score = float(entry["confidence_score"])
    return {
        "disease_key": entry["disease_key"],
        "disease_name": _pick_lang(entry["disease_name"], lang),
        "crop": entry["crop"],
        "confidence_score": score,
        "confidence_percent": round(score * 100, 2),
        "severity": entry["severity"],
        "is_inconclusive": entry["is_inconclusive"],
        "is_uncertain": entry["is_uncertain"],
        "symptoms": _pick_lang(entry["symptoms"], lang),
        "treatment_steps": _pick_lang(entry["treatment_steps"], lang),
        "prevention": _pick_lang(entry["prevention"], lang) if entry.get("prevention") else None,
        "caution": _pick_lang(entry["caution"], lang),
        "related_schemes": entry["related_schemes"],
        "mandi_crop": entry["mandi_crop"],
        "top_candidates": entry["top_candidates"],
        "model_version": "demo-leaf-v1",
        "model_loaded": False,
        "source_attribution": "Offline demo diagnosis (add GEMINI_API_KEY for live AI analysis)",
        "demo_mode": True,
    }


# MD5 fingerprints of frontend/public/samples/*.jpg so sample demos map correctly.
SAMPLE_FINGERPRINTS = {
    "e3fe40f25548da98e700586c545c09f2": "tomato_early_blight",
    "04d860a1df7de933d709d6cfab80f585": "wheat_yellow_rust",
    "5b8028c7e20a79ae0741e4d4978a14c7": "rice_leaf_blast",
    "3e5e660137bfa785804177fa5604e3eb": "tomato_healthy",
    "b6921f224ba5a12c1ee4c17e4077e549": "unclear_sample",
}


def _demo_diagnose(image_bytes: bytes, language: str) -> Dict[str, Any]:
    """Deterministic offline diagnosis so the Crop Doctor works without an API key."""
    digest = hashlib.md5(image_bytes).hexdigest()
    by_key = {e["disease_key"]: e for e in DEMO_CATALOG}

    if digest in SAMPLE_FINGERPRINTS:
        entry = by_key[SAMPLE_FINGERPRINTS[digest]]
        return _localize_demo(entry, language)

    # Very small payloads → inconclusive path
    if len(image_bytes) < 2500:
        return _localize_demo(by_key["unclear_sample"], language)

    idx = int(digest[:8], 16) % len(DEMO_CATALOG)
    entry = DEMO_CATALOG[idx]
    return _localize_demo(entry, language)


def diagnose_leaf_image(
    image_bytes: bytes,
    language: str = "en",
    db: Session = None,
) -> Dict[str, Any]:
    """Analyze a crop leaf image via Gemini when configured; otherwise rich offline demo."""
    if not image_bytes or len(image_bytes) < 100:
        raise ValueError("Uploaded file is empty or corrupted.")

    from app.config import settings

    api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()
    result: Optional[Dict[str, Any]] = None

    if api_key:
        try:
            result = analyze_leaf_image(
                image_bytes=image_bytes,
                language=language,
                api_key=api_key,
            )
            if isinstance(result, dict):
                result["demo_mode"] = False
                # Normalize candidate confidence to 0–100 for UI bars
                candidates = []
                for cand in result.get("top_candidates") or []:
                    conf = float(cand.get("confidence", 0) or 0)
                    if conf <= 1.0:
                        conf = conf * 100.0
                    candidates.append(
                        {
                            "class_key": cand.get("class_key", "unknown"),
                            "confidence": round(conf, 2),
                        }
                    )
                result["top_candidates"] = candidates
        except Exception as exc:
            print(f"[DiseaseService] Gemini failed, using demo: {exc}")
            result = None

    if not isinstance(result, dict):
        result = _demo_diagnose(image_bytes, language)

    if db is not None:
        try:
            audit = DiagnosisAudit(
                crop=result.get("crop", "Unknown"),
                disease_key=result.get("disease_key", "unknown"),
                confidence=float(result.get("confidence_score", 0.0)),
                is_inconclusive=bool(result.get("is_inconclusive", True)),
                language=language,
            )
            db.add(audit)
            db.commit()
        except Exception as exc:
            db.rollback()
            print(f"[DiagnosisAudit] Could not save diagnosis: {exc}")

    return result
