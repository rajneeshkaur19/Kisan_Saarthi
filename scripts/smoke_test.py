"""End-to-end smoke tests for KisanSaarthi API."""
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app

c = TestClient(app)
results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("OK  " if ok else "FAIL"), name, (detail or "")[:140])


r = c.get("/health")
check("health", r.status_code == 200 and r.json().get("status") == "ok", r.text[:80])

r = c.get("/prices", params={"crop": "Wheat", "mandi": "ludhiana"})
j = r.json()
ok = (
    r.status_code == 200
    and j.get("status") == "ok"
    and (j.get("data") or {}).get("selected_record", {}).get("current_price", 0) > 0
)
check("prices wheat", ok, str((j.get("data") or {}).get("selected_record", {}).get("current_price")))

nearby = (j.get("data") or {}).get("selected_record", {}).get("nearby_comparisons") or []
check(
    "prices nearby fields",
    bool(nearby) and all("distance" in n and "trend" in n for n in nearby),
    str(nearby[:1]),
)

r = c.get("/weather", params={"district": "moga"})
j = r.json()
check(
    "weather moga",
    r.status_code == 200 and j.get("status") == "ok" and j["data"]["district"] == "Moga",
)

payload = {
    "land_holding_acres": 3.5,
    "annual_income": "1 - 3 lakh",
    "primary_crop": "Wheat",
    "existing_loan_status": "no_active_loan",
    "bank_account_status": "aadhaar_linked_dbt",
    "language": "en",
}
r = c.post("/eligibility", json=payload)
j = r.json()
check(
    "eligibility",
    r.status_code == 200 and j.get("status") == "ok" and j["data"]["readiness_score"]["score"] > 0,
    str(j["data"]["readiness_score"]["score"]) if j.get("data") else j,
)

r = c.post(
    "/checklist",
    json={
        "scheme_id": "KCC",
        "language": "en",
        "farmer_name": "Test Farmer",
        "include_pdf_base64": True,
    },
)
j = r.json()
data = j.get("data") or {}
pdf = data.get("pdf_base64") or ""
check(
    "checklist post",
    r.status_code == 200 and j.get("status") == "ok" and len(data.get("required_documents") or []) > 0,
    f"docs={len(data.get('required_documents') or [])} pdf_len={len(pdf)}",
)
check("checklist pdf", len(pdf) > 100, f"len={len(pdf)}")

r = c.post(
    "/chat",
    json={"message": "How do I apply for Kisan Credit Card?", "language": "en", "history": []},
)
j = r.json()
resp = ((j.get("data") or {}).get("response") or "")
check(
    "chat kcc",
    r.status_code == 200 and j.get("status") == "ok" and ("KCC" in resp or "Credit" in resp),
    resp[:100],
)

img = Path("frontend/public/samples/wheat_yellow_rust.jpg").read_bytes()
r = c.post(
    "/diagnose",
    files={"file": ("wheat_yellow_rust.jpg", img, "image/jpeg")},
    data={"language": "en"},
)
j = r.json()
d = j.get("data") or {}
check(
    "diagnose wheat rust",
    r.status_code == 200 and j.get("status") == "ok" and d.get("disease_key") == "wheat_yellow_rust",
    f"{d.get('disease_name')} conf={d.get('confidence_percent')} demo={d.get('demo_mode')}",
)

img2 = Path("frontend/public/samples/unclear_sample.jpg").read_bytes()
r = c.post(
    "/diagnose",
    files={"file": ("unclear_sample.jpg", img2, "image/jpeg")},
    data={"language": "hi"},
)
j = r.json()
d = j.get("data") or {}
check(
    "diagnose unclear hi",
    j.get("status") == "ok" and d.get("is_inconclusive") is True,
    d.get("disease_name"),
)

fails = [x for x in results if not x[1]]
print(f"\nSUMMARY {len(results) - len(fails)}/{len(results)} passed")
if fails:
    raise SystemExit(1)
