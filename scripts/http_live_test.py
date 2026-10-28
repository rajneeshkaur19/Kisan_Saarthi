"""Hit the live server with timeouts to verify Gemini + all features."""
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

BASE = "http://127.0.0.1:8000"
TIMEOUT = httpx.Timeout(180.0, connect=10.0)
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS" if ok else "FAIL"), "-", name, "-", (str(detail) or "")[:180])


def main():
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    model = os.getenv("GEMINI_MODEL", "")
    print("key set:", bool(key), "| model:", model)

    with httpx.Client(base_url=BASE, timeout=TIMEOUT) as client:
        r = client.get("/health")
        j = r.json()
        check("health", r.status_code == 200 and j.get("status") == "ok", j.get("data"))

        r = client.get("/prices", params={"crop": "Wheat", "mandi": "ludhiana"})
        j = r.json()
        price = ((j.get("data") or {}).get("selected_record") or {}).get("current_price")
        check("prices", j.get("status") == "ok" and (price or 0) > 0, price)

        r = client.get("/weather", params={"district": "ludhiana"})
        j = r.json()
        check("weather", j.get("status") == "ok", (j.get("data") or {}).get("spray_advisory_status"))

        r = client.post(
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
        check("eligibility", j.get("status") == "ok" and (score or 0) > 0, score)

        r = client.post(
            "/checklist",
            json={
                "scheme_id": "KCC",
                "language": "en",
                "farmer_name": "Live Tester",
                "include_pdf_base64": True,
            },
        )
        j = r.json()
        pdf_len = len(((j.get("data") or {}).get("pdf_base64") or ""))
        check("checklist pdf", j.get("status") == "ok" and pdf_len > 100, f"pdf_len={pdf_len}")

        print("\n-- Gemini chat --")
        r = client.post(
            "/chat",
            json={
                "message": "Reply in 2 short sentences: what is Kisan Credit Card?",
                "language": "en",
                "history": [],
            },
        )
        j = r.json()
        data = j.get("data") or {}
        check(
            "chat gemini",
            j.get("status") == "ok" and len(data.get("response") or "") > 20,
            f"fallback={data.get('is_fallback')} | {(data.get('response') or '')[:140]}",
        )

        print("\n-- Gemini diagnose --")
        img = (ROOT / "frontend/public/samples/tomato_early_blight.jpg").read_bytes()
        r = client.post(
            "/diagnose",
            files={"file": ("tomato_early_blight.jpg", img, "image/jpeg")},
            data={"language": "en"},
        )
        j = r.json()
        d = j.get("data") or {}
        check(
            "diagnose gemini",
            j.get("status") == "ok" and bool(d.get("disease_name")),
            f"demo={d.get('demo_mode')} disease={d.get('disease_name')} conf={d.get('confidence_percent')} crop={d.get('crop')}",
        )

        print("\n-- Direct SDK --")
        try:
            from google import genai

            g = genai.Client(api_key=key)
            resp = g.models.generate_content(
                model=model,
                contents="Reply with exactly the word PONG",
                config={"temperature": 0, "max_output_tokens": 256},
            )
            text = (resp.text or "").strip()
            check("direct sdk", "PONG" in text.upper(), text or repr(resp))
        except Exception as exc:
            check("direct sdk", False, f"{type(exc).__name__}: {exc}")

    fails = [x for x in results if not x[1]]
    print(f"\nSUMMARY: {len(results) - len(fails)}/{len(results)} passed")
    for name, ok, detail in fails:
        print("FAIL DETAIL:", name, "=>", detail)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
