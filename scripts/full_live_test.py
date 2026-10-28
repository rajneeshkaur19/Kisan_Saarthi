"""Full live end-to-end tests including Gemini when key is present."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from fastapi.testclient import TestClient

from backend.app.main import app

c = TestClient(app)
results = []
key = (os.getenv("GEMINI_API_KEY") or "").strip()


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS" if ok else "FAIL"), "-", name, "-", (detail or "")[:160])


print("GEMINI_API_KEY set:", bool(key), "| prefix:", (key[:8] + "...") if key else "(empty)")
print("GEMINI_MODEL:", os.getenv("GEMINI_MODEL"))

# --- Core offline/online shared endpoints ---
r = c.get("/health")
j = r.json()
check(
    "health",
    r.status_code == 200 and j.get("status") == "ok",
    f"model_loaded={j.get('data', {}).get('model_loaded')}",
)
check("health model_loaded True", j.get("data", {}).get("model_loaded") is True)

r = c.get("/prices", params={"crop": "Wheat", "mandi": "ludhiana"})
j = r.json()
rec = (j.get("data") or {}).get("selected_record") or {}
check("prices", j.get("status") == "ok" and rec.get("current_price", 0) > 0, str(rec.get("current_price")))

r = c.get("/weather", params={"district": "ludhiana"})
j = r.json()
check("weather", j.get("status") == "ok" and "temperature_c" in (j.get("data") or {}), str((j.get("data") or {}).get("condition")))

r = c.post(
    "/eligibility",
    json={
        "land_holding_acres": 3.5,
        "annual_income": "1 - 3 lakh",
        "primary_crop": "Wheat",
        "existing_loan_status": "no_active_loan",
        "bank_account_status": "aadhaar_linked_dbt",
        "language": "en",
    },
)
j = r.json()
score = ((j.get("data") or {}).get("readiness_score") or {}).get("score")
check("eligibility", j.get("status") == "ok" and (score or 0) > 0, f"score={score}")

r = c.post(
    "/checklist",
    json={
        "scheme_id": "PM-KISAN",
        "language": "en",
        "farmer_name": "Live Test Farmer",
        "include_pdf_base64": True,
    },
)
j = r.json()
pdf = ((j.get("data") or {}).get("pdf_base64") or "")
check("checklist+pdf", j.get("status") == "ok" and len(pdf) > 100, f"pdf_len={len(pdf)}")

# --- Live Gemini chat ---
r = c.post(
    "/chat",
    json={
        "message": "In one short paragraph, how does Kisan Credit Card help a wheat farmer?",
        "language": "en",
        "history": [],
    },
)
j = r.json()
data = j.get("data") or {}
check(
    "chat live/gemini",
    j.get("status") == "ok" and len(data.get("response") or "") > 40,
    f"fallback={data.get('is_fallback')} conf={data.get('confidence')} | {(data.get('response') or '')[:100]}",
)

r = c.post(
    "/chat",
    json={
        "message": "PM-KISAN के लिए कौन से दस्तावेज़ चाहिए? संक्षेप में बताएं।",
        "language": "hi",
        "history": [],
    },
)
j = r.json()
data = j.get("data") or {}
check(
    "chat hindi",
    j.get("status") == "ok" and len(data.get("response") or "") > 20,
    (data.get("response") or "")[:100],
)

# --- Live Gemini leaf diagnosis on sample ---
img = (ROOT / "frontend/public/samples/tomato_early_blight.jpg").read_bytes()
r = c.post(
    "/diagnose",
    files={"file": ("tomato_early_blight.jpg", img, "image/jpeg")},
    data={"language": "en"},
)
j = r.json()
d = j.get("data") or {}
check(
    "diagnose tomato sample",
    j.get("status") == "ok" and bool(d.get("disease_name")),
    f"disease={d.get('disease_name')} conf={d.get('confidence_percent')} demo={d.get('demo_mode')} crop={d.get('crop')}",
)

img2 = (ROOT / "frontend/public/samples/wheat_yellow_rust.jpg").read_bytes()
r = c.post(
    "/diagnose",
    files={"file": ("wheat_yellow_rust.jpg", img2, "image/jpeg")},
    data={"language": "en"},
)
j = r.json()
d = j.get("data") or {}
check(
    "diagnose wheat sample",
    j.get("status") == "ok" and bool(d.get("disease_name")),
    f"disease={d.get('disease_name')} conf={d.get('confidence_percent')} demo={d.get('demo_mode')}",
)

# Direct Gemini SDK probe
try:
    from google import genai

    client = genai.Client(api_key=key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    resp = client.models.generate_content(
        model=model,
        contents="Reply with exactly the word PONG",
        config={"temperature": 0, "max_output_tokens": 16},
    )
    text = (resp.text or "").strip()
    check("direct gemini sdk", "PONG" in text.upper(), f"model={model} text={text}")
except Exception as exc:
    check("direct gemini sdk", False, f"{type(exc).__name__}: {exc}")

fails = [x for x in results if not x[1]]
print(f"\nSUMMARY: {len(results) - len(fails)}/{len(results)} passed")
for name, ok, detail in fails:
    print(" -", name, "=>", detail)
sys.exit(1 if fails else 0)
